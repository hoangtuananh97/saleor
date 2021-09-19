from ...celeryconf import app
from ..email_common import EmailConfig, send_email


@app.task(compression="zlib")
def send_staff_event_email_task(recipient_email, payload, config, subject, template):
    email_config = EmailConfig(**config)
    send_email(
        config=email_config,
        recipient_list=[recipient_email],
        context=payload,
        subject=subject,
        template_str=template,
    )
