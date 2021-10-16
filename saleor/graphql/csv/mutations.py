import csv
from typing import Dict, List, Mapping, Union

import graphene
from django.core.exceptions import ValidationError
from io import StringIO

from saleor_ai.models import SaleorAI
from ..core.types import Upload
from ..saleor_ai.bulk_mutations.saleor_ai import SaleorAIInput
from ...core.permissions import ProductMaxMinPermissions, ProductPermissions, \
    AccountPermissions
from ...csv import models as csv_models
from ...csv.events import export_started_event, import_started_event
from ...csv.tasks import export_products_max_min_task, export_products_task, \
    import_saleor_ai_task
from ..attribute.types import Attribute
from ..channel.types import Channel
from ..core.enums import ExportErrorCode
from ..core.mutations import BaseMutation, ModelMutation
from ..core.types.common import ExportError, UploadError
from ..product.filters import ProductFilterInput
from ..product.filters_product_max_min import ProductMaxMinFilterInput
from ..product.types import Product
from ..product.types.product_max_min import ProductMaxMin
from ..warehouse.types import Warehouse
from .enums import ExportScope, FileTypeEnum, ProductFieldEnum, ProductMaxMinFieldEnum
from .types import ExportFile


class ExportInfoInput(graphene.InputObjectType):
    attributes = graphene.List(
        graphene.NonNull(graphene.ID),
        description="List of attribute ids witch should be exported.",
    )
    warehouses = graphene.List(
        graphene.NonNull(graphene.ID),
        description="List of warehouse ids witch should be exported.",
    )
    channels = graphene.List(
        graphene.NonNull(graphene.ID),
        description="List of channels ids which should be exported.",
    )
    fields = graphene.List(
        graphene.NonNull(ProductFieldEnum),
        description="List of product fields witch should be exported.",
    )


class BaseExportProductsInput(graphene.InputObjectType):
    scope = ExportScope(
        description="Determine which products should be exported.", required=True
    )
    ids = graphene.List(
        graphene.NonNull(graphene.ID),
        description="List of products IDS to export.",
        required=False,
    )
    file_type = FileTypeEnum(description="Type of exported file.", required=True)


class ExportProductsInput(BaseExportProductsInput):
    filter = ProductFilterInput(
        description="Filtering options for products.", required=False
    )
    export_info = ExportInfoInput(
        description="Input with info about fields which should be exported.",
        required=False,
    )


class ExportProductsMaxMinInput(BaseExportProductsInput):
    filter = ProductMaxMinFilterInput(
        description="Filtering options for products.", required=False
    )
    fields = graphene.List(
        graphene.NonNull(ProductMaxMinFieldEnum),
        description="List of product fields witch should be exported.",
    )


class BaseExportProducts(BaseMutation):
    export_file = graphene.Field(
        ExportFile,
        description=(
            "The newly created export file job which is responsible for export data."
        ),
    )

    class Meta:
        abstract = True

    @classmethod
    def perform_mutation(cls, root, info, **data):
        raise NotImplementedError

    @classmethod
    def get_products_scope(cls, input) -> Mapping[str, Union[list, dict, str]]:
        scope = input["scope"]
        if scope == ExportScope.IDS.value:  # type: ignore
            return cls.clean_ids(input)
        elif scope == ExportScope.FILTER.value:  # type: ignore
            return cls.clean_filter(input)
        return {"all": ""}

    @classmethod
    def clean_ids(cls, input) -> Dict[str, List[str]]:
        raise NotImplementedError

    @staticmethod
    def clean_filter(input) -> Dict[str, dict]:
        filter = input.get("filter")
        if not filter:
            raise ValidationError(
                {
                    "filter": ValidationError(
                        "You must provide filter input.",
                        code=ExportErrorCode.REQUIRED.value,
                    )
                }
            )
        return {"filter": filter}

    @classmethod
    def get_export_info(cls, export_info_input):
        raise NotImplementedError

    @classmethod
    def get_items_pks(cls, field, export_info_input, graphene_type):
        ids = export_info_input.get(field)
        if not ids:
            return
        pks = cls.get_global_ids_or_error(ids, only_type=graphene_type, field=field)
        return pks


class ExportProducts(BaseExportProducts):
    class Arguments:
        input = ExportProductsInput(
            required=True, description="Fields required to export product data"
        )

    class Meta:
        description = "Export products to csv file."
        permissions = (ProductPermissions.MANAGE_PRODUCTS,)
        error_type_class = ExportError
        error_type_field = "export_errors"

    @classmethod
    def perform_mutation(cls, root, info, **data):
        input = data["input"]
        scope = cls.get_products_scope(input)
        export_info = cls.get_export_info(input["export_info"])
        file_type = input["file_type"]

        app = info.context.app
        kwargs = {"app": app} if app else {"user": info.context.user}

        export_file = csv_models.ExportFile.objects.create(**kwargs)
        export_started_event(export_file=export_file, **kwargs)
        export_products_task.delay(export_file.pk, scope, export_info, file_type)

        export_file.refresh_from_db()
        return cls(export_file=export_file)

    @classmethod
    def clean_ids(cls, input) -> Dict[str, List[str]]:
        ids = input.get("ids", [])
        if not ids:
            raise ValidationError(
                {
                    "ids": ValidationError(
                        "You must provide at least one product id.",
                        code=ExportErrorCode.REQUIRED.value,
                    )
                }
            )
        pks = cls.get_global_ids_or_error(ids, only_type=Product, field="ids")
        return {"ids": pks}

    @classmethod
    def get_export_info(cls, export_info_input):
        export_info = {}
        fields = export_info_input.get("fields")
        if fields:
            export_info["fields"] = fields

        for field, graphene_type in [
            ("attributes", Attribute),
            ("warehouses", Warehouse),
            ("channels", Channel),
        ]:
            pks = cls.get_items_pks(field, export_info_input, graphene_type)
            if pks:
                export_info[field] = pks

        return export_info


class ExportProductsMaxMin(BaseExportProducts):
    class Arguments:
        input = ExportProductsMaxMinInput(
            required=True, description="Fields required to export product max min data."
        )

    class Meta:
        description = "Export products max min to csv file."
        permissions = (ProductMaxMinPermissions.MANAGE_PRODUCT_MAX_MIN,)
        error_type_class = ExportError
        error_type_field = "export_errors"

    @classmethod
    def perform_mutation(cls, root, info, **data):
        input = data["input"]
        scope = cls.get_products_scope(input)
        export_info = cls.get_export_info(input)
        file_type = input["file_type"]

        app = info.context.app
        kwargs = {"app": app} if app else {"user": info.context.user}

        export_file = csv_models.ExportFile.objects.create(**kwargs)
        export_started_event(export_file=export_file, **kwargs)
        export_products_max_min_task.delay(
            export_file.pk, scope, export_info, file_type
        )

        export_file.refresh_from_db()
        return cls(export_file=export_file)

    @classmethod
    def clean_ids(cls, input) -> Dict[str, List[str]]:
        ids = input.get("ids", [])
        if not ids:
            raise ValidationError(
                {
                    "ids": ValidationError(
                        "You must provide at least one product max min id.",
                        code=ExportErrorCode.REQUIRED.value,
                    )
                }
            )
        pks = cls.get_global_ids_or_error(ids, only_type=ProductMaxMin, field="ids")
        return {"ids": pks}

    @classmethod
    def get_export_info(cls, export_info_input):
        export_info = {}
        fields = export_info_input.get("fields")
        if fields:
            export_info["fields"] = fields
        return export_info


class ImportSaleorAI(BaseMutation):
    import_file = graphene.Field(
        ExportFile,
        description=(
            "The newly created import file job which is responsible for import data."
        ),
    )

    class Arguments:
        file = Upload(
            required=True, description="Represents a file in a multipart request."
        )

    class Meta:
        description = "Import CSV saleor AI."
        permissions = (AccountPermissions.MANAGE_STAFF,)
        error_type_class = UploadError
        error_type_field = "upload_errors"

    @classmethod
    def perform_mutation(cls, _root, info, **kwargs):
        batch_size = 1000
        batch_data = []
        model = SaleorAI
        opts = model._meta
        file_data = info.context.FILES.get(kwargs["file"]).read()
        content = file_data.decode()
        csv_data = csv.reader(StringIO(content), delimiter=",")
        import_file = csv_models.ImportFile.objects.create(**kwargs)
        for row in csv_data:
            data = cls.read_one_row(row)
            for _, value in data.items():
                if any(
                        value == field.name for field in opts.fields
                ):
                    continue
            batch_data.append(row)
            if len(batch_data) > batch_size:
                import_saleor_ai_task.delay(import_file.pk, batch_data, batch_size)
                import_started_event(import_file=import_file, **kwargs)
                batch_data = []
        if batch_data:
            import_saleor_ai_task.delay(import_file.pk, batch_data, batch_size)
            import_started_event(import_file=import_file, **kwargs)

        import_file.refresh_from_db()
        return cls(import_file=import_file)

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
            "scgh_vmi_flag": True if row[15] == "X" else False,
            "scgh_showroom_flag": True if row[16] == "X" else False,
            "scgh_market_flag": True if row[17] == "X" else False,
            "scgh_shop_flag": True if row[18] == "X" else False,
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
