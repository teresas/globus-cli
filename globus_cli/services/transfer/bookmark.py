from __future__ import print_function

from globus_cli.helpers import (
    outformat_is_json, cliargs, CLIArg, print_json_response,
    colon_formatted_print)
from globus_cli.services.transfer.helpers import (
    print_json_from_iterator, text_header_and_format, get_client)


@cliargs('List Bookmarks for the current user', [])
def bookmark_list(args):
    """
    Executor for `globus transfer bookmark list`
    """
    client = get_client()

    bookmark_iterator = client.bookmark_list()

    if outformat_is_json(args):
        print_json_from_iterator(bookmark_iterator)
    else:
        text_col_format = text_header_and_format(
            [(32, 'Name'), (36, 'Endpoint ID'), (36, 'Bookmark ID'),
             (None, 'Path')])

        for result in bookmark_iterator:
            print(text_col_format.format(
                result.data['name'], result.data['endpoint_id'],
                result.data['id'], result.data['path']))


@cliargs('Show a Bookmark', [
    CLIArg('bookmark-id', required=True, help='ID of the Bookmark')
    ])
def bookmark_show(args):
    """
    Executor for `globus transfer bookmark show`
    """
    client = get_client()

    res = client.get_bookmark(args.bookmark_id)

    if outformat_is_json(args):
        print_json_response(res)
    else:
        fields = (('Name', 'name'), ('Endpoint ID', 'endpoint_id'),
                  ('Path', 'path'))
        colon_formatted_print(res.data, fields)


@cliargs('Create a Bookmark for the current user', [
    CLIArg('endpoint-id', required=True,
           help='ID of the endpoint on which to add a Bookmark'),
    CLIArg('path', required=True,
           help='Path on the endpoint for the Bookmark'),
    CLIArg('name', required=True, help='Name for the Bookmark')
    ])
def bookmark_create(args):
    """
    Executor for `globus transfer bookmark create`
    """
    client = get_client()

    submit_data = {
        'endpoint_id': args.endpoint_id,
        'path': args.path,
        'name': args.name
    }

    res = client.create_bookmark(submit_data)

    if outformat_is_json(args):
        print_json_response(res)
    else:
        print('Bookmark ID: {}'.format(res.data['id']))


@cliargs('Change a Bookmark\'s name', [
    CLIArg('bookmark-id', required=True, help='ID of the Bookmark'),
    CLIArg('name', required=True, help='New name for the Bookmark')
    ])
def bookmark_rename(args):
    """
    Executor for `globus transfer bookmark rename`
    """
    client = get_client()

    submit_data = {
        'name': args.name
    }

    res = client.update_bookmark(args.bookmark_id, submit_data)

    if outformat_is_json(args):
        print_json_response(res)
    else:
        print('Success')


@cliargs('Delete a Bookmark', [
    CLIArg('bookmark-id', required=True, help='ID of the Bookmark')
    ])
def bookmark_delete(args):
    """
    Executor for `globus transfer bookmark delete`
    """
    client = get_client()

    res = client.delete_bookmark(args.bookmark_id)

    if outformat_is_json(args):
        print_json_response(res)
    else:
        print(res.data['message'])
