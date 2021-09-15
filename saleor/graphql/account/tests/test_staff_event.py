import graphene
import pytest

from saleor.graphql.tests.utils import assert_no_permission, get_graphql_content

QUERY_LIST_STAFF_EVENT = """
query GetStaffEvents{
    staffEvents{
            id
            date
            title
            content
            user{
                id
            }
    }
}
"""


@pytest.fixture
def test_list_staff_event(staff_api_client, staff_event, permission_manage_staff_event):
    # given
    user_id_expect = staff_event.user_id
    query = QUERY_LIST_STAFF_EVENT
    staff_event_id = staff_event.id
    id = graphene.Node.to_global_id("StaffEvent", staff_event_id)
    variables = {"id": id}

    # when
    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_staff_event]
    )

    # then
    content = get_graphql_content(response)
    staff_events = content["data"]["staffEvents"][0]
    user_id = graphene.Node.from_global_id(staff_events["user"]["id"])
    assert user_id == user_id_expect


@pytest.fixture
def test_list_staff_event_no_permission(staff_api_client, staff_event):
    # give
    query = QUERY_LIST_STAFF_EVENT
    staff_event_id = staff_event.id
    id = graphene.Node.to_global_id("StaffEvent", staff_event_id)
    variables = {"id": id}

    # when
    response = staff_api_client.post_graphql(query, variables)

    # then
    assert_no_permission(response)
