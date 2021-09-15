import logging
from dataclasses import asdict, dataclass
from typing import Optional

from saleor import settings
from saleor.core.notify_events import NotifyEventType, StaffEventNotifyEvent
from saleor.plugins.base_plugin import BasePlugin, ConfigurationTypeField
from saleor.plugins.email_common import (
    DEFAULT_EMAIL_CONFIG_STRUCTURE,
    DEFAULT_EMAIL_CONFIGURATION,
    DEFAULT_EMAIL_VALUE,
    DEFAULT_SUBJECT_HELP_TEXT,
    DEFAULT_TEMPLATE_HELP_TEXT,
    EmailConfig,
    validate_default_email_configuration,
    validate_format_of_provided_templates,
)
from saleor.plugins.models import PluginConfiguration
from saleor.plugins.staff_event import constants
from saleor.plugins.staff_event.notify_events import send_staff_event_notify

logger = logging.getLogger(__name__)


@dataclass
class StaffEventTemplate:
    staff_event: Optional[str]


def get_staff_event_template_map(templates: StaffEventTemplate):
    return {
        StaffEventNotifyEvent.STAFF_EVENT: templates.staff_event,
    }


def get_staff_event_event_map():
    return {
        StaffEventNotifyEvent.STAFF_EVENT: send_staff_event_notify,
    }


class StaffEventPlugin(BasePlugin):
    PLUGIN_ID = constants.PLUGIN_ID
    PLUGIN_NAME = "StaffEvent"
    PLUGIN_DESCRIPTION = "Description of StaffEvent."
    DEFAULT_ACTIVE = True
    CONFIGURATION_PER_CHANNEL = False
    SEND_MAIL_STAFF_EVENT = True

    DEFAULT_CONFIGURATION = [
        {
            "name": constants.SET_STAFF_EVENT_TEMPLATE_FIELD,
            "value": DEFAULT_EMAIL_VALUE,
        },
        {
            "name": constants.SET_STAFF_EVENT_SUBJECT_FIELD,
            "value": constants.SET_STAFF_EVENT_DEFAULT_SUBJECT,
        },
    ] + DEFAULT_EMAIL_CONFIGURATION  # type: ignore

    CONFIG_STRUCTURE = {
        constants.SET_STAFF_EVENT_SUBJECT_FIELD: {
            "type": ConfigurationTypeField.STRING,
            "help_text": DEFAULT_SUBJECT_HELP_TEXT,
            "label": "Staff Event subject",
        },
        constants.SET_STAFF_EVENT_TEMPLATE_FIELD: {
            "type": ConfigurationTypeField.MULTILINE,
            "help_text": DEFAULT_TEMPLATE_HELP_TEXT,
            "label": "Staff Event template",
        },
    }
    CONFIG_STRUCTURE.update(DEFAULT_EMAIL_CONFIG_STRUCTURE)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        configuration = {item["name"]: item["value"] for item in self.configuration}
        self.config = EmailConfig(
            host=configuration["host"] or settings.EMAIL_HOST,
            port=configuration["port"] or settings.EMAIL_PORT,
            username=configuration["username"] or settings.EMAIL_HOST_USER,
            password=configuration["password"] or settings.EMAIL_HOST_PASSWORD,
            sender_name=configuration["sender_name"],
            sender_address=(
                configuration["sender_address"] or settings.DEFAULT_FROM_EMAIL
            ),
            use_tls=configuration["use_tls"] or settings.EMAIL_USE_TLS,
            use_ssl=configuration["use_ssl"] or settings.EMAIL_USE_SSL,
        )
        self.templates = StaffEventTemplate(
            staff_event=configuration[constants.SET_STAFF_EVENT_TEMPLATE_FIELD],
        )

    def notify(self, event: NotifyEventType, payload: dict, previous_value):
        if not self.active:
            return previous_value
        event_map = get_staff_event_event_map()
        if event not in StaffEventNotifyEvent.CHOICES:
            return previous_value
        if event not in event_map:
            logger.warning(f"Missing handler for event {event}")
            return previous_value
        template_map = get_staff_event_template_map(self.templates)
        if not template_map.get(event):
            return previous_value
        event_map[event](
            payload=payload,
            config=asdict(self.config),  # type: ignore
            plugin_configuration=self.configuration,
            send_mail=self.SEND_MAIL_STAFF_EVENT,
        )

    @classmethod
    def validate_plugin_configuration(cls, plugin_configuration: "PluginConfiguration"):
        """Validate if provided configuration is correct."""

        configuration = plugin_configuration.configuration
        configuration = {item["name"]: item["value"] for item in configuration}

        configuration["host"] = configuration["host"] or settings.EMAIL_HOST
        configuration["port"] = configuration["port"] or settings.EMAIL_PORT
        configuration["username"] = (
            configuration["username"] or settings.EMAIL_HOST_USER
        )
        configuration["password"] = (
            configuration["password"] or settings.EMAIL_HOST_PASSWORD
        )
        configuration["sender_address"] = (
            configuration["sender_address"] or settings.DEFAULT_FROM_EMAIL
        )
        configuration["use_tls"] = configuration["use_tls"] or settings.EMAIL_USE_TLS
        configuration["use_ssl"] = configuration["use_ssl"] or settings.EMAIL_USE_SSL

        validate_default_email_configuration(plugin_configuration, configuration)
        validate_format_of_provided_templates(
            plugin_configuration, constants.TEMPLATE_FIELDS
        )
