import graphene

from saleor.graphql.tests.utils import get_graphql_content, assert_no_permission

QUERY_PRODUCT_CLASS_CREATE = """
mutation ProductClassRecommendationCreate($input: ProductClassRecommendationInput!){
    productClassRecommendationCreate(input: $input){
        productClassRecommendation{
            id
            listing{
                id
            }
            productClassQty
            productClassValue
            productClassRecommendation
            status
        }
    }
}
"""


def test_product_class_create(
        staff_api_client,
        channel_variant,
        permission_manage_product_class
):
    # give
    listing_id_expect = channel_variant.id
    listing_id_convert = graphene.Node.to_global_id(
        "ProductVariantChannelListing", listing_id_expect
    )
    param = {
        "listingId": listing_id_convert,
        "productClassQty": "product_class_qty",
        "productClassValue": "product_class_value",
        "productClassRecommendation": "product_class_recommendation",
        "approvedAt": "2019-03-15T12:00:00.000Z"
    }
    query = QUERY_PRODUCT_CLASS_CREATE
    variables = {"input": param}

    # when
    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_product_class]
    )

    # then
    content = get_graphql_content(response)

    listing_id = \
    content["data"]["productClassRecommendationCreate"]["productClassRecommendation"][
        "listing"]["id"]
    _, listing_id = graphene.Node.from_global_id(listing_id)
    assert int(listing_id) == listing_id_expect


def test_product_class_create_no_permission(
        staff_api_client, channel_variant, product_class_recommendation
):
    # give
    listing_id_expect = channel_variant.id
    param = {
        "listingId": listing_id_expect,
        "productClassQty": "product_class_qty",
        "productClassValue": "product_class_value",
        "productClassRecommendation": "product_class_recommendation",
        "approvedAt": "2019-03-15T12:00:00.000Z"
    }
    query = QUERY_PRODUCT_CLASS_CREATE
    variables = {"input": param}

    # when
    response = staff_api_client.post_graphql(query, variables)

    # then
    assert_no_permission(response)


QUERY_PRODUCT_CLASS_UPDATE = """
mutation ProductClassRecommendationUpdate($id: ID!, $input: ProductClassRecommendationInput!){
    productClassRecommendationUpdate(id: $id, input: $input){
        productClassRecommendation{
            id
            listing{
                id
            }
            productClassQty
            productClassValue
            productClassRecommendation
        }
    }
}
"""


def test_product_class_update(
        staff_api_client,
        channel_variant,
        product_class_recommendation,
        permission_manage_product_class
):
    # give
    product_class_id_expect = product_class_recommendation.id
    listing_id_expect = channel_variant.id

    product_class_id = graphene.Node.to_global_id(
        "ProductClassRecommendation", product_class_id_expect
    )
    listing_id_convert = graphene.Node.to_global_id(
        "ProductVariantChannelListing", listing_id_expect
    )
    param = {
        "listingId": listing_id_convert,
        "productClassQty": "product_class_qty123",
        "productClassValue": "product_class_value123",
        "productClassRecommendation": "product_class_recommendation",
        "approvedAt": "2019-03-15T12:00:00.000Z"
    }
    query = QUERY_PRODUCT_CLASS_UPDATE
    variables = {"input": param, "id": product_class_id}

    # when
    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_product_class]
    )

    # then
    content = get_graphql_content(response)
    product_class_recommendation.refresh_from_db()
    product_class = content["data"]["productClassRecommendationUpdate"][
        "productClassRecommendation"]
    assert product_class[
               "productClassQty"] == product_class_recommendation.product_class_qty
    assert product_class[
               "productClassValue"] == product_class_recommendation.product_class_value


def test_product_class_update_no_permission(
        staff_api_client,
        channel_variant,
        product_class_recommendation,
        permission_manage_product_class
):
    # give
    product_class_id_expect = product_class_recommendation.id
    listing_id_expect = channel_variant.id

    product_class_id = graphene.Node.to_global_id(
        "ProductClassRecommendation", product_class_id_expect
    )
    param = {
        "listingId": listing_id_expect,
        "productClassQty": "product_class_qty123",
        "productClassValue": "product_class_value123",
        "productClassRecommendation": "product_class_recommendation",
        "approvedAt": "2019-03-15T12:00:00.000Z"
    }
    query = QUERY_PRODUCT_CLASS_UPDATE
    variables = {"input": param, "id": product_class_id}

    # when
    response = staff_api_client.post_graphql(query, variables)

    # then
    assert_no_permission(response)


QUERY_PRODUCT_CLASS_DELETE = """
mutation ProductClassRecommendationDelete($id: ID!){
    productClassRecommendationDelete(id: $id){
        deleted
    }
}
"""


def test_product_class_delete(
        staff_api_client, product_class_recommendation, permission_manage_product_class
):
    # give
    deleted_expect = True
    product_class_id = graphene.Node.to_global_id(
        "ProductClassRecommendation", product_class_recommendation.id
    )
    query = QUERY_PRODUCT_CLASS_DELETE
    variables = {"id": product_class_id}

    # when
    response = staff_api_client.post_graphql(
        query,
        variables,
        permissions=[permission_manage_product_class]
    )

    # then
    content = get_graphql_content(response)
    deleted = content["data"]["productClassRecommendationDelete"]["deleted"]
    assert deleted == deleted_expect


def test_product_class_delete_no_permission(
        staff_api_client, product_class_recommendation
):
    # give
    product_class_id_expect = product_class_recommendation.id
    product_class_id = graphene.Node.to_global_id(
        "ProductClassRecommendation", product_class_id_expect
    )
    query = QUERY_PRODUCT_CLASS_DELETE
    variables = {"id": product_class_id}

    # when
    response = staff_api_client.post_graphql(query, variables)

    # then
    assert_no_permission(response)
