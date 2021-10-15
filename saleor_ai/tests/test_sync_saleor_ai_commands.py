from collections import OrderedDict

from django.core.management import call_command

from saleor.product_class.models import ProductClassRecommendation
from saleor.product_max_min.models import ProductMaxMin
from saleor_ai.models import SaleorAI


def test_sync_saleor_ai_db():
    # give
    group_saleor_ai = OrderedDict()
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
    # when
    call_command("sync_db_ai")
    # then
    assert ProductMaxMin.objects.count() == len(group_saleor_ai)
    assert ProductClassRecommendation.objects.count() == len(group_saleor_ai)
