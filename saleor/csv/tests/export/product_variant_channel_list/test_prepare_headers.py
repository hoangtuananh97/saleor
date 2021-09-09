from ....product_variant_channel_list.product_variant_channel_list_headers import (
    get_export_fields_and_headers_info,
    get_product_export_fields_and_headers,
)


def test_get_export_fields_and_headers_no_fields():
    export_fields, file_headers = get_product_export_fields_and_headers({})

    assert export_fields == []
    assert file_headers == []


def test_get_export_fields_and_headers_info(warehouses):
    # given
    export_info = {
        "fields": [
            "fc_store_code",
            "fc_store_name",
            "article_number",
            "article_name",
            "purchase_price",
            "sale_price",
            "stock_on_hand",
            "stock_available",
        ],
    }

    expected_file_headers = [
        "Fc Store Code",
        "Fc Store Name",
        "Article Number",
        "Article Name",
        "Purchase Price",
        "Sale Price",
        "Stock On Hand",
        "Stock Available",
    ]

    # when
    export_fields, file_headers, data_headers = get_export_fields_and_headers_info(
        export_info
    )
    # then
    expected_fields = [
        "channel__slug",
        "channel__name",
        "variant__sku",
        "variant__product__name",
        "cost_price_amount",
        "price_amount",
        "stock_on_hand",
        "stock_available",
    ]
    excepted_headers = expected_fields
    assert expected_file_headers == file_headers
    assert set(export_fields) == set(expected_fields)
    assert data_headers == excepted_headers
