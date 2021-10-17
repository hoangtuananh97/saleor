from typing import TYPE_CHECKING, Optional

from . import ExportEvents, ImportEvents
from .models import ExportEvent, ImportEvent, ImportFile

if TYPE_CHECKING:
    from ..account.models import User
    from ..app.models import App
    from .models import ExportFile


UserType = Optional["User"]
AppType = Optional["App"]


def export_started_event(
    *, export_file: "ExportFile", user: UserType = None, app: AppType = None
):
    ExportEvent.objects.create(
        export_file=export_file, user=user, app=app, type=ExportEvents.EXPORT_PENDING
    )


def export_success_event(
    *, export_file: "ExportFile", user: UserType = None, app: AppType = None
):
    ExportEvent.objects.create(
        export_file=export_file, user=user, app=app, type=ExportEvents.EXPORT_SUCCESS
    )


def export_failed_event(
    *,
    export_file: "ExportFile",
    user: UserType = None,
    app: AppType = None,
    message: str,
    error_type: str
):
    ExportEvent.objects.create(
        export_file=export_file,
        user=user,
        app=app,
        type=ExportEvents.EXPORT_FAILED,
        parameters={"message": message, "error_type": error_type},
    )


def export_deleted_event(
    *, export_file: "ExportFile", user: UserType = None, app: AppType = None
):
    ExportEvent.objects.create(
        export_file=export_file, user=user, app=app, type=ExportEvents.EXPORT_DELETED
    )


def export_file_sent_event(*, export_file_id: int, user_id: int):
    ExportEvent.objects.create(
        export_file_id=export_file_id,
        user_id=user_id,
        type=ExportEvents.EXPORTED_FILE_SENT,
    )


def export_failed_info_sent_event(*, export_file_id: int, user_id: int):
    ExportEvent.objects.create(
        export_file_id=export_file_id,
        user_id=user_id,
        type=ExportEvents.EXPORT_FAILED_INFO_SENT,
    )


def import_started_event(*, import_file: "ImportFile", user: UserType = None):
    ImportEvent.objects.create(
        import_file=import_file, user=user, type=ImportEvents.IMPORT_PENDING
    )


def import_success_event(*, import_file: "ImportFile", user: UserType = None):
    ImportEvent.objects.create(
        import_file=import_file, user=user, type=ImportEvents.IMPORT_SUCCESS
    )


def import_failed_event(
    *, import_file: "ImportFile", user: UserType = None, message: str, error_type: str
):
    ImportEvent.objects.create(
        import_file=import_file,
        user=user,
        type=ImportEvents.IMPORT_FAILED,
        parameters={"message": message, "error_type": error_type},
    )


def import_deleted_event(*, import_file: "ImportFile", user: UserType = None):
    ImportEvent.objects.create(
        import_file=import_file, user=user, type=ImportEvents.IMPORT_DELETED
    )


def import_file_sent_event(*, import_file_id: int, user_id: int):
    ImportEvent.objects.create(
        import_file_id=import_file_id,
        user_id=user_id,
        type=ImportEvents.IMPORTED_FILE_SENT,
    )


def import_failed_info_sent_event(*, import_file_id: int, user_id: int):
    ImportEvent.objects.create(
        import_file_id=import_file_id,
        user_id=user_id,
        type=ImportEvents.IMPORT_FAILED_INFO_SENT,
    )
