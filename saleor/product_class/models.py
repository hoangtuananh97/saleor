from django.db import models

# Create your models here.
from saleor import settings
from saleor.core.permissions import ProductClassPermissions
from saleor.product.models import ProductVariantChannelListing
from saleor.product_class import ProductClassRecommendationType


class ProductClassRecommendation(models.Model):
    listing = models.ForeignKey(
        ProductVariantChannelListing,
        on_delete=models.CASCADE,
        related_name="products_class_recommendation",
    )
    product_class_qty = models.CharField(blank=True, null=True, max_length=256)
    product_class_value = models.CharField(blank=True, null=True, max_length=256)
    product_class_recommendation = models.CharField(
        blank=True, null=True, max_length=256
    )
    status = models.CharField(
        choices=ProductClassRecommendationType.CHOICES,
        max_length=128,
        default=ProductClassRecommendationType.DRAFT,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="staff_created_product_class",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="staff_updated_product_class",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="staff_approved_product_class",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    approved_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ("pk",)
        app_label = "product_class"

        permissions = (
            (
                ProductClassPermissions.MANAGE_PRODUCT_CLASS.codename,
                "Manage product class recommendation."
            ),
        )
