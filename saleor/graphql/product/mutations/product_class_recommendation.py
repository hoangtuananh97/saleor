import graphene
from django.core.exceptions import ValidationError
from django.db import transaction
from django.forms.models import model_to_dict
from django.utils import timezone

from saleor.core.permissions import ProductClassPermissions
from saleor.core.tracing import traced_atomic_transaction
from saleor.graphql.core.mutations import (
    BaseMutation,
    ModelDeleteMutation,
    ModelMutation,
)
from saleor.graphql.core.types.common import ProductClassRecommendationError
from saleor.graphql.product.types.product_class_recommendation import (
    ProductClassRecommendation,
)
from saleor.product_class import ProductClassRecommendationStatus

from ....core.exceptions import PermissionDenied
from ....product_class import models
from ....product_class.error_codes import ProductClassRecommendationErrorCode
from ..enums import ProductClassRecommendationEnum


class ProductClassRecommendationInput(graphene.InputObjectType):
    listing = graphene.ID(
        description="ID of the product variant channel listing.", required=True
    )
    product_class_qty = graphene.String(description="Product class qty")
    product_class_value = graphene.String(description="Product class value")
    product_class_recommendation = graphene.String(
        description="Product class recommendation"
    )


class ProductClassRecommendationMixin:
    class Meta:
        abstract = True

    @classmethod
    def validate_product_class(cls, cleaned_input):
        product_class_qty = cleaned_input.get("product_class_qty")
        product_class_value = cleaned_input.get("product_class_value")
        if not product_class_qty:
            raise ValidationError(
                {
                    "product_class": ValidationError(
                        "Product class qty is required",
                        code=ProductClassRecommendationErrorCode.REQUIRED.value,
                    )
                }
            )
        if not product_class_value:
            raise ValidationError(
                {
                    "product_class": ValidationError(
                        "Product class value is required",
                        code=ProductClassRecommendationErrorCode.REQUIRED.value,
                    )
                }
            )


class ProductClassRecommendationChangeStatusMixin:
    class Meta:
        abstract = True

    @classmethod
    def check_permission_change_status(cls, info, status):
        if status == ProductClassRecommendationStatus.APPROVED:
            approved_permission = (ProductClassPermissions.APPROVE_PRODUCT_CLASS,)
            if not BaseMutation.check_permissions(info.context, approved_permission):
                raise PermissionDenied()
        return True

    @classmethod
    def validate(cls, info, cleaned_input):
        pass

    @classmethod
    def fields_save_metadata(cls, data):
        return {
            "product_class_qty": data["product_class_qty"],
            "product_class_value": data["product_class_value"],
            "product_class_recommendation": data["product_class_recommendation"],
            "status": data["status"],
            "approved_at": data["approved_at"],
        }

    @classmethod
    def check_instance(cls, instance):
        if instance.status == ProductClassRecommendationStatus.APPROVED:
            raise ValidationError(
                {
                    "product_class": ValidationError(
                        "A product class have been approved",
                        code=ProductClassRecommendationErrorCode.INVALID.value,
                    )
                }
            )
        return True


class BaseProductClassRecommendation(ModelMutation, ProductClassRecommendationMixin):
    product_class_recommendation = graphene.Field(ProductClassRecommendation)

    class Meta:
        abstract = True

    @classmethod
    def add_field(cls, cleaned_input, data):
        raise NotImplementedError

    @classmethod
    def clean_input(cls, info, instance, data):
        cleaned_input = super().clean_input(info, instance, data)
        # validate product class before mutation
        cls.validate_product_class(cleaned_input)
        user = info.context.user
        cleaned_input = cls.add_field(cleaned_input, user)
        return cleaned_input

    @classmethod
    @traced_atomic_transaction()
    def save(cls, info, instance, cleaned_input):
        instance.save()


class ProductClassRecommendationCreate(BaseProductClassRecommendation):
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
    def add_field(cls, cleaned_input, data):
        cleaned_input["created_by"] = data
        return cleaned_input


class ProductClassRecommendationUpdate(BaseProductClassRecommendation):
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
    def add_field(cls, cleaned_input, data):
        cleaned_input["updated_by"] = data
        return cleaned_input


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


class ProductClassRecommendationChangeStatus(
    BaseMutation, ProductClassRecommendationChangeStatusMixin
):
    product_class_recommendation = graphene.Field(ProductClassRecommendation)

    class Arguments:
        id = graphene.ID(
            required=True, description="Id to update a product class recommendation."
        )
        status = ProductClassRecommendationEnum(
            required=True,
            description="Fields required to update status a product class.",
        )

    class Meta:
        description = "Update status a product class recommendation."
        model = models.ProductClassRecommendation
        permissions = (ProductClassPermissions.MANAGE_PRODUCT_CLASS,)
        error_type_class = ProductClassRecommendationError
        error_type_field = "product_class_recommendation_errors"

    @classmethod
    @traced_atomic_transaction()
    def update_metadata(cls, product_class_current):
        listing_id = product_class_current.listing_id
        listing = product_class_current.listing
        product_class_previous = (
            models.ProductClassRecommendation.objects.filter(
                listing_id=listing_id, status=ProductClassRecommendationStatus.APPROVED
            )
            .exclude(id=product_class_current.id)
            .order_by("-approved_at")
            .first()
        )

        obj_metadata = {
            "current": cls.fields_save_metadata(model_to_dict(product_class_current)),
        }
        if product_class_previous:
            obj_metadata["previous"] = cls.fields_save_metadata(
                model_to_dict(product_class_previous)
            )
        listing.store_value_in_metadata({"product_class": obj_metadata})
        listing.save()

    @classmethod
    @traced_atomic_transaction()
    def perform_mutation(cls, _root, info, **data):
        pk = data.get("id")
        status = data.get("status")
        user = info.context.user
        cls.validate(info, data)
        cls.check_permission_change_status(info, status)
        product_class = cls.get_node_or_error(
            info, pk, only_type=ProductClassRecommendation
        )
        cls.check_instance(product_class)
        product_class.status = status
        product_class.updated_by_id = user.id

        if status == ProductClassRecommendationStatus.APPROVED:
            product_class.approved_by_id = user.id
            product_class.approved_at = timezone.datetime.now()

        product_class.save()
        transaction.on_commit(lambda: cls.update_metadata(product_class))
        return ProductClassRecommendationChangeStatus(
            product_class_recommendation=product_class
        )
