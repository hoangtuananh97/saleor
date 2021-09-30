import graphene

from saleor.graphql.tests.utils import assert_no_permission, get_graphql_content
from saleor.product_class.error_codes import ProductClassRecommendationErrorCode
from saleor.product_class.models import ProductClassRecommendation
from saleor.tests.fixtures import permission_approve_product_class

QUERY_PRODUCT_CLASS_BULK_CREATE = """
mutation ProductClassRecommendationBulkCreate(
    $input: [ProductClassRecommendationInput!]!
    ){
        productClassRecommendationBulkCreate(input: $input){
            count
            productClassRecommendations{
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


def test_product_class_bulk_create(
        staff_api_client, channel_variant, permission_manage_product_class
):
    # give
    listing_id_expect = channel_variant.id
    listing_id_convert = graphene.Node.to_global_id(
        "ProductVariantChannelListing", listing_id_expect
    )
    param = [
        {
            "listing": listing_id_convert,
            "productClassQty": "product_class_qty",
            "productClassValue": "product_class_value",
            "productClassRecommendation": "product_class_recommendation",
        }
    ]
    query = QUERY_PRODUCT_CLASS_BULK_CREATE
    variables = {"input": param}

    # when
    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_product_class]
    )

    # then
    content = get_graphql_content(response)

    data = content["data"]["productClassRecommendationBulkCreate"]
    assert len(param) == int(data["count"])


def test_product_class_bulk_create_errors(
        staff_api_client, channel_variant, permission_manage_product_class
):
    # give
    listing_id_expect = channel_variant.id
    listing_id_convert = graphene.Node.to_global_id(
        "ProductVariantChannelListing", listing_id_expect
    )
    param = [
        {
            "listing": listing_id_convert,
            "productClassValue": "product_class_value",
            "productClassRecommendation": "product_class_recommendation",
        }
    ]
    query = QUERY_PRODUCT_CLASS_BULK_CREATE
    variables = {"input": param}

    # when
    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_product_class]
    )

    # then
    content = get_graphql_content(response)

    data = content["data"]["productClassRecommendationBulkCreate"]
    code = data["errors"][0]["code"]
    assert int(data["count"]) == 0
    assert code == str.upper(ProductClassRecommendationErrorCode.REQUIRED.value)


def test_product_class_bulk_create_no_permission(
        staff_api_client, channel_variant, product_class_recommendation
):
    # give
    listing_id_expect = channel_variant.id
    param = [
        {
            "listing": listing_id_expect,
            "productClassQty": "product_class_qty",
            "productClassValue": "product_class_value",
            "productClassRecommendation": "product_class_recommendation",
        }
    ]
    query = QUERY_PRODUCT_CLASS_BULK_CREATE
    variables = {"input": param}

    # when
    response = staff_api_client.post_graphql(query, variables)

    # then
    assert_no_permission(response)


QUERY_PRODUCT_CLASS_BULK_UPDATE = """
mutation ProductClassRecommendationBulkUpdate(
    $input: [ProductClassRecommendationBulkUpdateInput!]!
    ){
    productClassRecommendationBulkUpdate(input: $input){
        count
        productClassRecommendations{
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


def test_product_class_bulk_update(
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
    param = [
        {
            "id": product_class_id,
            "listing": listing_id_convert,
            "productClassQty": "product_class_qty123",
            "productClassValue": "product_class_value123",
            "productClassRecommendation": "product_class_recommendation",
        }
    ]
    query = QUERY_PRODUCT_CLASS_BULK_UPDATE
    variables = {"input": param}

    # when
    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_product_class]
    )

    # then
    content = get_graphql_content(response)
    product_class_recommendation.refresh_from_db()
    data = content["data"]["productClassRecommendationBulkUpdate"]
    product_class = data["productClassRecommendations"][0]
    product_class_qty = product_class_recommendation.product_class_qty
    product_class_value = product_class_recommendation.product_class_value

    assert len(param) == data["count"]
    assert product_class["productClassQty"] == product_class_qty
    assert product_class["productClassValue"] == product_class_value


def test_product_class_bulk_update_errors(
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
    param = [
        {
            "id": product_class_id,
            "listing": listing_id_convert,
            "productClassValue": "product_class_value123",
            "productClassRecommendation": "product_class_recommendation",
        }
    ]
    query = QUERY_PRODUCT_CLASS_BULK_UPDATE
    variables = {"input": param}

    # when
    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_product_class]
    )

    # then
    content = get_graphql_content(response)
    product_class_recommendation.refresh_from_db()
    data = content["data"]["productClassRecommendationBulkUpdate"]
    code = data["errors"][0]["code"]

    assert code == str.upper(ProductClassRecommendationErrorCode.REQUIRED.value)
    assert data["count"] == 0


def test_product_class_bulk_update_no_permission(
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
    param = [
        {
            "id": product_class_id,
            "listing": listing_id_convert,
            "productClassQty": "product_class_qty123",
            "productClassValue": "product_class_value123",
            "productClassRecommendation": "product_class_recommendation",
        }
    ]
    query = QUERY_PRODUCT_CLASS_BULK_UPDATE
    variables = {"input": param}

    # when
    response = staff_api_client.post_graphql(query, variables)

    # then
    assert_no_permission(response)


QUERY_PRODUCT_CLASS_DELETE_BULK = """
mutation ProductClassRecommendationBulkDelete($ids: [ID]!){
    productClassRecommendationBulkDelete(ids: $ids){
        count
        }
}
"""


def test_product_class_bulk_delete(
        staff_api_client, product_class_recommendation, permission_manage_product_class
):
    # give
    product_class_id = graphene.Node.to_global_id(
        "ProductClassRecommendation", product_class_recommendation.id
    )
    product_class_ids = [product_class_id]
    query = QUERY_PRODUCT_CLASS_DELETE_BULK
    variables = {"ids": product_class_ids}

    # when
    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_product_class]
    )

    # then
    content = get_graphql_content(response)
    data = content["data"]["productClassRecommendationBulkDelete"]
    objects = ProductClassRecommendation.objects.filter(id__in=product_class_ids)
    assert data["count"] == len(product_class_ids)
    assert len(objects) == 0


def test_product_class_bulk_delete_no_permission(
        staff_api_client, product_class_recommendation
):
    # give
    product_class_id_expect = product_class_recommendation.id
    product_class_id = graphene.Node.to_global_id(
        "ProductClassRecommendation", product_class_id_expect
    )
    query = QUERY_PRODUCT_CLASS_DELETE_BULK
    variables = {"ids": [product_class_id]}

    # when
    response = staff_api_client.post_graphql(query, variables)

    # then
    assert_no_permission(response)


QUERY_PRODUCT_CLASS_BULK_CHANGE_STATUS = """
mutation ProductClassRecommendationBulkChangeStatus($ids: [ID!]!, $status: String!){
    productClassRecommendationBulkChangeStatus(ids: $ids, status: $status){
        count
        errors{
            code
        }
    }
}
"""


def test_product_class_bulk_change_status_draft_submit(
        staff_api_client,
        channel_variant,
        product_class_recommendation,
        permission_manage_product_class,
):
    # give
    product_class_id_expect = product_class_recommendation.id

    product_class_id = graphene.Node.to_global_id(
        "ProductClassRecommendation", product_class_id_expect
    )
    product_class_ids = [product_class_id]
    variables = {"ids": product_class_ids, "status": "DRAFT"}
    query = QUERY_PRODUCT_CLASS_BULK_CHANGE_STATUS

    # when
    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_product_class]
    )

    # then
    content = get_graphql_content(response)
    product_class_recommendation.refresh_from_db()
    data = content["data"]["productClassRecommendationBulkChangeStatus"]
    product_class = ProductClassRecommendation.objects.filter(id__in=product_class_ids)

    assert product_class.first().status == "DRAFT"
    assert data["count"] == len(product_class_ids)


def test_product_class_bulk_change_status_approve(
        staff_api_client,
        channel_variant,
        product_class_recommendation,
        permission_manage_product_class,
):
    # give
    product_class_id_expect = product_class_recommendation.id

    product_class_id = graphene.Node.to_global_id(
        "ProductClassRecommendation", product_class_id_expect
    )
    product_class_ids = [product_class_id]
    variables = {"ids": product_class_ids, "status": "APPROVE"}
    query = QUERY_PRODUCT_CLASS_BULK_CHANGE_STATUS

    # when
    response = staff_api_client.post_graphql(
        query,
        variables,
        permissions=[permission_manage_product_class, permission_approve_product_class],
    )

    # then
    content = get_graphql_content(response)
    product_class_recommendation.refresh_from_db()
    data = content["data"]["productClassRecommendationBulkChangeStatus"]
    product_class = ProductClassRecommendation.objects.filter(id__in=product_class_ids)

    assert product_class.first().status == "APPROVE"
    assert data["count"] == len(product_class_ids)


def test_product_class_bulk_change_status_errors(
        staff_api_client,
        channel_variant,
        product_class_recommendation,
        permission_manage_product_class,
):
    # give
    product_class_id_expect = product_class_recommendation.id

    product_class_id = graphene.Node.to_global_id(
        "ProductClassRecommendation", product_class_id_expect
    )
    product_class_ids = [product_class_id]
    variables = {"ids": product_class_ids, "status": "DRAFT111111"}
    query = QUERY_PRODUCT_CLASS_BULK_CHANGE_STATUS

    # when
    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_product_class]
    )

    # then
    content = get_graphql_content(response)
    data = content["data"]["productClassRecommendationBulkChangeStatus"]
    code = data["errors"][0]["code"]

    assert code == str.upper(ProductClassRecommendationErrorCode.INVALID.value)
    assert data["count"] == 0


def test_product_class_bulk_change_status_no_permission(
        staff_api_client, product_class_recommendation
):
    # give
    # give
    product_class_id_expect = product_class_recommendation.id

    product_class_id = graphene.Node.to_global_id(
        "ProductClassRecommendation", product_class_id_expect
    )
    product_class_ids = [product_class_id]
    variables = {"ids": product_class_ids, "status": "DRAFT"}
    query = QUERY_PRODUCT_CLASS_BULK_CHANGE_STATUS

    # when
    response = staff_api_client.post_graphql(query, variables)

    # then
    assert_no_permission(response)


def test_product_class_bulk_change_status_approve_no_permission(
        staff_api_client,
        channel_variant,
        product_class_recommendation,
        permission_manage_product_class,
):
    # give
    product_class_id_expect = product_class_recommendation.id

    product_class_id = graphene.Node.to_global_id(
        "ProductClassRecommendation", product_class_id_expect
    )
    product_class_ids = [product_class_id]
    variables = {"ids": product_class_ids, "status": "APPROVE"}
    query = QUERY_PRODUCT_CLASS_BULK_CHANGE_STATUS

    # when
    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_product_class]
    )

    # then
    assert_no_permission(response)
