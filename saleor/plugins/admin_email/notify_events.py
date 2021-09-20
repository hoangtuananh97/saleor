from ...account.events import staff_event_create
from ..email_common import get_email_subject, get_email_template_or_default
from . import constants
from .constants import (
    order_confirmation_notify,
    product_export_failed_notify,
    product_export_success_notify,
    reset_password_notify,
    staff_password_notify,
)
from .tasks import (
    send_email_with_link_to_download_file_task,
    send_export_failed_email_task,
    send_set_staff_password_email_task,
    send_staff_event_email_task,
    send_staff_order_confirmation_email_task,
    send_staff_password_reset_email_task,
)


def send_set_staff_password_email(
    payload: dict, config: dict, plugin_configuration: list
):
    recipient_email = payload["recipient_email"]
    user = payload.get("user")
    staff_users = [user["id"]]  # type: ignore
    staff_user_email = [user["email"]]  # type: ignore
    payload_notify = {
        "staff_users": staff_users,
        "title": staff_password_notify.get("title"),
        "content": staff_password_notify.get("content"),
        "staff_user_email": staff_user_email,
        "send_mail_notify": payload.get("send_mail_notify"),
    }
    send_staff_event_notify(payload_notify, config, plugin_configuration)

    template = get_email_template_or_default(
        plugin_configuration,
        constants.SET_STAFF_PASSWORD_TEMPLATE_FIELD,
        constants.SET_STAFF_PASSWORD_DEFAULT_TEMPLATE,
        constants.DEFAULT_EMAIL_TEMPLATES_PATH,
    )
    subject = get_email_subject(
        plugin_configuration,
        constants.SET_STAFF_PASSWORD_SUBJECT_FIELD,
        constants.SET_STAFF_PASSWORD_DEFAULT_SUBJECT,
    )
    send_set_staff_password_email_task.delay(
        recipient_email, payload, config, subject, template
    )


def send_csv_product_export_success(
    payload: dict, config: dict, plugin_configuration: list
):
    export_info = payload.get("export")
    staff_users = [export_info["user_id"]]  # type: ignore
    staff_user_email = [export_info["user_email"]]  # type: ignore
    payload_notify = {
        "staff_users": staff_users,
        "title": product_export_success_notify.get("title"),
        "content": product_export_success_notify.get("content"),
        "staff_user_email": staff_user_email,
        "send_mail_notify": payload.get("send_mail_notify"),
    }
    send_staff_event_notify(payload_notify, config, plugin_configuration)

    recipient_email = payload.get("recipient_email")
    if recipient_email:
        template = get_email_template_or_default(
            plugin_configuration,
            constants.CSV_PRODUCT_EXPORT_SUCCESS_TEMPLATE_FIELD,
            constants.CSV_PRODUCT_EXPORT_SUCCESS_DEFAULT_TEMPLATE,
            constants.DEFAULT_EMAIL_TEMPLATES_PATH,
        )
        subject = get_email_subject(
            plugin_configuration,
            constants.CSV_PRODUCT_EXPORT_SUCCESS_SUBJECT_FIELD,
            constants.CSV_PRODUCT_EXPORT_SUCCESS_DEFAULT_SUBJECT,
        )
        send_email_with_link_to_download_file_task.delay(
            recipient_email, payload, config, subject, template
        )


def send_staff_order_confirmation(
    payload: dict, config: dict, plugin_configuration: list
):
    recipient_list = payload.get("recipient_list")
    recipient_id_list = payload.get("recipient_id_list")
    payload_notify = {
        "staff_users": recipient_id_list,
        "title": order_confirmation_notify.get("title"),
        "content": order_confirmation_notify.get("content"),
        "staff_user_email": recipient_list,
        "send_mail_notify": payload.get("send_mail_notify"),
    }
    send_staff_event_notify(payload_notify, config, plugin_configuration)
    template = get_email_template_or_default(
        plugin_configuration,
        constants.STAFF_ORDER_CONFIRMATION_TEMPLATE_FIELD,
        constants.STAFF_ORDER_CONFIRMATION_DEFAULT_TEMPLATE,
        constants.DEFAULT_EMAIL_TEMPLATES_PATH,
    )
    subject = get_email_subject(
        plugin_configuration,
        constants.STAFF_ORDER_CONFIRMATION_SUBJECT_FIELD,
        constants.STAFF_ORDER_CONFIRMATION_DEFAULT_SUBJECT,
    )
    send_staff_order_confirmation_email_task.delay(
        recipient_list, payload, config, subject, template
    )


def send_csv_export_failed(payload: dict, config: dict, plugin_configuration: list):
    recipient_email = payload.get("recipient_email")
    export_info = payload.get("export")
    staff_users = [export_info["user_id"]]  # type: ignore
    staff_user_email = [export_info["user_email"]]  # type: ignore
    payload_notify = {
        "staff_users": staff_users,
        "title": product_export_failed_notify.get("title"),
        "content": product_export_failed_notify.get("content"),
        "staff_user_email": staff_user_email,
        "send_mail_notify": payload.get("send_mail_notify"),
    }
    send_staff_event_notify(payload_notify, config, plugin_configuration)

    if recipient_email:
        template = get_email_template_or_default(
            plugin_configuration,
            constants.CSV_EXPORT_FAILED_TEMPLATE_FIELD,
            constants.CSV_EXPORT_FAILED_TEMPLATE_DEFAULT_TEMPLATE,
            constants.DEFAULT_EMAIL_TEMPLATES_PATH,
        )
        subject = get_email_subject(
            plugin_configuration,
            constants.CSV_EXPORT_FAILED_SUBJECT_FIELD,
            constants.CSV_EXPORT_FAILED_DEFAULT_SUBJECT,
        )
        send_export_failed_email_task.delay(
            recipient_email, payload, config, subject, template
        )


def send_staff_reset_password(payload: dict, config: dict, plugin_configuration: list):
    recipient_email = payload.get("recipient_email")
    user = payload.get("user")
    staff_users = [user["id"]]  # type: ignore
    staff_user_email = [user["email"]]  # type: ignore

    payload_notify = {
        "staff_users": staff_users,
        "title": reset_password_notify.get("title"),
        "content": reset_password_notify.get("content"),
        "staff_user_email": staff_user_email,
        "send_mail_notify": payload.get("send_mail_notify"),
    }
    send_staff_event_notify(payload_notify, config, plugin_configuration)

    if recipient_email:
        template = get_email_template_or_default(
            plugin_configuration,
            constants.STAFF_PASSWORD_RESET_TEMPLATE_FIELD,
            constants.STAFF_PASSWORD_RESET_DEFAULT_TEMPLATE,
            constants.DEFAULT_EMAIL_TEMPLATES_PATH,
        )
        subject = get_email_subject(
            plugin_configuration,
            constants.STAFF_PASSWORD_RESET_SUBJECT_FIELD,
            constants.STAFF_PASSWORD_RESET_DEFAULT_SUBJECT,
        )
        send_staff_password_reset_email_task.delay(
            recipient_email, payload, config, subject, template
        )


def send_staff_event_notify(payload: dict, config: dict, plugin_configuration: list):
    staff_event_create(
        staff_users=payload["staff_users"],  # type: ignore
        title=payload["title"],
        content=payload["content"],
    )
    if payload.get("send_mail_notify"):
        send_staff_event_email(
            payload=payload, config=config, plugin_configuration=plugin_configuration
        )


def send_staff_event_email(payload: dict, config: dict, plugin_configuration: list):
    recipient_email = payload["staff_user_email"]  # type: ignore
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
