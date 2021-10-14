import csv
from io import StringIO

import graphene

from saleor.core.tracing import traced_atomic_transaction
from saleor.graphql.core.mutations import BaseMutation, ModelMutation
from saleor.graphql.core.types import Upload
from saleor.graphql.core.types.common import UploadError
from saleor_ai import models


class SaleorAIInput(graphene.InputObjectType):
    scgh_mch3_code = graphene.String()
    scgh_mch3_desc = graphene.String()
    scgh_mch2_code = graphene.String()
    scgh_mch2_desc = graphene.String()
    scgh_mch1_code = graphene.String()
    scgh_mch1_desc = graphene.String()
    brand = graphene.String()
    article_code = graphene.String()
    article_name = graphene.String()
    item_flag = graphene.String()
    item_status = graphene.String()
    scgh_dc_item_flag = graphene.String()
    scgh_dc_stock = graphene.String()
    scgh_show_no_stock_flag = graphene.String()
    scgh_product_class = graphene.String()
    scgh_vmi_flag = graphene.String()
    scgh_showroom_flag = graphene.String()
    scgh_market_flag = graphene.String()
    scgh_shop_flag = graphene.String()
    sales_uom = graphene.String()
    sales_price = graphene.Int(default=0)
    purchase_uom = graphene.String()
    purchase_price = graphene.Float(default=0)
    purchase_group = graphene.String()
    moq = graphene.String()
    vendor_code = graphene.String()
    vendor_name = graphene.String()
    comp_code = graphene.String()
    comp_desc = graphene.String()
    dc_rdc_code = graphene.String()
    dc_rdc_desc = graphene.String()
    franchise_code = graphene.String()
    franchise_desc = graphene.String()
    actual_sales_value = graphene.Int(default=0)
    actual_sales_qty = graphene.Int(default=0)
    forecast_value = graphene.Float(default=0)
    forecast_qty = graphene.Int(default=0)
    safety_stock_qty = graphene.Int(default=0)
    min_qty = graphene.Int(default=0)
    max_qty = graphene.Int(default=0)
    product_class_qty = graphene.String()
    product_class_value = graphene.String()
    product_class_default = graphene.String()
    start_of_week = graphene.Date()
    start_of_month = graphene.Date()


class BaseSaleorAIBulk(ModelMutation):
    count = graphene.Int(
        required=True,
        default_value=0,
        description="Returns how many objects were created.",
    )

    class Meta:
        abstract = True

    @classmethod
    def config_input_cls(cls):
        raise NotImplementedError

    @classmethod
    def validate(cls, _root, info, **data):
        instances = []
        data = data.get("input")
        input_cls = cls.config_input_cls()
        for item in data:
            instance = cls.get_instance(info, **item)
            cleaned_input = cls.clean_input(info, instance, item, input_cls=input_cls)
            instance = cls.construct_instance(instance, cleaned_input)
            cls.clean_instance(info, instance)
            instances.append(instance)
        return instances


class FileUploadSaleorAI(BaseMutation):
    count = graphene.Int(
        required=True,
        default_value=0,
        description="Returns how many objects were created.",
    )

    class Arguments:
        file = Upload(
            required=True, description="Represents a file in a multipart request."
        )

    class Meta:
        description = "Upload saleor AI."
        # TODO : permissions tmp
        error_type_class = UploadError
        error_type_field = "upload_errors"

    @classmethod
    def config_input_cls(cls):
        return SaleorAIInput

    @classmethod
    @traced_atomic_transaction()
    def perform_mutation(cls, _root, info, **data):
        chunk_size = 1000
        instances = []
        count = 0
        file_data = info.context.FILES.get(data["file"]).read()
        content = file_data.decode()
        csv_data = csv.reader(StringIO(content), delimiter=",")
        for row in csv_data:
            data = cls.read_one_row(row)
            instance = cls.validate(_root, info, **data)
            if instance:
                instances.append(instance)
            if len(instances) > chunk_size:
                models.SaleorAI.objects.bulk_create(instances)
                count = count + len(instances)
                instances = []
        if instances:
            models.SaleorAI.objects.bulk_create(instances)
            count = count + len(instances)
        return FileUploadSaleorAI(count=count)

    @classmethod
    def read_one_row(cls, row):
        return {
            "scgh_mch3_code": row[0],
            "scgh_mch3_desc": row[1],
            "scgh_mch2_code": row[2],
            "scgh_mch2_desc": row[3],
            "scgh_mch1_code": row[4],
            "scgh_mch1_desc": row[5],
            "brand": row[6],
            "article_code": row[7],
            "article_name": row[8],
            "item_flag": row[9],
            "item_status": row[10],
            "scgh_dc_item_flag": row[11],
            "scgh_dc_stock": row[12],
            "scgh_show_no_stock_flag": row[13],
            "scgh_product_class": row[14],
            "scgh_vmi_flag": row[15],
            "scgh_showroom_flag": row[16],
            "scgh_market_flag": row[17],
            "scgh_shop_flag": row[18],
            "sales_uom": row[19],
            "sales_price": row[20],
            "purchase_uom": row[21],
            "purchase_price": row[22],
            "purchase_group": row[23],
            "moq": row[24],
            "vendor_code": row[25],
            "vendor_name": row[26],
            "comp_code": row[27],
            "comp_desc": row[28],
            "dc_rdc_code": row[29],
            "dc_rdc_desc": row[30],
            "franchise_code": row[31],
            "franchise_desc": row[32],
            "actual_sales_value": row[33],
            "actual_sales_qty": row[34],
            "forecast_value": row[35],
            "forecast_qty": row[36],
            "safety_stock_qty": row[37],
            "min_qty": row[38],
            "max_qty": row[39],
            "product_class_qty": row[40],
            "product_class_value": row[41],
            "product_class_default": row[42],
            "start_of_week": row[43],
            "start_of_month": row[44],
        }

    @classmethod
    def validate(cls, _root, info, **data):
        input_cls = SaleorAIInput
        instance = models.SaleorAI()
        for _, value in data.items():
            if any(
                value == field_name for field_name, _ in input_cls._meta.fields.items()
            ):
                return
        cleaned_input = ModelMutation.clean_input(
            info, instance, data, input_cls=input_cls
        )
        instance = cls.construct_instance(instance, cleaned_input)
        cls.clean_instance(info, instance)
        return instance

    @classmethod
    def check_one_row(cls, row):
        pass
