import json
from functools import partial

import graphene
from graphene.relay import PageInfo
from graphene_django.fields import DjangoConnectionField
from graphql.error import GraphQLError
from graphql_relay.connection.arrayconnection import connection_from_list_slice
from promise import Promise

from ...channel.exceptions import ChannelNotDefined, NoDefaultChannel
from ...product_class.models import ProductClassRecommendation
from ...product_max_min.models import ProductMaxMin
from ..channel import ChannelContext, ChannelQsContext
from ..channel.utils import get_default_channel_slug_or_graphql_error
from ..product.utils import check_permission_product_class_approved
from ..utils.sorting import sort_queryset_for_connection
from .connection import connection_from_queryset_slice


def patch_pagination_args(field: DjangoConnectionField):
    """Add descriptions to pagination arguments in a connection field.

    By default Graphene's connection fields comes without description for pagination
    arguments. This functions patches those fields to add the descriptions.
    """
    field.args["first"].description = "Return the first n elements from the list."
    field.args["last"].description = "Return the last n elements from the list."
    field.args[
        "before"
    ].description = (
        "Return the elements in the list that come before the specified cursor."
    )
    field.args[
        "after"
    ].description = (
        "Return the elements in the list that come after the specified cursor."
    )


class BaseConnectionField(graphene.ConnectionField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        patch_pagination_args(self)


class BaseDjangoConnectionField(DjangoConnectionField):
    @classmethod
    def resolve_connection(cls, connection, args, iterable, max_limit=None):
        common_args = {
            "connection_type": connection,
            "edge_type": connection.Edge,
            "pageinfo_type": PageInfo,
        }
        if isinstance(iterable, list):
            common_args["args"] = args
            _len = len(iterable)
            connection = connection_from_list_slice(
                iterable,
                slice_start=0,
                list_length=_len,
                list_slice_length=_len,
                **common_args,
            )
        else:
            iterable, sort_by = sort_queryset_for_connection(
                iterable=iterable, args=args
            )
            args["sort_by"] = sort_by
            common_args["args"] = args
            connection = connection_from_queryset_slice(iterable, **common_args)
        connection.iterable = iterable
        return connection

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        patch_pagination_args(self)


class PrefetchingConnectionField(BaseDjangoConnectionField):
    @classmethod
    def connection_resolver(
        cls,
        resolver,
        connection,
        default_manager,
        queryset_resolver,
        max_limit,
        enforce_first_or_last,
        root,
        info,
        **args,
    ):

        # Disable `enforce_first_or_last` if not querying for `edges`.
        values = [
            field.name.value for field in info.field_asts[0].selection_set.selections
        ]
        if "edges" not in values:
            enforce_first_or_last = False

        return super().connection_resolver(
            resolver,
            connection,
            default_manager,
            queryset_resolver,
            max_limit,
            enforce_first_or_last,
            root,
            info,
            **args,
        )


class FilterInputConnectionField(BaseDjangoConnectionField):
    def __init__(self, *args, **kwargs):
        self.filter_field_name = kwargs.pop("filter_field_name", "filter")
        self.filter_input = kwargs.get(self.filter_field_name)
        self.filterset_class = None
        if self.filter_input:
            self.filterset_class = self.filter_input.filterset_class
        super().__init__(*args, **kwargs)

    @classmethod
    def connection_resolver(
        cls,
        resolver,
        connection,
        default_manager,
        queryset_resolver,
        max_limit,
        enforce_first_or_last,
        filterset_class,
        filters_name,
        root,
        info,
        **args,
    ):
        # Disable `enforce_first_or_last` if not querying for `edges`.
        values = [
            field.name.value for field in info.field_asts[0].selection_set.selections
        ]
        if "edges" not in values:
            enforce_first_or_last = False

        first = args.get("first")
        last = args.get("last")

        if enforce_first_or_last and not (first or last):
            raise GraphQLError(
                f"You must provide a `first` or `last` value to properly paginate "
                f"the `{info.field_name}` connection."
            )

        if max_limit:
            if first:
                assert first <= max_limit, (
                    "Requesting {} records on the `{}` connection exceeds the "
                    "`first` limit of {} records."
                ).format(first, info.field_name, max_limit)
                args["first"] = min(first, max_limit)

            if last:
                assert last <= max_limit, (
                    "Requesting {} records on the `{}` connection exceeds the "
                    "`last` limit of {} records."
                ).format(last, info.field_name, max_limit)
                args["last"] = min(last, max_limit)

        iterable = resolver(root, info, **args)

        if iterable is None:
            iterable = default_manager
        # thus the iterable gets refiltered by resolve_queryset
        # but iterable might be promise
        iterable = queryset_resolver(connection, iterable, info, args)

        on_resolve = partial(
            cls.resolve_connection, connection, args, max_limit=max_limit
        )

        # for nested filters get channel from ChannelContext object
        if "channel" not in args and hasattr(root, "channel_slug"):
            args["channel"] = root.channel_slug

        iterable = cls.filter_iterable(
            iterable, filterset_class, filters_name, info, **args
        )

        if Promise.is_thenable(iterable):
            return Promise.resolve(iterable).then(on_resolve)
        return on_resolve(iterable)

    @classmethod
    def filter_iterable(cls, iterable, filterset_class, filters_name, info, **args):
        filter_input = args.get(filters_name)
        if filter_input:
            try:
                filter_channel = str(filter_input["channel"])
            except (NoDefaultChannel, ChannelNotDefined, GraphQLError, KeyError):
                filter_channel = None
            filter_input["channel"] = (
                args.get("channel")
                or filter_channel
                or get_default_channel_slug_or_graphql_error()
            )
        if filter_input and filterset_class:
            instance = filterset_class(
                data=dict(filter_input), queryset=iterable, request=info.context
            )
            # Make sure filter input has valid values
            if not instance.is_valid():
                raise GraphQLError(json.dumps(instance.errors.get_json_data()))
            iterable = instance.qs
        return iterable

    def get_resolver(self, parent_resolver):
        return partial(
            super().get_resolver(parent_resolver),
            self.filterset_class,
            self.filter_field_name,
        )


class ChannelContextFilterConnectionField(FilterInputConnectionField):
    @classmethod
    def filter_iterable(cls, iterable, filterset_class, filters_name, info, **args):
        # Overriding filter_iterable to unpack the queryset from iterable, which is
        # an instance of ChannelQsContext and pack it back after filtering is done.
        channel_slug = iterable.channel_slug
        iterable = super().filter_iterable(
            iterable.qs, filterset_class, filters_name, info, **args
        )
        return ChannelQsContext(qs=iterable, channel_slug=channel_slug)

    @classmethod
    def resolve_connection(
        cls, connection, args, iterable: ChannelQsContext, max_limit=None
    ):
        connection = super().resolve_connection(
            connection, args, iterable.qs, max_limit
        )
        edges_with_context = []
        for edge in connection.edges:
            node = edge.node
            edge.node = ChannelContext(node=node, channel_slug=iterable.channel_slug)
            edges_with_context.append(edge)
        connection.edges = edges_with_context
        return connection


class CurrentPreviousFilterConnectionField(FilterInputConnectionField):
    # Custom to filter both current and previous product class
    # remove id in 1 obj current previous
    @classmethod
    def filter_iterable(cls, iterable, filterset_class, filters_name, info, **args):
        group_data_by_listing = {}
        iterable = super().filter_iterable(
            iterable, filterset_class, filters_name, info, **args
        )
        list_status = check_permission_product_class_approved(info)
        iterable_ids = [item.id for item in iterable]
        product_classes = ProductClassRecommendation.objects.qs_group_current_previous(
            order_by="created_at desc",
            filter_row_number="<= 2",
            list_status=list_status,
        )
        for item in product_classes:
            if item.listing_id not in group_data_by_listing.keys():
                group_data_by_listing[item.listing_id] = [item.id]
            else:
                group_data_by_listing[item.listing_id].append(item.id)

        iterable_ids = remove_id_obj_current_previous(
            group_data_by_listing, iterable_ids
        )
        iterable = iterable.filter(id__in=iterable_ids)
        return iterable


class CurrentPreviousProductMaxMinFilterConnectionField(FilterInputConnectionField):
    # Custom to filter both current and previous product max min
    # remove id in 1 obj current previous
    @classmethod
    def filter_iterable(cls, iterable, filterset_class, filters_name, info, **args):
        iterable = super().filter_iterable(
            iterable, filterset_class, filters_name, info, **args
        )
        iterable_ids = [item.id for item in iterable]
        (
            _,
            group_data_by_listing,
        ) = ProductMaxMin.objects.get_data_after_group_partition()
        iterable_ids = remove_id_obj_current_previous(
            group_data_by_listing, iterable_ids
        )
        iterable = iterable.filter(id__in=iterable_ids)
        return iterable


def remove_id_obj_current_previous(group_data_by_listing, iterable_ids):
    for _, values in group_data_by_listing.items():
        arr_tmp = []
        if values[0] in iterable_ids:
            arr_tmp.append(values[0])
        if len(values) > 1 and values[1] in iterable_ids:
            arr_tmp.append(values[1])
        if len(arr_tmp) > 1:
            iterable_ids.remove(values[1])
    return iterable_ids
