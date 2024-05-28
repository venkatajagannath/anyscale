import ast
import json
from unittest.mock import Mock, patch, PropertyMock

import click
import pytest

import anyscale
from anyscale.authenticate import (
    CREDENTIALS_FILE,
    CREDENTIALS_FILE_PERMISSIONS,
)
from anyscale.client.openapi_client.models.organization import Organization
from anyscale.client.openapi_client.models.user_info import UserInfo
from anyscale.controllers.auth_controller import AuthController


url = anyscale.util.get_endpoint("/credentials")


def test_auth_token_get_json_string():
    """
    Test auth_token_get_json_string function by turning a random token
    into a json-formatted string and then load it back
    """
    random_str = "This/IsA#}{RanDom..stRiN9"

    assert json.loads(AuthController()._auth_token_get_json_string(random_str)) == {
        "cli_token": random_str
    }


def test_auth_info_to_formatted_string():
    """
    Test if auth_info_to_formatted_string returns a string with all necessary info
    """
    userinfo = UserInfo(
        name="Anyscale Test",
        email="anyscale@anyscale.com",
        id="usr_somerandomid",
        organization_permission_level="collaborator",
        organizations=[
            Organization(
                name="Anyscale Inc.",
                id="org_someorgid1",
                local_vars_configuration=Mock(client_side_validation=False),
            ),
            Organization(
                name="Noscale Inc.",
                id="org_someorgid2",
                local_vars_configuration=Mock(client_side_validation=False),
            ),
        ],
        local_vars_configuration=Mock(client_side_validation=False),
    )
    s = AuthController()._auth_info_to_formatted_string(userinfo)

    assert (
        s == "  user name:                    Anyscale Test\n"
        "  user email:                   anyscale@anyscale.com\n"
        "  user id:                      usr_somerandomid\n"
        "  organization name:            Anyscale Inc.\n"
        "  organization id:              org_someorgid1\n"
        "  organization name:            Noscale Inc.\n"
        "  organization id:              org_someorgid2\n"
        "  organization role:            collaborator"
    )


def test_auth_info_to_formatted_string_cannot_parse():
    """
    Test auth_info_to_formatted_string when the UserInfo has been changed thus unparseable.
    In that case, the function should dump the entire UserInfo object in json format.
    We simulate it by raising TypeError when UserInfo.name is first referenced
    """
    userinfo = UserInfo(
        name="Anyscale Test",
        email="anyscale@anyscale.com",
        id="usr_somerandomid",
        organization_permission_level="collaborator",
        organizations=[
            Organization(
                name="Anyscale Inc.",
                id="org_someorgid1",
                local_vars_configuration=Mock(client_side_validation=False),
            ),
        ],
        local_vars_configuration=Mock(client_side_validation=False),
    )

    with patch(
        "anyscale.controllers.auth_controller.UserInfo.name", new_callable=PropertyMock
    ) as mock_name:
        # simulate TypeError on the first referrence
        mock_name.side_effect = [AttributeError(), None]
        s = AuthController()._auth_info_to_formatted_string(userinfo)

    userinfo = ast.literal_eval(s)
    assert userinfo["email"] == "anyscale@anyscale.com"
    assert userinfo["id"] == "usr_somerandomid"
    assert userinfo["organizations"][0]["name"] == "Anyscale Inc."
    assert userinfo["organizations"][0]["id"] == "org_someorgid1"
    assert userinfo["organization_permission_level"] == "collaborator"


def test_auth_set_first_time():
    """
    The first-time auth set command should succeed,
    and it also should not trigger AuthenticationBlock to be initialized.
    """
    mock_click_prompt = Mock(return_value="random_value_that_works   ")
    mock_click_confirm = Mock(return_value=True)
    mock_authentication_block_init = Mock(return_value=None)

    with patch.multiple("os.path", exists=Mock(return_value=False)), patch.multiple(
        "click", confirm=mock_click_confirm, prompt=mock_click_prompt,
    ), patch(
        "anyscale.controllers.auth_controller.credentials_check_sanity",
        Mock(return_value=True),
    ), patch(
        "anyscale.controllers.auth_controller.AuthController._save_credentials", Mock()
    ) as mock_save_credentials, patch(
        "anyscale.authenticate.AuthenticationBlock.__init__",
        mock_authentication_block_init,
    ):
        auth_controller = AuthController()
        auth_controller.set()

    # the value should be stripped
    mock_save_credentials.assert_called_once_with("random_value_that_works")
    mock_click_confirm.assert_not_called()
    mock_click_prompt.assert_called_once()
    mock_authentication_block_init.assert_not_called()


def test_auth_set_without_user_interaction():
    """
    Test when the user uses `set` function with the token provided.
    This should not trigger user interaction and must save the credentials file directly.
    """
    mock_click_prompt = Mock(return_value="token_via_prompt")
    mock_click_confirm = Mock(return_value=True)
    with patch.multiple("os.path", exists=Mock(return_value=False)), patch.multiple(
        "click", confirm=mock_click_confirm, prompt=mock_click_prompt,
    ), patch(
        "anyscale.controllers.auth_controller.credentials_check_sanity",
        Mock(return_value=True),
    ), patch(
        "anyscale.controllers.auth_controller.AuthController._save_credentials", Mock()
    ) as mock_save_credentials:
        auth_controller = AuthController()
        auth_controller.set("token_via_argument")

    mock_save_credentials.assert_called_once_with("token_via_argument")
    mock_click_confirm.assert_not_called()
    mock_click_prompt.assert_not_called()


def test_auth_set_without_user_interaction_invalid():
    """
    Test when the user uses `set` function with the token provided, but the token fails the sanity check.
    This should not trigger user interaction and also raise an exception.
    """
    mock_click_prompt = Mock(return_value="token_via_prompt")
    mock_click_confirm = Mock(return_value=True)
    with patch.multiple("os.path", exists=Mock(return_value=False)), patch.multiple(
        "click", confirm=mock_click_confirm, prompt=mock_click_prompt,
    ), patch(
        "anyscale.controllers.auth_controller.credentials_check_sanity",
        Mock(return_value=False),
    ), patch(
        "anyscale.controllers.auth_controller.AuthController._save_credentials", Mock()
    ) as mock_save_credentials, pytest.raises(
        click.ClickException
    ) as e:
        auth_controller = AuthController()
        auth_controller.set("token_via_argument_but_invalid")

    assert "invalid" in e.value.message.lower()
    mock_save_credentials.assert_not_called()
    mock_click_confirm.assert_not_called()
    mock_click_prompt.assert_not_called()


def test_auth_set_invalid():
    """
    Test auth set when user enters token, but sanity check fails.
    Should not save credentials, and must raise an exception.
    """
    with patch.multiple("os.path", exists=Mock(return_value=False)), patch.multiple(
        "click", prompt=Mock(return_value="incorrectcredential")
    ), patch(
        "anyscale.controllers.auth_controller.credentials_check_sanity",
        Mock(return_value=False),
    ) as mock_credentials_check_sanity, patch(
        "anyscale.controllers.auth_controller.AuthController._save_credentials", Mock()
    ) as mock_save_credentials, pytest.raises(
        click.ClickException
    ) as e:
        auth_controller = AuthController()
        auth_controller.set()

    assert "invalid" in e.value.message.lower()
    mock_credentials_check_sanity.assert_called_once_with("incorrectcredential")
    mock_save_credentials.assert_not_called()


def test_auth_set_file_exists():
    """
    Test auth set when the credential file exists
    and the user accepts to replace it.
    """
    mock_os_path_exists = Mock(return_value=True)
    mock_click_confirm = Mock(return_value=True)
    mock_click_prompt = Mock(return_value="correctcredential")

    with patch.multiple("os.path", exists=mock_os_path_exists), patch.multiple(
        "click", confirm=mock_click_confirm, prompt=mock_click_prompt
    ), patch(
        "anyscale.controllers.auth_controller.credentials_check_sanity",
        Mock(return_value=True),
    ), patch(
        "anyscale.controllers.auth_controller.AuthController._save_credentials", Mock()
    ) as mock_save_credentials:
        auth_controller = AuthController(path="/home/usr0/.anyscale/credentials.json",)
        auth_controller.set()

    mock_os_path_exists.assert_called_once_with("/home/usr0/.anyscale/credentials.json")
    mock_click_confirm.assert_called_once()
    mock_click_prompt.assert_called_once()
    mock_save_credentials.assert_called_once_with("correctcredential")


def test_auth_set_file_exists_cancel():
    """
    Test auth set when the credential file exists
    and the user denies to replace it
    """
    mock_os_path_exists = Mock(return_value=True)
    mock_click_confirm = Mock(return_value=False)

    with patch.multiple("os.path", exists=mock_os_path_exists), patch.multiple(
        "click", confirm=mock_click_confirm
    ), patch(
        "anyscale.controllers.auth_controller.AuthController._save_credentials", Mock()
    ) as mock_save_credentials:
        auth_controller = AuthController(path="/home/usr0/.anyscale/credentials.json")
        auth_controller.set()

    mock_os_path_exists.assert_called_once_with("/home/usr0/.anyscale/credentials.json")
    mock_click_confirm.assert_called_once()
    mock_save_credentials.assert_not_called()


def test_auth_fix_file_not_exist():
    """
    Test auth fix command when the file does not exist.
    Must raise an exception
    """
    mock_os_path_exists = Mock(return_value=False)
    mock_os_chmod = Mock()

    with patch("os.path.exists", mock_os_path_exists), patch(
        "os.chmod", mock_os_chmod
    ), pytest.raises(click.ClickException) as e:
        auth_controller = AuthController()
        auth_controller.fix()

    assert CREDENTIALS_FILE in e.value.message
    mock_os_chmod.assert_not_called()


def test_auth_fix():
    """
    Test auth fix command when the file exists.
    This should not trigger AuthenticationBlock to be initialized.
    """
    mock_os_path_exists = Mock(return_value=True)
    mock_os_chmod = Mock()
    mock_authentication_block_init = Mock(return_value=None)

    with patch("os.path.exists", mock_os_path_exists), patch(
        "os.chmod", mock_os_chmod
    ), patch(
        "anyscale.authenticate.AuthenticationBlock.__init__",
        mock_authentication_block_init,
    ):
        auth_controller = AuthController(path="/home/usr0/.anyscale/credentials.json")
        auth_controller.fix()

    mock_os_chmod.assert_called_once_with(
        "/home/usr0/.anyscale/credentials.json", CREDENTIALS_FILE_PERMISSIONS
    )
    mock_authentication_block_init.assert_not_called()


def test_auth_remove_file_not_exist():
    """
    Test auth remove command when the file does not exist.
    Must return without any error.
    """
    mock_os_path_exists = Mock(return_value=False)
    mock_click_confirm = Mock()
    mock_os_remove = Mock()

    with patch("os.path.exists", mock_os_path_exists), patch(
        "click.confirm", mock_click_confirm
    ), patch("os.remove", mock_os_remove), pytest.raises(click.ClickException) as e:
        auth_controller = AuthController()
        auth_controller.remove()

    mock_click_confirm.assert_not_called()
    mock_os_remove.assert_not_called()
    assert "file does not exist" in e.value.message


def test_auth_remove_user_abort():
    """
    Test auth remove when the file exists, but the user aborts.
    """
    mock_os_path_exists = Mock(return_value=True)
    mock_click_confirm = Mock(return_value=False)
    mock_os_remove = Mock()

    with patch("os.path.exists", mock_os_path_exists), patch(
        "click.confirm", mock_click_confirm
    ), patch("os.remove", mock_os_remove):
        auth_controller = AuthController()
        auth_controller.remove()

    mock_os_remove.assert_not_called()


def test_auth_remove():
    """
    Test auth remove when the file exists and the user accepts.
    This should not trigger AuthenticationBlock to be initialized.
    """
    mock_os_path_exists = Mock(return_value=True)
    mock_click_confirm = Mock(return_value=True)
    mock_os_remove = Mock()
    mock_authentication_block_init = Mock(return_value=None)

    with patch("os.path.exists", mock_os_path_exists), patch(
        "click.confirm", mock_click_confirm
    ), patch("os.remove", mock_os_remove), patch(
        "anyscale.authenticate.AuthenticationBlock.__init__",
        mock_authentication_block_init,
    ):
        auth_controller = AuthController(path="/home/usr0/.anyscale/credentials.json")
        auth_controller.remove()

    mock_os_remove.assert_called_once_with("/home/usr0/.anyscale/credentials.json")
    mock_authentication_block_init.assert_not_called()


def test_auth_show_get_user_info_fails():
    """
    Test auth show but get_user_info is unable to fetch user data.
    This means that the token is invalid or does not exist.
    An exception should occur.
    """
    mock_get_user_info = Mock(return_value=None)
    Mock()
    with patch(
        "anyscale.controllers.auth_controller.get_user_info", mock_get_user_info
    ):
        auth_controller = AuthController()
        auth_controller.show()


def test_auth_show():
    """
    Test auth show command. Must not raise exception.
    """
    userinfo = UserInfo(
        name="Anyscale Test",
        email="anyscale@anyscale.com",
        id="usr_somerandomid",
        organization_permission_level="collaborator",
        organizations=[
            Organization(
                name="Anyscale Inc.",
                id="org_someorgid",
                local_vars_configuration=Mock(client_side_validation=False),
            )
        ],
        local_vars_configuration=Mock(client_side_validation=False),
    )
    mock_get_user_info = Mock(return_value=userinfo)

    with patch(
        "anyscale.controllers.auth_controller.get_user_info", mock_get_user_info
    ):
        auth_controller = AuthController()
        auth_controller.show()
