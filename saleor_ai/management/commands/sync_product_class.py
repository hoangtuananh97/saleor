import logging

from saleor.graphql.core.mutations import BaseMutation
from saleor.product.models import ProductVariantChannelListing
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
            listing = ProductVariantChannelListing.objects.get(id=item["listing_id"])
            product_class_metadata = {
                "product_class": {
                    "current": item["current_version"],
                    "previous": item["previous_version"],
                }
            }
            listing.store_value_in_metadata(product_class_metadata)
            listing.save()

    def handle(self, *args, **options):
        base_mutation = BaseMutation()
        data_product_class = []
        group_saleor_ai = self.data_group_saleor_ai()
        for key, values in group_saleor_ai.items():
            listing = ProductVariantChannelListing.objects.filter(
                variant__sku=key[0], channel__slug=key[1]
            ).first()
            value = values[0]

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

        if data_product_class:
            ProductClassRecommendation.objects.bulk_create(data_product_class)

        self.update_metadata()
