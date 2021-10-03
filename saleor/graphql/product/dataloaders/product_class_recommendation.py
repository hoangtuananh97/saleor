from django.db.models import F

from saleor.graphql.core.dataloaders import DataLoader
from saleor.product_class import ProductClassRecommendationStatus
from saleor.product_class.models import ProductClassRecommendation


class ProductClassRecommendationIdLoader(DataLoader):
    context_key = "product_class_recommendation_id_loader"

    def batch_load(self, keys):
        product_classes = ProductClassRecommendation.objects.query_add_row_number(
            [F("created_at").desc()]
        ).filter(
            listing_id__in=keys,
            status__in=[
                ProductClassRecommendationStatus.APPROVED,
                ProductClassRecommendationStatus.SUBMITTED
            ]
        )
        product_classes_previous = [item for item in product_classes if item.selected]
        product_classes_map = {}
        for product_class_obj in product_classes_previous:
            product_classes_map[product_class_obj.listing_id] = product_class_obj
        return [product_classes_map.get(listing_id, {}) for listing_id in keys]
