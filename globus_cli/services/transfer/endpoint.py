from __future__ import print_function
import json

from globus_cli.helpers import (
    outformat_is_json, cliargs, CLIArg, print_json_response,
    colon_formatted_print, not_implemented_func)
from globus_cli.services.transfer.helpers import (
    print_json_from_iterator, text_header_and_format, endpoint_list_to_text,
    assemble_generic_doc, get_client)
from globus_cli.services.transfer.activation import autoactivate


@cliargs('Search for Globus Endpoints', [
    CLIArg('filter-scope', default=None,
           choices=('all', 'my-endpoints', 'my-gcp-endpoints', 'recently-used',
                    'in-use', 'shared-by-me', 'shared-with-me'),
           help=('The set of endpoints to search over. '
                 'Omission is equivalent to "all"')),
    CLIArg('filter-fulltext', default=None,
           help='Text filter to apply to the selected set of endpoints.')
])
def endpoint_search(args):
    """
    Executor for `globus transfer endpoint-search`
    """
    client = get_client()
    search_iterator = client.endpoint_search(
        filter_fulltext=args.filter_fulltext, filter_scope=args.filter_scope)

    if outformat_is_json(args):
        print_json_from_iterator(search_iterator)
    else:
        endpoint_list_to_text(search_iterator)


@cliargs('Activate an Endpoint via autoactivation', [
    CLIArg('endpoint-id', required=True,
           help='ID of the endpoint, typically fetched from endpoint-search')
    ])
def endpoint_autoactivate(args):
    """
    Executor for `globus transfer endpoint-autoactivate`
    """
    client = get_client()
    res = autoactivate(client, args.endpoint_id)
    print(json.dumps(res.data, indent=2))


@cliargs('Deactivate an Endpoint', [
    CLIArg('endpoint-id', required=True,
           help='ID of the endpoint, typically fetched from endpoint-search')
    ])
def endpoint_deactivate(args):
    """
    Executor for `globus transfer endpoint-deactivate`
    """
    client = get_client()
    res = client.endpoint_deactivate(args.endpoint_id)
    print(json.dumps(res.data, indent=2))


@cliargs('List all servers belonging to an Endpoint', [
    CLIArg('endpoint-id', required=True,
           help='ID of the endpoint, typically fetched from endpoint-search')
    ])
def endpoint_server_list(args):
    """
    Executor for `globus transfer endpoint-server-list`
    """
    client = get_client()

    server_iterator = client.endpoint_server_list(args.endpoint_id)

    if outformat_is_json(args):
        print_json_from_iterator(server_iterator)
    else:
        text_col_format = text_header_and_format(
            [(36, 'URI')])

        for result in server_iterator:
            print(text_col_format.format(result.data['uri']))


@cliargs('List all Shared Endpoints on an Endpoint by the current user', [
    CLIArg('endpoint-id', required=True,
           help='ID of the endpoint, typically fetched from endpoint-search')
    ])
def my_shared_endpoint_list(args):
    """
    Executor for `globus transfer endpoint my-shared-endpoint-list`
    """
    client = get_client()

    ep_iterator = client.my_shared_endpoint_list(args.endpoint_id)

    if outformat_is_json(args):
        print_json_from_iterator(ep_iterator)
    else:
        endpoint_list_to_text(ep_iterator)


@cliargs('List of assigned Roles on an Endpoint', [
    CLIArg('endpoint-id', required=True,
           help='ID of the endpoint, typically fetched from endpoint-search')
    ])
def endpoint_role_list(args):
    """
    Executor for `globus transfer access endpoint-role-list`
    """
    client = get_client()

    role_iterator = client.endpoint_role_list(args.endpoint_id)

    if outformat_is_json(args):
        print_json_from_iterator(role_iterator)
    else:
        text_col_format = text_header_and_format(
            [(16, 'Principal Type'), (36, 'Role ID'), (36, 'Principal'),
             (16, 'Role')])

        for result in role_iterator:
            print(text_col_format.format(
                result.data['principal_type'], result.data['id'],
                result.data['principal'], result.data['role']))


@cliargs('Show full info for a Role on an Endpoint', [
    CLIArg('endpoint-id', required=True, help='ID of the endpoint'),
    CLIArg('role-id', required=True, help='ID of the role')
    ])
def endpoint_role_show(args):
    """
    Executor for `globus transfer endpoint role show`
    """
    client = get_client()

    role_doc = client.get_endpoint_role(args.endpoint_id, args.role_id)

    if outformat_is_json(args):
        print_json_response(role_doc)
    else:
        named_fields = (('Principal Type', 'principal_type'),
                        ('Principal', 'principal'), ('Role', 'role'))
        colon_formatted_print(role_doc.data, named_fields)


@cliargs('Create a Role on an Endpoint', [
    CLIArg('endpoint-id', required=True, help='ID of the endpoint'),
    CLIArg('principal-type', required=True,
           choices=('identity', 'group'), type=str.lower,
           help='Type of entity to set a role on'),
    CLIArg('principal', required=True, help='Entity to set a role on'),
    CLIArg('role', default='access_manager',
           choices=('access_manager',), type=str.lower,
           help='A role to assign. Currently only supports access_manager')
    ])
def endpoint_role_create(args):
    """
    Executor for `globus transfer endpoint role show`
    """
    client = get_client()

    role_doc = assemble_generic_doc(
        'role', principal_type=args.principal_type, principal=args.principal,
        role=args.role)

    res = client.add_endpoint_role(args.endpoint_id, role_doc)

    if outformat_is_json(args):
        print_json_response(res)
    else:
        print('ID: ' + res.data['id'])


@cliargs('Remove a Role from an Endpoint', [
    CLIArg('endpoint-id', required=True, help='ID of the endpoint'),
    CLIArg('role-id', required=True, help='ID of the role')
    ])
def endpoint_role_delete(args):
    """
    Executor for `globus transfer endpoint role delete`
    """
    client = get_client()

    res = client.delete_endpoint_role(args.endpoint_id, args.role_id)

    if outformat_is_json(args):
        print_json_response(res)
    else:
        print(res.data['message'])


@cliargs('Display a detailed endpoint definition', [
    CLIArg('endpoint-id', required=True,
           help='ID of the endpoint, typically fetched from endpoint-search')
    ])
def endpoint_show(args):
    """
    Executor for `globus transfer endpoint show`
    """
    client = get_client()

    res = client.get_endpoint(args.endpoint_id)

    if outformat_is_json(args):
        print_json_response(res)
    else:
        fields = (('Display Name', 'display_name'), ('ID', 'id'),
                  ('Owner', 'owner_string'), ('Activated', 'activated'),
                  ('Shareable', 'shareable'))
        colon_formatted_print(res.data, fields)


@cliargs('Not Implemented', [])
def endpoint_create(args):
    """
    Executor for `globus transfer endpoint create`
    """
    not_implemented_func()


@cliargs('Update attributes of an Endpoint', [
    CLIArg('endpoint-id', required=True, help='ID of the endpoint'),
    CLIArg('display-name', help='New Display Name for the Endpoint'),
    CLIArg('description', help='New Description for the Endpoint'),
    CLIArg('organization', help='New Organization for the Endpoint'),
    CLIArg('contact-email', help='New Contact Email for the Endpoint'),
    CLIArg('contact-info', help='New Contact Info for the Endpoint'),
    CLIArg('info-link', help='New Link for Info about the Endpoint'),
    CLIArg('force-encryption', choices=('true', 'false'), type=str.lower,
           help=('Only available on Globus Connect Server. '
                 '(Un)Force transfers to use encryption')),
    CLIArg('default-directory',
           help=('Only available on Globus Connect Server. '
                 'Set the default directory')),
    CLIArg('myproxy-server',
           help=('Only available on Globus Connect Server. '
                 'Set the MyProxy Server URI')),
    CLIArg('myproxy-dn',
           help=('Only available on Globus Connect Server. '
                 'Set the MyProxy Server DN')),
    CLIArg('oauth-server',
           help=('Only available on Globus Connect Server. '
                 'Set the OAuth Server URI')),
    ])
def endpoint_update(args):
    """
    Executor for `globus transfer endpoint update`
    """
    client = get_client()

    ep_doc = assemble_generic_doc(
        'endpoint',
        display_name=args.display_name, description=args.description,
        organization=args.organization, contact_email=args.contact_email,
        contact_info=args.contact_info, info_link=args.info_link,
        force_encryption=args.force_encryption,
        default_directory=args.default_directory,
        myproxy_server=args.myproxy_server, myproxy_dn=args.myproxy_dn,
        oauth_server=args.oauth_server)

    res = client.update_endpoint(args.endpoint_id, ep_doc)

    if outformat_is_json(args):
        print_json_response(res)
    else:
        print(res.data['message'])


@cliargs('Delete a given Endpoint', [
    CLIArg('endpoint-id', required=True, help='ID of the endpoint')
    ])
def endpoint_delete(args):
    """
    Executor for `globus transfer endpoint delete`
    """
    client = get_client()

    res = client.delete_endpoint(args.endpoint_id)

    if outformat_is_json(args):
        print_json_response(res)
    else:
        print(res.data['message'])
