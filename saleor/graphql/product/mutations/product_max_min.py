import graphene
from django.core.exceptions import ValidationError

from saleor.graphql.core.mutations import ModelDeleteMutation, ModelMutation

from ....core.permissions import ProductMaxMinPermissions
from ....product_max_min import models
from ....product_max_min.error_codes import ProductMaxMinErrorCode
from ...core.types.common import ProductMaxMinError
from ..types.product_max_min import ProductMaxMin


class ProductMaxMinInput(graphene.InputObjectType):
    listing = graphene.ID(
        description="ID of the product variant channel listing.", required=True
    )
    min_level = graphene.Int(description="Product min level")
    max_level = graphene.Int(description="Product max level")


class ProductMaxMinMixin:
    class Meta:
        abstract = True

    @classmethod
    def validate_product_max_min(cls, instance, cleaned_input):
        max_level = cleaned_input.get("max_level")
        min_level = cleaned_input.get("min_level")
        if max_level and min_level and max_level < min_level:
            raise ValidationError(
                {
                    "product_max_min": ValidationError(
                        "The max level must larger than the min level",
                        code=ProductMaxMinErrorCode.INVALID.value,
                    )
                }
            )
        if max_level and instance.min_level > max_level:
            raise ValidationError(
                {
                    "product_max_min": ValidationError(
                        "The max level input must larger than the current min level",
                        code=ProductMaxMinErrorCode.INVALID.value,
                    )
                }
            )


class BaseProductMaxMin(ModelMutation, ProductMaxMinMixin):
    product_max_min = graphene.Field(ProductMaxMin)

    class Meta:
        abstract = True

    @classmethod
    def add_field(cls, cleaned_input, data):
        raise NotImplementedError

    @classmethod
    def clean_input(cls, info, instance, data):
        cleaned_input = super().clean_input(info, instance, data)
        # validate product class before mutation
        cls.validate_product_max_min(instance, cleaned_input)
        user = info.context.user
        cleaned_input = cls.add_field(cleaned_input, user)
        return cleaned_input


class ProductMaxMinCreate(BaseProductMaxMin):
    class Arguments:
        input = ProductMaxMinInput(
            required=True,
            description="Fields required to create a product max min.",
        )

    class Meta:
        description = "Create a product max min."
        model = models.ProductMaxMin
        permissions = (ProductMaxMinPermissions.MANAGE_PRODUCT_MAX_MIN,)
        error_type_class = ProductMaxMinError
        error_type_field = "product_max_min_errors"

    @classmethod
    def add_field(cls, cleaned_input, data):
        cleaned_input["created_by"] = data
        return cleaned_input


class ProductMaxMinUpdate(BaseProductMaxMin):
    class Arguments:
        id = graphene.ID(required=True, description="Id to update a product max min.")
        input = ProductMaxMinInput(
            required=True,
            description="Fields required to update a product max min.",
        )

    class Meta:
        description = "Update a product max min."
        model = models.ProductMaxMin
        permissions = (ProductMaxMinPermissions.MANAGE_PRODUCT_MAX_MIN,)
        error_type_class = ProductMaxMinError
        error_type_field = "product_max_min_errors"

    @classmethod
    def add_field(cls, cleaned_input, data):
        cleaned_input["updated_by"] = data
        return cleaned_input


class ProductMaxMinDelete(ModelDeleteMutation):
    class Arguments:
        id = graphene.ID(required=True, description="Id to delete a product max min.")

    class Meta:
        description = "Delete a product max min."
        model = models.ProductMaxMin
        permissions = (ProductMaxMinPermissions.MANAGE_PRODUCT_MAX_MIN,)
        error_type_class = ProductMaxMinError
        error_type_field = "product_max_min_errors"
