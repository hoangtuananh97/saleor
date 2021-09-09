from typing import TYPE_CHECKING, Any, Dict, List, Set, Union

from django.db.models import Exists, OuterRef, Prefetch
from django.db.models.query import QuerySet

from saleor.channel.models import Channel
from saleor.csv.notifications import send_export_download_link_notification
from saleor.csv.utils.export import (
    append_to_file,
    create_file_with_headers,
    get_filename,
    queryset_in_batches,
    save_csv_file_in_export_file,
)
from saleor.product.models import ProductVariantChannelListing
from saleor.shipping.models import ShippingZone
from saleor.warehouse.models import Stock

from .product_variant_channel_list_data import get_products_variant_channel_list_data
from .product_variant_channel_list_headers import get_export_fields_and_headers_info

if TYPE_CHECKING:
    # flake8: noqa

    from saleor.csv.models import ExportFile

BATCH_SIZE = 10000


def export_products_variant_channel_list(
    export_file: "ExportFile",
    scope: Dict[str, Union[str, dict]],
    export_info: Dict[str, list],
    file_type: str,
    delimiter: str = ";",
):
    file_name = get_filename("product_variant_channel_list", file_type)

    queryset = filter_product_variant_channel_list_queryset(scope)

    export_fields, file_headers, data_headers = get_export_fields_and_headers_info(
        export_info
    )

    temporary_file = create_file_with_headers(file_headers, delimiter, file_type)

    export_products_variant_channel_list_in_batches(
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


def filter_product_variant_channel_list_queryset(
    scope: Dict[str, Union[str, dict]]
) -> "QuerySet":
    """Get product variant channel list queryset based on a scope."""

    queryset = ProductVariantChannelListing.objects.all()

    if "ids" in scope:
        queryset = ProductVariantChannelListing.objects.filter(pk__in=scope["ids"])

    queryset = queryset.order_by("pk")

    return queryset


def export_products_variant_channel_list_in_batches(
    queryset: "QuerySet",
    export_info: Dict[str, list],
    export_fields: Set[str],
    headers: List[str],
    delimiter: str,
    temporary_file: Any,
    file_type: str,
):
    for batch_pks in queryset_in_batches(queryset):
        products_variant_id = get_products_variant_ids_by_variant_channel_listing(
            batch_pks
        )
        product_batch = (
            ProductVariantChannelListing.objects.filter(pk__in=batch_pks)
            .select_related(
                "variant",
                "channel",
                "variant__product",
            )
            .prefetch_related(
                Prefetch(
                    "variant__stocks",
                    queryset=Stock.objects.select_related(
                        "variant__stocks__warehouse"
                    ).all(),
                )
            )
            .filter(variant__id__in=products_variant_id)
        )

        export_data = get_products_variant_channel_list_data(
            product_batch, export_fields
        )

        append_to_file(export_data, headers, temporary_file, file_type, delimiter)


def get_products_variant_ids_by_variant_channel_listing(batch_pks):
    channels_slug = (
        ProductVariantChannelListing.objects.values_list("channel__slug", flat=True)
        .filter(id__in=batch_pks)
        .distinct()
    )

    ShippingZoneChannel = Channel.shipping_zones.through  # type: ignore
    WarehouseShippingZone = ShippingZone.warehouses.through  # type: ignore
    channels = Channel.objects.filter(slug__in=set(channels_slug)).values("pk")
    shipping_zone_channels = ShippingZoneChannel.objects.filter(
        Exists(channels.filter(pk=OuterRef("channel_id")))
    ).values("shippingzone_id")
    warehouse_shipping_zones = WarehouseShippingZone.objects.filter(
        Exists(
            shipping_zone_channels.filter(shippingzone_id=OuterRef("shippingzone_id"))
        )
    ).values_list("warehouse_id", flat=True)

    products_variant_id = Stock.objects.filter(
        Exists(warehouse_shipping_zones.filter(warehouse_id=OuterRef("warehouse_id")))
    ).values_list("product_variant_id", flat=True)

    return products_variant_id
