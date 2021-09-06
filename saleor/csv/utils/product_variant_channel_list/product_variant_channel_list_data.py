from collections import defaultdict
from typing import TYPE_CHECKING, Dict, List, Optional, Set, Union

from django.db.models.aggregates import Sum
from django.db.models.expressions import RawSQL, Subquery
from django.db.models.fields import IntegerField
from django.db.models.functions import Coalesce
from django.db.models import OuterRef, Exists

from saleor.channel.models import Channel
from saleor.csv.utils.product_variant_channel_list import \
    ProductVariantChannelListExportFields
from saleor.product.models import ProductVariantChannelListing
from saleor.shipping.models import ShippingZone
from saleor.warehouse.models import Allocation, Stock

if TYPE_CHECKING:
    from django.db.models import QuerySet


def get_products_data(
        queryset: "QuerySet",
        export_fields: Set[str],
        attribute_ids: Optional[List[int]],
        warehouse_ids: Optional[List[int]],
        channel_ids: Optional[List[int]],
) -> List[Dict[str, Union[str, bool]]]:
    """Create data list of products and their variants with fields values.

    It return list with product and variant data which can be used as import to
    csv writer and list of attribute and warehouse headers.
    """

    products_with_variants_data = []

    product_fields = set(
        ProductVariantChannelListExportFields.HEADERS_TO_FIELDS_MAPPING[
            "fields"].values()
    )

    product_export_fields = export_fields & product_fields
    if not warehouse_ids:
        product_export_fields.add("total_stock_all_warehouse")
        raw_sql = """
         (SELECT SUM(U0."quantity") AS "total_stock"
         FROM "warehouse_stock" U0
         WHERE U0."product_variant_id" = "product_productvariant"."id"
         AND U0."warehouse_id" IN %s
         GROUP BY U0."product_variant_id")
        """
        products_data = (
            queryset.annotate(
                total_stock_all_warehouse=RawSQL(
                    sql=raw_sql, params=[get_warehouse_by_channels()]
                )
            )
                .order_by("pk", )
                .values(*product_export_fields)
                .distinct("pk", )
        )
        return products_data

    else:
        product_export_fields.add("variant__stocks__warehouse__id")
        products_data = (
            queryset
                .order_by("pk", "variant__stocks__warehouse__id")
                .values(*product_export_fields)
                .distinct("pk", "variant__stocks__warehouse__id")
        )

        if warehouse_ids:
            products_data = products_data.filter(variant__stocks__warehouse__id__in=warehouse_ids)

        variants_relations_data = get_variants_relations_data(
            queryset, export_fields, attribute_ids, warehouse_ids, channel_ids
        )

        for product_data in products_data:
            variant__stocks__warehouse__id = product_data.pop("variant__stocks__warehouse__id")
            variant__sku = product_data.pop("variant__sku")

            variant_relations_data: Dict[str, str] = variants_relations_data.get(
                "{}{}".format(variant__stocks__warehouse__id, variant__sku), {}
            )

            data = {**product_data, **variant_relations_data}

            products_with_variants_data.append(data)
        return products_with_variants_data


def get_warehouse_by_channels():

    channels_slug = ProductVariantChannelListing.objects.\
        values_list('channel__slug', flat=True).distinct()

    ShippingZoneChannel = Channel.shipping_zones.through  # type: ignore
    WarehouseShippingZone = ShippingZone.warehouses.through  # type: ignore
    channels = Channel.objects.filter(slug__in=channels_slug).values("pk")
    shipping_zone_channels = ShippingZoneChannel.objects.filter(
        Exists(channels.filter(pk=OuterRef("channel_id")))
    ).values("shippingzone_id")
    warehouse_shipping_zones = WarehouseShippingZone.objects.filter(
        Exists(
            shipping_zone_channels.filter(
                shippingzone_id=OuterRef("shippingzone_id")
            )
        )
    ).values_list("warehouse_id", flat=True)

    return tuple([str(ele) for ele in warehouse_shipping_zones])


def get_variants_relations_data(
    queryset: "QuerySet",
    export_fields: Set[str],
    attribute_ids: Optional[List[int]],
    warehouse_ids: Optional[List[int]],
    channel_ids: Optional[List[int]],
) -> Dict[int, Dict[str, str]]:
    """Get data about variants relations fields.

    If any many to many fields are in export_fields or some attribute_ids or
    warehouse_ids exists then dict with variant relations fields is returned.
    Otherwise it returns empty dict.
    """
    relations_fields = export_fields
    if relations_fields or attribute_ids or warehouse_ids or channel_ids:
        return prepare_variants_relations_data(
            queryset, relations_fields, attribute_ids, warehouse_ids, channel_ids
        )

    return {}

def prepare_variants_relations_data(
    queryset: "QuerySet",
    fields: Set[str],
    attribute_ids: Optional[List[int]],
    warehouse_ids: Optional[List[int]],
    channel_ids: Optional[List[int]],
) -> Dict[int, Dict[str, str]]:
    """Prepare data about variants relation fields for given queryset.

    It return dict where key is a product pk, value is a dict with relation fields data.
    """
    warehouse_fields = ProductVariantChannelListExportFields.WAREHOUSE_FIELDS

    result_data: Dict[str, dict] = defaultdict(dict)
    fields.add("variant__stocks__warehouse__id")

    if warehouse_ids:
        fields.update(warehouse_fields.values())

    relations_data = queryset.values(*fields).order_by('variant__stocks__warehouse__id')

    for data in relations_data.iterator():
        warehouse_id = data.get("variant__stocks__warehouse__id")
        variant_sku = data.get("variant__sku")
        result_data, data = handle_warehouse_data(
            "{}{}".format(warehouse_id, variant_sku), data, warehouse_ids, result_data, warehouse_fields
        )

    result: Dict[int, Dict[str, str]] = {
        pk: {
            header: ", ".join(sorted(values)) if isinstance(values, set) else values
            for header, values in data.items()
        }
        for pk, data in result_data.items()
    }
    return result


def handle_warehouse_data(
    pk: str,
    data: dict,
    warehouse_ids: Optional[List[int]],
    result_data: Dict[str, dict],
    warehouse_fields: dict,
):
    warehouse_data: dict = {}

    warehouse_pk = str(data.pop(warehouse_fields["warehouse_pk"], ""))
    warehouse_data = {
        "slug": data.pop(warehouse_fields["slug"], None),
        "qty": data.pop(warehouse_fields["quantity"], None),
    }

    if warehouse_ids and warehouse_pk in warehouse_ids:
        result_data = add_warehouse_info_to_data(pk, warehouse_data, result_data)

    return result_data, data


def add_warehouse_info_to_data(
    pk: str,
    warehouse_data: Dict[str, Union[Optional[str]]],
    result_data: Dict[str, dict],
) -> Dict[str, dict]:
    """Add info about stock quantity to variant data.

    This functions adds info about stock quantity to dict with variant data.
    It returns updated data.
    """

    slug = warehouse_data["slug"]
    if slug:
        warehouse_qty_header = f"{slug} (warehouse quantity)"
        if warehouse_qty_header not in result_data[pk]:
            result_data[pk][warehouse_qty_header] = warehouse_data["qty"]

    return result_data


