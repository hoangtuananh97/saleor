import base64
from typing import Dict, List, Mapping, Union

import graphene
from django.core.exceptions import ValidationError

from ...account.models import User
from ...core.permissions import ProductMaxMinPermissions, ProductPermissions
from ...csv import models as csv_models
from ...csv.events import export_started_event
from ...csv.tasks import (
    export_products_max_min_task,
    export_products_task,
    import_saleor_ai_task,
)
from ..attribute.types import Attribute
from ..channel.types import Channel
from ..core.enums import ExportErrorCode
from ..core.mutations import BaseMutation
from ..core.types import Upload
from ..core.types.common import ExportError, UploadError
from ..product.filters import ProductFilterInput
from ..product.filters_product_max_min import ProductMaxMinFilterInput
from ..product.types import Product
from ..product.types.product_max_min import ProductMaxMin
from ..warehouse.types import Warehouse
from .enums import ExportScope, FileTypeEnum, ProductFieldEnum, ProductMaxMinFieldEnum
from .types import ExportFile, ImportFile
from ...csv.utils.import_excel import ParserExcel


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
        ImportFile,
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
        permissions = ()
        error_type_class = UploadError
        error_type_field = "upload_errors"

    @classmethod
    def perform_mutation(cls, _root, info, **kwargs):
        batch_size = 5000
        user = User.objects.get(email="admin@example.com")
        # user = {
        #     "user": info.context.user,
        # }
        # user = info.context.user
        file = info.context.FILES.get(kwargs["file"])
        file_type = file.name.split(".")[1]
        if not file_type in ["csv", "xlsx"]:
            raise ValidationError(
                {
                    "file": ValidationError(
                        "You must provide file csv.",
                    )
                }
            )
        file_data = file.read()
        if file_type == "xlsx":
            file_bytes_base64 = base64.b64encode(file_data)
            content = file_bytes_base64.decode('ISO-8859-1')
        else:
            content = file_data.decode()
        import_file = csv_models.ImportFile.objects.create(user=user)
        import_saleor_ai_task.delay(
            import_file.pk, content, user.id, file_type, batch_size
        ).get()

        import_file.refresh_from_db()
        return cls(import_file=import_file)
