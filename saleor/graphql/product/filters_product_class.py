from typing import Dict, Iterable

import django_filters
import graphene
from django.db.models import Q
from graphene_django.filter import GlobalIDMultipleChoiceFilter

from ...product.models import ProductVariantChannelListing
from ...product_class import ProductClassRecommendationStatus
from ...product_class.models import ProductClassRecommendation
from ..core.filters import (
    MetadataFilter,
    ObjectTypeFilter,
    filter_created_at,
    filter_updated_at,
)
from ..core.types import FilterInputObjectType
from ..core.types.common import DateTimeRangeInput
from ..utils.filters import filter_range_field
from .filters_relation_product_class import (
    ChannelListingChannelFilterInput,
    ChannelListingProductVariantFilterInput,
    filter_channel_listing,
)

T_PRODUCT_FILTER_QUERIES = Dict[int, Iterable[int]]


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
