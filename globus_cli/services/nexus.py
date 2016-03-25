from __future__ import print_function

import getpass
import json

from globus_cli.helpers import (
    stderr_prompt, outformat_is_json, cliargs, CLIArg)

from globus_sdk import NexusClient


@cliargs('Get a Legacy GOAuth Token from Globus Nexus.', [
    CLIArg('username', default=None,
           help='Username for a GlobusID user to use to get a token.'),
    CLIArg('password', default=None,
           help='Password for a GlobusID user to use to get a token.')
    ])
def get_goauth_token(args):
    """
    Executor for `globus nexus get-goauth-token`
    Reads username and password from stdin if they aren't in the args.
    """
    # get username and/or password if not present
    if not args.username:
        args.username = stderr_prompt('GlobusID Username: ')
    if not args.password:
        args.password = getpass.getpass('GlobusID Password: ')

    # get the token itself
    client = NexusClient()
    tok = client.get_goauth_token(args.username, args.password)

    # print it out in JSON or TEXT format, then exit
    if outformat_is_json(args):
        print(json.dumps({'access_token': tok}))
    else:
        print(tok)
