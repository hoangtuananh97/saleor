import graphene

from saleor.graphql.tests.utils import assert_no_permission, get_graphql_content

QUERY_DETAIL_PRODUCT_MAX_MIN = """
query GetProductMaxMin($id: ID!){
    productMaxMin(id: $id){
        id
        maxLevel
        minLevel
    }
}
"""


def test_product_max_min_detail(
    staff_api_client, product_max_min, permission_manage_product_max_min
):
    # give
    product_max_min_id = graphene.Node.to_global_id("ProductMaxMin", product_max_min.id)
    query = QUERY_DETAIL_PRODUCT_MAX_MIN
    variables = {"id": product_max_min_id}

    # when
    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_product_max_min]
    )

    # then
    content = get_graphql_content(response)
    data = content["data"]["productMaxMin"]
    _, pk = graphene.Node.from_global_id(product_max_min_id)
    assert product_max_min.id == pk
    assert product_max_min.max_level == data["maxLevel"]
    assert product_max_min.min_level == data["minLevel"]


def test_product_max_min_update_no_permission(
    staff_api_client, channel_variant, product_max_min
):
    # give
    product_max_min_id = graphene.Node.to_global_id("ProductMaxMin", product_max_min.id)
    query = QUERY_DETAIL_PRODUCT_MAX_MIN
    variables = {"id": product_max_min_id}

    # when
    response = staff_api_client.post_graphql(
        query,
        variables,
    )

    # then
    assert_no_permission(response)
