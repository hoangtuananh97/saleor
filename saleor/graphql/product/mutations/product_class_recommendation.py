import graphene

from saleor.core.permissions import ProductClassPermissions
from saleor.core.tracing import traced_atomic_transaction
from saleor.graphql.core.mutations import BaseMutation
from saleor.graphql.core.types.common import ProductClassRecommendationError
from saleor.graphql.core.utils import from_global_id_or_error
from saleor.graphql.product.enums import ProductClassRecommendationEnum
from saleor.product_class import ProductClassRecommendationType
from saleor.product_class.models import ProductClassRecommendation


class ProductClassRecommendationInput(graphene.InputObjectType):
    listing_id = graphene.ID(
        description="ID of the product variant channel listing.",
        required=True
    )
    product_class_qty = graphene.String(description="Product class qty")
    product_class_value = graphene.String(description="Product class value")
    product_class_recommendation = graphene.String(
        description="Product class recommendation"
    )
    status = ProductClassRecommendationEnum(
        description="Status product class",
        required=False
    )
    created_by_id = graphene.ID(
        description="ID of user to create.",
        required=False,
    )
    updated_by_id = graphene.ID(
        description="ID of user to update.",
        required=False,
    )
    approved_by_id = graphene.ID(
        description="ID of user to approved.",
        required=False,
    )
    approved_at = graphene.DateTime(
        description="Time of user to approved.",
        required=False,
    )


class ProductClassRecommendationCreate(BaseMutation):
    from saleor.graphql.product.types.product_class_recommendation import \
        ProductClassRecommendation
    product_class_recommendation = graphene.Field(ProductClassRecommendation)

    class Arguments:
        input = ProductClassRecommendationInput(
            required=True,
            description="Fields required to create a product class recommendation."
        )

    class Meta:
        description = (
            "Create a product class recommendation."
        )
        permissions = (ProductClassPermissions.MANAGE_PRODUCT_CLASS,)
        error_type_class = ProductClassRecommendationError
        error_type_field = "product_class_recommendation_errors"

    @classmethod
    def perform_mutation(cls, _root, info, **data):
        from saleor.graphql.product.types.channels import ProductVariantChannelListing

        data = data.get("input")
        listing_id = data.get("listing_id")
        user_id = info.context.user.id

        listing = cls.get_node_or_error(
            info, listing_id, ProductVariantChannelListing
        )

        product_class_recommendation = ProductClassRecommendation.objects.create(
            listing_id=listing.id,
            product_class_qty=data.get("product_class_qty"),
            product_class_value=data.get("product_class_value"),
            product_class_recommendation=data.get("product_class_recommendation"),
            status=data.get("status", ProductClassRecommendationType.DRAFT),
            created_by_id=user_id,
            updated_by_id=user_id,
            approved_by_id=user_id,
            approved_at=data.get("approved_at"),
        )
        return ProductClassRecommendationCreate(
            product_class_recommendation=product_class_recommendation
        )


class ProductClassRecommendationUpdate(ProductClassRecommendationCreate):
    class Arguments:
        id = graphene.ID(
            required=True,
            description="Id to update a product class recommendation."
        )
        input = ProductClassRecommendationInput(
            required=True,
            description="Fields required to update a product class recommendation."
        )

    class Meta:
        description = (
            "Update a product class recommendation."
        )
        permissions = (ProductClassPermissions.MANAGE_PRODUCT_CLASS,)
        error_type_class = ProductClassRecommendationError
        error_type_field = "product_class_recommendation_errors"

    @classmethod
    @traced_atomic_transaction()
    def perform_mutation(cls, _root, info, **data):
        from saleor.graphql.product.types.channels import ProductVariantChannelListing

        pk = data.get("id")
        data = data.get("input")
        listing_id = data.get("listing_id")
        user_id = info.context.user.id

        listing = cls.get_node_or_error(
            info, listing_id, ProductVariantChannelListing
        )
        _, pk = from_global_id_or_error(pk, "ProductClassRecommendation")

        product_class = ProductClassRecommendation.objects.select_for_update().get(
            id=pk)
        product_class.listing_id = listing.id
        product_class.product_class_qty = data.get("product_class_qty")
        product_class.product_class_value = data.get("product_class_value")
        product_class.product_class_recommendation = data.get(
            "product_class_recommendation")
        product_class.status = data.get("status", ProductClassRecommendationType.DRAFT)
        product_class.created_by_id = user_id
        product_class.updated_by_id = user_id
        product_class.approved_by_id = user_id
        product_class.approved_at = data.get("approved_at")
        product_class.save()
        return ProductClassRecommendationUpdate(
            product_class_recommendation=product_class
        )


class ProductClassRecommendationDelete(BaseMutation):
    deleted = graphene.Boolean(
        description="Response after delete."
    )

    class Arguments:
        id = graphene.ID(
            required=True,
            description="Id to delete a product class recommendation."
        )

    class Meta:
        description = (
            "Delete a product class recommendation."
        )
        permissions = (ProductClassPermissions.MANAGE_PRODUCT_CLASS,)
        error_type_class = ProductClassRecommendationError
        error_type_field = "product_class_recommendation_errors"

    @classmethod
    @traced_atomic_transaction()
    def perform_mutation(cls, _root, info, **data):
        pk = data.get("id")

        _, pk = from_global_id_or_error(pk, "ProductClassRecommendation")

        product_class = ProductClassRecommendation.objects.select_for_update().get(
            id=pk)
        product_class.delete()
        return ProductClassRecommendationDelete(
            deleted=True
        )
