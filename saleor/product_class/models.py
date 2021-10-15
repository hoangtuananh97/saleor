from django.db import models
from django.db.models import F, OuterRef, Subquery
from django.db.models.functions import JSONObject  # type: ignore[attr-defined]

from saleor import settings
from saleor.core.permissions import ProductClassPermissions
from saleor.product.models import ProductVariantChannelListing
from saleor.product_class import ProductClassRecommendationStatus

# Create your models here.


class ProductClassesQueryset(models.QuerySet):
    def qs_group_current_previous(
        self, filter_row_number: str, order_by: str, list_status: list
    ):
        list_status = tuple(list_status)
        params = [list_status]
        sql_raw = """
        select id
        from (
                 select ROW_NUMBER() OVER (
                     PARTITION BY listing_id
                     ORDER BY {order_by}) AS row_number,
                        A.*
                 from product_class_productclassrecommendation A
                 WHERE A.status IN  %s
             ) AS B
        WHERE B.row_number {filter_row_number}
        """.format(
            order_by=order_by, filter_row_number=filter_row_number
        )
        return self.raw(sql_raw, params=params)

    def qs_filter_current_previous(
        self, filter_row_number: str, order_by: str, list_status: list
    ):
        group_product_classes = self.qs_group_current_previous(
            filter_row_number, order_by, list_status
        )
        ids = [item.id for item in group_product_classes]
        return self.filter(id__in=ids)

    def qs_filter_current_previous_one_query(self):
        queryset = self.all()
        queryset = (
            queryset.annotate(
                latest_id=Subquery(
                    queryset.filter(
                        listing=OuterRef("listing"),
                    )
                    .values("listing")
                    .order_by("-created_at")
                    .values("pk")[:1]
                ),
                current_version=JSONObject(
                    product_class_qty=F("product_class_qty"),
                    product_class_value=F("product_class_value"),
                    product_class_recommendation=F("product_class_recommendation"),
                ),
                previous_version=Subquery(
                    queryset.filter(
                        listing=OuterRef("listing"),
                        id__lt=OuterRef("latest_id"),
                    )
                    .annotate(
                        json_values=JSONObject(
                            product_class_qty=F("product_class_qty"),
                            product_class_value=F("product_class_value"),
                            product_class_recommendation=F(
                                "product_class_recommendation"
                            ),
                        )
                    )
                    .order_by("-created_at")
                    .values("json_values")[:1]
                ),
            )
            .filter(
                id=F("latest_id"),
            )
            .values("listing_id", "current_version", "previous_version")
        )
        return queryset


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
    created_at = models.DateTimeField(null=True, blank=True)
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
