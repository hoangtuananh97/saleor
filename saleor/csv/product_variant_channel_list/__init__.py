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
            "stock_on_hand": "stock_on_hand",
            "stock_available": "stock_available",
        },
    }
