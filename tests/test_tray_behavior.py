import pytest
from unittest.mock import MagicMock, patch
import sys

# Mock UI and external libs
sys.modules['customtkinter'] = MagicMock()
sys.modules['pystray'] = MagicMock()
sys.modules['PIL'] = MagicMock()
sys.modules['PIL.Image'] = MagicMock()
sys.modules['PIL.ImageDraw'] = MagicMock()

import src.hotspot_manager as hotspot_manager

@pytest.fixture
def mock_app():
    with patch('src.hotspot_manager.api_service'), patch('src.hotspot_manager.config_service'), patch('src.hotspot_manager.Thread'):
        app = hotspot_manager.HotspotManagerApp()
        return app

def test_window_close_interception(mock_app):
    # Verify that the WM_DELETE_WINDOW protocol is set to hide_window
    mock_app.root.protocol.assert_any_call("WM_DELETE_WINDOW", mock_app.hide_window)

def test_hide_window_withdraws_root(mock_app):
    # Call hide_window explicitly
    mock_app.hide_window()
    # Verify withdraw is called
    mock_app.root.withdraw.assert_called_once()

def test_show_window_deiconifies_root(mock_app):
    # Call show_window explicitly
    mock_app.show_window()
    # Verify after(0, deiconify) is called to restore the window safely in the main thread
    mock_app.root.after.assert_called_with(0, mock_app.root.deiconify)

def test_explicit_exit_button_creation(mock_app):
    # Verify that an exit button is created in the UI
    assert hasattr(mock_app, "exit_btn")

@patch('src.hotspot_manager.sys.exit')
def test_quit_app_terminates_correctly(mock_exit, mock_app):
    mock_app.quit_app()
    # Verify stop event is set
    assert mock_app.stop_event.is_set()
    # Verify root.quit is called
    mock_app.root.quit.assert_called_once()
    # Verify sys.exit is called
    mock_exit.assert_called_once_with(0)
