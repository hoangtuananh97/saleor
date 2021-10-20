from django.core.exceptions import ValidationError

from saleor.csv.events import import_failed_event, import_success_event
from saleor.csv.models import ExportFile
from saleor.csv.notifications import send_export_download_link_notification
from saleor.csv.utils.export import (
    append_to_file,
    create_file_with_headers,
    get_filename,
    save_csv_file_in_export_file,
)
from saleor.graphql.core.mutations import BaseMutation
from saleor_ai.models import SaleorAI


def validate(base_mutation, count_row, **data):
    instance = SaleorAI()
    instance = base_mutation.construct_instance(instance, data)
    instance_error = None
    try:
        instance.full_clean()
    except ValidationError as error:
        for key, value in error.message_dict.items():
            instance_error = {
                "position": {
                    "column": key,
                    "row": count_row,
                },
                "message": value[0],
            }
        instance = None
    return instance, instance_error


def import_saleor_ai(import_file, batch_data, user):
    instances = []
    instances_error = []
    base_mutation = BaseMutation()
    count_row = batch_data["start_row"]
    batch_data = batch_data["batch_data"]
    for data in batch_data:
        count_row = count_row + 1
        instance, instance_error = validate(base_mutation, count_row, **data)
        if instance:
            instances.append(instance)
        else:
            data["error"] = instance_error
            instances_error.append(data)
    SaleorAI.objects.bulk_create(instances)

    if not instances_error:
        import_success_event(import_file=import_file, user=user)
    else:
        import_failed_event(
            import_file=import_file,
            user=user,
            message=str(instances_error),
            error_type="",
        )

    return instances_error


def read_one_row(row):
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


def prepare_data_error_for_export(data_error):
    return data_error
    # data = []
    # for item in data_error:
    #     data.append(prepare_data_error_for_one_row(item))
    # return data


def prepare_data_error_for_one_row(item):
    return item


def data_error_saleor_ai_headers(export_info: list):
    export_info.remove("id")
    export_info.append("error")
    export_fields = export_info
    file_headers = export_info
    return export_fields, file_headers


def export_data_error_saleor_ai(
    export_file: "ExportFile",
    data_error: list,
    export_info: list,
    file_type: str = "csv",
    delimiter: str = ";",
):
    file_name = get_filename("import_saleor_ai_error", file_type)
    export_fields, file_headers = data_error_saleor_ai_headers(export_info)
    temporary_file = create_file_with_headers(file_headers, delimiter, file_type)
    export_data = prepare_data_error_for_export(data_error)
    append_to_file(
        export_data,
        export_fields,
        temporary_file,
        file_type,
        delimiter,
    )
    save_csv_file_in_export_file(export_file, temporary_file, file_name)
    temporary_file.close()

    send_export_download_link_notification(export_file)
