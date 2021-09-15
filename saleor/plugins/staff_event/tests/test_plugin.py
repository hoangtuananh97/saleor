from unittest.mock import patch

from saleor.core.notify_events import NotifyEventType
from saleor.plugins.staff_event.notify_events import send_staff_event_notify
from saleor.plugins.staff_event.plugin import get_staff_event_event_map


def test_event_map():
    assert get_staff_event_event_map() == {
        NotifyEventType.STAFF_EVENT: send_staff_event_notify,
    }


@patch("saleor.plugins.user_email.plugin.get_user_event_map")
def test_notify_event_plugin_is_not_active(
    mocked_get_event_map, staff_event_email_plugin
):
    # give
    event_type = NotifyEventType.STAFF_EVENT
    payload = {
        "field1": 1,
        "field2": 2,
    }
    # when
    plugin = staff_event_email_plugin(active=False)
    plugin.notify(event_type, payload, previous_value=None)
    # then
    assert not mocked_get_event_map.called
