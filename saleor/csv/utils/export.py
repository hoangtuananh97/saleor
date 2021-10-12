import secrets
from datetime import date, datetime
from tempfile import NamedTemporaryFile
from typing import IO, TYPE_CHECKING, Any, Dict, List, Set, Union

import petl as etl
from django.utils import timezone

from ...graphql.product.filters_product_max_min import ProductMaxMinFilter
from ...product.models import Product
from ...product_max_min.models import ProductMaxMin
from .. import FileTypes
from ..notifications import send_export_download_link_notification
from . import product_max_min
from .product_headers import get_export_fields_and_headers_info
from .product_max_min import EXPORT_PRODUCT_MAX_MIN_FIELDS
from .products_data import get_products_data

if TYPE_CHECKING:
    # flake8: noqa
    from django.db.models import QuerySet

    from ..models import ExportFile


BATCH_SIZE = 10000


def export_products(
    export_file: "ExportFile",
    scope: Dict[str, Union[str, dict]],
    export_info: Dict[str, list],
    file_type: str,
    delimiter: str = ";",
):
    file_name = get_filename("product", file_type)
    queryset = get_product_queryset(scope)

    export_fields, file_headers, data_headers = get_export_fields_and_headers_info(
        export_info
    )

    temporary_file = create_file_with_headers(file_headers, delimiter, file_type)

    export_products_in_batches(
        queryset,
        export_info,
        set(export_fields),
        data_headers,
        delimiter,
        temporary_file,
        file_type,
    )

    save_csv_file_in_export_file(export_file, temporary_file, file_name)
    temporary_file.close()

    send_export_download_link_notification(export_file)


def get_product_max_min_queryset(filters):
    current_product_max_min_ids = []
    previous_products_max_min = []
    qs_group_partition = ProductMaxMin.objects.qs_group_partition()
    for item in qs_group_partition:
        if item.row_number > 2:
            continue
        if item.row_number == 1:
            current_product_max_min_ids.append(item.id)
        if item.row_number == 2:
            previous_products_max_min.append(item)

    queryset = ProductMaxMin.objects.qs_filter_current_previous().filter(
        id__in=current_product_max_min_ids
    )
    ids = filters.get("ids")
    filters = filters.get("filters")
    if ids:
        queryset = queryset.filter(pk__in=ids)
    if filters:
        queryset = ProductMaxMinFilter(data=filters, queryset=queryset).qs

    return queryset.distinct().order_by("-created_at"), list(previous_products_max_min)


def product_max_min_filter_to_export_headers(export_info):
    export_fields = []
    file_headers = []

    fields = export_info.get("fields")
    if not fields:
        return export_fields, file_headers

    for field in fields:
        export_fields.append(field)
        file_headers.append(EXPORT_PRODUCT_MAX_MIN_FIELDS["fields"][field])

    return export_fields, file_headers


def export_products_max_min(
    export_file: "ExportFile",
    scope: Dict[str, Union[str, dict]],
    export_info: Dict[str, list],
    file_type: str,
    delimiter: str = ";",
):
    file_name = get_filename("product_max_min", file_type)
    queryset, previous_products_max_min = get_product_max_min_queryset(scope)
    export_fields, file_headers = product_max_min_filter_to_export_headers(export_info)
    temporary_file = create_file_with_headers(file_headers, delimiter, file_type)
    export_data = product_max_min.prepare_data_for_export(
        queryset, previous_products_max_min
    )
    append_to_file(
        export_data,
        export_fields,
        temporary_file,
        file_type,
        delimiter,
    )
    save_csv_file_in_export_file(export_file, temporary_file, file_name)
    temporary_file.close()

    send_export_download_link_notification(export_file)


def get_filename(model_name: str, file_type: str) -> str:
    hash = secrets.token_hex(nbytes=3)
    return "{}_data_{}_{}.{}".format(
        model_name, timezone.now().strftime("%d_%m_%Y_%H_%M_%S"), hash, file_type
    )


def parse_input(data: Any) -> Dict[str, Union[str, dict]]:
    """Parse input to correct data types, since scope coming from celery will be parsed to strings."""
    if "attributes" in data:
        serialized_attributes = []

        for attr in data.get("attributes") or []:
            if "date_time" in attr:
                if gte := attr["date_time"].get("gte"):
                    attr["date_time"]["gte"] = datetime.fromisoformat(gte)
                if lte := attr["date_time"].get("lte"):
                    attr["date_time"]["lte"] = datetime.fromisoformat(lte)

            if "date" in attr:
                if gte := attr["date"].get("gte"):
                    attr["date"]["gte"] = date.fromisoformat(gte)
                if lte := attr["date"].get("lte"):
                    attr["date"]["lte"] = date.fromisoformat(lte)

            serialized_attributes.append(attr)

        if serialized_attributes:
            data["attributes"] = serialized_attributes

    return data


def get_product_queryset(scope: Dict[str, Union[str, dict]]) -> "QuerySet":
    """Get product queryset based on a scope."""

    from ...graphql.product.filters import ProductFilter

    queryset = Product.objects.all()
    if "ids" in scope:
        queryset = Product.objects.filter(pk__in=scope["ids"])
    elif "filter" in scope:
        queryset = ProductFilter(
            data=parse_input(scope["filter"]), queryset=queryset
        ).qs

    queryset = queryset.order_by("pk")

    return queryset


def queryset_in_batches(queryset):
    """Slice a queryset into batches.

    Input queryset should be sorted be pk.
    """
    start_pk = 0

    while True:
        qs = queryset.filter(pk__gt=start_pk)[:BATCH_SIZE]
        pks = list(qs.values_list("pk", flat=True))

        if not pks:
            break

        yield pks

        start_pk = pks[-1]


def export_products_in_batches(
    queryset: "QuerySet",
    export_info: Dict[str, list],
    export_fields: Set[str],
    headers: List[str],
    delimiter: str,
    temporary_file: Any,
    file_type: str,
):
    warehouses = export_info.get("warehouses")
    attributes = export_info.get("attributes")
    channels = export_info.get("channels")

    for batch_pks in queryset_in_batches(queryset):
        product_batch = Product.objects.filter(pk__in=batch_pks).prefetch_related(
            "attributes",
            "variants",
            "collections",
            "media",
            "product_type",
            "category",
        )

        export_data = get_products_data(
            product_batch, export_fields, attributes, warehouses, channels
        )

        append_to_file(export_data, headers, temporary_file, file_type, delimiter)


def create_file_with_headers(file_headers: List[str], delimiter: str, file_type: str):
    table = etl.wrap([file_headers])

    if file_type == FileTypes.CSV:
        temp_file = NamedTemporaryFile("ab+", suffix=".csv")
        etl.tocsv(table, temp_file.name, delimiter=delimiter)
    else:
        temp_file = NamedTemporaryFile("ab+", suffix=".xlsx")
        etl.io.xlsx.toxlsx(table, temp_file.name)

    return temp_file


def append_to_file(
    export_data: List[Dict[str, Union[str, bool]]],
    headers: List[str],
    temporary_file: Any,
    file_type: str,
    delimiter: str,
):
    table = etl.fromdicts(export_data, header=headers, missing=" ")

    if file_type == FileTypes.CSV:
        etl.io.csv.appendcsv(table, temporary_file.name, delimiter=delimiter)
    else:
        etl.io.xlsx.appendxlsx(table, temporary_file.name)


def save_csv_file_in_export_file(
    export_file: "ExportFile", temporary_file: IO[bytes], file_name: str
):
    export_file.content_file.save(file_name, temporary_file)
