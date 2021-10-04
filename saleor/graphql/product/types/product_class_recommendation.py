import graphene
from graphene import relay
from graphene_federation import key

from ....core.permissions import ProductClassPermissions
from ....product_class import ProductClassRecommendationStatus, models
from ...account.types import User
from ...core.connection import CountableDjangoObjectType
from .channels import ProductVariantChannelListing


@key(fields="id")
class ProductClassRecommendation(CountableDjangoObjectType):
    listing = graphene.Field(
        ProductVariantChannelListing,
        description="ID of the product variant channel listing.",
    )
    product_class_qty = graphene.String(description="Product class qty")
    product_class_value = graphene.String(description="Product class value")
    product_class_recommendation = graphene.String(
        description="Product class recommendation"
    )
    status = graphene.String(
        description="Status product class",
    )
    created_by = graphene.Field(
        User,
        description="ID of user to create.",
    )
    updated_by = graphene.Field(
        User,
        description="ID of user to update.",
    )
    approved_by = graphene.Field(
        User,
        description="ID of user to approved.",
    )
    created_at = graphene.DateTime(
        description="Time of user to created.",
    )
    updated_at = graphene.DateTime(
        description="Time of user to update.",
    )
    approved_at = graphene.DateTime(
        description="Time of user to approved.",
    )

    class Meta:
        description = "Represents a type of ProductClassRecommendation."
        interfaces = [relay.Node]
        model = models.ProductClassRecommendation


@key(fields="id")
class CurrentPreviousProductClass(CountableDjangoObjectType):
    product_class_current = graphene.Field(ProductClassRecommendation, required=False)
    product_class_previous = graphene.Field(ProductClassRecommendation, required=False)

    class Meta:
        description = "Represents a type of ProductClassRecommendation."
        interfaces = [relay.Node]
        model = models.ProductClassRecommendation

    @staticmethod
    def resolve_product_class_current(
        root: models.ProductClassRecommendation, _info, **_kwargs
    ):
        product_classes = (
            models.ProductClassRecommendation.objects.qs_filter_current_previous(
                order_by="created_at desc",
                filter_row_number="= 1",
                list_status=[
                    ProductClassRecommendationStatus.APPROVED,
                    ProductClassRecommendationStatus.SUBMITTED,
                ],
            ).filter(listing_id=root.listing_id)
        )
        return product_classes.first()

    @staticmethod
    def resolve_product_class_previous(
        root: models.ProductClassRecommendation, _info, **_kwargs
    ):
        permissions = (ProductClassPermissions.APPROVE_PRODUCT_CLASS,)
        if not _info.context.user.has_perms(permissions):
            return None

        product_classes = (
            models.ProductClassRecommendation.objects.qs_filter_current_previous(
                order_by="created_at desc",
                filter_row_number="= 2",
                list_status=[
                    ProductClassRecommendationStatus.APPROVED,
                    ProductClassRecommendationStatus.SUBMITTED,
                ],
            ).filter(listing_id=root.listing_id)
        )
        return product_classes.first()
