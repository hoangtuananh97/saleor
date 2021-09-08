from django.db.models import OuterRef
from django.db.models.aggregates import Sum
from django.db.models.expressions import Subquery
from django.db.models.fields import IntegerField
from django.db.models.functions import Coalesce

from saleor.csv.product_variant_channel_list import \
    ProductVariantChannelListExportFields
from saleor.csv.product_variant_channel_list.product_variant_channel_list_data import \
    get_products_data
from saleor.product.models import ProductVariantChannelListing
from saleor.warehouse.models import Stock, Allocation


def test_get_products_variant_channel_list_data(stock, allocations):
    # given
    product_variant_channel_list = ProductVariantChannelListing.objects.all()
    export_fields = set(
        value
        for mapping in
        ProductVariantChannelListExportFields.HEADERS_TO_FIELDS_MAPPING.values()
        for value in mapping.values()
    )
    warehouse_ids = []
    attribute_ids = []
    channel_ids = []

    # when
    result_data = get_products_data(
        product_variant_channel_list, export_fields, attribute_ids, warehouse_ids,
        channel_ids
    )
    # then
    expected_data = []
    stocks = Stock.objects.values('product_variant_id'). \
        annotate(total_stock=Sum('quantity'))

    stock_allocations = (
        Allocation.objects.values('stock_id')
            .filter(quantity_allocated__gt=0, stock_id=OuterRef("pk"))
            .values_list(Sum("quantity_allocated"))
    )
    stock_allocated_subquery = Subquery(queryset=stock_allocations,
                                        output_field=IntegerField())

    allocations = Stock.objects.annotate(
        stock_allocation=Coalesce(stock_allocated_subquery, 0)). \
        values('product_variant_id', 'stock_allocation')

    for item in product_variant_channel_list:
        variant_id = item.variant_id
        total_stock = 0
        total_allocation = 0
        for stock in stocks:
            if stock['product_variant_id'] == variant_id:
                total_stock = stock['total_stock']
                break
        for allocation in allocations:
            if allocation['product_variant_id'] == variant_id:
                total_allocation = allocation['stock_allocation']
                break

        obj = {
            "price_amount": item.price_amount,
            "channel__name": item.channel.name,
            "variant__sku": item.variant.sku,
            "variant__product__name": item.variant.product.name,
            "cost_price_amount": item.cost_price_amount,
            "channel__slug": item.channel.slug,
            "total_stock_availability": total_stock - total_allocation,
            "total_stock_allocated": total_allocation,
        }
        expected_data.append(obj)
    assert result_data == expected_data
