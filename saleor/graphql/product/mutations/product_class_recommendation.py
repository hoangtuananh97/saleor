import graphene
from django.core.exceptions import ValidationError

from saleor.core.permissions import ProductClassPermissions
from saleor.core.tracing import traced_atomic_transaction
from saleor.graphql.core.mutations import (
    BaseMutation,
    ModelDeleteMutation,
    ModelMutation,
)
from saleor.graphql.core.types.common import ProductClassRecommendationError
from saleor.graphql.core.utils import from_global_id_or_error
from saleor.graphql.product.enums import ProductClassRecommendationEnum
from saleor.graphql.product.types.product_class_recommendation import (
    ProductClassRecommendation,
)
from saleor.product_class import ProductClassRecommendationStatus

from ....product_class import models
from ....product_class.error_codes import ProductClassRecommendationErrorCode
from ..types.channels import ProductVariantChannelListing


class ProductClassRecommendationInput(graphene.InputObjectType):
    listing = graphene.ID(
        description="ID of the product variant channel listing.", required=True
    )
    product_class_qty = graphene.String(description="Product class qty")
    product_class_value = graphene.String(description="Product class value")
    product_class_recommendation = graphene.String(
        description="Product class recommendation"
    )


class ProductClassRecommendationCreate(ModelMutation):
    product_class_recommendation = graphene.Field(ProductClassRecommendation)

    class Arguments:
        input = ProductClassRecommendationInput(
            required=True,
            description="Fields required to create a product class recommendation.",
        )

    class Meta:
        description = "Create a product class recommendation."
        model = models.ProductClassRecommendation
        permissions = (ProductClassPermissions.MANAGE_PRODUCT_CLASS,)
        error_type_class = ProductClassRecommendationError
        error_type_field = "product_class_recommendation_errors"

    @classmethod
    def clean_input(cls, info, instance, data):
        cleaned_input = super().clean_input(info, instance, data)
        # validate product class before mutation
        validate_product_class(cleaned_input)
        user = info.context.user
        cleaned_input["created_by"] = user
        return cleaned_input

    @classmethod
    @traced_atomic_transaction()
    def save(cls, info, instance, cleaned_input):
        instance.save()


class ProductClassRecommendationUpdate(ModelMutation):
    class Arguments:
        id = graphene.ID(
            required=True, description="Id to update a product class recommendation."
        )
        input = ProductClassRecommendationInput(
            required=True,
            description="Fields required to update a product class recommendation.",
        )

    class Meta:
        description = "Update a product class recommendation."
        model = models.ProductClassRecommendation
        permissions = (ProductClassPermissions.MANAGE_PRODUCT_CLASS,)
        error_type_class = ProductClassRecommendationError
        error_type_field = "product_class_recommendation_errors"

    @classmethod
    def clean_input(cls, info, instance, data):
        cleaned_input = super().clean_input(info, instance, data)
        # validate product class before mutation
        validate_product_class(cleaned_input)

        user = info.context.user
        cleaned_input["updated_by"] = user
        return cleaned_input

    @classmethod
    @traced_atomic_transaction()
    def save(cls, info, instance, cleaned_input):
        instance.save()


class ProductClassRecommendationDelete(ModelDeleteMutation):
    class Arguments:
        id = graphene.ID(
            required=True, description="Id to delete a product class recommendation."
        )

    class Meta:
        description = "Delete a product class recommendation."
        model = models.ProductClassRecommendation
        permissions = (ProductClassPermissions.MANAGE_PRODUCT_CLASS,)
        error_type_class = ProductClassRecommendationError
        error_type_field = "product_class_recommendation_errors"

    @classmethod
    @traced_atomic_transaction()
    def perform_mutation(cls, _root, info, **data):
        return super().perform_mutation(info, info, **data)


def validate_product_class(cleaned_input):
    validation_errors = {}
    product_class_qty = cleaned_input.get("product_class_qty")
    product_class_value = cleaned_input.get("product_class_value")
    if not product_class_qty:
        validation_errors["product_class_qty"] = ValidationError(
            {
                "product_class": ValidationError(
                    "Product class qty is required",
                    code=ProductClassRecommendationErrorCode.REQUIRED.value,
                )
            }
        )
    if not product_class_value:
        validation_errors["product_class_value"] = ValidationError(
            {
                "product_class": ValidationError(
                    "Product class qty is required",
                    code=ProductClassRecommendationErrorCode.REQUIRED.value,
                )
            }
        )
    if validation_errors:
        raise ValidationError(validation_errors)
    return True
