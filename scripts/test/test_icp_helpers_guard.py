"""The mainnet write guard in scripts/lib/icp_helpers.py.

The guard exists because the dfx -> icp-cli migration must not change anything that is
deployed: redeploying is a separate project. These tests assert the property that matters
-- that a blocked operation is refused *before* any network machinery is touched, not
merely that it eventually errors.

Every canister id and method name below is deliberately fictitious. Testing a guard with
the name of a real destructive endpoint is an unnecessary risk: it relies on the guard
being correct to stay safe, which is the very thing under test.

    pytest -q scripts/test/test_icp_helpers_guard.py
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "lib"))
import icp_helpers  # noqa: E402

FAKE_CANISTER = "aaaaa-fake-canister-id"
FAKE_METHOD = "someUpdateMethod"

MAINNET_ENVS = ["prd", "testing", "development", "demo", "backup", "ic"]


@pytest.fixture(autouse=True)
def _no_mainnet_override(monkeypatch):
    """The guard is lifted by an env var; make sure the suite never runs with it set."""
    monkeypatch.delenv("ICP_ALLOW_MAINNET_WRITES", raising=False)


@pytest.fixture
def tripwires(monkeypatch):
    """Fail loudly if anything reaches for the network, an identity, or the icp CLI."""
    hits = []
    monkeypatch.setattr(icp_helpers, "_agent", lambda *a, **k: hits.append("_agent"))
    monkeypatch.setattr(icp_helpers, "candid_of", lambda *a, **k: hits.append("candid_of"))
    monkeypatch.setattr(icp_helpers, "run_icp", lambda *a, **k: hits.append("run_icp"))
    return hits


@pytest.mark.parametrize("env", MAINNET_ENVS)
def test__update_call_is_refused_on_every_mainnet_environment(env, tripwires):
    with pytest.raises(icp_helpers.MainnetWriteBlocked):
        icp_helpers.call(FAKE_CANISTER, FAKE_METHOD, env=env)
    assert tripwires == [], f"guard let execution reach {tripwires} before refusing"


@pytest.mark.parametrize("env", MAINNET_ENVS)
def test__lifecycle_operations_are_refused_on_mainnet(env, tripwires):
    for op in (
        lambda: icp_helpers.install(FAKE_CANISTER, "nonexistent.wasm", env=env),
        lambda: icp_helpers.top_up(FAKE_CANISTER, 1, env=env),
        lambda: icp_helpers.add_controller(FAKE_CANISTER, "aaaaa-aa", env=env),
        lambda: icp_helpers.wallet_send(FAKE_CANISTER, 1, env=env),
    ):
        with pytest.raises(icp_helpers.MainnetWriteBlocked):
            op()
    assert tripwires == [], f"guard let execution reach {tripwires} before refusing"


@pytest.mark.parametrize("env", MAINNET_ENVS)
def test__call_argv_refuses_update_calls_on_mainnet(env, tripwires):
    argv = ["icp", "canister", "call", FAKE_CANISTER, FAKE_METHOD, "()", "-e", env]
    with pytest.raises(icp_helpers.MainnetWriteBlocked):
        icp_helpers.call_argv(argv, allow_mainnet=False)
    assert tripwires == []


def test__local_is_not_guarded():
    """The guard must not get in the way of local development."""
    assert "local" not in icp_helpers.MAINNET_ENVIRONMENTS
    icp_helpers.guard_write("local", "install onto a local canister")  # must not raise


def test__reads_are_never_guarded(tripwires):
    """Status/balance/hash lookups stay available on mainnet -- they change nothing."""
    for env in MAINNET_ENVS:
        icp_helpers.guard_write  # sanity: guard exists
        icp_helpers.status_json(FAKE_CANISTER, env)  # tripwired run_icp, so no real call
    assert tripwires, "expected the read path to reach run_icp"
    assert all(h == "run_icp" for h in tripwires)


def test__query_calls_are_not_guarded(tripwires):
    """A query cannot mutate state, so it is allowed on mainnet.

    The tripwired `_agent`/`candid_of` return None, so this fails deeper inside the call
    machinery. That is the point: failing there rather than with MainnetWriteBlocked is
    what proves the guard let a query through.
    """
    with pytest.raises(Exception) as exc:
        icp_helpers.call(FAKE_CANISTER, "someQueryMethod", env="prd", is_query=True)
    assert not isinstance(exc.value, icp_helpers.MainnetWriteBlocked)
    assert "_agent" in tripwires or "candid_of" in tripwires


def test__the_env_var_is_the_only_way_to_lift_the_guard(monkeypatch):
    monkeypatch.setenv("ICP_ALLOW_MAINNET_WRITES", "1")
    assert icp_helpers.mainnet_writes_allowed()
    icp_helpers.guard_write("prd", "deliberately allowed")  # must not raise

    monkeypatch.setenv("ICP_ALLOW_MAINNET_WRITES", "yes")  # only "1" counts
    assert not icp_helpers.mainnet_writes_allowed()
    with pytest.raises(icp_helpers.MainnetWriteBlocked):
        icp_helpers.guard_write("prd", "still refused")
