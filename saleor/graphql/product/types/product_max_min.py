import graphene
from graphene_federation import key

from saleor.graphql.core.connection import CountableDjangoObjectType
from saleor.graphql.product.types import ProductVariantChannelListing

from ....product_max_min import models
from ...account.types import User


@key(fields="id")
class ProductMaxMin(CountableDjangoObjectType):
    listing = graphene.Field(
        ProductVariantChannelListing,
        description="ID of the product variant channel listing.",
    )
    min_level = graphene.Int(description="Product min level")
    max_level = graphene.Int(description="Product max level")
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
        description = "Represents a type of ProductMaxMin."
        interfaces = [graphene.relay.Node]
        model = models.ProductMaxMin


@key(fields="id")
class CurrentPreviousProductMaxMin(CountableDjangoObjectType):
    product_max_min_current = graphene.Field(ProductMaxMin, required=False)
    product_max_min_previous = graphene.Field(ProductMaxMin, required=False)

    class Meta:
        description = "Represents a type of product max min."
        interfaces = [graphene.relay.Node]
        model = models.ProductMaxMin

    @staticmethod
    def product_max_min_current(root: models.ProductMaxMin, _info, **_kwargs):
        return root

    @staticmethod
    def product_max_min_previous(root: models.ProductMaxMin, _info, **_kwargs):
        return root
