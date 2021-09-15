from ...account.events import staff_event_create
from ..email_common import get_email_subject, get_email_template_or_default
from . import constants
from .tasks import send_staff_event_email_task


def send_staff_event_notify(
    payload: dict, config: dict, plugin_configuration: list, send_mail: bool
):
    staff_event_create(
        staff_user=payload["staff_user"],
        title=payload["title"],
        content=payload["content"],
    )
    if send_mail:
        send_staff_event_email(
            payload=payload, config=config, plugin_configuration=plugin_configuration
        )


def send_staff_event_email(payload: dict, config: dict, plugin_configuration: list):
    recipient_email = payload["staff_user_email"]
    template = get_email_template_or_default(
        plugin_configuration,
        constants.SET_STAFF_EVENT_TEMPLATE_FIELD,
        constants.SET_STAFF_EVENT_DEFAULT_TEMPLATE,
        constants.DEFAULT_EMAIL_TEMPLATES_PATH,
    )
    subject = get_email_subject(
        plugin_configuration,
        constants.SET_STAFF_EVENT_SUBJECT_FIELD,
        constants.SET_STAFF_EVENT_DEFAULT_SUBJECT,
    )

    send_staff_event_email_task.delay(
        recipient_email, payload, config, subject, template
    )
