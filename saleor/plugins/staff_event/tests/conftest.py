from unittest.mock import patch

import pytest

from ...email_common import DEFAULT_EMAIL_VALUE
from ...manager import get_plugins_manager
from .. import constants
from ..constants import SET_STAFF_EVENT_TEMPLATE_FIELD


@pytest.fixture
def email_dict_config():
    return {
        "host": "localhost",
        "port": "1025",
        "username": None,
        "password": None,
        "use_ssl": False,
        "use_tls": False,
    }


@pytest.fixture
def staff_event_email_plugin(settings):
    def fun(
        host="localhost",
        port="1025",
        username=None,
        password=None,
        sender_name="Admin Name",
        sender_address="admin@example.com",
        use_tls=False,
        use_ssl=False,
        active=True,
        staff_staff_event_template=DEFAULT_EMAIL_VALUE,
    ):
        settings.PLUGINS = ["saleor.plugins.staff_event.plugin.StaffEventPlugin"]
        manager = get_plugins_manager()
        with patch(
            "saleor.plugins.staff_event.plugin.validate_default_email_configuration"
        ):
            manager.save_plugin_configuration(
                constants.PLUGIN_ID,
                None,
                {
                    "active": active,
                    "configuration": [
                        {"name": "host", "value": host},
                        {"name": "port", "value": port},
                        {"name": "username", "value": username},
                        {"name": "password", "value": password},
                        {"name": "sender_name", "value": sender_name},
                        {"name": "sender_address", "value": sender_address},
                        {"name": "use_tls", "value": use_tls},
                        {"name": "use_ssl", "value": use_ssl},
                        {
                            "name": SET_STAFF_EVENT_TEMPLATE_FIELD,
                            "value": staff_staff_event_template,
                        },
                    ],
                },
            )
        manager = get_plugins_manager()
        return manager.global_plugins[0]

    return fun
