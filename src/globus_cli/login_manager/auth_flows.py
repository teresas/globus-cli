import click

from .tokenstore import internal_auth_client, token_storage_adapter

_STORE_CONFIG_USERINFO = "auth_user_data"


def do_link_auth_flow(scopes, *, session_params=None):
    """
    Prompts the user with a link to authenticate with globus auth
    and authorize the CLI to act on their behalf.
    """
    session_params = session_params or {}

    # get the ConfidentialApp client object
    auth_client = internal_auth_client()

    # start the Confidential App Grant flow
    auth_client.oauth2_start_flow(
        redirect_uri=auth_client.base_url + "v2/web/auth-code",
        refresh_tokens=True,
        requested_scopes=scopes,
    )

    # prompt
    query_params = {"prompt": "login"}
    query_params.update(session_params)
    linkprompt = "Please authenticate with Globus here"
    click.echo(
        "{0}:\n{1}\n{2}\n{1}\n".format(
            linkprompt,
            "-" * len(linkprompt),
            auth_client.oauth2_get_authorize_url(query_params=query_params),
        )
    )

    # come back with auth code
    auth_code = click.prompt("Enter the resulting Authorization Code here").strip()

    # finish auth flow
    exchange_code_and_store(auth_client, auth_code)
    return True


def do_local_server_auth_flow(scopes, *, session_params=None):
    """
    Starts a local http server, opens a browser to have the user authenticate,
    and gets the code redirected to the server (no copy and pasting required)
    """
    import webbrowser

    from .local_server import LocalServerError, start_local_server

    session_params = session_params or {}

    # start local server and create matching redirect_uri
    with start_local_server(listen=("127.0.0.1", 0)) as server:
        _, port = server.socket.getsockname()
        redirect_uri = f"http://localhost:{port}"

        # get the ConfidentialApp client object and start a flow
        auth_client = internal_auth_client()
        auth_client.oauth2_start_flow(
            refresh_tokens=True, redirect_uri=redirect_uri, requested_scopes=scopes
        )
        query_params = {"prompt": "login"}
        query_params.update(session_params)
        url = auth_client.oauth2_get_authorize_url(query_params=query_params)

        # open web-browser for user to log in, get auth code
        webbrowser.open(url, new=1)
        auth_code = server.wait_for_code()

    if isinstance(auth_code, LocalServerError):
        click.echo(f"Authorization failed: {auth_code}", err=True)
        click.get_current_context().exit(1)
    elif isinstance(auth_code, Exception):
        click.echo(
            f"Authorization failed with unexpected error:\n{auth_code}",
            err=True,
        )
        click.get_current_context().exit(1)

    # finish auth flow and return true
    exchange_code_and_store(auth_client, auth_code)
    return True


def exchange_code_and_store(auth_client, auth_code):
    """
    Finishes auth flow after code is gotten from command line or local server.
    Exchanges code for tokens and stores them.

    A user may have a different identity this time than what they previously logged in
    as, so to secure incremental auth flows, if the new tokens don't match the previous
    identity we revoke them and instruct the user to logout before continuing.
    """
    adapter = token_storage_adapter()
    tkn = auth_client.oauth2_exchange_code_for_tokens(auth_code)
    sub_new = tkn.decode_id_token()["sub"]
    auth_user_data = adapter.read_config(_STORE_CONFIG_USERINFO)
    if auth_user_data and sub_new != auth_user_data.get("sub"):
        try:
            for tokens in tkn.by_resource_server.values():
                auth_client.oauth2_revoke_token(tokens["access_token"])
                auth_client.oauth2_revoke_token(tokens["refresh_token"])
        finally:
            click.echo(
                "Authorization failed: tried to login with an account that didn't "
                "match existing credentials. If you meant to do this, first `globus "
                "logout`, then try again. ",
                err=True,
            )
        click.get_current_context().exit(1)
    if not auth_user_data:
        adapter.store_config(_STORE_CONFIG_USERINFO, {"sub": sub_new})
    adapter.store(tkn)
