import csv
from io import StringIO
from typing import Dict, Union

from celery import chord

from saleor_ai.models import SaleorAI

from ..account.models import User
from ..celeryconf import app
from ..core import JobStatus
from . import events
from .events import import_started_event
from .models import ExportFile, ImportFile
from .notifications import send_export_failed_info, send_import_failed_info
from .utils.export import export_products, export_products_max_min
from .utils.import_csv import (
    export_data_error_saleor_ai,
    import_saleor_ai,
    read_one_row,
)


def on_task_failure(self, exc, task_id, args, kwargs, einfo):
    export_file_id = args[0]
    export_file = ExportFile.objects.get(pk=export_file_id)

    export_file.content_file = None
    export_file.status = JobStatus.FAILED
    export_file.save(update_fields=["status", "updated_at", "content_file"])

    events.export_failed_event(
        export_file=export_file,
        user=export_file.user,
        app=export_file.app,
        message=str(exc),
        error_type=str(einfo.type),
    )

    send_export_failed_info(export_file)


def on_task_success(self, retval, task_id, args, kwargs):
    export_file_id = args[0]

    export_file = ExportFile.objects.get(pk=export_file_id)
    export_file.status = JobStatus.SUCCESS
    export_file.save(update_fields=["status", "updated_at"])
    events.export_success_event(
        export_file=export_file, user=export_file.user, app=export_file.app
    )


@app.task(on_success=on_task_success, on_failure=on_task_failure)
def export_products_task(
    export_file_id: int,
    scope: Dict[str, Union[str, dict]],
    export_info: Dict[str, list],
    file_type: str,
    delimiter: str = ";",
):
    export_file = ExportFile.objects.get(pk=export_file_id)
    export_products(export_file, scope, export_info, file_type, delimiter)


@app.task(on_success=on_task_success, on_failure=on_task_failure)
def export_products_max_min_task(
    export_file_id: int,
    scope: Dict[str, Union[str, dict]],
    export_info: Dict[str, list],
    file_type: str,
    delimiter: str = ";",
):
    export_file = ExportFile.objects.get(pk=export_file_id)
    export_products_max_min(export_file, scope, export_info, file_type, delimiter)


def on_task_import_success(import_file):
    import_file.status = JobStatus.SUCCESS
    import_file.save(update_fields=["status", "updated_at"])
    events.import_success_event(import_file=import_file, user=import_file.user)


def on_task_import_failure(import_file, exc, error_type):
    import_file.content_file = None
    import_file.status = JobStatus.FAILED
    import_file.save(update_fields=["status", "updated_at", "content_file"])

    events.import_failed_event(
        import_file=import_file,
        user=import_file.user,
        message=str(exc),
        error_type=str(error_type),
    )

    send_import_failed_info(import_file)


@app.task()
def import_saleor_ai_task(
    import_file_id: int,
    content,
    user_id,
    batch_size,
):
    batch_data = []
    group_batch_data = []
    user = User.objects.get(id=user_id)
    import_file = ImportFile.objects.get(pk=import_file_id)
    csv_data = csv.reader(StringIO(content), delimiter=",")
    next(csv_data)
    start_row = 1
    for row in csv_data:
        data = read_one_row(row)
        batch_data.append(data)
        len_batch_data = len(batch_data)
        if len_batch_data > batch_size:
            batch_data_obj = {
                "start_row": start_row,
                "batch_data": batch_data,
            }
            group_batch_data.append(batch_data_obj)
            import_started_event(import_file=import_file, user=user)
            start_row = start_row + len_batch_data
            batch_data = []
    if batch_data:
        batch_data_obj = {
            "start_row": start_row,
            "batch_data": batch_data,
        }
        group_batch_data.append(batch_data_obj)
        import_started_event(import_file=import_file, user=user)

    return chord(
        import_saleor_ai_sub_task.s(import_file, item, user)
        for item in group_batch_data
    )(import_saleor_ai_result.s(import_file, user))


@app.task()
def import_saleor_ai_sub_task(import_file, batch_data, user):
    return import_saleor_ai(import_file, batch_data, user)


@app.task(on_success=on_task_success, on_failure=on_task_failure)
def export_data_error_saleor_ai_task(
    export_file_id,
    data_error,
    export_info,
):
    export_file = ExportFile.objects.get(pk=export_file_id)
    export_data_error_saleor_ai(export_file, data_error, export_info)


@app.task()
def import_saleor_ai_result(result_error, import_file, user):
    result_success = True
    data_error = []
    for items in result_error:
        if items:
            result_success = False
            for item in items:
                data_error.append(item)
    import_file = ImportFile.objects.get(pk=import_file.id)
    if result_success:
        on_task_import_success(import_file)
    else:
        export_info = [field.name for field in SaleorAI._meta.fields]
        export_file = ExportFile.objects.create(user=user)
        export_data_error_saleor_ai_task.delay(export_file.id, data_error, export_info)
        on_task_import_failure(import_file, "FAILED", "Validation")
