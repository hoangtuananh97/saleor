from collections import ChainMap
from typing import Dict, List, Tuple

from django.db.models import Value as V
from django.db.models.functions import Concat

from saleor.attribute.models import Attribute
from saleor.channel.models import Channel
from saleor.csv.product_variant_channel_list import (
    ProductVariantChannelListExportFields,
)
from saleor.warehouse.models import Warehouse


def get_export_fields_and_headers_info(
    export_info: Dict[str, list]
) -> Tuple[List[str], List[str], List[str]]:
    """Get export fields, all headers and headers mapping.

    Based on export_info returns exported fields, fields to headers mapping and
    all headers.
    Headers contains product, variant, attribute and warehouse headers.
    """
    export_fields, file_headers = get_product_export_fields_and_headers(export_info)

    data_headers = export_fields
    return export_fields, file_headers, data_headers


def get_product_export_fields_and_headers(
    export_info: Dict[str, list]
) -> Tuple[List[str], List[str]]:
    """Get export fields from export info and prepare headers mapping.

    Based on given fields headers from export info, export fields set and
    headers mapping is prepared.
    """
    export_fields = []  # type: List[str]
    file_headers = []  # type: List[str]

    fields = export_info.get("fields")
    if not fields:
        return export_fields, file_headers

    fields_mapping = dict(
        ChainMap(
            *reversed(
                ProductVariantChannelListExportFields.HEADERS_TO_FIELDS_MAPPING.values()
            )  # type: ignore
        )
    )
    for field in fields:
        lookup_field = fields_mapping[field]
        export_fields.append(lookup_field)
        file_headers.append(field.replace("_", " ").title())

    return export_fields, file_headers
