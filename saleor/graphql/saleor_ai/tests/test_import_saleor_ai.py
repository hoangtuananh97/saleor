from saleor.graphql.tests.utils import (
    assert_no_permission,
    get_graphql_content,
    get_multipart_request_body,
)
from saleor.product.tests.utils import create_csv_file_with_saleor_ai

QUERY_IMPORT = """
mutation FileUploadSaleorAI($file:Upload!) {
    fileUploadSaleorAi(file: $file){
        count
    }
}
"""


def test_file_upload_saleor_ai_by_staff(
    staff_api_client, site_settings, media_root, permission_manage_staff
):
    # given
    data_file, file_name = create_csv_file_with_saleor_ai()
    variables = {"file": file_name}
    body = get_multipart_request_body(QUERY_IMPORT, variables, data_file, file_name)

    # when
    response = staff_api_client.post_multipart(
        body, permissions=[permission_manage_staff]
    )

    # then
    content = get_graphql_content(response)
    data = content["data"]["fileUploadSaleorAi"]

    assert data["count"] == 1


def test_file_upload_saleor_ai_no_permission(
    staff_api_client, site_settings, media_root
):
    # give
    data_file, file_name = create_csv_file_with_saleor_ai()
    variables = {"file": file_name}
    body = get_multipart_request_body(QUERY_IMPORT, variables, data_file, file_name)
    # when
    response = staff_api_client.post_multipart(body)

    # then
    assert_no_permission(response)
