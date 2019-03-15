import json

from tests.framework.cli_testcase import CliTestCase
from tests.framework.constants import GO_EP1_ID, GO_EP2_ID
from tests.framework.tools import get_user_data, on_windows

# TODO: remove this as part of handling #455
PATHSEP = "\\" if on_windows() else "/"


class BasicTests(CliTestCase):
    """
    Tests basic functionality of both the CLI and the test suite framework
    """

    def test_parsing(self):
        """
        Runs --help and confirms the option is parsed
        """
        # globus --help
        output = self.run_line("globus --help")
        self.assertIn("-h, --help", output)
        self.assertIn("Show this message and exit.", output)

    def test_command(self):
        """
        Runs list-commands and confirms the command is run
        """
        output = self.run_line("globus list-commands")
        self.assertIn("=== globus ===", output)

    def test_command_parsing(self):
        """
        Runs list-commands --help
        confirms both the command and the option are parsed
        """
        output = self.run_line("globus list-commands --help")
        self.assertIn("List all Globus CLI Commands with short help output.", output)

    def test_command_missing_args(self):
        """
        Runs get-identities without values, confirms exit_code 2
        """
        output = self.run_line("globus get-identities", assert_exit_code=2)
        self.assertIn("Error: Missing argument", output)

    def test_invalid_command(self):
        """
        Runs globus invalid-command, confirms Error
        """
        output = self.run_line("globus invalid-command", assert_exit_code=2)
        self.assertIn("Error: No such command", output)

    def test_whoami(self):
        """
        Runs whoami to confirm test config successfully setup
        """
        output = self.run_line("globus whoami")
        self.assertIn(get_user_data()["clitester1a"]["username"], output)

    def test_whoami_no_auth(self):
        """
        Runs whoami with config set to be empty, confirms no login seen.
        """
        output = self.run_line("globus whoami", config={}, assert_exit_code=1)
        self.assertIn("Unable to get user information", output)

    def test_json_raw_string_output(self):
        """
        Get single-field jmespath output and make sure it's quoted
        """
        output = self.run_line("globus whoami --jmespath name").strip()
        self.assertEquals('"{}"'.format(get_user_data()["clitester1a"]["name"]), output)

    def test_auth_call_no_auth(self):
        """
        Runs get-identities with config set to be empty,
        confirms No Authentication CLI error.
        """
        output = self.run_line(
            "globus get-identities " + get_user_data()["clitester1a"]["username"],
            config={},
            assert_exit_code=1,
        )
        self.assertIn("No Authentication provided.", output)

    def test_auth_call(self):
        """
        Runs get-identities using test auth refresh token to confirm
        test auth refresh token is live and configured correctly
        """
        output = self.run_line(
            "globus get-identities " + get_user_data()["clitester1a"]["username"]
        )
        self.assertIn(get_user_data()["clitester1a"]["id"], output)

    def test_transfer_call_no_auth(self):
        """
        Runs ls with config set to be empty,
        confirms No Authentication CLI error.
        """
        output = self.run_line(
            "globus ls " + str(GO_EP1_ID), config={}, assert_exit_code=1
        )
        self.assertIn("No Authentication provided.", output)

    def test_transfer_call(self):
        """
        Runs ls using test transfer refresh token to confirm
        test transfer refresh token is live and configured correctly
        """
        output = self.run_line("globus ls " + str(GO_EP1_ID) + ":/")
        self.assertIn("home/", output)

    def test_transfer_batchmode_dryrun(self):
        """
        Dry-runs a transfer in batchmode, confirms batchmode inputs received
        """
        batch_input = u"abc /def\n/xyz p/q/r\n"
        output = self.run_line(
            "globus transfer -F json --batch --dry-run "
            + str(GO_EP1_ID)
            + " "
            + str(GO_EP2_ID),
            batch_input=batch_input,
        )
        # rely on json.dumps() in order to get the quoting right in the Windows
        # case
        # FIXME: this should be removed after we resolve #455
        for src, dst in [
            ("abc", "{}def".format(PATHSEP)),
            ("{}xyz".format(PATHSEP), "p{sep}q{sep}r".format(sep=PATHSEP)),
        ]:
            self.assertIn('"source_path": {}'.format(json.dumps(src)), output)
            self.assertIn('"destination_path": {}'.format(json.dumps(dst)), output)

    def test_delete_batchmode_dryrun(self):
        """
        Dry-runs a delete in batchmode
        """
        batch_input = u"abc/def\n/xyz\n"
        output = self.run_line(
            "globus delete --batch --dry-run " + str(GO_EP1_ID), batch_input=batch_input
        )
        self.assertEqual(
            ("\n".join(("Path   ", "-------", "abc{sep}def", "{sep}xyz   \n"))).format(
                sep=PATHSEP
            ),
            output,
        )
