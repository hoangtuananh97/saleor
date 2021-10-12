import django_filters
from graphene_django.filter import GlobalIDMultipleChoiceFilter

from saleor.graphql.core.filters import (
    ObjectTypeFilter,
    filter_created_at,
    filter_updated_at,
)
from saleor.graphql.core.types import FilterInputObjectType
from saleor.graphql.core.types.common import DateTimeRangeInput, IntRangeInput
from saleor.graphql.product.filters_product_class import (
    ChannelListingFilter,
    ChannelListingFilterInput,
)
from saleor.graphql.utils.filters import filter_range_field
from saleor.product_max_min.models import ProductMaxMin


def filter_range_min_level(qs, _, value):
    return filter_range_field(qs, "min_level", value)


def filter_range_max_level(qs, _, value):
    return filter_range_field(qs, "max_level", value)


class BaseProductMaxMinFilter(django_filters.FilterSet):
    created_at = ObjectTypeFilter(
        input_class=DateTimeRangeInput, method=filter_created_at
    )
    updated_at = ObjectTypeFilter(
        input_class=DateTimeRangeInput, method=filter_updated_at
    )
    min_level = ObjectTypeFilter(
        input_class=IntRangeInput, method=filter_range_min_level
    )
    max_level = ObjectTypeFilter(
        input_class=IntRangeInput, method=filter_range_max_level
    )
    created_by_ids = GlobalIDMultipleChoiceFilter(field_name="created_by_id")
    updated_by_ids = GlobalIDMultipleChoiceFilter(field_name="updated_by_id")
    listing_ids = GlobalIDMultipleChoiceFilter(field_name="listing_id")

    class Meta:
        model = ProductMaxMin
        fields = [
            "min_level",
            "max_level",
            "created_at",
            "updated_at",
            "created_by_ids",
            "updated_by_ids",
        ]


class ProductMaxMinFilter(BaseProductMaxMinFilter):
    channel_listing = ObjectTypeFilter(
        input_class=ChannelListingFilterInput, method="filter_channel_listing"
    )

    class Meta:
        model = ProductMaxMin
        fields = [
            "min_level",
            "max_level",
            "created_at",
            "updated_at",
            "created_by_ids",
            "updated_by_ids",
            "channel_listing",
        ]

    def filter_channel_listing(self, queryset, name, value):
        return ChannelListingFilter(data=value, queryset=queryset).qs


class ProductMaxMinFilterInput(FilterInputObjectType):
    class Meta:
        filterset_class = ProductMaxMinFilter
