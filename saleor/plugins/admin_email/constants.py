import os

from django.conf import settings

DEFAULT_EMAIL_TEMPLATES_PATH = os.path.join(
    settings.PROJECT_ROOT, "saleor/plugins/admin_email/default_email_templates"
)

STAFF_ORDER_CONFIRMATION_TEMPLATE_FIELD = "staff_order_confirmation_template"
SET_STAFF_PASSWORD_TEMPLATE_FIELD = "set_staff_password_template"
CSV_PRODUCT_EXPORT_SUCCESS_TEMPLATE_FIELD = "csv_product_export_success_template"
CSV_EXPORT_FAILED_TEMPLATE_FIELD = "csv_export_failed_template"
STAFF_PASSWORD_RESET_TEMPLATE_FIELD = "staff_password_reset_template"
SET_STAFF_EVENT_TEMPLATE_FIELD = "staff_event_template"


TEMPLATE_FIELDS = [
    STAFF_ORDER_CONFIRMATION_TEMPLATE_FIELD,
    SET_STAFF_PASSWORD_TEMPLATE_FIELD,
    CSV_PRODUCT_EXPORT_SUCCESS_TEMPLATE_FIELD,
    CSV_EXPORT_FAILED_TEMPLATE_FIELD,
    STAFF_PASSWORD_RESET_TEMPLATE_FIELD,
    SET_STAFF_EVENT_TEMPLATE_FIELD,
]

SET_STAFF_PASSWORD_DEFAULT_TEMPLATE = "set_password.html"
CSV_PRODUCT_EXPORT_SUCCESS_DEFAULT_TEMPLATE = "export_products_file.html"
CSV_EXPORT_FAILED_TEMPLATE_DEFAULT_TEMPLATE = "export_failed.html"
STAFF_ORDER_CONFIRMATION_DEFAULT_TEMPLATE = "staff_confirm_order.html"
STAFF_PASSWORD_RESET_DEFAULT_TEMPLATE = "password_reset.html"
SET_STAFF_EVENT_DEFAULT_TEMPLATE = "staff_event.html"


STAFF_ORDER_CONFIRMATION_SUBJECT_FIELD = "staff_order_confirmation_subject"
SET_STAFF_PASSWORD_SUBJECT_FIELD = "set_staff_password_subject"
CSV_PRODUCT_EXPORT_SUCCESS_SUBJECT_FIELD = "csv_product_export_success_subject"
CSV_EXPORT_FAILED_SUBJECT_FIELD = "csv_export_failed_subject"
STAFF_PASSWORD_RESET_SUBJECT_FIELD = "staff_password_reset_subject"
SET_STAFF_EVENT_SUBJECT_FIELD = "set_staff_event_subject_field"


STAFF_ORDER_CONFIRMATION_DEFAULT_SUBJECT = "Order {{ order.id }} details"
SET_STAFF_PASSWORD_DEFAULT_SUBJECT = "Set password e-mail"
CSV_PRODUCT_EXPORT_SUCCESS_DEFAULT_SUBJECT = "Export products data"
CSV_EXPORT_FAILED_DEFAULT_SUBJECT = "Export products data"
STAFF_PASSWORD_RESET_DEFAULT_SUBJECT = "Staff password reset"
SET_STAFF_EVENT_DEFAULT_SUBJECT = "Staff Event e-mail"

staff_password_notify = {
    "title": "Set Password",
    "content": "Notification set Password",
}
product_export_success_notify = {
    "title": "Export product success",
    "content": "Notification export product success",
}
order_confirmation_notify = {
    "title": "Order Confirmation",
    "content": "Notification new order confirmation",
}
product_export_failed_notify = {
    "title": "export product failed",
    "content": "Notification export product failed",
}
reset_password_notify = {
    "title": "export product failed",
    "content": "Notification export product failed",
}

PLUGIN_ID = "mirumee.notifications.admin_email"
