import graphene

from saleor.core.permissions import ProductClassPermissions
from saleor.core.tracing import traced_atomic_transaction
from saleor.graphql.core.mutations import ModelMutation, ModelBulkDeleteMutation
from saleor.graphql.core.types.common import ProductClassRecommendationError
from saleor.graphql.product.mutations.product_class_recommendation import \
    ProductClassRecommendationInput, validate_product_class
from saleor.graphql.product.types import ProductClassRecommendation
from ....product_class import models


class ProductClassRecommendationBulkUpdateInput(ProductClassRecommendationInput):
    id = graphene.ID(
        description="ID of the product class recommendation.", required=True
    )


class ProductClassRecommendationBulkCreate(ModelMutation):
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
        input_cls = ProductClassRecommendationInput
        return input_cls

    @classmethod
    def add_field(cls, cleaned_input, data):
        cleaned_input["created_by"] = data
        return cleaned_input

    @classmethod
    def validate(cls, _root, info, **data):
        cleaned_inputs = []
        instances = []
        data = data.get("input")
        user = info.context.user
        input_cls = cls.config_input_cls()
        for item in data:
            instance = cls.get_instance(info, **item)
            cleaned_input = cls.clean_input(
                info,
                instance,
                item,
                input_cls=input_cls
            )
            validate_product_class(cleaned_input)
            cleaned_input = cls.add_field(cleaned_input, user)
            instance = cls.construct_instance(instance, cleaned_input)
            cls.clean_instance(info, instance)
            cleaned_inputs.append(cleaned_input)
            instances.append(instance)
        return instances, cleaned_inputs

    @classmethod
    def prepare_data(cls, _root, info, **data):
        instances, cleaned_inputs = cls.validate(_root, info, **data)
        return instances

    @classmethod
    @traced_atomic_transaction()
    def perform_mutation(cls, _root, info, **data):
        instances = cls.prepare_data(_root, info, **data)
        data = models.ProductClassRecommendation.objects.bulk_create(
            instances
        )
        return ProductClassRecommendationBulkCreate(
            count=len(data),
            product_class_recommendations=data
        )


class ProductClassRecommendationBulkUpdate(ProductClassRecommendationBulkCreate):
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
        input_cls = ProductClassRecommendationBulkUpdateInput
        return input_cls

    @classmethod
    def add_field(cls, cleaned_input, data):
        cleaned_input["updated_by"] = data
        return cleaned_input

    @classmethod
    @traced_atomic_transaction()
    def perform_mutation(cls, _root, info, **data):
        instances = cls.prepare_data(_root, info, **data)
        models.ProductClassRecommendation.objects.bulk_update(
            instances,
            [
                "listing_id",
                "product_class_qty",
                "product_class_value",
                "product_class_recommendation"
            ]
        )
        return ProductClassRecommendationBulkUpdate(
            count=len(instances),
            product_class_recommendations=instances
        )


class ProductClassRecommendationBulDelete(ModelBulkDeleteMutation):
    class Arguments:
        ids = graphene.List(
            graphene.ID,
            required=True,
            description="List of product class IDs to delete."
        )

    class Meta:
        model = models.ProductClassRecommendation
        description = "Delete product class."
        permissions = (ProductClassPermissions.MANAGE_PRODUCT_CLASS,)
        error_type_class = ProductClassRecommendationError
        error_type_field = "product_class_recommendation_errors"
