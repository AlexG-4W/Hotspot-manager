import unittest
from unittest.mock import patch, MagicMock
import sys
import asyncio
import logging
import importlib

# Use the centralized winsdk mock
from tests.mock_winsdk import patch_winsdk
patch_winsdk()

import src.api_service as api_service

class TestApiService(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Force reload to ensure it uses the sys.modules mocks above
        # even if it was already imported by another test file
        importlib.reload(api_service)

    @patch('src.api_service.NetworkInformation')
    @patch('src.api_service.TetheringManager')
    def test_get_tethering_manager_success(self, mock_tethering_mgr, mock_net_info):
        mock_profile = MagicMock()
        mock_net_info.get_internet_connection_profile.return_value = mock_profile
        mock_tethering_mgr.create_from_connection_profile.return_value = "Manager"
        
        manager = api_service.get_tethering_manager()
        
        self.assertEqual(manager, "Manager")
        mock_tethering_mgr.create_from_connection_profile.assert_called_once_with(mock_profile)

    @patch('src.api_service.get_tethering_manager')
    def test_get_hotspot_status_on(self, mock_get_manager):
        mock_manager = MagicMock()
        mock_manager.tethering_operational_state = api_service.TetheringOperationalState.ON
        mock_get_manager.return_value = mock_manager
        
        self.assertTrue(api_service.get_hotspot_status())

    @patch('src.api_service.get_tethering_manager')
    def test_get_hotspot_status_off(self, mock_get_manager):
        mock_manager = MagicMock()
        mock_manager.tethering_operational_state = api_service.TetheringOperationalState.OFF
        mock_get_manager.return_value = mock_manager
        
        self.assertFalse(api_service.get_hotspot_status())

if __name__ == '__main__':
    unittest.main()