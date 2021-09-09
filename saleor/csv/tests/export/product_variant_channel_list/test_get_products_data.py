from django.db.models.aggregates import Sum

from saleor.csv.product_variant_channel_list import (
    ProductVariantChannelListExportFields,
)
from saleor.csv.product_variant_channel_list.product_variant_channel_list_data import (
    get_products_variant_channel_list_data,
    get_total_quality_allocation,
)
from saleor.product.models import ProductVariantChannelListing
from saleor.warehouse.models import Stock


def test_get_products_variant_channel_list_data(stock, allocations):
    # given
    product_variant_channel_list = ProductVariantChannelListing.objects.all()
    export_fields = set(
        value
        for mapping in ProductVariantChannelListExportFields.HEADERS_TO_FIELDS_MAPPING.values()  # noqa
        for value in mapping.values()
    )

    # when
    result_data = get_products_variant_channel_list_data(
        product_variant_channel_list,
        export_fields,
    )
    # then
    expected_data = []
    stocks = Stock.objects.values("product_variant_id").annotate(
        total_stock=Sum("quantity")
    )

    obj_allocation = get_total_quality_allocation()

    for item in product_variant_channel_list:
        variant_id = item.variant_id
        total_stock = 0
        for stock in stocks:
            if stock["product_variant_id"] == variant_id:
                total_stock = stock["total_stock"]
                break

        total_allocation = obj_allocation.get(variant_id, 0)

        obj = {
            "price_amount": item.price_amount,
            "channel__name": item.channel.name,
            "variant__sku": item.variant.sku,
            "variant__product__name": item.variant.product.name,
            "cost_price_amount": item.cost_price_amount,
            "channel__slug": item.channel.slug,
            "stock_on_hand": total_stock,
            "stock_available": total_stock - total_allocation,
        }
        expected_data.append(obj)
    assert result_data == expected_data
