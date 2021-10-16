import logging

from saleor.product_class.models import ProductClassRecommendation
from saleor_ai.utils import BaseSyncSaleorAICommand

logger = logging.getLogger(__name__)


class Command(BaseSyncSaleorAICommand):
    help = "Sync product class in Saleor AI to DB."

    def update_metadata(self):
        qs_product_classes = (
            ProductClassRecommendation.objects.qs_filter_current_previous_one_query()
        )
        for item in qs_product_classes:
            listing = item.listing
            product_class_metadata = {
                "product_class": {
                    "current": item.current_version,
                    "previous": item.previous_version,
                }
            }
            listing.store_value_in_metadata(product_class_metadata)
            listing.save()

    def prepare_data_one_row(self, listing, value):
        return {
            "listing": listing,
            "product_class_qty": value["product_class_qty"],
            "product_class_value": value["product_class_value"],
            "product_class_recommendation": value["product_class_recommendation"],
            "created_at": value["created_at"],
        }

    def handle(self, *args, **options):
        group_saleor_ai, listing_dict = self.data_group_saleor_ai(**options)
        if group_saleor_ai:
            instance = ProductClassRecommendation()
            model = ProductClassRecommendation
            self.bulk_create(instance, model, group_saleor_ai, listing_dict)
            self.update_metadata()
