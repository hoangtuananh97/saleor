import graphene
from django.db import transaction
from django.forms.models import model_to_dict
from django.utils import timezone

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

from ....product_class import ProductClassRecommendationStatus, models
from ..enums import ProductClassRecommendationEnum


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
        for instance in instances:
            instance.updated_at = timezone.datetime.now()
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
        status = ProductClassRecommendationEnum(
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
    def clean_instance(cls, info, instance):
        status = info.variable_values["status"]
        cls.check_permission_change_status(info, status)
        cls.check_instance(instance)

    @classmethod
    def save_bulk_metadata(cls, listing_ids):
        group_data_by_listing = {}
        # get new values
        product_classes = models.ProductClassRecommendation.objects.filter(
            status=ProductClassRecommendationStatus.APPROVED, listing_id__in=listing_ids
        )
        product_classes = product_classes.order_by("listing_id", "-approved_at")
        # because loop order by approved_at => only get 1 or 2 value in dict
        for item in product_classes:
            if item.listing_id not in group_data_by_listing.keys():
                group_data_by_listing[item.listing_id] = [model_to_dict(item)]
            else:
                value = group_data_by_listing[item.listing_id]
                if len(value) == 2:
                    continue
                group_data_by_listing[item.listing_id].append(model_to_dict(item))

        # TODO: (issue performance) Update many value different with many id different
        with transaction.atomic():
            for key, values in group_data_by_listing.items():
                obj_metadata = {
                    "current": cls.fields_save_metadata(values[0]),
                }
                if len(values) > 1:
                    obj_metadata["previous"] = cls.fields_save_metadata(values[1])

                listing = models.ProductVariantChannelListing.objects.get(id=key)
                listing.store_value_in_metadata({"product_class": obj_metadata})
                listing.save()
        return True

    @classmethod
    @traced_atomic_transaction()
    def bulk_action(cls, info, queryset, **data):
        listing_ids = []
        status = data.get("status")
        cls.validate(info, data)
        user = info.context.user
        obj_update = {
            "updated_by_id": user.id,
            "status": status,
            "updated_at": timezone.datetime.now(),
        }
        if status == ProductClassRecommendationStatus.APPROVED:
            obj_update["approved_by_id"] = user.id
            obj_update["approved_at"] = timezone.datetime.now()
            listing_ids = queryset.values_list("listing_id", flat=True)
        queryset.update(**obj_update)
        cls.save_bulk_metadata(listing_ids)
