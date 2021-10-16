from collections import OrderedDict

from django.core.management import BaseCommand
from django.db.models import Q
from django.utils import timezone

from saleor.graphql.core.mutations import BaseMutation
from saleor.product.models import ProductVariantChannelListing
from saleor_ai.models import SaleorAI


class BaseSyncSaleorAICommand(BaseCommand):
    help = "Sync product max min in Saleor AI to DB."
    chunk_size = 500

    def add_arguments(self, parser):
        parser.add_argument(
            "--from_date",
            nargs="?",
            const=str(timezone.now().date()),
            default=str(timezone.now().date()),
            required=True,
            help="Sync by from date.",
        )
        parser.add_argument(
            "--to_date",
            type=str,
            help="Sync by to date.",
        )
        parser.add_argument(
            "--article_codes",
            nargs="+",
            help="Sync by list variant sku.",
        )
        parser.add_argument(
            "--franchise_codes",
            nargs="+",
            help="Sync by list channel slug.",
        )

    def filter_saleor_ai(self, **options):
        from_date = options.get("from_date")
        to_date = options.get("to_date")
        article_codes = options.get("article_codes")
        franchise_codes = options.get("franchise_codes")

        saleor_ai = SaleorAI.objects.values(
            "article_code",
            "franchise_code",
            "min_qty",
            "max_qty",
            "start_of_week",
            "product_class_qty",
            "product_class_value",
            "product_class_default",
        ).filter(start_of_week__gte=from_date)
        if to_date:
            saleor_ai = saleor_ai.filter(start_of_week__lte=from_date)
        if article_codes:
            saleor_ai = saleor_ai.filter(article_code__in=article_codes)
        if franchise_codes:
            saleor_ai = saleor_ai.filter(franchise_code__in=franchise_codes)

        return saleor_ai

    def data_group_saleor_ai(self, **options):
        group_saleor_ai = OrderedDict()
        skus = set()
        slugs = set()
        listing_dict = {}
        saleor_ai = self.filter_saleor_ai(**options)
        for item in saleor_ai:
            skus.add(item["article_code"])
            slugs.add(item["franchise_code"])

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

        listing = ProductVariantChannelListing.objects.filter(
            Q(variant__sku__in=skus) | Q(channel__slug__in=slugs)
        )
        for item in listing:
            sku = item.variant.sku
            slug = item.channel.slug
            listing_dict[f"{sku}{slug}"] = item

        return group_saleor_ai, listing_dict

    def prepare_data_one_row(self, listing, value):
        return NotImplementedError

    def bulk_create(self, instance, model, group_saleor_ai, listing_dict):
        base_mutation = BaseMutation()
        data_product_class = []

        for key, values in group_saleor_ai.items():
            sku = key[0]
            slug = key[1]
            listing = listing_dict[f"{sku}{slug}"]
            value = values[0]
            obj_insert = self.prepare_data_one_row(listing, value)

            instance_product_class = base_mutation.construct_instance(
                instance, obj_insert
            )
            data_product_class.append(instance_product_class)
            if len(data_product_class) > self.chunk_size:
                model.objects.bulk_create(data_product_class)
                data_product_class = []

        if data_product_class:
            model.objects.bulk_create(data_product_class)

    def update_metadata(self):
        raise NotImplementedError
