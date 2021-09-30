import django_filters
import graphene
from django.db.models import Q
from graphene_django.filter import GlobalIDMultipleChoiceFilter

from saleor.channel.models import Channel
from saleor.graphql.attribute.types import AttributeInput
from saleor.graphql.core.filters import MetadataFilter, \
    ObjectTypeFilter
from saleor.graphql.product.filters import ProductFilter, ProductVariantFilter
from saleor.graphql.utils.filters import filter_fields_containing_value
from saleor.product.models import ProductVariant, Product, ProductVariantChannelListing


def filter_metadata(qs, _, value):
    for metadata_item in value:
        if metadata_item.value:
            qs = qs.filter(
                Q(metadata__current__contains={
                    metadata_item.key: metadata_item.value
                })
                | Q(metadata__previous__contains={
                    metadata_item.key: metadata_item.value
                })
            )
        else:
            qs = qs.filter(
                Q(metadata__current__has_key=metadata_item.key)
                | Q(metadata__previous__has_key=metadata_item.key)
            )
    return qs


class ChannelListingProductVariantFilter(ProductVariantFilter):
    ids = GlobalIDMultipleChoiceFilter(field_name="id")


class ChannelListingProductFilterInput(graphene.InputObjectType):
    metadata = graphene.List(
        MetadataFilter, required=False, description="Filter variant metadata."
    )
    ids = graphene.List(
        graphene.NonNull(graphene.ID), required=False, description="Filter product ids."
    )
    search = graphene.String(required=False, description="Filter name or slug product.")
    attributes = graphene.List(
        AttributeInput, required=False, description="Filter attributes of product."
    )


class ChannelListingProductVariantFilterInput(graphene.InputObjectType):
    metadata = graphene.List(
        MetadataFilter, required=False, description="Filter variant metadata."
    )
    ids = graphene.List(
        graphene.NonNull(graphene.ID), required=False, description="Filter variant ids."
    )
    search = graphene.String(required=False, description="Filter name or slug variant.")
    product = graphene.Field(
        ChannelListingProductFilterInput, required=False, description="Filter variant."
    )


class ChannelListingChannelFilterInput(graphene.InputObjectType):
    ids = graphene.List(
        graphene.NonNull(graphene.ID), required=False, description="Filter channel ids."
    )
    search = graphene.String(required=False, description="Filter name or slug channel.")


class ChannelListingChannelFilter(django_filters.FilterSet):
    search = ObjectTypeFilter(
        input_class=ChannelListingChannelFilterInput,
        method=filter_fields_containing_value("name", "slug"),
    )
    ids = GlobalIDMultipleChoiceFilter(field_name="id")

    class Meta:
        model = Channel
        fields = ["search", "ids"]


class FilterFieldChannelListing:
    def filter_channel(self, qs, _, channel):
        qs_channel = Channel.objects.values_list("id", flat=True)
        qs_channel = ChannelListingChannelFilter(data=channel, queryset=qs_channel).qs
        qs = qs.filter(listing__channel_id__in=qs_channel)
        return qs

    def filter_metadata(self, qs, _, metadata):
        qs_listing = ProductVariantChannelListing.objects.values_list("id", flat=True)
        qs_listing = filter_metadata(qs_listing, _, metadata)
        qs = qs.filter(listing_id__in=qs_listing)
        return qs

    def filter_variant(self, qs, _, variant):
        product = variant.get("product")
        qs_variant = ProductVariant.objects.values_list("id", flat=True)
        qs_variant = ChannelListingProductVariantFilter(
            data=variant, queryset=qs_variant
        ).qs
        if product:
            qs_variant = self.filter_product_by_variant(qs_variant, _, product)
        qs = qs.filter(listing__variant_id__in=qs_variant)
        return qs

    def filter_product_by_variant(self, qs_variant, _, product):
        qs_product = Product.objects.values_list("id", flat=True)
        qs_product = ProductFilter(data=product, queryset=qs_product).qs
        qs_variant = qs_variant.filter(product_id__in=qs_product)
        return qs_variant


filter_channel_listing = FilterFieldChannelListing()
