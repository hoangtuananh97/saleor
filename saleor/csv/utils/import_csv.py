from django.core.exceptions import ValidationError

from saleor.graphql.core.mutations import BaseMutation
from saleor_ai.models import SaleorAI


def validate(base_mutation, **data):
    instance = SaleorAI()
    instance = base_mutation.construct_instance(instance, data)
    try:
        base_mutation.clean_instance({}, instance)
    except Exception as e:
        return
    return instance


def import_saleor_ai(import_file, batch_data, batch_size):
    instances = []
    instances_error = []
    base_mutation = BaseMutation()
    for data in batch_data:
        instance = validate(base_mutation, **data)
        if instance:
            instances.append(instance)
        else:
            instances_error.append(instance)
    SaleorAI.objects.bulk_create(instances)
    if instances_error:
        raise ValidationError(
            instances_error,
            code="Validation Error",
        )

