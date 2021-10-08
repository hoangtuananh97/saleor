import json

from saleor.attribute.models import AssignedProductAttribute

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
        "selling_unit": get_product_attribute_value(listing.variant, "selling_unit"),
        "item_type": get_product_attribute_value(listing.variant, "item_type"),
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
    current = product_class.get("current", None)
    previous = product_class.get("previous", None)
    if not current and type_content == "current":
        return ""
    if not previous and type_content == "previous":
        return ""
    return json.dumps(current) if type_content == "current" else json.dumps(previous)


def get_product_attribute_value(variant, field_attribute):
    data = []
    product = variant.product
    assigned_products = AssignedProductAttribute.objects.filter(product_id=product.id)
    if not assigned_products:
        return ""
    for item in assigned_products:
        if field_attribute == "selling_unit":
            unit = item.attribute.unit
            if unit:
                data.append(unit)
        if field_attribute == "item_type":
            entity_type = item.attribute.entity_type
            if entity_type:
                data.append(entity_type)

    return json.dumps(data) if data else ""
