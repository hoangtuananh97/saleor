from django.db import models
from django.db.models.expressions import F, Window
from django.db.models.functions import RowNumber

from saleor import settings
from saleor.core.permissions import ProductMaxMinPermissions
from saleor.product.models import ProductVariantChannelListing


class ProductMaxMinQueryset(models.QuerySet):
    def qs_group_partition(self):
        return ProductMaxMin.objects.annotate(
            row_number=Window(
                expression=RowNumber(),
                partition_by=[F("listing_id")],
                order_by=F("created_at").desc(),
            )
        ).order_by("-created_at")

    def get_data_after_group_partition(self):
        group_data_by_listing = {}
        ids = []
        products_max_min = self.qs_group_partition().values(
            "listing_id", "id", "row_number"
        )
        for item in products_max_min:
            if item["row_number"] > 2:
                continue
            if item["listing_id"] not in group_data_by_listing.keys():
                group_data_by_listing[item["listing_id"]] = [item["id"]]
            else:
                group_data_by_listing[item["listing_id"]].append(item["id"])
            ids.append(item["id"])
        return ids, group_data_by_listing

    def qs_filter_current_previous(self):
        product_max_min_ids, _ = self.get_data_after_group_partition()
        return self.filter(id__in=product_max_min_ids)


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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    objects = models.Manager.from_queryset(ProductMaxMinQueryset)()

    class Meta:
        app_label = "product_max_min"

        permissions = (
            (
                ProductMaxMinPermissions.MANAGE_PRODUCT_MAX_MIN.codename,
                "Manage product max min.",
            ),
        )
