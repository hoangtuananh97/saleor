from typing import TYPE_CHECKING

from ..core.notifications import get_site_context
from ..core.notify_events import NotifyEventType
from ..core.utils import build_absolute_uri
from ..plugins.admin_email.constants import (
    PRODUCT_EXPORT_FAILED_NOTIFY,
    PRODUCT_EXPORT_SUCCESS_NOTIFY,
)
from ..plugins.manager import get_plugins_manager

if TYPE_CHECKING:
    from .models import ExportFile


def get_default_export_payload(export_file: "ExportFile") -> dict:
    user_id = export_file.user.id if export_file.user else None
    user_email = export_file.user.email if export_file.user else None
    app_id = export_file.app.id if export_file.app else None
    return {
        "user_id": user_id,
        "user_email": user_email,
        "app_id": app_id,
        "id": export_file.id,
        "status": export_file.status,
        "message": export_file.message,
        "created_at": export_file.created_at,
        "updated_at": export_file.updated_at,
    }


def send_export_download_link_notification(export_file: "ExportFile"):
    """Call PluginManager.notify to trigger the notification for success export."""
    export_payload = get_default_export_payload(export_file)
    payload = {
        "export": export_payload,
        "csv_link": build_absolute_uri(export_file.content_file.url),
        "recipient_email": export_file.user.email if export_file.user else None,
        **get_site_context(),
    }

    manager = get_plugins_manager()
    manager.notify(NotifyEventType.CSV_PRODUCT_EXPORT_SUCCESS, payload)

    staff_event_csv_product_notify(
        manager, export_payload, PRODUCT_EXPORT_SUCCESS_NOTIFY
    )


def send_export_failed_info(export_file: "ExportFile"):
    """Call PluginManager.notify to trigger the notification for failed export."""
    export_payload = get_default_export_payload(export_file)
    payload = {
        "export": get_default_export_payload(export_file),
        "recipient_email": export_file.user.email if export_file.user else None,
        **get_site_context(),
    }
    manager = get_plugins_manager()
    manager.notify(NotifyEventType.CSV_EXPORT_FAILED, payload)

    staff_event_csv_product_notify(
        manager, export_payload, PRODUCT_EXPORT_FAILED_NOTIFY
    )


def staff_event_csv_product_notify(manager, export_payload, notify_info):
    staff_users = [export_payload["user_id"]]  # type: ignore
    staff_user_email = [export_payload["user_email"]]  # type: ignore
    payload_notify = {
        "staff_users": staff_users,
        "title": notify_info.get("title"),
        "content": notify_info.get("content"),
        "staff_user_email": staff_user_email,
    }
    manager.notify(NotifyEventType.STAFF_EVENT, payload=payload_notify)
