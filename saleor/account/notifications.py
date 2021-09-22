from typing import Optional
from urllib.parse import urlencode

from django.contrib.auth.tokens import default_token_generator

from ..core.notifications import get_site_context
from ..core.notify_events import NotifyEventType
from ..core.utils.url import prepare_url
from ..plugins.admin_email.constants import RESET_PASSWORD_NOTIFY, STAFF_PASSWORD_NOTIFY
from .models import User


def get_default_user_payload(user: User):
    return {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_staff": user.is_staff,
        "is_active": user.is_active,
        "private_metadata": user.private_metadata,
        "metadata": user.metadata,
        "language_code": user.language_code,
    }


def send_password_reset_notification(
    redirect_url, user, manager, channel_slug: Optional[str], staff=False
):
    """Trigger sending a password reset notification for the given customer/staff."""
    token = default_token_generator.make_token(user)
    params = urlencode({"email": user.email, "token": token})
    reset_url = prepare_url(params, redirect_url)
    user_info = get_default_user_payload(user)
    payload = {
        "user": user_info,
        "recipient_email": user.email,
        "token": token,
        "reset_url": reset_url,
        "channel_slug": channel_slug,
        **get_site_context(),
    }

    if staff:
        event = NotifyEventType.ACCOUNT_STAFF_RESET_PASSWORD
        staff_event_account_notify(manager, user_info, RESET_PASSWORD_NOTIFY)
    else:
        event = NotifyEventType.ACCOUNT_PASSWORD_RESET
    manager.notify(event, payload=payload, channel_slug=channel_slug)


def send_account_confirmation(user, redirect_url, manager, channel_slug):
    """Trigger sending an account confirmation notification for the given user."""
    token = default_token_generator.make_token(user)
    params = urlencode({"email": user.email, "token": token})
    confirm_url = prepare_url(params, redirect_url)
    payload = {
        "user": get_default_user_payload(user),
        "recipient_email": user.email,
        "token": token,
        "confirm_url": confirm_url,
        "channel_slug": channel_slug,
        **get_site_context(),
    }
    manager.notify(
        NotifyEventType.ACCOUNT_CONFIRMATION, payload=payload, channel_slug=channel_slug
    )


def send_request_user_change_email_notification(
    redirect_url, user, new_email, token, manager, channel_slug
):
    """Trigger sending a notification change email for the given user."""
    params = urlencode({"token": token})
    redirect_url = prepare_url(params, redirect_url)
    payload = {
        "user": get_default_user_payload(user),
        "recipient_email": new_email,
        "old_email": user.email,
        "new_email": new_email,
        "token": token,
        "redirect_url": redirect_url,
        "channel_slug": channel_slug,
        **get_site_context(),
    }
    manager.notify(
        NotifyEventType.ACCOUNT_CHANGE_EMAIL_REQUEST,
        payload=payload,
        channel_slug=channel_slug,
    )


def send_user_change_email_notification(recipient_email, user, manager, channel_slug):
    """Trigger sending a email change notification for the given user."""
    payload = {
        "user": get_default_user_payload(user),
        "recipient_email": recipient_email,
        "channel_slug": channel_slug,
        **get_site_context(),
    }
    manager.notify(
        NotifyEventType.ACCOUNT_CHANGE_EMAIL_CONFIRM,
        payload=payload,
        channel_slug=channel_slug,
    )


def send_account_delete_confirmation_notification(
    redirect_url, user, manager, channel_slug
):
    """Trigger sending a account delete notification for the given user."""
    token = default_token_generator.make_token(user)
    params = urlencode({"token": token})
    delete_url = prepare_url(params, redirect_url)
    payload = {
        "user": get_default_user_payload(user),
        "recipient_email": user.email,
        "token": token,
        "delete_url": delete_url,
        "channel_slug": channel_slug,
        **get_site_context(),
    }
    manager.notify(
        NotifyEventType.ACCOUNT_DELETE, payload=payload, channel_slug=channel_slug
    )


def send_set_password_notification(
    redirect_url, user, manager, channel_slug, staff=False
):
    """Trigger sending a set password notification for the given customer/staff."""
    token = default_token_generator.make_token(user)
    params = urlencode({"email": user.email, "token": token})
    password_set_url = prepare_url(params, redirect_url)
    user_info = get_default_user_payload(user)
    payload = {
        "user": user_info,
        "token": default_token_generator.make_token(user),
        "recipient_email": user.email,
        "password_set_url": password_set_url,
        "channel_slug": channel_slug,
        **get_site_context(),
    }
    if staff:
        event = NotifyEventType.ACCOUNT_SET_STAFF_PASSWORD
        staff_event_account_notify(manager, user_info, STAFF_PASSWORD_NOTIFY)
    else:
        event = NotifyEventType.ACCOUNT_SET_CUSTOMER_PASSWORD
    manager.notify(event, payload=payload, channel_slug=channel_slug)


def staff_event_account_notify(manager, user_info, notify_info):
    staff_users = [user_info["id"]]  # type: ignore
    staff_user_email = [user_info["email"]]  # type: ignore
    payload_notify = {
        "staff_users": staff_users,
        "title": notify_info.get("title"),
        "content": notify_info.get("content"),
        "staff_user_email": staff_user_email,
    }
    manager.notify(NotifyEventType.STAFF_EVENT, payload=payload_notify)
