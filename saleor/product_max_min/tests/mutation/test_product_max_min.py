import graphene

from saleor.graphql.tests.utils import assert_no_permission, get_graphql_content
from saleor.product_max_min.error_codes import ProductMaxMinErrorCode
from saleor.product_max_min.models import ProductMaxMin

QUERY_CREATE_PRODUCT_MAX_MIN = """
mutation ProductMaxMinCreate($input: ProductMaxMinInput!){
    productMaxMinCreate(input: $input){
        productMaxMin{
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


def test_product_max_min_create(
    staff_api_client, channel_variant, permission_manage_product_max_min
):
    # give
    listing_id_expect = channel_variant.id
    listing_id_convert = graphene.Node.to_global_id(
        "ProductVariantChannelListing", listing_id_expect
    )
    param = {"listing": listing_id_convert, "maxLevel": 11, "minLevel": 2}
    query = QUERY_CREATE_PRODUCT_MAX_MIN
    variables = {"input": param}

    # when
    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_product_max_min]
    )

    # then
    content = get_graphql_content(response)
    data = content["data"]["productMaxMinCreate"]["productMaxMin"]
    assert ProductMaxMin.objects.count() == 1
    assert param["maxLevel"] == data["maxLevel"]
    assert param["minLevel"] == data["minLevel"]


def test_product_max_min_create_error(
    staff_api_client, channel_variant, permission_manage_product_max_min
):
    # give
    listing_id_expect = channel_variant.id
    listing_id_convert = graphene.Node.to_global_id(
        "ProductVariantChannelListing", listing_id_expect
    )
    param = {"listing": listing_id_convert, "maxLevel": 11, "minLevel": 222}
    query = QUERY_CREATE_PRODUCT_MAX_MIN
    variables = {"input": param}

    # when
    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_product_max_min]
    )

    # then
    content = get_graphql_content(response)
    error = content["data"]["productMaxMinCreate"]["errors"][0]
    assert error["code"] == str.upper(ProductMaxMinErrorCode.INVALID.value)


def test_product_max_min_create_no_permission(
    staff_api_client, channel_variant, product_max_min
):
    # give
    listing_id_expect = channel_variant.id
    listing_id_convert = graphene.Node.to_global_id(
        "ProductVariantChannelListing", listing_id_expect
    )
    param = {"listing": listing_id_convert, "maxLevel": 11, "minLevel": 2}
    query = QUERY_CREATE_PRODUCT_MAX_MIN
    variables = {"input": param}

    # when
    response = staff_api_client.post_graphql(query, variables)

    # then
    assert_no_permission(response)


QUERY_UPDATE_PRODUCT_MAX_MIN = """
mutation ProductMaxMinUpdate($id: ID!, $input: ProductMaxMinInput!){
    productMaxMinUpdate(id: $id, input: $input){
        productMaxMin{
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


def test_product_max_min_update(
    staff_api_client,
    channel_variant,
    product_max_min,
    permission_manage_product_max_min,
):
    # give
    product_max_min_id = graphene.Node.to_global_id("ProductMaxMin", product_max_min.id)
    listing_id_convert = graphene.Node.to_global_id(
        "ProductVariantChannelListing", channel_variant.id
    )
    param = {"listing": listing_id_convert, "maxLevel": 11, "minLevel": 2}
    query = QUERY_UPDATE_PRODUCT_MAX_MIN
    variables = {"id": product_max_min_id, "input": param}

    # when
    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_product_max_min]
    )

    # then
    content = get_graphql_content(response)
    data = content["data"]["productMaxMinUpdate"]["productMaxMin"]
    listing_id = data["listing"]["id"]
    _, listing_id = graphene.Node.from_global_id(listing_id)
    assert ProductMaxMin.objects.count() == 1
    assert param["maxLevel"] == data["maxLevel"]
    assert param["minLevel"] == data["minLevel"]


def test_product_max_min_update_error(
    staff_api_client,
    channel_variant,
    product_max_min,
    permission_manage_product_max_min,
):
    # give
    product_max_min_id = graphene.Node.to_global_id("ProductMaxMin", product_max_min.id)
    listing_id_convert = graphene.Node.to_global_id(
        "ProductVariantChannelListing", channel_variant.id
    )
    param = {"listing": listing_id_convert, "maxLevel": 11, "minLevel": 2}
    query = QUERY_UPDATE_PRODUCT_MAX_MIN
    variables = {"id": product_max_min_id, "input": param}

    # when
    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_product_max_min]
    )

    # then
    content = get_graphql_content(response)
    error = content["data"]["productMaxMinCreate"]["errors"][0]
    assert error["code"] == str.upper(ProductMaxMinErrorCode.INVALID.value)


def test_product_max_min_update_no_permission(
    staff_api_client, channel_variant, product_max_min
):
    # give
    product_max_min_id = graphene.Node.to_global_id("ProductMaxMin", product_max_min.id)
    listing_id_convert = graphene.Node.to_global_id(
        "ProductVariantChannelListing", channel_variant.id
    )
    param = {"listing": listing_id_convert, "maxLevel": 11, "minLevel": 2}
    query = QUERY_UPDATE_PRODUCT_MAX_MIN
    variables = {"id": product_max_min_id, "input": param}

    # when
    response = staff_api_client.post_graphql(query, variables)

    # then
    assert_no_permission(response)


QUERY_DELETE_PRODUCT_MAX_MIN = """
mutation ProductMaxMinDelete($id: ID!){
    productMaxMinDelete(id: $id){
        productMaxMin{
            id
        }
        errors{
            code
        }
    }
}
"""


def test_product_max_min_delete(staff_api_client, channel_variant, product_max_min):
    # give
    product_max_min_id = graphene.Node.to_global_id("ProductMaxMin", product_max_min.id)
    query = QUERY_DELETE_PRODUCT_MAX_MIN
    variables = {"id": product_max_min_id}

    # when
    response = staff_api_client.post_graphql(query, variables)

    # then
    assert_no_permission(response)


def test_product_max_min_delete_no_permission(
    staff_api_client,
    channel_variant,
    product_max_min,
    permission_manage_product_max_min,
):
    # give
    product_max_min_id = graphene.Node.to_global_id("ProductMaxMin", product_max_min.id)
    query = QUERY_DELETE_PRODUCT_MAX_MIN
    variables = {"id": product_max_min_id}

    # when
    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_product_max_min]
    )

    # then
    assert_no_permission(response)
