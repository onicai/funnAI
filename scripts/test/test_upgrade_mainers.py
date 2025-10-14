#!/usr/bin/env python3

import pytest
import sys
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch, call, mock_open
import signal

# Add parent directory to path to import the module
sys.path.insert(0, str(Path(__file__).parent.parent))

import upgrade_mainers


class TestLogMessage:
    """Test the log_message function."""

    @patch('upgrade_mainers.datetime')
    def test_log_message_info(self, mock_datetime, capsys):
        """Test INFO level log message."""
        mock_datetime.now.return_value.strftime.return_value = "2024-01-01 12:00:00"

        upgrade_mainers.log_message("Test message", "INFO")

        captured = capsys.readouterr()
        assert "[2024-01-01 12:00:00] INFO: Test message" in captured.out
        assert upgrade_mainers.BLUE in captured.out

    @patch('upgrade_mainers.datetime')
    def test_log_message_error(self, mock_datetime, capsys):
        """Test ERROR level log message."""
        mock_datetime.now.return_value.strftime.return_value = "2024-01-01 12:00:00"

        upgrade_mainers.log_message("Error message", "ERROR")

        captured = capsys.readouterr()
        assert "[2024-01-01 12:00:00] ERROR: Error message" in captured.out
        assert upgrade_mainers.RED in captured.out

    @patch('upgrade_mainers.datetime')
    def test_log_message_warning(self, mock_datetime, capsys):
        """Test WARNING level log message."""
        mock_datetime.now.return_value.strftime.return_value = "2024-01-01 12:00:00"

        upgrade_mainers.log_message("Warning message", "WARNING")

        captured = capsys.readouterr()
        assert "[2024-01-01 12:00:00] WARNING: Warning message" in captured.out
        assert upgrade_mainers.YELLOW in captured.out

    @patch('upgrade_mainers.datetime')
    def test_log_message_success(self, mock_datetime, capsys):
        """Test SUCCESS level log message."""
        mock_datetime.now.return_value.strftime.return_value = "2024-01-01 12:00:00"

        upgrade_mainers.log_message("Success message", "SUCCESS")

        captured = capsys.readouterr()
        assert "[2024-01-01 12:00:00] SUCCESS: Success message" in captured.out
        assert upgrade_mainers.GREEN in captured.out


class TestRunCommand:
    """Test the run_command function."""

    @patch('upgrade_mainers.subprocess.run')
    def test_run_command_success(self, mock_run):
        """Test successful command execution with captured output."""
        mock_run.return_value = subprocess.CompletedProcess(
            args=['test'],
            returncode=0,
            stdout="test output",
            stderr=""
        )

        result = upgrade_mainers.run_command(['test', 'command'])

        assert result.stdout == "test output"
        mock_run.assert_called_once_with(
            ['test', 'command'],
            capture_output=True,
            text=True,
            check=True,
            cwd=None
        )

    @patch('upgrade_mainers.subprocess.run')
    def test_run_command_no_capture(self, mock_run):
        """Test command execution without capturing output."""
        mock_run.return_value = subprocess.CompletedProcess(
            args=['test'],
            returncode=0
        )

        result = upgrade_mainers.run_command(['test', 'command'], capture_output=False)

        mock_run.assert_called_once_with(
            ['test', 'command'],
            check=True,
            cwd=None
        )

    @patch('upgrade_mainers.subprocess.run')
    def test_run_command_with_cwd(self, mock_run):
        """Test command execution with custom working directory."""
        mock_run.return_value = subprocess.CompletedProcess(
            args=['test'],
            returncode=0,
            stdout="",
            stderr=""
        )

        upgrade_mainers.run_command(['test'], cwd="/custom/path")

        mock_run.assert_called_once_with(
            ['test'],
            capture_output=True,
            text=True,
            check=True,
            cwd="/custom/path"
        )

    @patch('upgrade_mainers.subprocess.run')
    def test_run_command_failure(self, mock_run):
        """Test command execution failure."""
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1,
            cmd=['test'],
            stderr="error message"
        )

        with pytest.raises(subprocess.CalledProcessError):
            upgrade_mainers.run_command(['test', 'command'])


class TestGetMainers:
    """Test the get_mainers function."""

    @patch('upgrade_mainers.run_command')
    def test_get_mainers_success(self, mock_run):
        """Test successful retrieval of mainers."""
        mainers_data = [
            {'address': 'abc123', 'ownedBy': 'user1'},
            {'address': 'def456', 'ownedBy': 'user2'}
        ]
        mock_run.return_value = Mock(stdout=json.dumps({'Ok': mainers_data}))

        result = upgrade_mainers.get_mainers('testing')

        assert result == mainers_data
        assert len(result) == 2
        mock_run.assert_called_once()

    @patch('upgrade_mainers.run_command')
    def test_get_mainers_empty(self, mock_run):
        """Test get_mainers with empty result."""
        mock_run.return_value = Mock(stdout=json.dumps({'Ok': []}))

        result = upgrade_mainers.get_mainers('testing')

        assert result == []

    @patch('upgrade_mainers.run_command')
    @patch('upgrade_mainers.sys.exit')
    def test_get_mainers_failure(self, mock_exit, mock_run):
        """Test get_mainers failure handling."""
        mock_run.side_effect = Exception("Connection failed")

        upgrade_mainers.get_mainers('testing')

        mock_exit.assert_called_once_with(1)


class TestGetCanisterStatus:
    """Test the get_canister_status function."""

    @patch('upgrade_mainers.run_command')
    def test_get_canister_status_running(self, mock_run):
        """Test getting Running status."""
        mock_run.return_value = Mock(stdout="Status: Running\nOther: info")

        status = upgrade_mainers.get_canister_status('testing', 'abc123')

        assert status == "Running"

    @patch('upgrade_mainers.run_command')
    def test_get_canister_status_stopped(self, mock_run):
        """Test getting Stopped status."""
        mock_run.return_value = Mock(stdout="Status: Stopped\n")

        status = upgrade_mainers.get_canister_status('testing', 'abc123')

        assert status == "Stopped"

    @patch('upgrade_mainers.run_command')
    def test_get_canister_status_failure(self, mock_run):
        """Test status retrieval failure."""
        mock_run.side_effect = Exception("Failed")

        status = upgrade_mainers.get_canister_status('testing', 'abc123')

        assert status is None


class TestGetCanisterWasmHash:
    """Test the get_canister_wasm_hash function."""

    @patch('upgrade_mainers.run_command')
    def test_get_wasm_hash_success(self, mock_run):
        """Test successful wasm hash retrieval."""
        mock_run.return_value = Mock(
            stdout="Info:\nModule hash: 0xabcdef123456\nOther: info"
        )

        hash_value = upgrade_mainers.get_canister_wasm_hash('testing', 'abc123')

        assert hash_value == "0xabcdef123456"

    @patch('upgrade_mainers.run_command')
    def test_get_wasm_hash_not_found(self, mock_run):
        """Test wasm hash not found in output."""
        mock_run.return_value = Mock(stdout="Info:\nOther: info")

        hash_value = upgrade_mainers.get_canister_wasm_hash('testing', 'abc123')

        assert hash_value is None

    @patch('upgrade_mainers.run_command')
    def test_get_wasm_hash_failure(self, mock_run):
        """Test wasm hash retrieval failure."""
        mock_run.side_effect = Exception("Failed")

        hash_value = upgrade_mainers.get_canister_wasm_hash('testing', 'abc123')

        assert hash_value is None


class TestStopTimer:
    """Test the stop_timer function."""

    @patch('upgrade_mainers.run_command')
    def test_stop_timer_success(self, mock_run):
        """Test successful timer stop."""
        mock_run.return_value = Mock(
            stdout='(variant { Ok = record { auth = "You stopped the timers: " } })'
        )

        result = upgrade_mainers.stop_timer('testing', 'abc123')

        assert result is True

    @patch('upgrade_mainers.run_command')
    def test_stop_timer_dry_run(self, mock_run):
        """Test timer stop in dry run mode."""
        result = upgrade_mainers.stop_timer('testing', 'abc123', dry_run=True)

        assert result is True
        mock_run.assert_not_called()

    @patch('upgrade_mainers.run_command')
    def test_stop_timer_failure(self, mock_run):
        """Test timer stop failure."""
        mock_run.side_effect = Exception("Failed")

        result = upgrade_mainers.stop_timer('testing', 'abc123')

        assert result is False


class TestStartTimer:
    """Test the start_timer function."""

    @patch('upgrade_mainers.run_command')
    def test_start_timer_success(self, mock_run):
        """Test successful timer start."""
        mock_run.return_value = Mock(
            stdout='(variant { Ok = record { auth = "You started the timers:  1, " } })'
        )

        result = upgrade_mainers.start_timer('testing', 'abc123')

        assert result is True

    @patch('upgrade_mainers.run_command')
    def test_start_timer_dry_run(self, mock_run):
        """Test timer start in dry run mode."""
        result = upgrade_mainers.start_timer('testing', 'abc123', dry_run=True)

        assert result is True
        mock_run.assert_not_called()

    @patch('upgrade_mainers.run_command')
    def test_start_timer_failure(self, mock_run):
        """Test timer start failure."""
        mock_run.side_effect = Exception("Failed")

        result = upgrade_mainers.start_timer('testing', 'abc123')

        assert result is False


class TestCheckQueue:
    """Test the check_queue function."""

    @patch('upgrade_mainers.run_command')
    def test_check_queue_empty(self, mock_run):
        """Test checking empty queue."""
        mock_run.return_value = Mock(stdout=json.dumps({'Ok': []}))

        has_entries, last_time = upgrade_mainers.check_queue('testing', 'abc123')

        assert has_entries is False
        assert last_time is None

    @patch('upgrade_mainers.run_command')
    @patch('upgrade_mainers.datetime')
    def test_check_queue_with_entries(self, mock_datetime, mock_run):
        """Test checking queue with entries."""
        now = datetime(2024, 1, 1, 12, 0, 0)
        mock_datetime.now.return_value = now
        mock_datetime.fromtimestamp = datetime.fromtimestamp

        # Timestamp 5 minutes ago in nanoseconds
        five_min_ago = (now - timedelta(minutes=5)).timestamp() * 1_000_000_000

        mock_run.return_value = Mock(stdout=json.dumps({
            'Ok': [
                {'challengeQueuedTimestamp': str(int(five_min_ago))},
            ]
        }))

        has_entries, last_time = upgrade_mainers.check_queue('testing', 'abc123')

        assert has_entries is True
        assert last_time is not None

    @patch('upgrade_mainers.run_command')
    def test_check_queue_multiple_entries(self, mock_run):
        """Test checking queue with multiple entries, returns most recent."""
        now = datetime.now()
        older_time = int((now - timedelta(minutes=10)).timestamp() * 1_000_000_000)
        newer_time = int((now - timedelta(minutes=2)).timestamp() * 1_000_000_000)

        mock_run.return_value = Mock(stdout=json.dumps({
            'Ok': [
                {'challengeQueuedTimestamp': str(older_time)},
                {'challengeQueuedTimestamp': str(newer_time)},
            ]
        }))

        has_entries, last_time = upgrade_mainers.check_queue('testing', 'abc123')

        assert has_entries is True
        # Should return the newer timestamp
        age_minutes = (datetime.now() - last_time).total_seconds() / 60
        assert 1.5 < age_minutes < 3

    @patch('upgrade_mainers.run_command')
    def test_check_queue_failure(self, mock_run):
        """Test queue check failure."""
        mock_run.side_effect = Exception("Failed")

        has_entries, last_time = upgrade_mainers.check_queue('testing', 'abc123')

        assert has_entries is False
        assert last_time is None


class TestClearQueue:
    """Test the clear_queue function."""

    @patch('upgrade_mainers.run_command')
    def test_clear_queue_success(self, mock_run):
        """Test successful queue clear."""
        mock_run.return_value = Mock(
            stdout='(variant { Ok = record { status_code = 200 } })'
        )

        result = upgrade_mainers.clear_queue('testing', 'abc123')

        assert result is True

    @patch('upgrade_mainers.run_command')
    def test_clear_queue_dry_run(self, mock_run):
        """Test queue clear in dry run mode."""
        result = upgrade_mainers.clear_queue('testing', 'abc123', dry_run=True)

        assert result is True
        mock_run.assert_not_called()

    @patch('upgrade_mainers.run_command')
    @patch('upgrade_mainers.sys.exit')
    def test_clear_queue_failure(self, mock_exit, mock_run):
        """Test queue clear failure."""
        mock_run.return_value = Mock(stdout='(variant { Err = "Failed" })')

        upgrade_mainers.clear_queue('testing', 'abc123')

        mock_exit.assert_called_once_with(1)


class TestStopCanister:
    """Test the stop_canister function."""

    @patch('upgrade_mainers.run_command')
    def test_stop_canister_success(self, mock_run):
        """Test successful canister stop."""
        mock_run.return_value = Mock(stdout='')

        result = upgrade_mainers.stop_canister('testing', 'abc123')

        assert result is True

    @patch('upgrade_mainers.run_command')
    def test_stop_canister_dry_run(self, mock_run):
        """Test canister stop in dry run mode."""
        result = upgrade_mainers.stop_canister('testing', 'abc123', dry_run=True)

        assert result is True
        mock_run.assert_not_called()

    @patch('upgrade_mainers.run_command')
    def test_stop_canister_failure(self, mock_run):
        """Test canister stop failure."""
        mock_run.side_effect = Exception("Failed")

        result = upgrade_mainers.stop_canister('testing', 'abc123')

        assert result is False


class TestStartCanister:
    """Test the start_canister function."""

    @patch('upgrade_mainers.run_command')
    def test_start_canister_success(self, mock_run):
        """Test successful canister start."""
        mock_run.return_value = Mock(stdout='')

        result = upgrade_mainers.start_canister('testing', 'abc123')

        assert result is True

    @patch('upgrade_mainers.run_command')
    def test_start_canister_dry_run(self, mock_run):
        """Test canister start in dry run mode."""
        result = upgrade_mainers.start_canister('testing', 'abc123', dry_run=True)

        assert result is True
        mock_run.assert_not_called()

    @patch('upgrade_mainers.run_command')
    def test_start_canister_failure(self, mock_run):
        """Test canister start failure."""
        mock_run.side_effect = Exception("Failed")

        result = upgrade_mainers.start_canister('testing', 'abc123')

        assert result is False


class TestCreateSnapshot:
    """Test the create_snapshot function."""

    @patch('upgrade_mainers.run_command')
    def test_create_snapshot_success(self, mock_run):
        """Test successful snapshot creation."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout='',
            stderr='Created a new snapshot of canister abc123. Snapshot ID: snap_123456'
        )

        snapshot_id = upgrade_mainers.create_snapshot('testing', 'abc123')

        assert snapshot_id == 'snap_123456'

    @patch('upgrade_mainers.run_command')
    def test_create_snapshot_dry_run(self, mock_run):
        """Test snapshot creation in dry run mode."""
        snapshot_id = upgrade_mainers.create_snapshot('testing', 'abc123', dry_run=True)

        assert snapshot_id == 'dry-run-snapshot-id'
        mock_run.assert_not_called()

    @patch('upgrade_mainers.run_command')
    def test_create_snapshot_no_id_parsed(self, mock_run):
        """Test snapshot creation when ID cannot be parsed."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout='',
            stderr='Snapshot created but no ID in output'
        )

        snapshot_id = upgrade_mainers.create_snapshot('testing', 'abc123')

        assert snapshot_id == 'created-but-not-parsed'

    @patch('upgrade_mainers.run_command')
    def test_create_snapshot_failure(self, mock_run):
        """Test snapshot creation failure."""
        mock_run.side_effect = Exception("Failed")

        snapshot_id = upgrade_mainers.create_snapshot('testing', 'abc123')

        assert snapshot_id is None


class TestUpgradeCanister:
    """Test the upgrade_canister function."""

    @patch('upgrade_mainers.run_command')
    def test_upgrade_canister_success(self, mock_run):
        """Test successful canister upgrade."""
        mock_run.return_value = Mock(returncode=0)

        result = upgrade_mainers.upgrade_canister('testing', 'mainer_share_agent_0001')

        assert result is True
        # Verify command was called with correct cwd
        call_args = mock_run.call_args
        assert call_args[1]['cwd'] == str(upgrade_mainers.POAIW_MAINER_DIR)

    @patch('upgrade_mainers.run_command')
    def test_upgrade_canister_dry_run(self, mock_run):
        """Test canister upgrade in dry run mode."""
        result = upgrade_mainers.upgrade_canister('testing', 'mainer_share_agent_0001', dry_run=True)

        assert result is True
        mock_run.assert_not_called()

    @patch('upgrade_mainers.run_command')
    def test_upgrade_canister_failure(self, mock_run):
        """Test canister upgrade failure."""
        mock_run.side_effect = Exception("Upgrade failed")

        result = upgrade_mainers.upgrade_canister('testing', 'mainer_share_agent_0001')

        assert result is False


class TestCheckHealth:
    """Test the check_health function."""

    @patch('upgrade_mainers.run_command')
    def test_check_health_success(self, mock_run):
        """Test successful health check."""
        mock_run.return_value = Mock(
            stdout='(variant { Ok = record { status_code = 200 : nat16 } })'
        )

        result = upgrade_mainers.check_health('testing', 'abc123')

        assert result is True

    @patch('upgrade_mainers.run_command')
    def test_check_health_dry_run(self, mock_run):
        """Test health check in dry run mode."""
        result = upgrade_mainers.check_health('testing', 'abc123', dry_run=True)

        assert result is True
        mock_run.assert_not_called()

    @patch('upgrade_mainers.run_command')
    def test_check_health_failure(self, mock_run):
        """Test health check failure."""
        mock_run.return_value = Mock(stdout='(variant { Err = "Unhealthy" })')

        result = upgrade_mainers.check_health('testing', 'abc123')

        assert result is False


class TestGetMaintenanceFlag:
    """Test the get_maintenance_flag function."""

    @patch('upgrade_mainers.run_command')
    def test_get_maintenance_flag_true(self, mock_run):
        """Test getting maintenance flag when true."""
        mock_run.return_value = Mock(
            stdout=json.dumps({'Ok': {'flag': True}})
        )

        flag = upgrade_mainers.get_maintenance_flag('testing', 'abc123')

        assert flag is True

    @patch('upgrade_mainers.run_command')
    def test_get_maintenance_flag_false(self, mock_run):
        """Test getting maintenance flag when false."""
        mock_run.return_value = Mock(
            stdout=json.dumps({'Ok': {'flag': False}})
        )

        flag = upgrade_mainers.get_maintenance_flag('testing', 'abc123')

        assert flag is False

    @patch('upgrade_mainers.run_command')
    def test_get_maintenance_flag_failure(self, mock_run):
        """Test getting maintenance flag failure."""
        mock_run.side_effect = Exception("Failed")

        flag = upgrade_mainers.get_maintenance_flag('testing', 'abc123')

        assert flag is None


class TestTurnOffMaintenanceFlag:
    """Test the turn_off_maintenance_flag function."""

    @patch('upgrade_mainers.get_maintenance_flag')
    def test_turn_off_already_off(self, mock_get_flag):
        """Test when maintenance flag is already off."""
        mock_get_flag.return_value = False

        result = upgrade_mainers.turn_off_maintenance_flag('testing', 'abc123')

        assert result is True

    @patch('upgrade_mainers.run_command')
    @patch('upgrade_mainers.get_maintenance_flag')
    def test_turn_off_success(self, mock_get_flag, mock_run):
        """Test successfully turning off maintenance flag."""
        # First call returns True (flag is on), second call returns False (flag is off)
        mock_get_flag.side_effect = [True, False]
        mock_run.return_value = Mock(stdout='')

        result = upgrade_mainers.turn_off_maintenance_flag('testing', 'abc123')

        assert result is True
        assert mock_get_flag.call_count == 2

    @patch('upgrade_mainers.get_maintenance_flag')
    def test_turn_off_dry_run(self, mock_get_flag):
        """Test turn off maintenance flag in dry run mode."""
        result = upgrade_mainers.turn_off_maintenance_flag('testing', 'abc123', dry_run=True)

        assert result is True
        mock_get_flag.assert_not_called()

    @patch('upgrade_mainers.run_command')
    @patch('upgrade_mainers.get_maintenance_flag')
    def test_turn_off_toggle_failed(self, mock_get_flag, mock_run):
        """Test when toggle doesn't change the flag."""
        # Flag stays True after toggle
        mock_get_flag.side_effect = [True, True]
        mock_run.return_value = Mock(stdout='')

        result = upgrade_mainers.turn_off_maintenance_flag('testing', 'abc123')

        assert result is False

    @patch('upgrade_mainers.get_maintenance_flag')
    def test_turn_off_unexpected_value(self, mock_get_flag):
        """Test when maintenance flag has unexpected value."""
        mock_get_flag.return_value = None

        result = upgrade_mainers.turn_off_maintenance_flag('testing', 'abc123')

        assert result is False


class TestPrepareForDeployment:
    """Test the prepare_for_deployment function."""

    @patch('upgrade_mainers.run_command')
    def test_prepare_for_deployment_success(self, mock_run):
        """Test successful preparation for deployment."""
        mock_run.return_value = Mock(returncode=0)

        result = upgrade_mainers.prepare_for_deployment('testing')

        assert result is True

    @patch('upgrade_mainers.run_command')
    def test_prepare_for_deployment_dry_run(self, mock_run):
        """Test preparation in dry run mode."""
        result = upgrade_mainers.prepare_for_deployment('testing', dry_run=True)

        assert result is True
        mock_run.assert_not_called()

    @patch('upgrade_mainers.run_command')
    def test_prepare_for_deployment_failure(self, mock_run):
        """Test preparation failure."""
        mock_run.side_effect = Exception("Script failed")

        result = upgrade_mainers.prepare_for_deployment('testing')

        assert result is False


class TestGetCanisterNameFromAddress:
    """Test the get_canister_name_from_address function."""

    def test_get_canister_name_found(self):
        """Test finding canister name from address."""
        canister_ids_data = {
            'mainer_share_agent_0001': {
                'testing': 'abc123',
                'ic': 'def456'
            },
            'mainer_share_agent_0002': {
                'testing': 'xyz789'
            }
        }

        with patch('builtins.open', mock_open(read_data=json.dumps(canister_ids_data))):
            name = upgrade_mainers.get_canister_name_from_address('abc123', 'testing')

        assert name == 'mainer_share_agent_0001'

    def test_get_canister_name_not_found(self):
        """Test when canister name is not found."""
        canister_ids_data = {
            'mainer_share_agent_0001': {
                'testing': 'abc123'
            }
        }

        with patch('builtins.open', mock_open(read_data=json.dumps(canister_ids_data))):
            name = upgrade_mainers.get_canister_name_from_address('nonexistent', 'testing')

        assert name is None

    def test_get_canister_name_file_error(self):
        """Test when file cannot be read."""
        with patch('builtins.open', side_effect=FileNotFoundError()):
            name = upgrade_mainers.get_canister_name_from_address('abc123', 'testing')

        assert name is None


class TestStatusTracking:
    """Test status tracking functions."""

    def setup_method(self):
        """Reset the status tracker before each test."""
        upgrade_mainers.mainer_status_tracker.clear()

    def test_update_mainer_status(self):
        """Test updating mainer status."""
        upgrade_mainers.update_mainer_status('abc123', upgrade_mainers.MainerStatus.SUCCESS)

        assert 'abc123' in upgrade_mainers.mainer_status_tracker
        assert upgrade_mainers.mainer_status_tracker['abc123']['status'] == upgrade_mainers.MainerStatus.SUCCESS
        assert upgrade_mainers.mainer_status_tracker['abc123']['error'] is None

    def test_update_mainer_status_with_error(self):
        """Test updating mainer status with error message."""
        upgrade_mainers.update_mainer_status('abc123', upgrade_mainers.MainerStatus.FAILED_HEALTH, "Health check failed")

        assert 'abc123' in upgrade_mainers.mainer_status_tracker
        assert upgrade_mainers.mainer_status_tracker['abc123']['status'] == upgrade_mainers.MainerStatus.FAILED_HEALTH
        assert upgrade_mainers.mainer_status_tracker['abc123']['error'] == "Health check failed"

    def test_get_status_summary(self):
        """Test getting status summary."""
        upgrade_mainers.update_mainer_status('abc1', upgrade_mainers.MainerStatus.SUCCESS)
        upgrade_mainers.update_mainer_status('abc2', upgrade_mainers.MainerStatus.SUCCESS)
        upgrade_mainers.update_mainer_status('abc3', upgrade_mainers.MainerStatus.FAILED_HEALTH)

        summary = upgrade_mainers.get_status_summary()

        assert summary['success'] == 2
        assert summary['failed_health'] == 1

    @patch('builtins.open', new_callable=mock_open)
    def test_write_status_to_json(self, mock_file):
        """Test writing status to JSON file."""
        upgrade_mainers.update_mainer_status('abc123', upgrade_mainers.MainerStatus.SUCCESS)
        upgrade_mainers.update_mainer_status('def456', upgrade_mainers.MainerStatus.FAILED_HEALTH, "Health check failed")

        upgrade_mainers.write_status_to_json('test.json')

        mock_file.assert_called_once_with('test.json', 'w')
        handle = mock_file()
        written_data = ''.join(call.args[0] for call in handle.write.call_args_list)
        assert 'abc123' in written_data
        assert 'def456' in written_data
        assert 'success' in written_data
        assert 'failed_health' in written_data

    @patch('builtins.open', new_callable=mock_open)
    def test_write_status_to_markdown(self, mock_file):
        """Test writing status to Markdown file."""
        upgrade_mainers.update_mainer_status('abc123', upgrade_mainers.MainerStatus.SUCCESS)
        upgrade_mainers.update_mainer_status('def456', upgrade_mainers.MainerStatus.FAILED_HEALTH, "Health check failed")

        upgrade_mainers.write_status_to_markdown('test.md')

        mock_file.assert_called_once_with('test.md', 'w')
        handle = mock_file()
        written_data = ''.join(call.args[0] for call in handle.write.call_args_list)
        assert '# mAIner Upgrade Status Report' in written_data
        assert 'abc123' in written_data
        assert 'def456' in written_data
        assert 'SUCCESS' in written_data
        assert 'FAILED_HEALTH' in written_data
        assert 'Health check failed' in written_data

    def test_write_status_empty_tracker(self, capsys):
        """Test writing status when tracker is empty."""
        upgrade_mainers.write_status_to_json()
        upgrade_mainers.write_status_to_markdown()

        captured = capsys.readouterr()
        assert 'No status data' in captured.out


class TestShouldSkipUpgrade:
    """Test the should_skip_upgrade function."""

    @patch('upgrade_mainers.check_health')
    @patch('upgrade_mainers.get_canister_wasm_hash')
    def test_skip_when_hash_matches_and_healthy(self, mock_hash, mock_health):
        """Test skipping when hash matches target and health check passes."""
        mock_hash.return_value = '0xabcdef'
        mock_health.return_value = True

        result = upgrade_mainers.should_skip_upgrade(
            'testing', 'abc123', '0xabcdef', dry_run=False
        )

        assert result is True
        mock_health.assert_called_once_with('testing', 'abc123', False)

    @patch('upgrade_mainers.check_health')
    @patch('upgrade_mainers.get_canister_wasm_hash')
    def test_no_skip_when_hash_matches_but_unhealthy(self, mock_hash, mock_health):
        """Test not skipping when hash matches but health check fails."""
        mock_hash.return_value = '0xabcdef'
        mock_health.return_value = False

        result = upgrade_mainers.should_skip_upgrade(
            'testing', 'abc123', '0xabcdef', dry_run=False
        )

        assert result is False
        mock_health.assert_called_once_with('testing', 'abc123', False)

    @patch('upgrade_mainers.check_health')
    @patch('upgrade_mainers.get_canister_wasm_hash')
    def test_no_skip_when_hash_mismatch(self, mock_hash, mock_health):
        """Test not skipping when hash doesn't match target."""
        mock_hash.return_value = '0xabcdef'
        mock_health.return_value = True

        result = upgrade_mainers.should_skip_upgrade(
            'testing', 'abc123', '0xdifferent', dry_run=False
        )

        assert result is False
        # Health check should not be called when hash doesn't match
        mock_health.assert_not_called()

    @patch('upgrade_mainers.check_health')
    @patch('upgrade_mainers.get_canister_wasm_hash')
    def test_no_skip_when_no_target_hash(self, mock_hash, mock_health):
        """Test not skipping when no target hash is provided."""
        mock_hash.return_value = '0xabcdef'
        mock_health.return_value = True

        result = upgrade_mainers.should_skip_upgrade(
            'testing', 'abc123', None, dry_run=False
        )

        assert result is False
        # Health check should not be called when no target hash
        mock_health.assert_not_called()

    @patch('upgrade_mainers.check_health')
    @patch('upgrade_mainers.get_canister_wasm_hash')
    def test_no_skip_when_current_hash_none(self, mock_hash, mock_health):
        """Test not skipping when current hash cannot be retrieved."""
        mock_hash.return_value = None
        mock_health.return_value = True

        result = upgrade_mainers.should_skip_upgrade(
            'testing', 'abc123', '0xabcdef', dry_run=False
        )

        assert result is False
        # Health check should not be called when hash can't be retrieved
        mock_health.assert_not_called()

    @patch('upgrade_mainers.check_health')
    @patch('upgrade_mainers.get_canister_wasm_hash')
    def test_skip_in_dry_run_mode(self, mock_hash, mock_health):
        """Test skipping in dry run mode when hash matches."""
        mock_hash.return_value = '0xabcdef'
        mock_health.return_value = True

        result = upgrade_mainers.should_skip_upgrade(
            'testing', 'abc123', '0xabcdef', dry_run=True
        )

        assert result is True
        mock_health.assert_called_once_with('testing', 'abc123', True)

    @patch('upgrade_mainers.check_health')
    @patch('upgrade_mainers.get_canister_wasm_hash')
    def test_no_skip_empty_target_hash(self, mock_hash, mock_health):
        """Test not skipping when target hash is empty string."""
        mock_hash.return_value = '0xabcdef'
        mock_health.return_value = True

        result = upgrade_mainers.should_skip_upgrade(
            'testing', 'abc123', '', dry_run=False
        )

        assert result is False
        mock_health.assert_not_called()


class TestUpgradeMainer:
    """Test the upgrade_mainer function."""

    @patch('upgrade_mainers.turn_off_maintenance_flag')
    @patch('upgrade_mainers.start_timer')
    @patch('upgrade_mainers.get_maintenance_flag')
    @patch('upgrade_mainers.check_health')
    @patch('upgrade_mainers.time.sleep')
    @patch('upgrade_mainers.start_canister')
    @patch('upgrade_mainers.upgrade_canister')
    @patch('upgrade_mainers.create_snapshot')
    @patch('upgrade_mainers.stop_canister')
    @patch('upgrade_mainers.check_queue')
    @patch('upgrade_mainers.stop_timer')
    @patch('upgrade_mainers.get_canister_status')
    @patch('upgrade_mainers.get_canister_name_from_address')
    def test_upgrade_mainer_full_success(
        self, mock_get_name, mock_status, mock_stop_timer, mock_check_queue,
        mock_stop_canister, mock_snapshot, mock_upgrade, mock_start, mock_sleep, mock_health,
        mock_get_maintenance, mock_start_timer, mock_maintenance
    ):
        """Test successful full mainer upgrade."""
        mainer = {'address': 'abc123'}
        mock_get_name.return_value = 'mainer_share_agent_0001'
        mock_status.return_value = 'Running'
        mock_stop_timer.return_value = True
        mock_check_queue.return_value = (False, None)
        mock_stop_canister.return_value = True
        mock_snapshot.return_value = 'snap_123'
        mock_upgrade.return_value = True
        mock_start.return_value = True
        mock_health.return_value = True
        mock_get_maintenance.return_value = True
        mock_start_timer.return_value = True
        mock_maintenance.return_value = True

        result = upgrade_mainers.upgrade_mainer('testing', mainer, None)

        assert result is True

    @patch('upgrade_mainers.get_canister_name_from_address')
    def test_upgrade_mainer_no_canister_name(self, mock_get_name):
        """Test upgrade when canister name cannot be found."""
        mainer = {'address': 'abc123'}
        mock_get_name.return_value = None

        result = upgrade_mainers.upgrade_mainer('testing', mainer, None)

        assert result is False

    @patch('upgrade_mainers.start_timer')
    @patch('upgrade_mainers.start_canister')
    @patch('upgrade_mainers.create_snapshot')
    @patch('upgrade_mainers.check_queue')
    @patch('upgrade_mainers.stop_timer')
    @patch('upgrade_mainers.get_canister_status')
    @patch('upgrade_mainers.get_canister_name_from_address')
    def test_upgrade_mainer_stop_timer_fails(
        self, mock_get_name, mock_status, mock_stop_timer,
        mock_check_queue, mock_snapshot, mock_start, mock_start_timer
    ):
        """Test upgrade failure when stop timer fails."""
        mainer = {'address': 'abc123'}
        mock_get_name.return_value = 'mainer_share_agent_0001'
        mock_status.return_value = 'Running'
        mock_stop_timer.return_value = False

        result = upgrade_mainers.upgrade_mainer('testing', mainer, None)

        assert result is False

    @patch('upgrade_mainers.turn_off_maintenance_flag')
    @patch('upgrade_mainers.start_timer')
    @patch('upgrade_mainers.get_maintenance_flag')
    @patch('upgrade_mainers.check_health')
    @patch('upgrade_mainers.time.sleep')
    @patch('upgrade_mainers.start_canister')
    @patch('upgrade_mainers.upgrade_canister')
    @patch('upgrade_mainers.create_snapshot')
    @patch('upgrade_mainers.get_canister_status')
    @patch('upgrade_mainers.get_canister_name_from_address')
    def test_upgrade_mainer_already_stopped(
        self, mock_get_name, mock_status, mock_snapshot, mock_upgrade,
        mock_start, mock_sleep, mock_health, mock_get_maintenance, mock_start_timer, mock_maintenance
    ):
        """Test upgrade when canister is already stopped."""
        mainer = {'address': 'abc123'}
        mock_get_name.return_value = 'mainer_share_agent_0001'
        mock_status.return_value = 'Stopped'
        mock_snapshot.return_value = 'snap_123'
        mock_upgrade.return_value = True
        mock_start.return_value = True
        mock_health.return_value = True
        mock_get_maintenance.return_value = True
        mock_start_timer.return_value = True
        mock_maintenance.return_value = True

        result = upgrade_mainers.upgrade_mainer('testing', mainer, None)

        assert result is True

    @patch('upgrade_mainers.turn_off_maintenance_flag')
    @patch('upgrade_mainers.start_timer')
    @patch('upgrade_mainers.get_maintenance_flag')
    @patch('upgrade_mainers.check_health')
    @patch('upgrade_mainers.start_canister')
    @patch('upgrade_mainers.upgrade_canister')
    @patch('upgrade_mainers.create_snapshot')
    @patch('upgrade_mainers.stop_canister')
    @patch('upgrade_mainers.clear_queue')
    @patch('upgrade_mainers.time.sleep')
    @patch('upgrade_mainers.check_queue')
    @patch('upgrade_mainers.stop_timer')
    @patch('upgrade_mainers.get_canister_status')
    @patch('upgrade_mainers.get_canister_name_from_address')
    def test_upgrade_mainer_queue_wait(
        self, mock_get_name, mock_status, mock_stop_timer, mock_check_queue, mock_sleep, mock_clear_queue,
        mock_stop_canister, mock_snapshot, mock_upgrade, mock_start, mock_health, mock_get_maintenance,
        mock_start_timer, mock_maintenance
    ):
        """Test upgrade waits for queue to age when entries are recent."""
        mainer = {'address': 'abc123'}
        mock_get_name.return_value = 'mainer_share_agent_0001'
        mock_status.return_value = 'Running'
        mock_stop_timer.return_value = True
        mock_clear_queue.return_value = True
        mock_stop_canister.return_value = True
        mock_snapshot.return_value = 'snap_123'
        mock_upgrade.return_value = True
        mock_start.return_value = True
        mock_health.return_value = True
        mock_get_maintenance.return_value = True
        mock_start_timer.return_value = True
        mock_maintenance.return_value = True

        # Queue has entry from 5 minutes ago, then empty after wait
        recent_time = datetime.now() - timedelta(minutes=5)
        mock_check_queue.side_effect = [
            (True, recent_time),
            (False, None)
        ]

        result = upgrade_mainers.upgrade_mainer('testing', mainer, None, dry_run=True)

        # In dry run, should not actually sleep
        assert mock_check_queue.call_count >= 1
        assert result is True


class TestMain:
    """Test the main function."""

    @patch('upgrade_mainers.should_skip_upgrade')
    @patch('upgrade_mainers.get_canister_wasm_hash')
    @patch('upgrade_mainers.upgrade_mainer')
    @patch('upgrade_mainers.get_mainers')
    @patch('upgrade_mainers.prepare_for_deployment')
    @patch('builtins.input')
    @patch('sys.argv', ['upgrade_mainers.py', '--network', 'testing', '--dry-run'])
    def test_main_dry_run(self, mock_input, mock_prepare, mock_get_mainers, mock_upgrade, mock_hash, mock_should_skip):
        """Test main function in dry run mode."""
        mock_input.return_value = ''
        mock_prepare.return_value = True
        mock_get_mainers.return_value = [
            {
                'address': 'abc123',
                'canisterType': {'MainerAgent': {'ShareAgent': {}}},
                'ownedBy': 'user1'
            }
        ]
        mock_upgrade.return_value = True
        mock_hash.return_value = '0xabcdef'
        mock_should_skip.return_value = False

        upgrade_mainers.main()

        assert mock_prepare.called
        assert mock_get_mainers.called
        assert mock_upgrade.called

    @patch('upgrade_mainers.should_skip_upgrade')
    @patch('upgrade_mainers.get_canister_wasm_hash')
    @patch('upgrade_mainers.upgrade_mainer')
    @patch('upgrade_mainers.get_mainers')
    @patch('upgrade_mainers.prepare_for_deployment')
    @patch('builtins.input')
    @patch('sys.argv', ['upgrade_mainers.py', '--network', 'testing', '--num', '1'])
    def test_main_with_limit(self, mock_input, mock_prepare, mock_get_mainers, mock_upgrade, mock_hash, mock_should_skip):
        """Test main function with num limit."""
        mock_input.return_value = 'yes'
        mock_prepare.return_value = True
        mock_get_mainers.return_value = [
            {'address': 'abc1', 'canisterType': {'MainerAgent': {'ShareAgent': {}}}, 'ownedBy': 'user1'},
            {'address': 'abc2', 'canisterType': {'MainerAgent': {'ShareAgent': {}}}, 'ownedBy': 'user1'},
            {'address': 'abc3', 'canisterType': {'MainerAgent': {'ShareAgent': {}}}, 'ownedBy': 'user1'},
        ]
        mock_upgrade.return_value = True
        mock_hash.return_value = '0xabcdef'
        mock_should_skip.return_value = False

        upgrade_mainers.main()

        # Should only upgrade 1 mainer
        assert mock_upgrade.call_count == 1

    @patch('upgrade_mainers.should_skip_upgrade')
    @patch('upgrade_mainers.get_canister_wasm_hash')
    @patch('upgrade_mainers.upgrade_mainer')
    @patch('upgrade_mainers.get_mainers')
    @patch('upgrade_mainers.prepare_for_deployment')
    @patch('builtins.input')
    @patch('sys.argv', ['upgrade_mainers.py', '--network', 'testing', '--mainer', 'abc123'])
    def test_main_specific_mainer(self, mock_input, mock_prepare, mock_get_mainers, mock_upgrade, mock_hash, mock_should_skip):
        """Test main function with specific mainer."""
        mock_input.return_value = 'yes'
        mock_prepare.return_value = True
        mock_get_mainers.return_value = [
            {'address': 'abc123', 'canisterType': {'MainerAgent': {'ShareAgent': {}}}, 'ownedBy': 'user1'},
            {'address': 'def456', 'canisterType': {'MainerAgent': {'ShareAgent': {}}}, 'ownedBy': 'user1'},
        ]
        mock_upgrade.return_value = True
        mock_hash.return_value = '0xabcdef'
        mock_should_skip.return_value = False

        upgrade_mainers.main()

        # Should only upgrade the specific mainer
        assert mock_upgrade.call_count == 1
        call_args = mock_upgrade.call_args[0]
        assert call_args[1]['address'] == 'abc123'

    @patch('upgrade_mainers.should_skip_upgrade')
    @patch('upgrade_mainers.get_canister_wasm_hash')
    @patch('upgrade_mainers.upgrade_mainer')
    @patch('upgrade_mainers.get_mainers')
    @patch('upgrade_mainers.prepare_for_deployment')
    @patch('builtins.input')
    @patch('sys.argv', ['upgrade_mainers.py', '--network', 'testing', '--user', 'user2'])
    def test_main_filter_by_user(self, mock_input, mock_prepare, mock_get_mainers, mock_upgrade, mock_hash, mock_should_skip):
        """Test main function filtering by user."""
        mock_input.return_value = 'yes'
        mock_prepare.return_value = True
        mock_get_mainers.return_value = [
            {'address': 'abc1', 'canisterType': {'MainerAgent': {'ShareAgent': {}}}, 'ownedBy': 'user1'},
            {'address': 'abc2', 'canisterType': {'MainerAgent': {'ShareAgent': {}}}, 'ownedBy': 'user2'},
        ]
        mock_upgrade.return_value = True
        mock_hash.return_value = '0xabcdef'
        mock_should_skip.return_value = False

        upgrade_mainers.main()

        # Should only upgrade user2's mainer
        assert mock_upgrade.call_count == 1
        call_args = mock_upgrade.call_args[0]
        assert call_args[1]['ownedBy'] == 'user2'

    @patch('upgrade_mainers.get_mainers')
    @patch('upgrade_mainers.prepare_for_deployment')
    @patch('builtins.input')
    @patch('sys.argv', ['upgrade_mainers.py', '--network', 'testing'])
    def test_main_user_cancels(self, mock_input, mock_prepare, mock_get_mainers):
        """Test main function when user cancels."""
        mock_input.return_value = 'no'
        mock_prepare.return_value = True

        with pytest.raises(SystemExit) as exc_info:
            upgrade_mainers.main()

        assert exc_info.value.code == 0
        mock_get_mainers.assert_not_called()

    @patch('upgrade_mainers.should_skip_upgrade')
    @patch('upgrade_mainers.get_canister_wasm_hash')
    @patch('upgrade_mainers.upgrade_mainer')
    @patch('upgrade_mainers.get_mainers')
    @patch('upgrade_mainers.prepare_for_deployment')
    @patch('builtins.input')
    @patch('sys.argv', ['upgrade_mainers.py', '--network', 'testing', '--ask-before-upgrade'])
    def test_main_ask_before_upgrade_yes(self, mock_input, mock_prepare, mock_get_mainers, mock_upgrade, mock_hash, mock_should_skip):
        """Test main function with --ask-before-upgrade responding yes."""
        # First input for initial confirmation, second for ask-before-upgrade
        mock_input.side_effect = ['yes', 'y']
        mock_prepare.return_value = True
        mock_get_mainers.return_value = [
            {'address': 'abc123', 'canisterType': {'MainerAgent': {'ShareAgent': {}}}, 'ownedBy': 'user1'},
        ]
        mock_upgrade.return_value = True
        mock_hash.return_value = '0xabcdef'
        mock_should_skip.return_value = False

        upgrade_mainers.main()

        assert mock_upgrade.call_count == 1

    @patch('upgrade_mainers.should_skip_upgrade')
    @patch('upgrade_mainers.get_canister_wasm_hash')
    @patch('upgrade_mainers.upgrade_mainer')
    @patch('upgrade_mainers.get_mainers')
    @patch('upgrade_mainers.prepare_for_deployment')
    @patch('builtins.input')
    @patch('sys.argv', ['upgrade_mainers.py', '--network', 'testing', '--ask-before-upgrade'])
    def test_main_ask_before_upgrade_no(self, mock_input, mock_prepare, mock_get_mainers, mock_upgrade, mock_hash, mock_should_skip):
        """Test main function with --ask-before-upgrade responding no to skip."""
        mock_input.side_effect = ['yes', 'n']
        mock_prepare.return_value = True
        mock_get_mainers.return_value = [
            {'address': 'abc123', 'canisterType': {'MainerAgent': {'ShareAgent': {}}}, 'ownedBy': 'user1'},
        ]
        mock_upgrade.return_value = True
        mock_hash.return_value = '0xabcdef'
        mock_should_skip.return_value = False

        upgrade_mainers.main()

        # Should not upgrade, just skip
        assert mock_upgrade.call_count == 0

    @patch('upgrade_mainers.should_skip_upgrade')
    @patch('upgrade_mainers.get_canister_wasm_hash')
    @patch('upgrade_mainers.upgrade_mainer')
    @patch('upgrade_mainers.get_mainers')
    @patch('upgrade_mainers.prepare_for_deployment')
    @patch('builtins.input')
    @patch('sys.argv', ['upgrade_mainers.py', '--network', 'testing', '--ask-before-upgrade'])
    def test_main_ask_before_upgrade_exit(self, mock_input, mock_prepare, mock_get_mainers, mock_upgrade, mock_hash, mock_should_skip):
        """Test main function with --ask-before-upgrade responding exit."""
        mock_input.side_effect = ['yes', 'exit']
        mock_prepare.return_value = True
        mock_get_mainers.return_value = [
            {'address': 'abc1', 'canisterType': {'MainerAgent': {'ShareAgent': {}}}, 'ownedBy': 'user1'},
            {'address': 'abc2', 'canisterType': {'MainerAgent': {'ShareAgent': {}}}, 'ownedBy': 'user1'},
        ]
        mock_upgrade.return_value = True
        mock_hash.return_value = '0xabcdef'
        mock_should_skip.return_value = False

        upgrade_mainers.main()

        # Should exit after first prompt, not upgrading any
        assert mock_upgrade.call_count == 0

    @patch('upgrade_mainers.should_skip_upgrade')
    @patch('upgrade_mainers.get_canister_wasm_hash')
    @patch('upgrade_mainers.upgrade_mainer')
    @patch('upgrade_mainers.get_mainers')
    @patch('upgrade_mainers.prepare_for_deployment')
    @patch('builtins.input')
    @patch('sys.argv', ['upgrade_mainers.py', '--network', 'testing', '--ask-before-upgrade'])
    def test_main_ask_before_upgrade_default(self, mock_input, mock_prepare, mock_get_mainers, mock_upgrade, mock_hash, mock_should_skip):
        """Test main function with --ask-before-upgrade using default (empty = yes)."""
        mock_input.side_effect = ['yes', '']  # Empty string should default to 'y'
        mock_prepare.return_value = True
        mock_get_mainers.return_value = [
            {'address': 'abc123', 'canisterType': {'MainerAgent': {'ShareAgent': {}}}, 'ownedBy': 'user1'},
        ]
        mock_upgrade.return_value = True
        mock_hash.return_value = '0xabcdef'
        mock_should_skip.return_value = False

        upgrade_mainers.main()

        assert mock_upgrade.call_count == 1

    @patch('upgrade_mainers.get_mainers')
    @patch('upgrade_mainers.prepare_for_deployment')
    @patch('builtins.input')
    @patch('sys.argv', ['upgrade_mainers.py', '--network', 'testing', '--skip-preparation'])
    def test_main_skip_preparation(self, mock_input, mock_prepare, mock_get_mainers):
        """Test main function with skip-preparation flag."""
        mock_input.return_value = 'yes'
        mock_get_mainers.return_value = []

        with pytest.raises(SystemExit) as exc_info:
            upgrade_mainers.main()

        assert exc_info.value.code == 0
        mock_prepare.assert_not_called()

    @patch('upgrade_mainers.should_skip_upgrade')
    @patch('upgrade_mainers.get_canister_wasm_hash')
    @patch('upgrade_mainers.upgrade_mainer')
    @patch('upgrade_mainers.get_mainers')
    @patch('upgrade_mainers.prepare_for_deployment')
    @patch('builtins.input')
    @patch('sys.argv', ['upgrade_mainers.py', '--network', 'testing', '--target-hash', '0xtarget'])
    def test_main_skip_already_upgraded(self, mock_input, mock_prepare, mock_get_mainers, mock_upgrade, mock_hash, mock_should_skip):
        """Test main function skips already upgraded mainers."""
        mock_input.return_value = 'yes'
        mock_prepare.return_value = True
        mock_get_mainers.return_value = [
            {'address': 'abc1', 'canisterType': {'MainerAgent': {'ShareAgent': {}}}, 'ownedBy': 'user1'},
            {'address': 'abc2', 'canisterType': {'MainerAgent': {'ShareAgent': {}}}, 'ownedBy': 'user1'},
        ]
        # First mainer should be skipped (already upgraded and healthy)
        # Second mainer should be upgraded
        mock_should_skip.side_effect = [True, False]
        mock_hash.return_value = '0xnew'
        mock_upgrade.return_value = True

        upgrade_mainers.main()

        # Should only upgrade the second mainer
        assert mock_upgrade.call_count == 1
        assert mock_should_skip.call_count == 2

    @patch('upgrade_mainers.should_skip_upgrade')
    @patch('upgrade_mainers.get_canister_wasm_hash')
    @patch('upgrade_mainers.upgrade_mainer')
    @patch('upgrade_mainers.get_mainers')
    @patch('upgrade_mainers.prepare_for_deployment')
    @patch('builtins.input')
    @patch('sys.exit')
    @patch('sys.argv', ['upgrade_mainers.py', '--network', 'testing'])
    def test_main_upgrade_failure_exits(self, mock_exit, mock_input, mock_prepare, mock_get_mainers, mock_upgrade, mock_hash, mock_should_skip):
        """Test main function exits on upgrade failure."""
        mock_input.return_value = 'yes'
        mock_prepare.return_value = True
        mock_get_mainers.return_value = [
            {'address': 'abc1', 'canisterType': {'MainerAgent': {'ShareAgent': {}}}, 'ownedBy': 'user1'},
        ]
        mock_upgrade.return_value = False
        mock_hash.return_value = '0xhash'
        mock_should_skip.return_value = False

        upgrade_mainers.main()

        mock_exit.assert_called_with(1)


class TestSignalHandler:
    """Test the signal handler."""

    @patch('upgrade_mainers.sys.exit')
    def test_signal_handler(self, mock_exit, capsys):
        """Test signal handler sets interrupted flag and exits."""
        upgrade_mainers.interrupted = False

        upgrade_mainers.signal_handler(signal.SIGINT, None)

        assert upgrade_mainers.interrupted is True
        captured = capsys.readouterr()
        assert "interrupted" in captured.out.lower()
        mock_exit.assert_called_once_with(1)


class TestFilterMainers:
    """Test mainer filtering logic in main."""

    @patch('upgrade_mainers.should_skip_upgrade')
    @patch('upgrade_mainers.get_canister_wasm_hash')
    @patch('upgrade_mainers.upgrade_mainer')
    @patch('upgrade_mainers.get_mainers')
    @patch('upgrade_mainers.prepare_for_deployment')
    @patch('builtins.input')
    @patch('sys.argv', ['upgrade_mainers.py', '--network', 'testing'])
    def test_filter_excludes_non_share_agents(self, mock_input, mock_prepare, mock_get_mainers, mock_upgrade, mock_hash, mock_should_skip):
        """Test that non-ShareAgent mainers are filtered out."""
        # Reset interrupted flag in case previous test set it
        upgrade_mainers.interrupted = False

        mock_input.return_value = 'yes'
        mock_prepare.return_value = True
        mock_get_mainers.return_value = [
            {'address': 'abc1', 'canisterType': {'MainerAgent': {'ShareAgent': {}}}, 'ownedBy': 'user1'},
            {'address': 'abc2', 'canisterType': {'MainerAgent': {'OtherType': {}}}, 'ownedBy': 'user1'},
            {'address': '', 'canisterType': {'MainerAgent': {'ShareAgent': {}}}, 'ownedBy': 'user1'},
        ]
        mock_upgrade.return_value = True
        mock_hash.return_value = '0xhash'
        mock_should_skip.return_value = False

        upgrade_mainers.main()

        # Should only upgrade 1 ShareAgent with valid address
        assert mock_upgrade.call_count == 1

    @patch('upgrade_mainers.get_mainers')
    @patch('upgrade_mainers.prepare_for_deployment')
    @patch('builtins.input')
    @patch('sys.argv', ['upgrade_mainers.py', '--network', 'testing'])
    def test_filter_excludes_empty_address(self, mock_input, mock_prepare, mock_get_mainers):
        """Test that mainers with empty addresses are filtered out."""
        mock_input.return_value = 'yes'
        mock_prepare.return_value = True
        mock_get_mainers.return_value = [
            {'address': '', 'canisterType': {'MainerAgent': {'ShareAgent': {}}}, 'ownedBy': 'user1'},
        ]

        with pytest.raises(SystemExit) as exc_info:
            upgrade_mainers.main()

        # Should exit because no valid mainers found
        assert exc_info.value.code == 0
