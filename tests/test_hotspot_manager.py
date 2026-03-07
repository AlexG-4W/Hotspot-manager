import unittest
from unittest.mock import patch, MagicMock
import sys

# Mock UI and external libs
sys.modules['customtkinter'] = MagicMock()
sys.modules['pystray'] = MagicMock()
sys.modules['PIL'] = MagicMock()
sys.modules['PIL.Image'] = MagicMock()
sys.modules['PIL.ImageDraw'] = MagicMock()

import src.hotspot_manager as hotspot_manager

class TestHotspotManager(unittest.TestCase):
    @patch('src.hotspot_manager.api_service')
    @patch('src.hotspot_manager.config_service')
    @patch('src.hotspot_manager.Thread')
    def test_app_initialization_uses_services(self, mock_thread, mock_config, mock_api):
        # Setup mocks
        mock_config.check_autostart.return_value = True
        mock_api.get_hotspot_status.return_value = False
        
        # We need to prevent the app from starting its main loop or threading issues
        
        app = hotspot_manager.HotspotManagerApp()
        
        mock_config.check_autostart.assert_called_once()
        mock_api.get_hotspot_status.assert_called()

if __name__ == '__main__':
    unittest.main()