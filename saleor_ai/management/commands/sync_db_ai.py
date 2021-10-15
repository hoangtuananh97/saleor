import logging
from collections import OrderedDict

from django.core.management.base import BaseCommand

from saleor.graphql.core.mutations import BaseMutation
from saleor.product.models import ProductVariantChannelListing
from saleor.product_class.models import ProductClassRecommendation
from saleor.product_max_min.models import ProductMaxMin
from saleor_ai.models import SaleorAI

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Sync product class, product max min in Saleor AI to DB."
    chunk_size = 500

    def update_metadata(self):
        qs_product_classes = (
            ProductClassRecommendation.objects.qs_filter_current_previous_one_query()
        )
        qs_products_max_min = (
            ProductMaxMin.objects.qs_filter_current_previous_one_query()
        )
        for item in qs_product_classes:
            listing = ProductVariantChannelListing.objects.get(id=item["listing_id"])
            product_class_metadata = {
                "product_class": {
                    "current": item["current_version"],
                    "previous": item["previous_version"],
                }
            }
            listing.store_value_in_metadata(product_class_metadata)
            listing.save()
        for item in qs_products_max_min:
            listing = ProductVariantChannelListing.objects.get(id=item["listing_id"])
            product_class_metadata = {
                "product_max_min": {
                    "current": item["current_version"],
                    "previous": item["previous_version"],
                }
            }
            listing.store_value_in_metadata(product_class_metadata)
            listing.save()

    def handle(self, *args, **options):
        group_saleor_ai = OrderedDict()
        base_mutation = BaseMutation()
        data_product_class = []
        data_max_min = []
        saleor_ai = SaleorAI.objects.values(
            "article_code", "franchise_code", "min_qty", "max_qty", "start_of_week",
            "product_class_qty", "product_class_value", "product_class_default"
        ).all()
        for item in saleor_ai:
            group_data = {
                "min_qty": item['min_qty'],
                "max_qty": item['max_qty'],
                "product_class_qty": item['product_class_qty'],
                "product_class_value": item['product_class_value'],
                "product_class_recommendation": item['product_class_default'],
                "created_at": item['start_of_week'],
            }
            group_saleor_ai.setdefault(
                (item['article_code'], item['franchise_code']), list()
            ).append(group_data)

        for key, values in group_saleor_ai.items():
            listing = ProductVariantChannelListing.objects.filter(
                variant__sku=key[0],
                channel__slug=key[1]
            ).first()
            value = values[0]

            # bulk_create product max min
            instance_max_min = ProductMaxMin()
            obj_max_min = {
                "listing": listing,
                "min_level": value["min_qty"] if values else 0,
                "max_level": value["max_qty"] if values else 0,
                "created_at": value["created_at"],
            }
            instance_max_min = base_mutation.construct_instance(
                instance_max_min, obj_max_min
            )
            data_max_min.append(instance_max_min)
            if len(data_max_min) > self.chunk_size:
                ProductMaxMin.objects.bulk_create(data_max_min)
                data_max_min = []

            # bulk_create product class
            instance_product_class = ProductClassRecommendation()
            obj_product_class = {
                "listing": listing,
                "product_class_qty": value["product_class_qty"],
                "product_class_value": value["product_class_value"],
                "product_class_recommendation": value["product_class_recommendation"],
                "created_at": value["created_at"],
            }

            instance_product_class = base_mutation.construct_instance(
                instance_product_class, obj_product_class
            )
            data_product_class.append(instance_product_class)
            if len(data_product_class) > self.chunk_size:
                ProductClassRecommendation.objects.bulk_create(data_product_class)
                data_product_class = []

        if data_max_min:
            ProductMaxMin.objects.bulk_create(data_max_min)
        if data_product_class:
            ProductClassRecommendation.objects.bulk_create(data_product_class)

        self.update_metadata()
