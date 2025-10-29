import subprocess
"""
pytest-based test suite for core.managers.recon_manager.ReconManager

Test Coverage:
- Unit tests for _run_subfinder: success, CalledProcessError, FileNotFoundError, TimeoutExpired
- Unit/integration tests for run: success, no subdomains, state_manager interaction, UI messages
- All external dependencies (subprocess, ui, state_manager) are mocked
- OPSEC enforcement (Proxychains4/Whonix) is NOT present in the code, so not tested (limitation)
- Assumes 'ui' is imported in recon_manager.py and is patchable
- Assumes ReconManager is imported from core.managers.recon_manager
- Assumes subfinder output is newline-separated subdomains

Limitations:
- No OPSEC enforcement logic to test
- Only subfinder runner is present; add more runners as code evolves
- Does not test actual subprocess or file system

"""
import pytest
from unittest.mock import patch, MagicMock, call
from core.managers.recon_manager import ReconManager

# --- Fixtures ---
@pytest.fixture
def mock_state_manager():
    return MagicMock()

@pytest.fixture
def recon_manager(mock_state_manager):
    return ReconManager(state_manager=mock_state_manager)

# --- _run_subfinder tests ---
def test_run_subfinder_success(recon_manager):
    fake_output = 'a.example.com\nb.example.com\n'
    with patch('core.managers.recon_manager.subprocess.run') as mock_run, \
         patch('core.managers.recon_manager.ui') as mock_ui:
        mock_run.return_value = MagicMock(stdout=fake_output, stderr='', returncode=0)
        result = recon_manager._run_subfinder('example.com')
        assert result == ['a.example.com', 'b.example.com']
        mock_ui.print_info.assert_called_once()
        mock_run.assert_called_once()


def test_run_subfinder_calledprocesserror(recon_manager):
    with patch('core.managers.recon_manager.subprocess.run') as mock_run, \
         patch('core.managers.recon_manager.ui') as mock_ui:
        mock_run.side_effect = subprocess.CalledProcessError(1, 'subfinder', stderr='fail!')
        result = recon_manager._run_subfinder('example.com')
        assert result == []
        mock_ui.print_error.assert_called_once()
        assert 'fail!' in mock_ui.print_error.call_args[0][0]


def test_run_subfinder_filenotfounderror(recon_manager):
    with patch('core.managers.recon_manager.subprocess.run') as mock_run, \
         patch('core.managers.recon_manager.ui') as mock_ui:
        mock_run.side_effect = FileNotFoundError('not found')
        result = recon_manager._run_subfinder('example.com')
        assert result == []
        mock_ui.print_error.assert_called_once()
        assert 'not found' in mock_ui.print_error.call_args[0][0]


def test_run_subfinder_timeoutexpired(recon_manager):
    with patch('core.managers.recon_manager.subprocess.run') as mock_run, \
         patch('core.managers.recon_manager.ui') as mock_ui:
        mock_run.side_effect = subprocess.TimeoutExpired('subfinder', 60)
        result = recon_manager._run_subfinder('example.com')
        assert result == []
        mock_ui.print_warning.assert_called_once()
        assert 'timed out' in mock_ui.print_warning.call_args[0][0].lower()

# --- run() tests ---
def test_run_success(recon_manager, mock_state_manager):
    subdomains = ['a.example.com', 'b.example.com']
    with patch.object(recon_manager, '_run_subfinder', return_value=subdomains) as mock_runner, \
         patch('core.managers.recon_manager.ui') as mock_ui:
        result = recon_manager.run(42, 'example.com')
        assert result == {'target': 'example.com', 'subdomains': subdomains}
        mock_runner.assert_called_once_with('example.com')
        mock_state_manager.add_assets.assert_called_once_with(42, subdomains)
        mock_ui.print_success.assert_called_once()


def test_run_no_subdomains(recon_manager, mock_state_manager):
    with patch.object(recon_manager, '_run_subfinder', return_value=[]) as mock_runner, \
         patch('core.managers.recon_manager.ui') as mock_ui:
        result = recon_manager.run(42, 'example.com')
        assert result == {'target': 'example.com', 'subdomains': []}
        mock_runner.assert_called_once_with('example.com')
        mock_state_manager.add_assets.assert_not_called()
        mock_ui.print_success.assert_not_called()

# --- Documentation of test cases ---
"""
Test Cases:
1. _run_subfinder returns parsed subdomains on success, prints info
2. _run_subfinder handles CalledProcessError, prints error, returns []
3. _run_subfinder handles FileNotFoundError, prints error, returns []
4. _run_subfinder handles TimeoutExpired, prints warning, returns []
5. run() aggregates subdomains, calls add_assets, prints success
6. run() with no subdomains skips add_assets and print_success

Assumptions:
- ui is patchable and imported in recon_manager.py
- Only subfinder runner is present
- No OPSEC enforcement logic to test
- All subprocess and state_manager interactions are mocked

Limitations:
- No real subprocess or file system calls
- No OPSEC/Proxychains/Whonix enforcement in code
- Add more runners as code evolves
"""
