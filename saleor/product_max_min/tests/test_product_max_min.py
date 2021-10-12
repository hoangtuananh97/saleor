import graphene

from saleor.graphql.tests.utils import assert_no_permission, get_graphql_content
from saleor.product_max_min.models import ProductMaxMin

QUERY_CURRENT_PREVIOUS_PRODUCT_MAX_MIN = """
query GetCurrentPreviousProductsMaxMin($first: Int, $last: Int,
    $filter: ProductMaxMinFilterInput
){
    currentPreviousProductsMaxMin(first: $first, last: $last, filter: $filter){
        edges {
            node {
                productMaxMinCurrent{
                    id
                    minLevel
                    maxLevel
                    createdAt
                }
                productMaxMinPrevious{
                    id
                    minLevel
                    maxLevel
                    createdAt
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


def test_current_previous_product_max_min(
    staff_api_client, product_max_min, permission_manage_product_max_min
):
    # given
    product_max_min_id_expect = product_max_min.id
    query = QUERY_CURRENT_PREVIOUS_PRODUCT_MAX_MIN
    variables = {"first": 1}

    # when
    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_product_max_min]
    )

    # then
    content = get_graphql_content(response)
    data = content["data"]["currentPreviousProductsMaxMin"]["edges"][0]["node"]
    _, product_max_min_id = graphene.Node.from_global_id(
        data["productMaxMinCurrent"]["id"]
    )
    assert int(product_max_min_id) == product_max_min_id_expect


def test_current_previous_product_max_min_conditions(
    staff_api_client, products_max_min, permission_manage_product_max_min
):
    # given
    query = QUERY_CURRENT_PREVIOUS_PRODUCT_MAX_MIN
    variables = {
        "first": 10,
        "sort": {"direction": "ASC", "field": "DATETIME"},
        "filter": {
            "minLevel": {"lte": 4},
            "channelListing": {
                "metadata": {"current": [{"key": "key_A"}]},
                "channel": {"search": "Main Channel"},
                "productVariant": {
                    "search": "SKU_A",
                    "product": {"attributes": [{"slug": "color", "values": ["red"]}]},
                },
            },
        },
    }

    # when
    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_product_max_min]
    )

    # then
    content = get_graphql_content(response)
    products_max_min = ProductMaxMin.objects.all().order_by("-created_at")
    data = content["data"]["currentPreviousProductsMaxMin"]["edges"][0]["node"]
    current = data["productMaxMinCurrent"]
    previous = data["productMaxMinPrevious"]
    assert current["minLevel"] == products_max_min[0].min_level
    assert current["maxLevel"] == products_max_min[0].max_level
    assert previous["minLevel"] == products_max_min[1].min_level
    assert previous["maxLevel"] == products_max_min[1].max_level


def test_current_previous_product_max_min_no_permission(
    staff_api_client, products_max_min
):
    # give
    query = QUERY_CURRENT_PREVIOUS_PRODUCT_MAX_MIN
    variables = {"first": 1}

    # when
    response = staff_api_client.post_graphql(query, variables)

    # then
    assert_no_permission(response)


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
    assert product_max_min.id == int(pk)
    assert product_max_min.max_level == data["maxLevel"]
    assert product_max_min.min_level == data["minLevel"]


def test_product_max_min_update_no_permission(staff_api_client, product_max_min):
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
