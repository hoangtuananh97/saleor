from typing import Dict, Union

from .utils.import_csv import import_saleor_ai
from ..celeryconf import app
from ..core import JobStatus
from . import events
from .models import ExportFile, ImportFile
from .notifications import send_export_failed_info
from .utils.export import export_products, export_products_max_min


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


def on_task_import_success(self, retval, task_id, args, kwargs):
    import_file_id = args[0]

    import_file = ImportFile.objects.get(pk=import_file_id)
    import_file.status = JobStatus.SUCCESS
    import_file.save(update_fields=["status", "updated_at"])
    events.import_success_event(
        import_file=import_file, user=import_file.user
    )


def on_task_import_failure(self, exc, task_id, args, kwargs, einfo):
    import_file_id = args[0]
    import_file = ImportFile.objects.get(pk=import_file_id)

    import_file.content_file = None
    import_file.status = JobStatus.FAILED
    import_file.save(update_fields=["status", "updated_at", "content_file"])

    events.import_failed_event(
        import_file=import_file,
        user=import_file.user,
        message=str(exc),
        error_type=str(einfo.type),
    )

    send_export_failed_info(import_file)


@app.task(on_success=on_task_import_success, on_failure=on_task_import_failure)
def import_saleor_ai_task(
    import_file_id: int,
    batch_data,
    batch_size,
):
    import_file = ImportFile.objects.get(pk=import_file_id)
    import_saleor_ai(import_file, batch_data, batch_size)
