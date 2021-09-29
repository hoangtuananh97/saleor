from typing import Dict, Iterable

import django_filters
import graphene
from django.db.models import Q
from graphene_django.filter import GlobalIDMultipleChoiceFilter

from ...channel.models import Channel
from ...product.models import Product, ProductVariant, ProductVariantChannelListing
from ...product_class import ProductClassRecommendationStatus
from ...product_class.models import ProductClassRecommendation
from ..attribute.types import AttributeInput
from ..core.filters import (
    MetadataFilter,
    ObjectTypeFilter,
    filter_created_at,
    filter_metadata,
    filter_updated_at,
)
from ..core.types import FilterInputObjectType
from ..core.types.common import DateTimeRangeInput
from ..utils.filters import filter_fields_containing_value, filter_range_field
from .filters import ProductFilter, ProductVariantFilter

T_PRODUCT_FILTER_QUERIES = Dict[int, Iterable[int]]


class ChannelListingProductVariantFilter(ProductVariantFilter):
    ids = GlobalIDMultipleChoiceFilter(field_name="id")


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


def filter_approved_at(qs, _, value):
    return filter_range_field(qs, "approved_at", value)


def filter_product_class_search(qs, _, value):
    if value:
        qs = qs.filter(
            Q(product_class_qty__icontains=value)
            | Q(product_class_value__icontains=value)
            | Q(product_class_recommendation__icontains=value)
        )
    return qs


def filter_product_class_status(qs, _, value):
    if value == ProductClassRecommendationStatus.DRAFT:
        return qs.filter(status=value)
    if value == ProductClassRecommendationStatus.SUBMITTED:
        return qs.filter(status=value)
    if value == ProductClassRecommendationStatus.APPROVED:
        return qs.filter(status=value)
    return qs


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


class ChannelListingFilterInput(graphene.InputObjectType):
    metadata = graphene.List(
        MetadataFilter, required=False, description="Filter listing metadata."
    )
    channel_listing_ids = graphene.List(
        graphene.NonNull(graphene.ID),
        required=False,
        description="Filter channel listing ids.",
    )
    product_variant = graphene.Field(
        ChannelListingProductVariantFilterInput,
        required=False,
        description="Filter product variant",
    )
    channel = graphene.Field(
        ChannelListingChannelFilterInput, required=False, description="Filter channel"
    )


class ChannelListingChannelFilter(django_filters.FilterSet):
    search = ObjectTypeFilter(
        input_class=ChannelListingChannelFilterInput,
        method=filter_fields_containing_value("name", "slug"),
    )
    ids = GlobalIDMultipleChoiceFilter(field_name="id")

    class Meta:
        model = Channel
        fields = ["search", "ids"]


class ChannelListingFilter(django_filters.FilterSet):
    ids = GlobalIDMultipleChoiceFilter(field_name="id")
    metadata = ObjectTypeFilter(input_class=MetadataFilter, method="filter_metadata")
    product_variant = ObjectTypeFilter(
        input_class=ChannelListingProductVariantFilterInput,
        method="filter_product_variant",
    )
    channel = ObjectTypeFilter(
        input_class=ChannelListingChannelFilterInput, method="filter_channel"
    )

    def filter_product_variant(self, queryset, name, value):
        return filter_channel_listing.filter_variant(queryset, name, value)

    def filter_channel(self, queryset, name, value):
        return filter_channel_listing.filter_channel(queryset, name, value)

    def filter_metadata(self, queryset, name, value):
        return filter_channel_listing.filter_metadata(queryset, name, value)

    class Meta:
        model = ProductVariantChannelListing
        fields = ["ids", "product_variant", "channel"]


class ProductClassRecommendationFilter(django_filters.FilterSet):
    channel_listing = ObjectTypeFilter(
        input_class=ChannelListingFilterInput, method="filter_channel_listing"
    )
    created_at = ObjectTypeFilter(
        input_class=DateTimeRangeInput, method=filter_created_at
    )
    updated_at = ObjectTypeFilter(
        input_class=DateTimeRangeInput, method=filter_updated_at
    )
    approved_at = ObjectTypeFilter(
        input_class=DateTimeRangeInput, method=filter_approved_at
    )

    search = django_filters.CharFilter(method=filter_product_class_search)
    status = django_filters.CharFilter(method=filter_product_class_status)
    created_by_ids = GlobalIDMultipleChoiceFilter(field_name="created_by_id")
    updated_by_ids = GlobalIDMultipleChoiceFilter(field_name="updated_by_id")
    approved_by_ids = GlobalIDMultipleChoiceFilter(
        field_name="approved_by_id",
    )
    listing_ids = GlobalIDMultipleChoiceFilter(field_name="listing_id")

    class Meta:
        model = ProductClassRecommendation
        fields = [
            "search",
            "created_at",
            "updated_at",
            "approved_at",
            "status",
            "created_by_ids",
            "updated_by_ids",
            "approved_by_ids",
            "channel_listing",
        ]

    def filter_channel_listing(self, queryset, name, value):
        return ChannelListingFilter(data=value, queryset=queryset).qs


class ProductClassRecommendationFilterInput(FilterInputObjectType):
    class Meta:
        filterset_class = ProductClassRecommendationFilter
