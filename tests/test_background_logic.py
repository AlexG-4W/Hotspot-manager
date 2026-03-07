import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import sys

# Mock UI and external libs
sys.modules['customtkinter'] = MagicMock()
sys.modules['pystray'] = MagicMock()
sys.modules['PIL'] = MagicMock()
sys.modules['PIL.Image'] = MagicMock()
sys.modules['PIL.ImageDraw'] = MagicMock()

import src.hotspot_manager as hotspot_manager

class TestBackgroundLogic(unittest.TestCase):
    def setUp(self):
        self.patcher_api = patch('src.hotspot_manager.api_service')
        self.patcher_config = patch('src.hotspot_manager.config_service')
        self.patcher_thread = patch('src.hotspot_manager.Thread')
        
        self.mock_api = self.patcher_api.start()
        self.mock_config = self.patcher_config.start()
        self.mock_thread = self.patcher_thread.start()
        
        self.mock_config.check_autostart.return_value = False
        self.mock_api.get_hotspot_status.return_value = True
        
        self.app = hotspot_manager.HotspotManagerApp()

    def tearDown(self):
        self.patcher_api.stop()
        self.patcher_config.stop()
        self.patcher_thread.stop()

    def test_timer_trigger_turns_off_hotspot(self):
        # Setup timer in the past
        self.app.target_off_time = datetime.now() - timedelta(minutes=1)
        self.app.timer_minutes = MagicMock()
        self.app.restart_minutes = MagicMock()
        self.app.restart_minutes.get.return_value = 0
        self.app.root = MagicMock()
        
        # Hotspot is ON
        self.mock_api.get_hotspot_status.return_value = True
        
        self.app._background_tick()
        
        self.mock_api.set_hotspot.assert_called_with(False)
        self.assertIsNone(self.app.target_off_time)
        self.app.timer_minutes.set.assert_called_with(0)

    @patch('src.hotspot_manager.HotspotManagerApp.restart_hotspot')
    def test_hourly_restart_triggers(self, mock_restart):
        self.app.last_restart_time = datetime.now() - timedelta(hours=1, minutes=1)
        self.app.restart_minutes = MagicMock()
        self.app.restart_minutes.get.return_value = 60
        self.app.root = MagicMock()
        
        # Hotspot is ON
        self.mock_api.get_hotspot_status.return_value = True
        
        self.app._background_tick()
        
        mock_restart.assert_called_once()

    @patch('src.hotspot_manager.HotspotManagerApp.restart_hotspot')
    def test_hourly_restart_skipped_if_off(self, mock_restart):
        self.app.last_restart_time = datetime.now() - timedelta(hours=1, minutes=1)
        self.app.restart_minutes = MagicMock()
        self.app.restart_minutes.get.return_value = 0
        self.app.root = MagicMock()
        
        # Hotspot is ON
        self.mock_api.get_hotspot_status.return_value = True
        
        self.app._background_tick()
        
        mock_restart.assert_not_called()

if __name__ == '__main__':
    unittest.main()