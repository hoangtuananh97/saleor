from django.db import models

# Create your models here.
from django.db.models import ExpressionWrapper, Q
from django.db.models.expressions import F, Window
from django.db.models.functions import RowNumber

from saleor import settings
from saleor.core.permissions import ProductClassPermissions
from saleor.product.models import ProductVariantChannelListing
from saleor.product_class import ProductClassRecommendationStatus


class ProductClassesQueryset(models.QuerySet):
    def query_add_row_number(self, list_order_by):
        return self.annotate(
            row_number=Window(
                expression=RowNumber(),
                partition_by=[F("listing_id")],
                order_by=list_order_by,
            ),
            selected=ExpressionWrapper(
                Q(row_number__lte=2), output_field=models.BooleanField()
            ),
        )


class ProductClassRecommendation(models.Model):
    listing = models.ForeignKey(
        ProductVariantChannelListing,
        on_delete=models.CASCADE,
        related_name="product_class_recommendations",
    )
    product_class_qty = models.CharField(blank=True, null=True, max_length=256)
    product_class_value = models.CharField(blank=True, null=True, max_length=256)
    product_class_recommendation = models.CharField(
        blank=True, null=True, max_length=256
    )
    status = models.CharField(
        choices=ProductClassRecommendationStatus.CHOICES,
        max_length=128,
        default=ProductClassRecommendationStatus.DRAFT,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="staff_created_product_classes",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="staff_updated_product_classes",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="staff_approved_product_classes",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    approved_at = models.DateTimeField(blank=True, null=True)

    objects = models.Manager.from_queryset(ProductClassesQueryset)()

    class Meta:
        app_label = "product_class"

        permissions = (
            (
                ProductClassPermissions.MANAGE_PRODUCT_CLASS.codename,
                "Manage product class recommendation.",
            ),
            (
                ProductClassPermissions.APPROVE_PRODUCT_CLASS.codename,
                "Approve product class recommendation.",
            ),
        )
