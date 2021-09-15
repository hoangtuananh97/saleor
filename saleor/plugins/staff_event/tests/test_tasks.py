from unittest import mock

from ...email_common import EmailConfig
from ..tasks import send_staff_event_email_task


@mock.patch("saleor.plugins.email_common.send_mail")
def test_send_staff_event_email_task_default_template(
    mocked_send_mail, email_dict_config, staff_users
):
    # give
    recipient_email = "admin@example.com"
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
    # when
    send_staff_event_email_task(
        recipient_email, payload, email_dict_config, "subject", "template"
    )

    # then
    # confirm that mail has correct structure and email was sent
    assert mocked_send_mail.called


@mock.patch("saleor.plugins.user_email.tasks.send_email")
def test_send_staff_event_email_task_custom_template(
    mocked_send_email, email_dict_config, staff_users
):
    # give
    expected_template_str = "<html><body>You create category success</body></html>"
    expected_subject = "Staff Event e-mail"
    recipient_email = "admin@example.com"
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

    # when
    send_staff_event_email_task(
        recipient_email,
        payload,
        email_dict_config,
        expected_subject,
        expected_template_str,
    )

    email_config = EmailConfig(**email_dict_config)
    # then
    mocked_send_email.assert_called_with(
        config=email_config,
        recipient_list=[recipient_email],
        context=payload,
        subject=expected_subject,
        template_str=expected_template_str,
    )
