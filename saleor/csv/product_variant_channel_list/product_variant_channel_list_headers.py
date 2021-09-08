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
    warehouses_headers = get_warehouses_headers(export_info)

    data_headers = export_fields + warehouses_headers
    file_headers += warehouses_headers
    return export_fields, file_headers, data_headers


def get_product_export_fields_and_headers(
    export_info: Dict[str, list]
) -> Tuple[List[str], List[str]]:
    """Get export fields from export info and prepare headers mapping.

    Based on given fields headers from export info, export fields set and
    headers mapping is prepared.
    """
    export_fields = []
    file_headers = []

    fields = export_info.get("fields")
    warehouses_ids = export_info.get("warehouses")
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
        if warehouses_ids and (
            field == "total_stock_availability" or field == "total_stock_allocated"
        ):
            continue
        lookup_field = fields_mapping[field]
        export_fields.append(lookup_field)
        file_headers.append(field.replace("_", " ").title())

    return export_fields, file_headers


def get_attributes_headers(export_info: Dict[str, list]) -> List[str]:
    """Get headers for exported attributes.

    Headers are build from slug and contains information if it's a product or variant
    attribute. Respectively for product: "slug-value (product attribute)"
    and for variant: "slug-value (variant attribute)".
    """

    attribute_ids = export_info.get("attributes")
    if not attribute_ids:
        return []

    attributes = Attribute.objects.filter(pk__in=attribute_ids).order_by("slug")

    products_headers = (
        attributes.filter(product_types__isnull=False)
        .distinct()
        .annotate(header=Concat("slug", V(" (product attribute)")))
        .values_list("header", flat=True)
    )

    variant_headers = (
        attributes.filter(product_variant_types__isnull=False)
        .distinct()
        .annotate(header=Concat("slug", V(" (variant attribute)")))
        .values_list("header", flat=True)
    )

    return list(products_headers) + list(variant_headers)


def get_warehouses_headers(export_info: Dict[str, list]) -> List[str]:
    """Get headers for exported warehouses.

    Headers are build from slug. Example: "slug-value (warehouse quantity)"
    """
    warehouse_ids = export_info.get("warehouses")
    if not warehouse_ids:
        return []

    warehouses_headers = (
        Warehouse.objects.filter(pk__in=warehouse_ids)
        .order_by("slug")
        .annotate(header=Concat("slug", V(" (warehouse quantity)")))
        .values_list("header", flat=True)
    )

    return list(warehouses_headers)


def get_channels_headers(export_info: Dict[str, list]) -> List[str]:
    """Get headers for exported channels.

    Headers are build from slug and exported field.

    Example:
    - currency code data header: "slug-value (channel currency code)"
    - published data header: "slug-value (channel visible)"
    - publication date data header: "slug-value (channel publication date)"

    """
    channel_ids = export_info.get("channels")
    if not channel_ids:
        return []

    channels_slugs = (
        Channel.objects.filter(pk__in=channel_ids)
        .order_by("slug")
        .values_list("slug", flat=True)
    )

    return list(channels_slugs)
