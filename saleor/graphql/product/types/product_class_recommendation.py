import graphene
from graphene import relay
from graphene_federation import key

from .channels import ProductVariantChannelListing
from ...account.types import User
from ...core.connection import CountableDjangoObjectType
from ....product_class import models


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
        description = (
            "Represents a type of ProductClassRecommendation."
        )
        interfaces = [relay.Node]
        model = models.ProductClassRecommendation
