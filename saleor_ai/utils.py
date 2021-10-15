from collections import OrderedDict

from django.core.management import BaseCommand
from django.utils import timezone

from saleor_ai.models import SaleorAI


class BaseSyncSaleorAICommand(BaseCommand):
    help = "Sync product max min in Saleor AI to DB."
    chunk_size = 500

    def add_arguments(self, parser):
        parser.add_argument(
            "-date_now",
            "--date_now",
            action="store_const",
            const=str(timezone.now().today()),
            type=str,
            help="Sync by default today.",
        )
        parser.add_argument(
            "-from_date",
            "--from_date",
            type=str,
            help="Sync by from date.",
        )
        parser.add_argument(
            "-to_date",
            "--to_date",
            type=str,
            help="Sync by to date.",
        )
        parser.add_argument(
            "-franchise_code",
            "--franchise_code",
            type=str,
            help="Sync by channel slug.",
        )
        parser.add_argument(
            "-article_code",
            "--article_code",
            type=str,
            help="Sync by variant sku.",
        )

    def data_group_saleor_ai(self):
        group_saleor_ai = OrderedDict()
        saleor_ai = SaleorAI.objects.values(
            "article_code",
            "franchise_code",
            "min_qty",
            "max_qty",
            "start_of_week",
            "product_class_qty",
            "product_class_value",
            "product_class_default",
        ).all()
        for item in saleor_ai:
            group_data = {
                "min_qty": item["min_qty"],
                "max_qty": item["max_qty"],
                "product_class_qty": item["product_class_qty"],
                "product_class_value": item["product_class_value"],
                "product_class_recommendation": item["product_class_default"],
                "created_at": item["start_of_week"],
            }
            group_saleor_ai.setdefault(
                (item["article_code"], item["franchise_code"]), list()
            ).append(group_data)
        return group_saleor_ai
