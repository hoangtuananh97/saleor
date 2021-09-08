class ProductVariantChannelListExportFields:
    """Data structure with fields for product Variant Channel List export."""

    HEADERS_TO_FIELDS_MAPPING = {
        "fields": {
            "fc_store_code": "channel__slug",
            "fc_store_name": "channel__name",
            "article_number": "variant__sku",
            "article_name": "variant__product__name",
            "purchase_price": "cost_price_amount",
            "sale_price": "price_amount",
            "total_stock_availability": "total_stock_availability",
            "total_stock_allocated": "total_stock_allocated",
        },
    }

    WAREHOUSE_FIELDS = {
        "slug": "variant__stocks__warehouse__slug",
        "quantity": "variant__stocks__quantity",
        "warehouse_pk": "variant__stocks__warehouse__id",
    }
