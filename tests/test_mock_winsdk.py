import unittest
import sys
from tests.mock_winsdk import patch_winsdk

class TestMockWinsdk(unittest.TestCase):
    def setUp(self):
        self.mock_winsdk = patch_winsdk()
        
    def test_mock_winsdk_in_sys_modules(self):
        self.assertIn('winsdk', sys.modules)
        self.assertIn('winsdk.windows.networking.networkoperators', sys.modules)
        
    def test_mock_tethering_manager(self):
        from winsdk.windows.networking.networkoperators import TetheringManager, TetheringOperationalState
        from winsdk.windows.networking.connectivity import NetworkInformation
        
        profile = NetworkInformation.get_internet_connection_profile()
        self.assertIsNotNone(profile)
        
        manager = TetheringManager.create_from_connection_profile(profile)
        self.assertIsNotNone(manager)
        self.assertEqual(manager.tethering_operational_state, TetheringOperationalState.OFF)

if __name__ == '__main__':
    unittest.main()