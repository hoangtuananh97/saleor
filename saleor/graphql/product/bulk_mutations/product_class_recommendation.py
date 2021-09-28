import graphene

from saleor.core.permissions import ProductClassPermissions
from saleor.core.tracing import traced_atomic_transaction
from saleor.graphql.core.mutations import (
    BaseBulkMutation,
    ModelBulkDeleteMutation,
    ModelMutation,
)
from saleor.graphql.core.types.common import ProductClassRecommendationError
from saleor.graphql.product.mutations.product_class_recommendation import (
    ProductClassRecommendationChangeStatusMixin,
    ProductClassRecommendationInput,
    ProductClassRecommendationMixin,
)
from saleor.graphql.product.types import ProductClassRecommendation

from ....product_class import models


class ProductClassRecommendationBulkUpdateInput(ProductClassRecommendationInput):
    id = graphene.ID(
        description="ID of the product class recommendation.", required=True
    )


class BaseProductClassRecommendationBulk(
    ModelMutation, ProductClassRecommendationMixin
):
    count = graphene.Int(
        required=True,
        default_value=0,
        description="Returns how many objects were created.",
    )
    product_class_recommendations = graphene.List(
        graphene.NonNull(ProductClassRecommendation),
        required=True,
        default_value=[],
        description="List of the created product class.",
    )

    class Meta:
        abstract = True

    @classmethod
    def config_input_cls(cls):
        raise NotImplementedError

    @classmethod
    def add_field(cls, cleaned_input, data):
        raise NotImplementedError

    @classmethod
    def validate(cls, _root, info, **data):
        cleaned_inputs = []
        instances = []
        data = data.get("input")
        input_cls = cls.config_input_cls()
        user = info.context.user
        for item in data:
            instance = cls.get_instance(info, **item)
            cleaned_input = cls.clean_input(info, instance, item, input_cls=input_cls)
            cls.validate_product_class(cleaned_input)
            cleaned_input = cls.add_field(cleaned_input, user)
            instance = cls.construct_instance(instance, cleaned_input)
            cls.clean_instance(info, instance)
            cleaned_inputs.append(cleaned_input)
            instances.append(instance)
        return instances


class ProductClassRecommendationBulkCreate(BaseProductClassRecommendationBulk):
    class Arguments:
        input = graphene.List(
            graphene.NonNull(ProductClassRecommendationInput),
            required=True,
            description="Input list of product class to create.",
        )

    class Meta:
        model = models.ProductClassRecommendation
        description = "Creates product class."
        permissions = (ProductClassPermissions.MANAGE_PRODUCT_CLASS,)
        error_type_class = ProductClassRecommendationError
        error_type_field = "product_class_recommendation_errors"

    @classmethod
    def config_input_cls(cls):
        return ProductClassRecommendationInput

    @classmethod
    def add_field(cls, cleaned_input, data):
        cleaned_input["created_by"] = data
        return cleaned_input

    @classmethod
    @traced_atomic_transaction()
    def perform_mutation(cls, _root, info, **data):
        instances = cls.validate(_root, info, **data)
        data = models.ProductClassRecommendation.objects.bulk_create(instances)
        return ProductClassRecommendationBulkCreate(
            count=len(data), product_class_recommendations=data
        )


class ProductClassRecommendationBulkUpdate(BaseProductClassRecommendationBulk):
    class Arguments:
        input = graphene.List(
            graphene.NonNull(ProductClassRecommendationBulkUpdateInput),
            required=True,
            description="Input list of product class to update.",
        )

    class Meta:
        model = models.ProductClassRecommendation
        description = "Update product class."
        permissions = (ProductClassPermissions.MANAGE_PRODUCT_CLASS,)
        error_type_class = ProductClassRecommendationError
        error_type_field = "product_class_recommendation_errors"

    @classmethod
    def config_input_cls(cls):
        return ProductClassRecommendationBulkUpdateInput

    @classmethod
    def add_field(cls, cleaned_input, data):
        cleaned_input["updated_by"] = data
        return cleaned_input

    @classmethod
    @traced_atomic_transaction()
    def perform_mutation(cls, _root, info, **data):
        instances = cls.validate(_root, info, **data)
        models.ProductClassRecommendation.objects.bulk_update(
            instances,
            [
                "listing_id",
                "product_class_qty",
                "product_class_value",
                "product_class_recommendation",
            ],
        )
        return ProductClassRecommendationBulkUpdate(
            count=len(instances), product_class_recommendations=instances
        )


class ProductClassRecommendationBulkDelete(ModelBulkDeleteMutation):
    class Arguments:
        ids = graphene.List(
            graphene.ID,
            required=True,
            description="List of product class IDs to delete.",
        )

    class Meta:
        model = models.ProductClassRecommendation
        description = "Delete product class."
        permissions = (ProductClassPermissions.MANAGE_PRODUCT_CLASS,)
        error_type_class = ProductClassRecommendationError
        error_type_field = "product_class_recommendation_errors"


class ProductClassRecommendationBulkChangeStatus(
    BaseBulkMutation, ProductClassRecommendationChangeStatusMixin
):
    class Arguments:
        ids = graphene.List(
            graphene.NonNull(graphene.ID),
            required=True,
            description="Ids of product class to update status.",
        )
        status = graphene.String(
            required=True,
            description="Status of product class to update status.",
        )

    class Meta:
        model = models.ProductClassRecommendation
        description = "Update status product class."
        permissions = (ProductClassPermissions.MANAGE_PRODUCT_CLASS,)
        error_type_class = ProductClassRecommendationError
        error_type_field = "product_class_recommendation_errors"

    @classmethod
    @traced_atomic_transaction()
    def bulk_action(cls, info, queryset, **data):
        status = data.get("status")
        cls.validate(data)
        queryset.update(status=status)
