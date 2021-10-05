from django.db import models

from saleor import settings
from saleor.core.permissions import ProductMaxMinPermissions
from saleor.product.models import ProductVariantChannelListing


class ProductMaxMin(models.Model):
    listing = models.ForeignKey(
        ProductVariantChannelListing,
        on_delete=models.CASCADE,
        related_name="products_max_min",
    )
    min_level = models.PositiveIntegerField(default=0)
    max_level = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="staff_created_products_max_min",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="staff_updated_products_max_min",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="staff_approved_products_max_min",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    approved_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        app_label = "product_max_min"

        permissions = (
            (
                ProductMaxMinPermissions.MANAGE_PRODUCT_MAX_MIN.codename,
                "Manage product max min.",
            ),
        )
