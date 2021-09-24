import graphene

from saleor.graphql.tests.utils import get_graphql_content, assert_no_permission

QUERY_LIST_PRODUCT_CLASS = """
query GetProductsClassRecommendation(
    $first: Int, $last: Int, $filter: ProductClassRecommendationFilterInput
){
    productsClassRecommendation(first: $first, last: $last, filter: $filter){
        edges {
            node {
                id
                productClassQty
                createdBy{
                    id
                }
                }
            }
            pageInfo{
                startCursor
                endCursor
                hasNextPage
                hasPreviousPage
            }
    }
}
"""


def test_list_product_class(
        staff_api_client, product_class_recommendation, permission_manage_product_class
):
    # given
    product_class_id_expect = product_class_recommendation.id
    query = QUERY_LIST_PRODUCT_CLASS
    variables = {"first": 1}

    # when
    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_product_class]
    )

    # then
    content = get_graphql_content(response)
    product_class = content["data"]["productsClassRecommendation"]["edges"][0]["node"]
    _, product_class_id = graphene.Node.from_global_id(product_class["id"])
    assert int(product_class_id) == product_class_id_expect


def test_list_product_class_no_permission(
        staff_api_client, product_class_recommendation
):
    # give
    query = QUERY_LIST_PRODUCT_CLASS
    variables = {"first": 1}

    # when
    response = staff_api_client.post_graphql(query, variables)

    # then
    assert_no_permission(response)


QUERY_DETAIL_PRODUCT_CLASS = """
query GetProductClassRecommendation($id: ID!){
    productClassRecommendation(id: $id){
        id
        productClassQty
    }
}
"""


def test_detail_product_class(
        staff_api_client,
        product_class_recommendation,
        permission_manage_product_class
):
    # given
    product_class_id_expect = product_class_recommendation.id
    product_class_id = graphene.Node.to_global_id(
        "ProductClassRecommendation", product_class_id_expect
    )
    query = QUERY_DETAIL_PRODUCT_CLASS
    variables = {"id": product_class_id}

    # when
    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_product_class]
    )

    # then
    content = get_graphql_content(response)
    product_class = content["data"]["productClassRecommendation"]
    _, product_class_id = graphene.Node.from_global_id(product_class["id"])
    assert int(product_class_id) == product_class_id_expect


def test_detail_product_class_no_permission(
        staff_api_client, product_class_recommendation
):
    # give
    product_class_id_expect = product_class_recommendation.id
    product_class_id = graphene.Node.to_global_id(
        "ProductClassRecommendation", product_class_id_expect
    )
    query = QUERY_DETAIL_PRODUCT_CLASS
    variables = {"id": product_class_id}

    # when
    response = staff_api_client.post_graphql(query, variables)

    # then
    assert_no_permission(response)
