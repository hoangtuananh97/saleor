import graphene

from saleor.graphql.core.enums import to_enum
from saleor.product_class import ProductClassRecommendationStatus

ProductClassRecommendationEnum = to_enum(
    ProductClassRecommendationStatus, type_name="ProductClassRecommendationEnum"
)


class ProductAttributeType(graphene.Enum):
    PRODUCT = "PRODUCT"
    VARIANT = "VARIANT"


class StockAvailability(graphene.Enum):
    IN_STOCK = "AVAILABLE"
    OUT_OF_STOCK = "OUT_OF_STOCK"


class CollectionPublished(graphene.Enum):
    PUBLISHED = "published"
    HIDDEN = "hidden"


class ProductTypeConfigurable(graphene.Enum):
    CONFIGURABLE = "configurable"
    SIMPLE = "simple"


class ProductTypeEnum(graphene.Enum):
    DIGITAL = "digital"
    SHIPPABLE = "shippable"


class VariantAttributeScope(graphene.Enum):
    ALL = "all"
    VARIANT_SELECTION = "variant_selection"
    NOT_VARIANT_SELECTION = "not_variant_selection"
