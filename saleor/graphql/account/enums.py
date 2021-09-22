import graphene
from django_countries import countries

from ...account import CustomerEvents
from ...checkout import AddressType
from ...graphql.core.enums import to_enum
from ..core.utils import str_to_enum

AddressTypeEnum = to_enum(AddressType, type_name="AddressTypeEnum")
CustomerEventsEnum = to_enum(CustomerEvents)


CountryCodeEnum = graphene.Enum(
    "CountryCode", [(str_to_enum(country[0]), country[0]) for country in countries]
)


class StaffMemberStatus(graphene.Enum):
    ACTIVE = "active"
    DEACTIVATED = "deactivated"

    @property
    def description(self):
        if self == StaffMemberStatus.ACTIVE:
            return "User account has been activated."
        elif self == StaffMemberStatus.DEACTIVATED:
            return "User account has not been activated yet."
        return None


class StaffEventMarkRead(graphene.Enum):
    SEEN = True
    NO_SEEN = False

    @property
    def description(self):
        if self == StaffEventMarkRead.SEEN:
            return "Staff event mark read."
        elif self == StaffEventMarkRead.NO_SEEN:
            return "Staff event don't mark read."
        return None
