import json

from saleor.graphql.product.constants import (
    PRODUCT_ATTRIBUTE_ITEM_TYPE,
    PRODUCT_ATTRIBUTE_SELLING_UNIT,
)

EXPORT_PRODUCT_MAX_MIN_FIELDS = {
    "fields": {
        "channel_slug": "Channel Slug",
        "channel_name": "Channel Name",
        "variant_sku": "Variant SKU",
        "product_name": "Product Name",
        "selling_unit": "Selling Unit",
        "item_type": "Item Type",
        "current_product_class": "Current Product Class Recommendation",
        "previous_product_class": "Previous Product Class Recommendation",
        "previous_min_level": "Previous Min Level",
        "previous_max_level": "Previous Max Level",
        "current_min_level": "Current Min Level",
        "current_max_level": "Current Max Level",
    }
}


def prepare_data_for_export(queryset, previous_products_max_min):
    data = []
    for item in queryset:
        data.append(prepare_data_for_one_row(item, previous_products_max_min))

    return data


def prepare_data_for_one_row(item, previous_products_max_min):
    previous_min_level = 0
    previous_max_level = 0
    listing = item.listing

    for product_max_min in previous_products_max_min:
        if product_max_min.listing_id == item.listing_id:
            previous_min_level = product_max_min.min_level
            previous_max_level = product_max_min.max_level
            break

    obj = {
        "channel_slug": listing.channel.slug,
        "channel_name": listing.channel.name,
        "variant_sku": listing.variant.sku,
        "product_name": listing.variant.product.name,
        "selling_unit": get_product_attribute_value(
            listing.variant, "selling_unit", PRODUCT_ATTRIBUTE_SELLING_UNIT
        ),
        "item_type": get_product_attribute_value(
            listing.variant, "item_type", PRODUCT_ATTRIBUTE_ITEM_TYPE
        ),
        "current_product_class": get_product_class_metadata(
            listing.metadata, "current"
        ),
        "previous_product_class": get_product_class_metadata(
            listing.metadata, "previous"
        ),
        "previous_min_level": previous_min_level,
        "previous_max_level": previous_max_level,
        "current_min_level": item.min_level,
        "current_max_level": item.max_level,
    }

    return obj


def get_product_class_metadata(metadata, type_content):
    product_class = metadata.get("product_class")
    if not product_class:
        return ""
    data = product_class.get(type_content, None)
    if not data:
        return ""
    return json.dumps(data)


def get_product_attribute_value(variant, field_attribute, attribute_key):
    field = "unit"
    product = variant.product
    attribute = (
        product.attributes.values("unit", "entity_type")
        .filter(assignment__attribute__slug=attribute_key)
        .first()
    )
    if not attribute:
        return ""
    if field_attribute == "item_type":
        field = "entity_type"
    return attribute[field]

