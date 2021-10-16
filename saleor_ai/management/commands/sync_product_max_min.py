import logging

from saleor.product_max_min.models import ProductMaxMin
from saleor_ai.utils import BaseSyncSaleorAICommand

logger = logging.getLogger(__name__)


class Command(BaseSyncSaleorAICommand):
    help = "Sync product max min in Saleor AI to DB."

    def update_metadata(self):
        qs_products_max_min = (
            ProductMaxMin.objects.qs_filter_current_previous_one_query()
        )
        for item in qs_products_max_min:
            listing = item.listing
            product_class_metadata = {
                "product_max_min": {
                    "current": item["current_version"],
                    "previous": item["previous_version"],
                }
            }
            listing.store_value_in_metadata(product_class_metadata)
            listing.save()

    def prepare_data_one_row(self, listing, value):
        return {
            "listing": listing,
            "min_level": value["min_qty"],
            "max_level": value["max_qty"],
            "created_at": value["created_at"],
        }

    def handle(self, *args, **options):
        group_saleor_ai, listing_dict = self.data_group_saleor_ai(**options)
        instance = ProductMaxMin()
        model = ProductMaxMin
        self.bulk_create(instance, model, group_saleor_ai, listing_dict)
        self.update_metadata()
