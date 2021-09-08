from ....product_variant_channel_list.product_variant_channel_list_headers import \
    get_product_export_fields_and_headers, get_export_fields_and_headers_info


def test_get_export_fields_and_headers_no_fields():
    export_fields, file_headers = get_product_export_fields_and_headers({})

    assert export_fields == []
    assert file_headers == []


def test_get_export_fields_and_headers_info(warehouses):
    # given
    export_info = {
        "fields": [
            "FC_STORE_CODE",
            "FC_STORE_NAME",
            "ARTICLE_NUMBER",
            "ARTICLE_NAME",
            "PURCHASE_PRICE",
            "SALE_PRICE",
            "TOTAL_STOCK_AVAILABILITY",
            "TOTAL_STOCK_ALLOCATED"
        ],
    }

    expected_file_headers = [
        "Fc Store Code",
        "Fc Store Name",
        "Article Number",
        "Article Name",
        "Purchase Price",
        "Sale Price",
        "Total Stock Availability",
        "Total Stock Allocated",
    ]

    # when
    export_fields, file_headers, data_headers = get_export_fields_and_headers_info(
        export_info
    )

    # then
    expected_fields = [
        "id",
        "collections__slug",
        "description_as_str",
    ]

    warehouse_headers = [f"{w.slug} (warehouse quantity)" for w in warehouses]

    excepted_headers = (
            expected_fields
            + warehouse_headers
    )

    expected_file_headers += (
        warehouse_headers
    )
    assert expected_file_headers == file_headers
    assert set(export_fields) == set(expected_fields)
    assert data_headers == excepted_headers
