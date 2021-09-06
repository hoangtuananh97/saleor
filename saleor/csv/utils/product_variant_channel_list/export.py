from typing import TYPE_CHECKING, Dict, Union, Set, List, Any

from django.db.models import Prefetch, OuterRef, Exists
from django.db.models.aggregates import Sum
from django.db.models.expressions import Subquery
from django.db.models.fields import IntegerField
from django.db.models.functions import Coalesce

from saleor.channel.models import Channel
from saleor.product.models import ProductVariantChannelListing
from saleor.shipping.models import ShippingZone
from saleor.warehouse.models import Stock, Allocation
from .product_variant_channel_list_data import get_products_data
from .product_variant_channel_list_headers import get_export_fields_and_headers_info
from ..export import get_filename, create_file_with_headers, \
    save_csv_file_in_export_file, queryset_in_batches, append_to_file, parse_input
from ...notifications import send_export_download_link_notification

if TYPE_CHECKING:
    # flake8: noqa

    from ...models import ExportFile

BATCH_SIZE = 10000


def export_products_variant_channel_list(
        export_file: "ExportFile",
        scope: Dict[str, Union[str, dict]],
        export_info: Dict[str, list],
        file_type: str,
        delimiter: str = ";",
):
    file_name = get_filename("product_variant_channel_list", file_type)

    queryset = filter_product_queryset(scope)

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


def filter_product_queryset(scope: Dict[str, Union[str, dict]]) -> "QuerySet":
    """Get product queryset based on a scope."""

    from saleor.graphql.product.filters import ProductFilter

    queryset = ProductVariantChannelListing.objects.all()

    if "ids" in scope:
        queryset = ProductVariantChannelListing.objects.filter(pk__in=scope["ids"])
    elif "filter" in scope:
        product_ids = ProductFilter(
            data=parse_input(scope["filter"]), queryset=queryset
        ).qs.values_list('id', flat=True)
        queryset = queryset.filter(variant__product_id__in=product_ids)

    queryset = queryset.order_by("pk")

    return queryset


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
        product_batch = ProductVariantChannelListing.objects.filter(pk__in=batch_pks). \
            select_related(
            "variant",
            "channel",
            "variant__product",
        ).prefetch_related(
            Prefetch(
                "variant__stocks",
                queryset=Stock.objects.select_related("variant__stocks__warehouse").all())
        )

        export_data = get_products_data(
            product_batch, export_fields, attributes, warehouses, channels
        )

        append_to_file(export_data, headers, temporary_file, file_type, delimiter)
