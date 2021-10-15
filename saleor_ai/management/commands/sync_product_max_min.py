import logging

from saleor.graphql.core.mutations import BaseMutation
from saleor.product.models import ProductVariantChannelListing
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
        group_saleor_ai = self.data_group_saleor_ai()
        base_mutation = BaseMutation()
        data_max_min = []

        for key, values in group_saleor_ai.items():
            listing = ProductVariantChannelListing.objects.filter(
                variant__sku=key[0], channel__slug=key[1]
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

        if data_max_min:
            ProductMaxMin.objects.bulk_create(data_max_min)

        self.update_metadata()
