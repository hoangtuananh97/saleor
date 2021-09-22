import graphene

from saleor.graphql.tests.utils import assert_no_permission, get_graphql_content

QUERY_LIST_STAFF_EVENT = """
# Write your query or mutation here
query GetStaffEvents($first: Int, $last: Int, $filter: StaffEventInput) {
  staffEvents(first: $first, last: $last, filter: $filter) {
    edges {
      node {
        id
        date
        title
        content
        user {
          id
        }
      }
    }
    pageInfo {
      startCursor
      endCursor
      hasNextPage
      hasPreviousPage
    }
  }
}

"""


def test_list_staff_event(staff_api_client, staff_event, permission_manage_staff_event):
    # given
    user_id_expect = staff_event.user_id
    query = QUERY_LIST_STAFF_EVENT
    variables = {"first": 1}

    # when
    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_staff_event]
    )

    # then
    content = get_graphql_content(response)
    staff_events = content["data"]["staffEvents"]["edges"][0]["node"]
    _, user_id = graphene.Node.from_global_id(staff_events["user"]["id"])
    assert int(user_id) == user_id_expect


def test_list_staff_event_no_permission(staff_api_client, staff_event):
    # give
    query = QUERY_LIST_STAFF_EVENT
    variables = {"first": 1}

    # when
    response = staff_api_client.post_graphql(query, variables)

    # then
    assert_no_permission(response)
