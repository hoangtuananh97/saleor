import graphene
from django.utils import timezone

from saleor.graphql.core.mutations import ModelBulkDeleteMutation, ModelMutation
from saleor.graphql.product.mutations.product_max_min import (
    ProductMaxMinInput,
    ProductMaxMinMixin,
)
from saleor.graphql.product.types.product_max_min import ProductMaxMin

from ....core.permissions import ProductMaxMinPermissions
from ....core.tracing import traced_atomic_transaction
from ....product_max_min import models
from ...core.types.common import ProductMaxMinError


class ProductMaxMinBulkUpdateInput(ProductMaxMinInput):
    id = graphene.ID(description="ID of the product class max min.", required=True)


class BaseProductMaxMinBulk(ModelMutation, ProductMaxMinMixin):
    count = graphene.Int(
        required=True,
        default_value=0,
        description="Returns how many objects were created.",
    )
    products_max_min = graphene.List(
        graphene.NonNull(ProductMaxMin),
        required=True,
        default_value=[],
        description="List of the created product max min.",
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
        instances = []
        data = data.get("input")
        input_cls = cls.config_input_cls()
        user = info.context.user
        for item in data:
            instance = cls.get_instance(info, **item)
            cleaned_input = cls.clean_input(info, instance, item, input_cls=input_cls)
            cls.validate_product_max_min(instance, cleaned_input)
            cleaned_input = cls.add_field(cleaned_input, user)
            instance = cls.construct_instance(instance, cleaned_input)
            cls.clean_instance(info, instance)
            instances.append(instance)
        return instances


class ProductMaxMinBulkCreate(BaseProductMaxMinBulk):
    class Arguments:
        input = graphene.List(
            graphene.NonNull(ProductMaxMinInput),
            required=True,
            description="Input list of product max min to create.",
        )

    class Meta:
        model = models.ProductMaxMin
        description = "Creates product max min."
        permissions = (ProductMaxMinPermissions.MANAGE_PRODUCT_MAX_MIN,)
        error_type_class = ProductMaxMinError
        error_type_field = "product_class_max_min_errors"

    @classmethod
    def config_input_cls(cls):
        return ProductMaxMinInput

    @classmethod
    def add_field(cls, cleaned_input, data):
        cleaned_input["created_by"] = data
        return cleaned_input

    @classmethod
    @traced_atomic_transaction()
    def perform_mutation(cls, _root, info, **data):
        instances = cls.validate(_root, info, **data)
        data = models.ProductMaxMin.objects.bulk_create(instances)
        return ProductMaxMinBulkCreate(count=len(data), products_max_min=data)


class ProductMaxMinBulkUpdate(BaseProductMaxMinBulk):
    class Arguments:
        input = graphene.List(
            graphene.NonNull(ProductMaxMinBulkUpdateInput),
            required=True,
            description="Input list of product max min to update.",
        )

    class Meta:
        model = models.ProductMaxMin
        description = "Update product max min."
        permissions = (ProductMaxMinPermissions.MANAGE_PRODUCT_MAX_MIN,)
        error_type_class = ProductMaxMinError
        error_type_field = "product_class_max_min_errors"

    @classmethod
    def config_input_cls(cls):
        return ProductMaxMinBulkUpdateInput

    @classmethod
    def add_field(cls, cleaned_input, data):
        cleaned_input["updated_by"] = data
        return cleaned_input

    @classmethod
    @traced_atomic_transaction()
    def perform_mutation(cls, _root, info, **data):
        instances = cls.validate(_root, info, **data)
        for instance in instances:
            instance.updated_at = timezone.datetime.now()
        models.ProductMaxMin.objects.bulk_update(
            instances,
            [
                "min_level",
                "max_level",
                "listing_id",
            ],
        )
        return ProductMaxMinBulkUpdate(count=len(instances), products_max_min=instances)


class ProductMaxMinBulkDelete(ModelBulkDeleteMutation):
    class Arguments:
        ids = graphene.List(
            graphene.ID,
            required=True,
            description="List of product class IDs to delete.",
        )

    class Meta:
        model = models.ProductMaxMin
        description = "Delete product max min."
        permissions = (ProductMaxMinPermissions.MANAGE_PRODUCT_MAX_MIN,)
        error_type_class = ProductMaxMinError
        error_type_field = "product_class_max_min_errors"
