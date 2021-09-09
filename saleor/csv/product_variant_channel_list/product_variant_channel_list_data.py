from typing import TYPE_CHECKING, Dict, List, Set, Union

from django.db.models import OuterRef
from django.db.models.aggregates import Sum
from django.db.models.expressions import Subquery
from django.db.models.fields import IntegerField
from django.db.models.functions import Coalesce

from saleor.csv.product_variant_channel_list import (
    ProductVariantChannelListExportFields,
)
from saleor.warehouse.models import Allocation, Stock

if TYPE_CHECKING:
    from django.db.models import QuerySet


def get_products_variant_channel_list_data(
    queryset: "QuerySet",
    export_fields: Set[str],
) -> List[Dict[str, Union[str, bool]]]:
    """Create data list of products variant channel list."""

    products_variant_channel_list_data = []

    product_fields = set(
        ProductVariantChannelListExportFields.HEADERS_TO_FIELDS_MAPPING[
            "fields"
        ].values()
    )

    product_export_fields = export_fields & product_fields

    product_export_fields.add("stock_on_hand")
    product_export_fields.remove("stock_available")
    product_export_fields.add("variant_id")

    obj_allocation = get_total_quality_allocation()

    stock_on_hand = (
        Stock.objects.values("product_variant_id")
        .filter(product_variant_id=OuterRef("variant"))
        .values_list(Sum("quantity"))
    )
    stock_on_hand_subquery = Subquery(
        queryset=stock_on_hand, output_field=IntegerField()
    )

    products_data = (
        queryset.annotate(
            stock_on_hand=Coalesce(stock_on_hand_subquery, 0),
        )
        .order_by(
            "pk",
        )
        .values(*product_export_fields)
        .distinct(
            "pk",
        )
    )
    for product_data in products_data:
        variant_id = product_data.pop("variant_id")
        stock_allocation: Dict[int, str] = obj_allocation.get(variant_id, 0)
        product_data["stock_available"] = (
            product_data["stock_on_hand"] - stock_allocation
        )
        products_variant_channel_list_data.append(product_data)
    return products_variant_channel_list_data


def get_total_quality_allocation():
    # Get total quality allocate by product variant id
    obj_allocation = {}
    stock_allocations = (
        Allocation.objects.values("stock_id")
        .filter(quantity_allocated__gt=0, stock_id=OuterRef("pk"))
        .values_list(Sum("quantity_allocated"))
    )
    stock_allocated_subquery = Subquery(
        queryset=stock_allocations, output_field=IntegerField()
    )

    stock_allocations = Stock.objects.annotate(
        quantity_allocated=Coalesce(stock_allocated_subquery, 0)
    ).values("product_variant_id", "quantity_allocated")

    for stock_allocation in stock_allocations:
        item_id = stock_allocation["product_variant_id"]
        item_quantity = stock_allocation["quantity_allocated"]
        obj_allocation[item_id] = obj_allocation.get(item_id, 0) + item_quantity

    return obj_allocation
