import graphene
from graphql_relay import from_global_id

from saleor.graphql.tests.utils import assert_no_permission, get_graphql_content
from saleor.product_class.error_codes import ProductClassRecommendationErrorCode
from saleor.product_class.models import ProductClassRecommendation
from saleor.tests.fixtures import permission_approve_product_class

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
        errors{
            code
        }
    }
}
"""


def test_product_class_create(
        staff_api_client, channel_variant, permission_manage_product_class
):
    # give
    listing_id_expect = channel_variant.id
    listing_id_convert = graphene.Node.to_global_id(
        "ProductVariantChannelListing", listing_id_expect
    )
    param = {
        "listing": listing_id_convert,
        "productClassQty": "product_class_qty",
        "productClassValue": "product_class_value",
        "productClassRecommendation": "product_class_recommendation",
    }
    query = QUERY_PRODUCT_CLASS_CREATE
    variables = {"input": param}

    # when
    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_product_class]
    )

    # then
    content = get_graphql_content(response)
    data = content["data"]["productClassRecommendationCreate"]
    obj = data["productClassRecommendation"]
    listing_id = obj["listing"]["id"]
    _, listing_id = graphene.Node.from_global_id(listing_id)
    assert ProductClassRecommendation.objects.count() == 1
    assert param["productClassQty"] == obj["productClassQty"]
    assert param["productClassValue"] == obj["productClassValue"]
    assert param["productClassRecommendation"] == obj["productClassRecommendation"]


def test_product_class_create_error(
        staff_api_client, channel_variant, permission_manage_product_class
):
    # give
    listing_id_expect = channel_variant.id
    listing_id_convert = graphene.Node.to_global_id(
        "ProductVariantChannelListing", listing_id_expect
    )
    param = {
        "listing": listing_id_convert,
        "productClassValue": "product_class_value",
        "productClassRecommendation": "product_class_recommendation",
    }
    query = QUERY_PRODUCT_CLASS_CREATE
    variables = {"input": param}

    # when
    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_product_class]
    )

    # then
    content = get_graphql_content(response)
    data = content["data"]["productClassRecommendationCreate"]
    code = data["errors"][0]["code"]
    assert code == str.upper(ProductClassRecommendationErrorCode.REQUIRED.value)


def test_product_class_create_no_permission(
        staff_api_client, channel_variant, product_class_recommendation
):
    # give
    listing_id_expect = channel_variant.id
    param = {
        "listing": listing_id_expect,
        "productClassQty": "product_class_qty",
        "productClassValue": "product_class_value",
        "productClassRecommendation": "product_class_recommendation",
    }
    query = QUERY_PRODUCT_CLASS_CREATE
    variables = {"input": param}

    # when
    response = staff_api_client.post_graphql(query, variables)

    # then
    assert_no_permission(response)


QUERY_PRODUCT_CLASS_UPDATE = """
mutation ProductClassRecommendationUpdate(
    $id: ID!, $input: ProductClassRecommendationInput!
    ){
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
        errors{
            code
        }
    }
}
"""


def test_product_class_update(
        staff_api_client,
        channel_variant,
        product_class_recommendation,
        permission_manage_product_class,
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
        "listing": listing_id_convert,
        "productClassQty": "product_class_qty123",
        "productClassValue": "product_class_value123",
        "productClassRecommendation": "product_class_recommendation",
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
    data = content["data"]["productClassRecommendationUpdate"]
    product_class = data["productClassRecommendation"]
    product_class_qty = product_class_recommendation.product_class_qty
    product_class_value = product_class_recommendation.product_class_value
    assert product_class["productClassQty"] == product_class_qty
    assert product_class["productClassValue"] == product_class_value


def test_product_class_update_error(
        staff_api_client,
        channel_variant,
        product_class_recommendation,
        permission_manage_product_class,
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
        "listing": listing_id_convert,
        "productClassValue": "product_class_value123",
        "productClassRecommendation": "product_class_recommendation",
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
    data = content["data"]["productClassRecommendationUpdate"]
    code = data["errors"][0]["code"]
    assert code == str.upper(ProductClassRecommendationErrorCode.REQUIRED.value)


def test_product_class_update_no_permission(
        staff_api_client,
        channel_variant,
        product_class_recommendation,
        permission_manage_product_class,
):
    # give
    product_class_id_expect = product_class_recommendation.id
    listing_id_expect = channel_variant.id

    product_class_id = graphene.Node.to_global_id(
        "ProductClassRecommendation", product_class_id_expect
    )
    param = {
        "listing": listing_id_expect,
        "productClassQty": "product_class_qty123",
        "productClassValue": "product_class_value123",
        "productClassRecommendation": "product_class_recommendation",
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
        productClassRecommendation{
            id
        }
        errors{
            code
        }
    }
}
"""


def test_product_class_delete(
        staff_api_client, product_class_recommendation, permission_manage_product_class
):
    # give
    product_class_id_expect = product_class_recommendation.id
    product_class_id = graphene.Node.to_global_id(
        "ProductClassRecommendation", product_class_recommendation.id
    )
    query = QUERY_PRODUCT_CLASS_DELETE
    variables = {"id": product_class_id}

    # when
    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_product_class]
    )

    # then
    content = get_graphql_content(response)
    data = content["data"]["productClassRecommendationDelete"]
    product_class_id = data["productClassRecommendation"]["id"]
    _, product_class_id = from_global_id(product_class_id)
    product_class = ProductClassRecommendation.objects.filter(id=product_class_id)
    assert len(product_class) == 0
    assert product_class_id_expect == int(product_class_id)


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


QUERY_PRODUCT_CLASS_CHANGE_STATUS = """
mutation ProductClassRecommendationChangeStatus($id: ID!, $status: String!){
    productClassRecommendationChangeStatus(id: $id, status: $status){
        productClassRecommendation{
            id
            productClassQty
            productClassValue
            productClassRecommendation
            status
        }
        errors{
            code
        }
    }
}
"""


def test_product_class_change_status_draft_submit(
        staff_api_client, product_class_recommendation, permission_manage_product_class
):
    # give
    product_class_id_expect = product_class_recommendation.id
    product_class_id = graphene.Node.to_global_id(
        "ProductClassRecommendation", product_class_recommendation.id
    )
    query = QUERY_PRODUCT_CLASS_CHANGE_STATUS
    variables = {"id": product_class_id, "status": "DRAFT"}

    # when
    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_product_class]
    )

    # then
    content = get_graphql_content(response)
    product_class_recommendation.refresh_from_db()
    data = content["data"]["productClassRecommendationChangeStatus"]
    product_class = data["productClassRecommendation"]
    product_class_id = product_class["id"]
    _, product_class_id = graphene.Node.from_global_id(product_class_id)
    assert product_class["status"] == "DRAFT"
    assert int(product_class_id) == product_class_id_expect


def test_product_class_change_status_approve(
        staff_api_client, product_class_recommendation, permission_manage_product_class
):
    # give
    product_class_id_expect = product_class_recommendation.id
    product_class_id = graphene.Node.to_global_id(
        "ProductClassRecommendation", product_class_recommendation.id
    )
    query = QUERY_PRODUCT_CLASS_CHANGE_STATUS
    variables = {"id": product_class_id, "status": "APPROVED"}

    # when
    response = staff_api_client.post_graphql(
        query,
        variables,
        permissions=[permission_manage_product_class, permission_approve_product_class],
    )

    # then
    content = get_graphql_content(response)
    data = content["data"]["productClassRecommendationChangeStatus"]
    product_class = data["productClassRecommendation"]
    product_class_id = product_class["id"]
    _, product_class_id = graphene.Node.from_global_id(product_class_id)
    assert product_class["status"] == "APPROVED"
    assert int(product_class_id) == product_class_id_expect


def test_product_class_change_status_errors(
        staff_api_client, product_class_recommendation, permission_manage_product_class
):
    # give
    product_class_id = graphene.Node.to_global_id(
        "ProductClassRecommendation", product_class_recommendation.id
    )
    query = QUERY_PRODUCT_CLASS_CHANGE_STATUS
    variables = {"id": product_class_id, "status": "DRAFT1"}

    # when
    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_product_class]
    )

    # then
    content = get_graphql_content(response)
    data = content["data"]["productClassRecommendationChangeStatus"]
    code = data["errors"][0]["code"]
    assert code == str.upper(ProductClassRecommendationErrorCode.INVALID.value)


def test_product_class_change_status_no_permission(
        staff_api_client, product_class_recommendation
):
    # give
    product_class_id_expect = product_class_recommendation.id
    product_class_id = graphene.Node.to_global_id(
        "ProductClassRecommendation", product_class_id_expect
    )
    query = QUERY_PRODUCT_CLASS_CHANGE_STATUS
    variables = {"id": product_class_id, "status": "DRAFT"}

    # when
    response = staff_api_client.post_graphql(query, variables)

    # then
    assert_no_permission(response)


def test_product_class_change_status_approved_no_permission(
        staff_api_client, product_class_recommendation, permission_manage_product_class
):
    # give
    product_class_id = graphene.Node.to_global_id(
        "ProductClassRecommendation", product_class_recommendation.id
    )
    query = QUERY_PRODUCT_CLASS_CHANGE_STATUS
    variables = {"id": product_class_id, "status": "APPROVED"}

    # when
    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_product_class]
    )

    # then
    assert_no_permission(response)
