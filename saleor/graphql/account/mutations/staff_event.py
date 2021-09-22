import graphene
from django.core.exceptions import ValidationError

from saleor.account.error_codes import StaffEventErrorCode
from saleor.core.permissions import StaffEventPermissions
from saleor.graphql.core.mutations import BaseMutation
from saleor.graphql.core.types.common import StaffEventError

from ....account import models
from ..types import StaffEvent


class StaffEventMarkRead(BaseMutation):

    staff_event = graphene.Field(StaffEvent, description="Staff Event mark read")

    class Arguments:
        staff_event_id = graphene.ID(
            description="ID of a staff event mark read.", required=True
        )

    class Meta:
        description = "Staff Event mark read."
        model = models.StaffEvent
        permissions = (StaffEventPermissions.MANAGE_STAFF_EVENT,)
        error_type_class = StaffEventError
        error_type_field = "staff_event_errors"

    @classmethod
    def perform_mutation(cls, _root, info, staff_event_id, **data):
        # Retrieve the data
        staff_event = cls.get_node_or_error(info, staff_event_id, only_type=StaffEvent)
        user = info.context.user
        check_staff_event_permission_mutation(user, staff_event)
        staff_event.is_seen = True
        staff_event.save()

        return StaffEventMarkRead(staff_event=staff_event)


class StaffEventDelete(BaseMutation):

    message = graphene.String()

    class Arguments:
        staff_event_id = graphene.ID(
            description="ID of a staff event to delete.", required=True
        )

    class Meta:
        description = "Delete staff event."
        model = models.StaffEvent
        permissions = (StaffEventPermissions.MANAGE_STAFF_EVENT,)
        error_type_class = StaffEventError
        error_type_field = "staff_event_errors"

    @classmethod
    def perform_mutation(cls, _root, info, staff_event_id, **data):
        # Retrieve the data
        staff_event = cls.get_node_or_error(info, staff_event_id, only_type=StaffEvent)
        user = info.context.user
        check_staff_event_permission_mutation(user, staff_event)
        staff_event.delete()

        return StaffEventDelete(message="Delete Success")


def check_staff_event_permission_mutation(user, staff_event):
    if user.id != staff_event.user_id:
        raise ValidationError(
            {
                "staff_event": ValidationError(
                    message="User no permission for mutation staff event.",
                    code=StaffEventErrorCode.OUT_OF_SCOPE_PERMISSION.value,
                )
            }
        )
    return True
