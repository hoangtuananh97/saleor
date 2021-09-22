import graphene

from saleor.graphql.tests.utils import assert_no_permission, get_graphql_content

STAFF_EVENT_MARK_READ = """
mutation StaffEventMarkRead($staffEventId: ID!){
    staffEventMarkRead(staffEventId: $staffEventId){
        staffEvent{
            id
            isSeen
        }
        errors{
            code
        }
    }
}
"""


def test_staff_event_mark_read(
    staff_api_client, staff_event, permission_manage_staff_event
):
    # given
    is_seen_expect = True
    query = STAFF_EVENT_MARK_READ
    staff_event_id = staff_event.id
    id = graphene.Node.to_global_id("StaffEvent", staff_event_id)
    variables = {"staffEventId": id}

    # when
    response = staff_api_client.post_graphql(
        query,
        variables,
        permissions=(permission_manage_staff_event,),
    )

    # then
    content = get_graphql_content(response)
    staff_event = content["data"]["staffEventMarkRead"]["staffEvent"]
    assert staff_event["isSeen"] == is_seen_expect


def test_staff_event_mark_read_no_permission(staff_api_client, staff_event):
    # give
    query = STAFF_EVENT_MARK_READ
    staff_event_id = staff_event.id
    id = graphene.Node.to_global_id("StaffEvent", staff_event_id)
    variables = {"staffEventId": id}

    # when
    response = staff_api_client.post_graphql(query, variables)

    # then
    assert_no_permission(response)


STAFF_EVENT_DELETE = """
mutation StaffEventDelete($staffEventId: ID!){
    staffEventDelete(staffEventId: $staffEventId){
        message
        errors{
            code
        }
    }
}
"""


def test_staff_event_delete(
    staff_api_client, staff_event, permission_manage_staff_event
):
    # given
    message_expect = "Delete Success"
    query = STAFF_EVENT_DELETE
    staff_event_id = staff_event.id
    id = graphene.Node.to_global_id("StaffEvent", staff_event_id)
    variables = {"staffEventId": id}

    # when
    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_staff_event]
    )

    # then
    content = get_graphql_content(response)
    message = content["data"]["staffEventDelete"]["message"]
    assert message_expect == message


def test_staff_event_delete_no_permission(staff_api_client, staff_event):
    # give
    query = STAFF_EVENT_DELETE
    staff_event_id = staff_event.id
    id = graphene.Node.to_global_id("StaffEvent", staff_event_id)
    variables = {"staffEventId": id}

    # when
    response = staff_api_client.post_graphql(query, variables)

    # then
    assert_no_permission(response)


STAFF_EVENT_BULK_DELETE_MUTATION = """
    mutation staffEventBulkDelete($ids: [ID]!) {
        staffEventBulkDelete(ids: $ids) {
            count
            errors{
                code
                field
            }
        }
    }
"""


def test_staff_event_bulk_delete(
    staff_api_client, staff_events, permission_manage_staff_event
):
    # give
    query = STAFF_EVENT_BULK_DELETE_MUTATION
    variables = {
        "ids": [
            graphene.Node.to_global_id("StaffEvent", staff_event.id)
            for staff_event in staff_events
        ]
    }
    # when
    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_staff_event]
    )
    content = get_graphql_content(response)
    data = content["data"]["staffEventBulkDelete"]
    # then
    assert data["count"] == 2
    assert not data["errors"]


STAFF_EVENT_BULK_UPDATE_MUTATION = """
    mutation StaffEventBulkMarkRead($ids: [ID]!) {
        staffEventBulkMarkRead(ids: $ids) {
            count
            errors{
                code
                field
            }
        }
    }
"""


def test_staff_event_bulk_update(
    staff_api_client, staff_events, permission_manage_staff_event
):
    # give
    query = STAFF_EVENT_BULK_UPDATE_MUTATION
    variables = {
        "ids": [
            graphene.Node.to_global_id("StaffEvent", staff_event.id)
            for staff_event in staff_events
        ]
    }
    # when
    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_staff_event]
    )
    content = get_graphql_content(response)
    data = content["data"]["staffEventBulkMarkRead"]
    # then
    assert data["count"] == 2
    assert not data["errors"]
