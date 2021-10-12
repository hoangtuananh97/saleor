import graphene

from ...csv import ExportEvents, FileTypes
from ...graphql.core.enums import to_enum

ExportEventEnum = to_enum(ExportEvents)
FileTypeEnum = to_enum(FileTypes)


class ExportScope(graphene.Enum):
    ALL = "all"
    IDS = "ids"
    FILTER = "filter"

    @property
    def description(self):
        # pylint: disable=no-member
        description_mapping = {
            ExportScope.ALL.name: "Export all products.",
            ExportScope.IDS.name: "Export products with given ids.",
            ExportScope.FILTER.name: "Export the filtered products.",
        }
        if self.name in description_mapping:
            return description_mapping[self.name]
        raise ValueError("Unsupported enum value: %s" % self.value)


class ProductFieldEnum(graphene.Enum):
    NAME = "name"
    DESCRIPTION = "description"
    PRODUCT_TYPE = "product type"
    CATEGORY = "category"
    PRODUCT_WEIGHT = "product weight"
    COLLECTIONS = "collections"
    CHARGE_TAXES = "charge taxes"
    PRODUCT_MEDIA = "product media"
    VARIANT_SKU = "variant sku"
    VARIANT_WEIGHT = "variant weight"
    VARIANT_MEDIA = "variant media"


class ProductMaxMinFieldEnum(graphene.Enum):
    CHANNEL_SLUG = "channel_slug"
    CHANNEL_NAME = "channel_name"
    VARIANT_SKU = "variant_sku"
    PRODUCT_NAME = "product_name"
    SELLING_UNIT = "selling_unit"
    ITEM_TYPE = "item_type"
    CURRENT_PRODUCT_CLASS = "current_product_class"
    PREVIOUS_PRODUCT_CLASS = "previous_product_class"
    PREVIOUS_MIN_LEVEL = "previous_min_level"
    PREVIOUS_MAX_LEVEL = "previous_max_level"
    CURRENT_MIN_LEVEL = "current_min_level"
    CURRENT_MAX_LEVEL = "current_max_level"
