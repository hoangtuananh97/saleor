from django.core.management import call_command

from saleor.product_class.models import ProductClassRecommendation
from saleor.product_max_min.models import ProductMaxMin
from saleor_ai.utils import BaseSyncSaleorAICommand


def test_sync_product_max_min():
    # give
    options = {
        "from_date": "2021-05-24",
        "to_date": "2021-11-22",
        "article_codes": ["8100"],
        "franchise_codes": ["44492"],
    }
    base_saleor_command = BaseSyncSaleorAICommand()
    group_saleor_ai, listing_dict = base_saleor_command.data_group_saleor_ai(**options)
    # when
    call_command("sync_product_max_min")
    # then
    assert ProductMaxMin.objects.count() == len(group_saleor_ai)


def test_sync_product_class():
    # give
    options = {
        "from_date": "2021-05-24",
        "to_date": "2021-11-22",
        "article_codes": ["8100"],
        "franchise_codes": ["44492"],
    }
    base_saleor_command = BaseSyncSaleorAICommand()
    group_saleor_ai, listing_dict = base_saleor_command.data_group_saleor_ai(**options)
    # when
    call_command("sync_product_class")
    # then
    assert ProductClassRecommendation.objects.count() == len(group_saleor_ai)
