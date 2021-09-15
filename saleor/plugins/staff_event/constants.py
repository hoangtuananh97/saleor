import os

from django.conf import settings

DEFAULT_EMAIL_TEMPLATES_PATH = os.path.join(
    settings.PROJECT_ROOT, "saleor/plugins/staff_event/default_email_templates"
)

SET_STAFF_EVENT_TEMPLATE_FIELD = "staff_event_template"


TEMPLATE_FIELDS = [
    SET_STAFF_EVENT_TEMPLATE_FIELD,
]

SET_STAFF_EVENT_DEFAULT_TEMPLATE = "staff_event.html"

SET_STAFF_EVENT_SUBJECT_FIELD = "set_staff_event_subject_field"
SET_STAFF_EVENT_DEFAULT_SUBJECT = "Staff Event e-mail"


PLUGIN_ID = "staff_event"
