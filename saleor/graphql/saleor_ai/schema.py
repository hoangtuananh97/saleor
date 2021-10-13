import graphene

from saleor.graphql.saleor_ai.bulk_mutations.saleor_ai import FileUploadSaleorAI


class SaleorAIMutations(graphene.ObjectType):
    file_upload_saleor_ai = FileUploadSaleorAI.Field()
