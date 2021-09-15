from unittest import mock

from ..tasks import send_staff_event_email_task


@mock.patch(
    "saleor.plugins.staff_event.notify_events.send_staff_event_email_task.delay"
)
def test_send_staff_event_email_task(mocked_email_task, staff_users, staff_event):
    # give
    title = "title"
    content = "content"
    payload = {
        "staff_user": staff_users.id,
        "staff_user_email": staff_users.email,
        "title": title,
        "content": content,
        "send_email": True,
        "domain": "localhost:8000",
        "site_name": "Saleor",
    }
    config = {"host": "localhost", "port": "1025"}
    # when
    send_staff_event_email_task(payload=payload, config=config, plugin_configuration=[])
    # then
    mocked_email_task.assert_called_with(
        payload["staff_user_email"], payload, config, mock.ANY, mock.ANY
    )
