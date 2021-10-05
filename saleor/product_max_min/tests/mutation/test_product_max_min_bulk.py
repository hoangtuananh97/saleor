import graphene

from saleor.graphql.tests.utils import get_graphql_content, assert_no_permission
from saleor.product_max_min.error_codes import ProductMaxMinErrorCode
from saleor.product_max_min.models import ProductMaxMin

QUERY_BULK_CREATE_PRODUCT_MAX_MIN = """
mutation ProductMaxMinBulkCreate($input: [ProductMaxMinInput!]!){
    productMaxMinBulkCreate(input: $input){
        productsMaxMin{
            id
            maxLevel
            minLevel
        }
        errors{
            code
        }
    }
}
"""


def test_product_max_min_bulk_create(
        staff_api_client, channel_variant, permission_manage_product_max_min
):
    # give
    listing_id_convert = graphene.Node.to_global_id(
        "ProductVariantChannelListing", channel_variant.id
    )
    param = [
        {
            "listing": listing_id_convert,
            "maxLevel": 11,
            "minLevel": 2
        }
    ]
    query = QUERY_BULK_CREATE_PRODUCT_MAX_MIN
    variables = {"input": param}

    # when
    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_product_max_min]
    )

    # then
    content = get_graphql_content(response)
    data = content["data"]["productMaxMinBulkCreate"]["productsMaxMin"][0]
    assert ProductMaxMin.objects.count() == 1
    assert param[0]["maxLevel"] == data["maxLevel"]
    assert param[0]["minLevel"] == data["minLevel"]


def test_product_max_min_bulk_create_error(
        staff_api_client, channel_variant, permission_manage_product_max_min
):
    # give
    listing_id_expect = channel_variant.id
    listing_id_convert = graphene.Node.to_global_id(
        "ProductVariantChannelListing", listing_id_expect
    )
    param = [
        {
            "listing": listing_id_convert,
            "maxLevel": 11,
            "minLevel": 212
        }
    ]
    query = QUERY_BULK_CREATE_PRODUCT_MAX_MIN
    variables = {"input": param}

    # when
    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_product_max_min]
    )

    # then
    content = get_graphql_content(response)
    error = content["data"]["productMaxMinBulkCreate"]["errors"][0]
    assert error["code"] == str.upper(ProductMaxMinErrorCode.INVALID.value)


def test_product_max_min_bulk_create_no_permission(
        staff_api_client, channel_variant, product_max_min
):
    # give
    listing_id_expect = channel_variant.id
    listing_id_convert = graphene.Node.to_global_id(
        "ProductVariantChannelListing", listing_id_expect
    )
    param = [
        {
            "listing": listing_id_convert,
            "maxLevel": 11,
            "minLevel": 2111
        }
    ]
    query = QUERY_BULK_CREATE_PRODUCT_MAX_MIN
    variables = {"input": param}

    # when
    response = staff_api_client.post_graphql(query, variables)

    # then
    assert_no_permission(response)


QUERY_BULK_UPDATE_PRODUCT_MAX_MIN = """
mutation ProductMaxMinBulkUpdate($input: [ProductMaxMinBulkUpdateInput!]!){
    productMaxMinBulkUpdate(input: $input){
        count
        productsMaxMin{
            id
            maxLevel
            minLevel
        }
        errors{
            code
        }
    }
}
"""


def test_product_max_min_bulk_update(
        staff_api_client, channel_variant, permission_manage_product_max_min,
        product_max_min
):
    # give
    product_max_min_id = graphene.Node.to_global_id(
        "ProductMaxMin", product_max_min.id
    )
    listing_id_convert = graphene.Node.to_global_id(
        "ProductVariantChannelListing", channel_variant.id
    )
    param = [
        {
            "id": product_max_min_id,
            "listing": listing_id_convert,
            "maxLevel": 11,
            "minLevel": 2
        }
    ]
    query = QUERY_BULK_UPDATE_PRODUCT_MAX_MIN
    variables = {"input": param}

    # when
    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_product_max_min]
    )

    # then
    content = get_graphql_content(response)
    product_max_min.refresh_from_db()
    data = content["data"]["productMaxMinBulkUpdate"]
    obj = data["productsMaxMin"][0]
    assert len(param) == data["count"]
    assert product_max_min.max_level == obj["maxLevel"]
    assert product_max_min.min_level == obj["minLevel"]


def test_product_max_min_bulk_update_error(
        staff_api_client, channel_variant, permission_manage_product_max_min,
        product_max_min
):
    # give
    product_max_min_id = graphene.Node.to_global_id(
        "ProductMaxMin", product_max_min.id
    )
    listing_id_convert = graphene.Node.to_global_id(
        "ProductVariantChannelListing", channel_variant.id
    )
    param = [
        {
            "id": product_max_min_id,
            "listing": listing_id_convert,
            "maxLevel": 11,
            "minLevel": 2111
        }
    ]
    query = QUERY_BULK_UPDATE_PRODUCT_MAX_MIN
    variables = {"input": param}

    # when
    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_product_max_min]
    )

    # then
    content = get_graphql_content(response)
    error = content["data"]["productMaxMinBulkUpdate"]["errors"][0]
    assert error["code"] == str.upper(ProductMaxMinErrorCode.INVALID.value)


def test_product_max_min_bulk_update_no_permission(
        staff_api_client, channel_variant, permission_manage_product_max_min,
        product_max_min
):
    # give
    product_max_min_id = graphene.Node.to_global_id(
        "ProductMaxMin", product_max_min.id
    )
    listing_id_convert = graphene.Node.to_global_id(
        "ProductVariantChannelListing", channel_variant.id
    )
    param = [
        {
            "id": product_max_min_id,
            "listing": listing_id_convert,
            "maxLevel": 11,
            "minLevel": 2111
        }
    ]
    query = QUERY_BULK_UPDATE_PRODUCT_MAX_MIN
    variables = {"input": param}

    # when
    response = staff_api_client.post_graphql(
        query, variables
    )

    # then
    assert_no_permission(response)


QUERY_BULK_DELETE_PRODUCT_MAX_MIN = """
mutation ProductMaxMinBulkDelete($ids: [ID!]!){
    productMaxMinBulkDelete(ids: $ids){
        count
        errors{
            code
        }
    }
}
"""


def test_product_max_min_bulk_delete(
        staff_api_client, channel_variant, permission_manage_product_max_min,
        product_max_min
):
    # give
    product_max_min_id = graphene.Node.to_global_id(
        "ProductMaxMin", product_max_min.id
    )
    product_max_min_ids = [product_max_min_id]
    query = QUERY_BULK_DELETE_PRODUCT_MAX_MIN
    variables = {"ids": product_max_min_ids}

    # when
    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_product_max_min]
    )

    # then
    content = get_graphql_content(response)
    data = content["data"]["productMaxMinBulkDelete"]
    objects = ProductMaxMin.objects.filter(id__in=[product_max_min.id])
    assert data["count"] == len(product_max_min_ids)
    assert len(objects) == 0


def test_product_max_min_bulk_delete_no_permission(
        staff_api_client, product_max_min
):
    # give
    product_max_min_id = graphene.Node.to_global_id(
        "ProductMaxMin", product_max_min.id
    )
    query = QUERY_BULK_DELETE_PRODUCT_MAX_MIN
    variables = {"ids": [product_max_min_id]}

    # when
    response = staff_api_client.post_graphql(query, variables)

    # then
    assert_no_permission(response)
