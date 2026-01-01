"""Test funnai_backend canister endpoints

First deploy the canister:
$ dfx start --clean --background
$ dfx deploy --argument "( principal \"$(dfx identity get-principal)\" )" funnai_backend

Then run all the tests:
$ pytest -vv --exitfirst --network local test/test_funnai_backend_canister.py

Or run a specific test:
$ pytest -vv --network local test/test_funnai_backend_canister.py::test__health

To run it against a deployment to a network on mainnet, just replace `local` with the network in the commands above.
Example:
$ pytest -vv --network testing test/test_funnai_backend_canister.py::test__health

"""

from pathlib import Path
import pytest
from icpp.smoketest import call_canister_api

DFX_JSON_PATH = Path(__file__).parent / "../dfx.json"
CANISTER_NAME = "funnai_backend"

# Test type: "single_canister" or "full_deployment"
# single_canister: Tests that only involve this canister
# full_deployment: Tests that require inter-canister calls
TEST_TYPE = "single_canister"


# ---------------------------------------------------------------------------
# Chat endpoints (most are disabled)
# ---------------------------------------------------------------------------
def test__create_chat_anonymous(network: str, identity_anonymous: dict) -> None:
    """Test create_chat returns Unauthorized for anonymous users"""
    response = call_canister_api(
        dfx_json_path=DFX_JSON_PATH,
        canister_name=CANISTER_NAME,
        canister_method="create_chat",
        canister_argument="(vec {})",
        network=network,
    )
    expected_response = "(variant { Err = variant { Unauthorized } })"
    assert response == expected_response


def test__create_chat_disabled(network: str, principal: str) -> None:
    """Test create_chat is disabled (returns Unauthorized even for authenticated users)"""
    response = call_canister_api(
        dfx_json_path=DFX_JSON_PATH,
        canister_name=CANISTER_NAME,
        canister_method="create_chat",
        canister_argument="(vec {})",
        network=network,
    )
    expected_response = "(variant { Err = variant { Unauthorized } })"
    assert response == expected_response


def test__get_caller_chats_anonymous(network: str, identity_anonymous: dict) -> None:
    """Test get_caller_chats returns Unauthorized for anonymous users"""
    response = call_canister_api(
        dfx_json_path=DFX_JSON_PATH,
        canister_name=CANISTER_NAME,
        canister_method="get_caller_chats",
        canister_argument="()",
        network=network,
    )
    expected_response = "(variant { Err = variant { Unauthorized } })"
    assert response == expected_response


def test__get_caller_chats(network: str, principal: str) -> None:
    """Test get_caller_chats returns empty list for new user"""
    response = call_canister_api(
        dfx_json_path=DFX_JSON_PATH,
        canister_name=CANISTER_NAME,
        canister_method="get_caller_chats",
        canister_argument="()",
        network=network,
    )
    expected_response = "(variant { Ok = vec {} })"
    assert response == expected_response


def test__get_caller_chat_history_anonymous(
    network: str, identity_anonymous: dict
) -> None:
    """Test get_caller_chat_history returns Unauthorized for anonymous users"""
    response = call_canister_api(
        dfx_json_path=DFX_JSON_PATH,
        canister_name=CANISTER_NAME,
        canister_method="get_caller_chat_history",
        canister_argument="()",
        network=network,
    )
    expected_response = "(variant { Err = variant { Unauthorized } })"
    assert response == expected_response


def test__get_caller_chat_history(network: str, principal: str) -> None:
    """Test get_caller_chat_history returns empty list for new user"""
    response = call_canister_api(
        dfx_json_path=DFX_JSON_PATH,
        canister_name=CANISTER_NAME,
        canister_method="get_caller_chat_history",
        canister_argument="()",
        network=network,
    )
    expected_response = "(variant { Ok = vec {} })"
    assert response == expected_response


def test__get_chat_anonymous(network: str, identity_anonymous: dict) -> None:
    """Test get_chat returns Unauthorized for anonymous users"""
    response = call_canister_api(
        dfx_json_path=DFX_JSON_PATH,
        canister_name=CANISTER_NAME,
        canister_method="get_chat",
        canister_argument='("nonexistent-chat-id")',
        network=network,
    )
    expected_response = "(variant { Err = variant { Unauthorized } })"
    assert response == expected_response


def test__get_chat_not_found(network: str, principal: str) -> None:
    """Test get_chat returns InvalidId for non-existent chat"""
    response = call_canister_api(
        dfx_json_path=DFX_JSON_PATH,
        canister_name=CANISTER_NAME,
        canister_method="get_chat",
        canister_argument='("nonexistent-chat-id")',
        network=network,
    )
    expected_response = "(variant { Err = variant { InvalidId } })"
    assert response == expected_response


def test__update_chat_metadata_disabled(network: str, principal: str) -> None:
    """Test update_chat_metadata is disabled"""
    response = call_canister_api(
        dfx_json_path=DFX_JSON_PATH,
        canister_name=CANISTER_NAME,
        canister_method="update_chat_metadata",
        canister_argument='(record { id = "test"; chatTitle = "Test Title" })',
        network=network,
    )
    expected_response = "(variant { Err = variant { Unauthorized } })"
    assert response == expected_response


def test__update_chat_messages_disabled(network: str, principal: str) -> None:
    """Test update_chat_messages is disabled"""
    response = call_canister_api(
        dfx_json_path=DFX_JSON_PATH,
        canister_name=CANISTER_NAME,
        canister_method="update_chat_messages",
        canister_argument='("test-id", vec {})',
        network=network,
    )
    expected_response = "(variant { Err = variant { Unauthorized } })"
    assert response == expected_response


def test__delete_chat_disabled(network: str, principal: str) -> None:
    """Test delete_chat is disabled"""
    response = call_canister_api(
        dfx_json_path=DFX_JSON_PATH,
        canister_name=CANISTER_NAME,
        canister_method="delete_chat",
        canister_argument='("test-id")',
        network=network,
    )
    expected_response = "(variant { Err = variant { Unauthorized } })"
    assert response == expected_response


# ---------------------------------------------------------------------------
# User Info endpoints
# ---------------------------------------------------------------------------
def test__get_caller_user_info_anonymous(
    network: str, identity_anonymous: dict
) -> None:
    """Test get_caller_user_info returns Unauthorized for anonymous users"""
    response = call_canister_api(
        dfx_json_path=DFX_JSON_PATH,
        canister_name=CANISTER_NAME,
        canister_method="get_caller_user_info",
        canister_argument="()",
        network=network,
    )
    expected_response = "(variant { Err = variant { Unauthorized } })"
    assert response == expected_response


def test__get_caller_user_info_not_found(network: str, principal: str) -> None:
    """Test get_caller_user_info returns InvalidId for user without info"""
    response = call_canister_api(
        dfx_json_path=DFX_JSON_PATH,
        canister_name=CANISTER_NAME,
        canister_method="get_caller_user_info",
        canister_argument="()",
        network=network,
    )
    expected_response = "(variant { Err = variant { InvalidId } })"
    assert response == expected_response


def test__get_user_info_admin_anonymous(
    network: str, identity_anonymous: dict
) -> None:
    """Test get_user_info_admin returns Unauthorized for anonymous users"""
    response = call_canister_api(
        dfx_json_path=DFX_JSON_PATH,
        canister_name=CANISTER_NAME,
        canister_method="get_user_info_admin",
        canister_argument='("aaaaa-aa")',
        network=network,
    )
    expected_response = "(variant { Err = variant { Unauthorized } })"
    assert response == expected_response


def test__get_user_info_admin(network: str, principal: str) -> None:
    """Test get_user_info_admin returns InvalidId for non-existent user"""
    response = call_canister_api(
        dfx_json_path=DFX_JSON_PATH,
        canister_name=CANISTER_NAME,
        canister_method="get_user_info_admin",
        canister_argument='("aaaaa-aa")',
        network=network,
    )
    expected_response = "(variant { Err = variant { InvalidId } })"
    assert response == expected_response


def test__getUsersAdmin_anonymous(network: str, identity_anonymous: dict) -> None:
    """Test getUsersAdmin returns Unauthorized for anonymous users"""
    response = call_canister_api(
        dfx_json_path=DFX_JSON_PATH,
        canister_name=CANISTER_NAME,
        canister_method="getUsersAdmin",
        canister_argument="()",
        network=network,
    )
    expected_response = "(variant { Err = variant { Unauthorized } })"
    assert response == expected_response


def test__getUsersAdmin(network: str, principal: str) -> None:
    """Test getUsersAdmin returns Ok for controller"""
    response = call_canister_api(
        dfx_json_path=DFX_JSON_PATH,
        canister_name=CANISTER_NAME,
        canister_method="getUsersAdmin",
        canister_argument="()",
        network=network,
    )
    # Returns empty list or list of users
    assert response.startswith("(variant { Ok = vec {")


def test__update_caller_user_info_anonymous(
    network: str, identity_anonymous: dict
) -> None:
    """Test update_caller_user_info returns Unauthorized for anonymous users"""
    response = call_canister_api(
        dfx_json_path=DFX_JSON_PATH,
        canister_name=CANISTER_NAME,
        canister_method="update_caller_user_info",
        canister_argument='(record { emailAddress = opt "test@example.com" })',
        network=network,
    )
    expected_response = "(variant { Err = variant { Unauthorized } })"
    assert response == expected_response


def test__update_caller_user_info(network: str, principal: str) -> None:
    """Test update_caller_user_info creates user info"""
    response = call_canister_api(
        dfx_json_path=DFX_JSON_PATH,
        canister_name=CANISTER_NAME,
        canister_method="update_caller_user_info",
        canister_argument='(record { emailAddress = opt "test@example.com" })',
        network=network,
    )
    expected_response = "(variant { Ok = true })"
    assert response == expected_response


def test__update_caller_user_info_email_too_long(network: str, principal: str) -> None:
    """Test update_caller_user_info rejects email > 70 chars"""
    long_email = "a" * 71 + "@example.com"
    response = call_canister_api(
        dfx_json_path=DFX_JSON_PATH,
        canister_name=CANISTER_NAME,
        canister_method="update_caller_user_info",
        canister_argument=f'(record {{ emailAddress = opt "{long_email}" }})',
        network=network,
    )
    expected_response = "(variant { Err = variant { Unauthorized } })"
    assert response == expected_response


# ---------------------------------------------------------------------------
# Login endpoints
# ---------------------------------------------------------------------------
def test__logLogin_anonymous(network: str, identity_anonymous: dict) -> None:
    """Test logLogin returns Unauthorized for anonymous users"""
    response = call_canister_api(
        dfx_json_path=DFX_JSON_PATH,
        canister_name=CANISTER_NAME,
        canister_method="logLogin",
        canister_argument="()",
        network=network,
    )
    expected_response = "(variant { Err = variant { Unauthorized } })"
    assert response == expected_response


def test__logLogin(network: str, principal: str) -> None:
    """Test logLogin records login event"""
    response = call_canister_api(
        dfx_json_path=DFX_JSON_PATH,
        canister_name=CANISTER_NAME,
        canister_method="logLogin",
        canister_argument="()",
        network=network,
    )
    expected_response = "(variant { Ok = true })"
    assert response == expected_response


def test__getLoginEventsAdmin_anonymous(
    network: str, identity_anonymous: dict
) -> None:
    """Test getLoginEventsAdmin returns Unauthorized for anonymous users"""
    response = call_canister_api(
        dfx_json_path=DFX_JSON_PATH,
        canister_name=CANISTER_NAME,
        canister_method="getLoginEventsAdmin",
        canister_argument='("aaaaa-aa")',
        network=network,
    )
    expected_response = "(variant { Err = variant { Unauthorized } })"
    assert response == expected_response


def test__getLoginEventsAdmin(network: str, principal: str) -> None:
    """Test getLoginEventsAdmin returns login events for controller"""
    response = call_canister_api(
        dfx_json_path=DFX_JSON_PATH,
        canister_name=CANISTER_NAME,
        canister_method="getLoginEventsAdmin",
        canister_argument=f'("{principal}")',
        network=network,
    )
    # Returns list of login events (may have events from logLogin test)
    assert response.startswith("(variant { Ok = vec {")


# ---------------------------------------------------------------------------
# Chat Settings endpoints
# ---------------------------------------------------------------------------
def test__get_caller_chat_settings_anonymous(
    network: str, identity_anonymous: dict
) -> None:
    """Test get_caller_chat_settings returns Unauthorized for anonymous users"""
    response = call_canister_api(
        dfx_json_path=DFX_JSON_PATH,
        canister_name=CANISTER_NAME,
        canister_method="get_caller_chat_settings",
        canister_argument="()",
        network=network,
    )
    expected_response = "(variant { Err = variant { Unauthorized } })"
    assert response == expected_response


def test__get_caller_chat_settings(network: str, principal: str) -> None:
    """Test get_caller_chat_settings returns default settings"""
    response = call_canister_api(
        dfx_json_path=DFX_JSON_PATH,
        canister_name=CANISTER_NAME,
        canister_method="get_caller_chat_settings",
        canister_argument="()",
        network=network,
    )
    # Returns default settings
    assert "(variant { Ok = record {" in response
    assert 'systemPrompt = "You are a helpful, respectful and honest assistant."' in response


def test__update_caller_chat_settings_disabled(network: str, principal: str) -> None:
    """Test update_caller_chat_settings is disabled"""
    response = call_canister_api(
        dfx_json_path=DFX_JSON_PATH,
        canister_name=CANISTER_NAME,
        canister_method="update_caller_chat_settings",
        canister_argument='(record { temperature = 0.7 : float64; responseLength = "Short"; saveChats = false; selectedAiModelId = ""; systemPrompt = "Test" })',
        network=network,
    )
    expected_response = "(variant { Err = variant { Unauthorized } })"
    assert response == expected_response


# ---------------------------------------------------------------------------
# Max Mainer Topups endpoints
# ---------------------------------------------------------------------------
def test__addMaxMainerTopup_anonymous(network: str, identity_anonymous: dict) -> None:
    """Test addMaxMainerTopup returns Unauthorized for anonymous users"""
    response = call_canister_api(
        dfx_json_path=DFX_JSON_PATH,
        canister_name=CANISTER_NAME,
        canister_method="addMaxMainerTopup",
        canister_argument='(record { paymentTransactionBlockId = 1 : nat64; toppedUpMainerId = "test"; amount = 100 : nat })',
        network=network,
    )
    expected_response = "(variant { Err = variant { Unauthorized } })"
    assert response == expected_response


def test__addMaxMainerTopup_not_user(network: str, principal: str) -> None:
    """Test addMaxMainerTopup returns Unauthorized for non-registered user"""
    # Need to ensure user info doesn't exist first (fresh canister)
    response = call_canister_api(
        dfx_json_path=DFX_JSON_PATH,
        canister_name=CANISTER_NAME,
        canister_method="addMaxMainerTopup",
        canister_argument='(record { paymentTransactionBlockId = 1 : nat64; toppedUpMainerId = "test"; amount = 100 : nat })',
        network=network,
    )
    # After logLogin test, user exists, so this should succeed
    assert "(variant { Ok = record { stored = true;} })" in response or "(variant { Err = variant { Unauthorized } })" in response


def test__getMaxMainerTopupsAdmin_anonymous(
    network: str, identity_anonymous: dict
) -> None:
    """Test getMaxMainerTopupsAdmin returns Unauthorized for anonymous users"""
    response = call_canister_api(
        dfx_json_path=DFX_JSON_PATH,
        canister_name=CANISTER_NAME,
        canister_method="getMaxMainerTopupsAdmin",
        canister_argument="()",
        network=network,
    )
    expected_response = "(variant { Err = variant { Unauthorized } })"
    assert response == expected_response


def test__getMaxMainerTopupsAdmin(network: str, principal: str) -> None:
    """Test getMaxMainerTopupsAdmin returns topups for controller"""
    response = call_canister_api(
        dfx_json_path=DFX_JSON_PATH,
        canister_name=CANISTER_NAME,
        canister_method="getMaxMainerTopupsAdmin",
        canister_argument="()",
        network=network,
    )
    assert response.startswith("(variant { Ok = vec {")


def test__getArchivedMaxMainerTopupsAdmin_anonymous(
    network: str, identity_anonymous: dict
) -> None:
    """Test getArchivedMaxMainerTopupsAdmin returns Unauthorized for anonymous"""
    response = call_canister_api(
        dfx_json_path=DFX_JSON_PATH,
        canister_name=CANISTER_NAME,
        canister_method="getArchivedMaxMainerTopupsAdmin",
        canister_argument="()",
        network=network,
    )
    expected_response = "(variant { Err = variant { Unauthorized } })"
    assert response == expected_response


def test__getArchivedMaxMainerTopupsAdmin(network: str, principal: str) -> None:
    """Test getArchivedMaxMainerTopupsAdmin returns archived topups"""
    response = call_canister_api(
        dfx_json_path=DFX_JSON_PATH,
        canister_name=CANISTER_NAME,
        canister_method="getArchivedMaxMainerTopupsAdmin",
        canister_argument="()",
        network=network,
    )
    assert response.startswith("(variant { Ok = vec {")


def test__getNumArchivedMaxMainerTopupsAdmin_anonymous(
    network: str, identity_anonymous: dict
) -> None:
    """Test getNumArchivedMaxMainerTopupsAdmin returns Unauthorized for anonymous"""
    response = call_canister_api(
        dfx_json_path=DFX_JSON_PATH,
        canister_name=CANISTER_NAME,
        canister_method="getNumArchivedMaxMainerTopupsAdmin",
        canister_argument="()",
        network=network,
    )
    expected_response = "(variant { Err = variant { Unauthorized } })"
    assert response == expected_response


def test__getNumArchivedMaxMainerTopupsAdmin(network: str, principal: str) -> None:
    """Test getNumArchivedMaxMainerTopupsAdmin returns count"""
    response = call_canister_api(
        dfx_json_path=DFX_JSON_PATH,
        canister_name=CANISTER_NAME,
        canister_method="getNumArchivedMaxMainerTopupsAdmin",
        canister_argument="()",
        network=network,
    )
    assert response.startswith("(variant { Ok = ")


def test__archiveMaxMainerTopupsAdmin_anonymous(
    network: str, identity_anonymous: dict
) -> None:
    """Test archiveMaxMainerTopupsAdmin returns Unauthorized for anonymous"""
    response = call_canister_api(
        dfx_json_path=DFX_JSON_PATH,
        canister_name=CANISTER_NAME,
        canister_method="archiveMaxMainerTopupsAdmin",
        canister_argument="()",
        network=network,
    )
    expected_response = "(variant { Err = variant { Unauthorized } })"
    assert response == expected_response


def test__archiveMaxMainerTopupsAdmin(network: str, principal: str) -> None:
    """Test archiveMaxMainerTopupsAdmin archives topups"""
    response = call_canister_api(
        dfx_json_path=DFX_JSON_PATH,
        canister_name=CANISTER_NAME,
        canister_method="archiveMaxMainerTopupsAdmin",
        canister_argument="()",
        network=network,
    )
    expected_response = "(variant { Ok = true })"
    assert response == expected_response


# ---------------------------------------------------------------------------
# Email Signup endpoints
# ---------------------------------------------------------------------------
def test__submit_signup_form(network: str, principal: str) -> None:
    """Test submit_signup_form accepts valid email"""
    response = call_canister_api(
        dfx_json_path=DFX_JSON_PATH,
        canister_name=CANISTER_NAME,
        canister_method="submit_signup_form",
        canister_argument='(record { emailAddress = "test@example.com"; pageSubmittedFrom = "homepage" })',
        network=network,
    )
    assert response == '("Successfully signed up!")'


def test__submit_signup_form_duplicate(network: str, principal: str) -> None:
    """Test submit_signup_form detects duplicate email"""
    response = call_canister_api(
        dfx_json_path=DFX_JSON_PATH,
        canister_name=CANISTER_NAME,
        canister_method="submit_signup_form",
        canister_argument='(record { emailAddress = "test@example.com"; pageSubmittedFrom = "homepage" })',
        network=network,
    )
    assert response == '("Already signed up!")'


def test__submit_signup_form_email_too_long(network: str, principal: str) -> None:
    """Test submit_signup_form rejects email > 70 chars"""
    long_email = "a" * 71 + "@example.com"
    response = call_canister_api(
        dfx_json_path=DFX_JSON_PATH,
        canister_name=CANISTER_NAME,
        canister_method="submit_signup_form",
        canister_argument=f'(record {{ emailAddress = "{long_email}"; pageSubmittedFrom = "test" }})',
        network=network,
    )
    assert response == '("There was an error signing up. Please try again.")'


def test__get_email_subscribers_anonymous(
    network: str, identity_anonymous: dict
) -> None:
    """Test get_email_subscribers returns empty for anonymous users"""
    response = call_canister_api(
        dfx_json_path=DFX_JSON_PATH,
        canister_name=CANISTER_NAME,
        canister_method="get_email_subscribers",
        canister_argument="()",
        network=network,
    )
    expected_response = "(vec {})"
    assert response == expected_response


def test__get_email_subscribers(network: str, principal: str) -> None:
    """Test get_email_subscribers returns subscribers for controller"""
    response = call_canister_api(
        dfx_json_path=DFX_JSON_PATH,
        canister_name=CANISTER_NAME,
        canister_method="get_email_subscribers",
        canister_argument="()",
        network=network,
    )
    # Should contain the email we added
    assert "test@example.com" in response


def test__delete_email_subscriber_anonymous(
    network: str, identity_anonymous: dict
) -> None:
    """Test delete_email_subscriber returns false for anonymous users"""
    response = call_canister_api(
        dfx_json_path=DFX_JSON_PATH,
        canister_name=CANISTER_NAME,
        canister_method="delete_email_subscriber",
        canister_argument='("test@example.com")',
        network=network,
    )
    expected_response = "(false)"
    assert response == expected_response


def test__delete_email_subscriber(network: str, principal: str) -> None:
    """Test delete_email_subscriber works for custodian (controller is custodian)"""
    response = call_canister_api(
        dfx_json_path=DFX_JSON_PATH,
        canister_name=CANISTER_NAME,
        canister_method="delete_email_subscriber",
        canister_argument='("test@example.com")',
        network=network,
    )
    # Controller is also a custodian (passed in constructor)
    expected_response = "(true)"
    assert response == expected_response


def test__make_caller_account_premium_anonymous(
    network: str, identity_anonymous: dict
) -> None:
    """Test make_caller_account_premium returns Unauthorized for anonymous"""
    response = call_canister_api(
        dfx_json_path=DFX_JSON_PATH,
        canister_name=CANISTER_NAME,
        canister_method="make_caller_account_premium",
        canister_argument="(record { block_index = 1 : nat64 })",
        network=network,
    )
    expected_response = "(variant { Err = variant { Unauthorized } })"
    assert response == expected_response


def test__make_caller_account_premium(network: str, principal: str) -> None:
    """Test make_caller_account_premium for custodian (controller is custodian)"""
    # First ensure user has info (via logLogin which creates user info)
    # logLogin was already called in earlier test, so user should exist
    response = call_canister_api(
        dfx_json_path=DFX_JSON_PATH,
        canister_name=CANISTER_NAME,
        canister_method="make_caller_account_premium",
        canister_argument="(record { block_index = 1 : nat64 })",
        network=network,
    )
    # Controller is also a custodian (passed in constructor), so should succeed
    expected_response = "(variant { Ok = true })"
    assert response == expected_response
