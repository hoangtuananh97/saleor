import graphene

from ...tests.utils import assert_no_permission, get_graphql_content

PRIVATE_KEY = "private_key"
PRIVATE_VALUE = "private_value"

PUBLIC_KEY = "public_key"
PUBLIC_VALUE = "public_value"

QUERY_CHANNELS_WITH_PUBLIC_METADATA = """
query {
    channels {
        name
        slug
        currencyCode
        defaultCountry {
            code
            country
        }
        metadata {
            key
            value
        }
    }
}
"""


def test_query_channels_with_public_metadata_as_staff_user(
    staff_api_client, channel_USD
):
    # given
    channel_USD.store_value_in_metadata({PUBLIC_KEY: PUBLIC_VALUE})
    channel_USD.save(update_fields=["metadata"])

    # when
    response = staff_api_client.post_graphql(
        QUERY_CHANNELS_WITH_PUBLIC_METADATA,
        {},
        check_no_permissions=False,
    )
    content = get_graphql_content(response)

    # then
    channels = content["data"]["channels"]
    assert len(channels) == 1
    assert {
        "slug": channel_USD.slug,
        "name": channel_USD.name,
        "currencyCode": channel_USD.currency_code,
        "defaultCountry": {
            "code": channel_USD.default_country.code,
            "country": channel_USD.default_country.name,
        },
        "metadata": [
            {
                "key": PUBLIC_KEY,
                "value": PUBLIC_VALUE,
            }
        ],
    } in channels


def test_query_channels_with_public_metadata_as_app(app_api_client, channel_USD):
    # given
    channel_USD.store_value_in_metadata({PUBLIC_KEY: PUBLIC_VALUE})
    channel_USD.save(update_fields=["metadata"])

    # when
    response = app_api_client.post_graphql(
        QUERY_CHANNELS_WITH_PUBLIC_METADATA,
        {},
        check_no_permissions=False,
    )
    content = get_graphql_content(response)

    # then
    channels = content["data"]["channels"]
    assert len(channels) == 1
    assert {
        "slug": channel_USD.slug,
        "name": channel_USD.name,
        "currencyCode": channel_USD.currency_code,
        "defaultCountry": {
            "code": channel_USD.default_country.code,
            "country": channel_USD.default_country.name,
        },
        "metadata": [
            {
                "key": PUBLIC_KEY,
                "value": PUBLIC_VALUE,
            }
        ],
    } in channels


def test_query_channels_with_public_metadata_as_customer(user_api_client, channel_USD):
    # given

    # when
    response = user_api_client.post_graphql(QUERY_CHANNELS_WITH_PUBLIC_METADATA, {})

    # then
    assert_no_permission(response)


def test_query_channels_with_public_metadata_as_anonymous(api_client, channel_USD):
    # given

    # when
    response = api_client.post_graphql(QUERY_CHANNELS_WITH_PUBLIC_METADATA, {})

    # then
    assert_no_permission(response)


QUERY_CHANNELS_WITH_PUBLIC_METADATA_HAS_ORDERS = """
query {
    channels {
        name
        slug
        currencyCode
        hasOrders
        metadata {
            key
            value
        }
    }
}
"""


def test_query_channels_with_public_metadata_has_orders_order(
    staff_api_client, permission_manage_channels, channel_USD, order_list
):
    # given
    channel_USD.store_value_in_metadata({PUBLIC_KEY: PUBLIC_VALUE})
    channel_USD.save(update_fields=["metadata"])
    # when
    response = staff_api_client.post_graphql(
        QUERY_CHANNELS_WITH_PUBLIC_METADATA_HAS_ORDERS,
        {},
        permissions=(permission_manage_channels,),
        check_no_permissions=False,
    )
    content = get_graphql_content(response)

    # then
    channels = content["data"]["channels"]
    assert len(channels) == 1
    assert {
        "slug": channel_USD.slug,
        "name": channel_USD.name,
        "currencyCode": channel_USD.currency_code,
        "hasOrders": True,
        "metadata": [
            {
                "key": PUBLIC_KEY,
                "value": PUBLIC_VALUE,
            }
        ],
    } in channels


def test_query_channels_with_public_metadata_has_orders_without_permission(
    staff_api_client, channel_USD, channel_PLN
):
    # given

    # when
    response = staff_api_client.post_graphql(QUERY_CHANNELS_WITH_PUBLIC_METADATA, {})

    # then
    assert_no_permission(response)


QUERY_CHANNELS_WITH_PRIVATE_METADATA = """
query {
    channels {
        name
        slug
        currencyCode
        defaultCountry {
            code
            country
        }
        privateMetadata {
            key
            value
        }
    }
}
"""


def test_query_channels_with_private_metadata_as_staff_user(
    staff_api_client, permission_manage_channels, customer_user, channel_USD
):
    # given
    channel_USD.store_value_in_private_metadata({PRIVATE_KEY: PRIVATE_VALUE})
    channel_USD.save(update_fields=["private_metadata"])
    variables = {"id": graphene.Node.to_global_id("user", customer_user.pk)}

    # when
    response = staff_api_client.post_graphql(
        QUERY_CHANNELS_WITH_PRIVATE_METADATA,
        variables=variables,
        permissions=(permission_manage_channels,),
        check_no_permissions=False,
    )
    content = get_graphql_content(response)

    # then
    channels = content["data"]["channels"]
    assert len(channels) == 1
    assert {
        "slug": channel_USD.slug,
        "name": channel_USD.name,
        "currencyCode": channel_USD.currency_code,
        "defaultCountry": {
            "code": channel_USD.default_country.code,
            "country": channel_USD.default_country.name,
        },
        "privateMetadata": [
            {
                "key": PRIVATE_KEY,
                "value": PRIVATE_VALUE,
            }
        ],
    } in channels


def test_query_channels_with_private_metadata_as_app(
    app_api_client, customer_user, channel_USD
):
    # given
    channel_USD.store_value_in_private_metadata({PRIVATE_KEY: PRIVATE_VALUE})
    channel_USD.save(update_fields=["private_metadata"])
    variables = {"id": graphene.Node.to_global_id("user", customer_user.pk)}

    # when
    response = app_api_client.post_graphql(
        QUERY_CHANNELS_WITH_PUBLIC_METADATA,
        variables=variables,
        check_no_permissions=False,
    )
    content = get_graphql_content(response)

    # then
    channels = content["data"]["channels"]
    assert len(channels) == 1
    assert {
        "slug": channel_USD.slug,
        "name": channel_USD.name,
        "currencyCode": channel_USD.currency_code,
        "defaultCountry": {
            "code": channel_USD.default_country.code,
            "country": channel_USD.default_country.name,
        },
        "metadata": [
            {
                "key": PUBLIC_KEY,
                "value": PUBLIC_VALUE,
            }
        ],
    } in channels


QUERY_CHANNEL_WITH_PRIVATE_METADATA = """
    query getChannel($id: ID!){
        channel(id: $id){
            id
            name
            slug
            privateMetadata {
                key
                value
            }
        }
    }
"""


def test_query_channel_with_private_metadata_as_staff_user(
    staff_api_client, permission_manage_channels, channel_USD
):
    # given
    channel_USD.store_value_in_private_metadata({PRIVATE_KEY: PRIVATE_VALUE})
    channel_USD.save(update_fields=["private_metadata"])
    channel_id = graphene.Node.to_global_id("Channel", channel_USD.id)
    variables = {"id": channel_id}

    # when
    response = staff_api_client.post_graphql(
        QUERY_CHANNEL_WITH_PRIVATE_METADATA,
        variables,
        permissions=[permission_manage_channels],
        check_no_permissions=False,
    )
    content = get_graphql_content(response)

    # then
    channel_data = content["data"]["channel"]
    private_metadata = channel_data["privateMetadata"][0]
    assert channel_data["id"] == channel_id
    assert channel_data["name"] == channel_USD.name
    assert channel_data["slug"] == channel_USD.slug
    assert private_metadata["key"] == PRIVATE_KEY
    assert private_metadata["value"] == PRIVATE_VALUE


def test_query_channel_private_metadata_as_app(
    app_api_client, permission_manage_channels, channel_USD
):

    # given
    channel_USD.store_value_in_private_metadata({PRIVATE_KEY: PRIVATE_VALUE})
    channel_USD.save(update_fields=["private_metadata"])
    channel_id = graphene.Node.to_global_id("Channel", channel_USD.id)
    variables = {"id": channel_id}

    # when
    response = app_api_client.post_graphql(
        QUERY_CHANNEL_WITH_PRIVATE_METADATA,
        variables,
        permissions=[permission_manage_channels],
        check_no_permissions=False,
    )
    content = get_graphql_content(response)

    # then
    channel_data = content["data"]["channel"]
    private_metadata = channel_data["privateMetadata"][0]
    assert channel_data["id"] == channel_id
    assert channel_data["name"] == channel_USD.name
    assert channel_data["slug"] == channel_USD.slug
    assert private_metadata["key"] == PRIVATE_KEY
    assert private_metadata["value"] == PRIVATE_VALUE
