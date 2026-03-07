import unittest
from unittest.mock import patch, MagicMock
import sys
import builtins

import src.config_service as config_service

class TestConfigService(unittest.TestCase):
    @patch('src.config_service.winreg.CloseKey')
    @patch('src.config_service.winreg.OpenKey')
    @patch('src.config_service.winreg.QueryValueEx')
    @patch('src.config_service.sys.argv', ['test_app.exe'])
    def test_check_autostart_true(self, mock_query, mock_open, mock_close):
        mock_query.return_value = ('test_app.exe', None)
        self.assertTrue(config_service.check_autostart())
        
    @patch('src.config_service.winreg.CloseKey')
    @patch('src.config_service.winreg.OpenKey')
    @patch('src.config_service.winreg.QueryValueEx')
    def test_check_autostart_false(self, mock_query, mock_open, mock_close):
        mock_query.side_effect = FileNotFoundError()
        self.assertFalse(config_service.check_autostart())

    @patch('src.config_service.winreg.CloseKey')
    @patch('src.config_service.winreg.OpenKey')
    @patch('src.config_service.winreg.SetValueEx')
    @patch('src.config_service.sys.argv', ['test_app.exe'])
    def test_set_autostart_on(self, mock_set, mock_open, mock_close):
        config_service.set_autostart(True)
        mock_set.assert_called_once_with(mock_open.return_value, config_service.APP_NAME, 0, config_service.winreg.REG_SZ, 'test_app.exe')

    @patch('src.config_service.winreg.CloseKey')
    @patch('src.config_service.winreg.OpenKey')
    @patch('src.config_service.winreg.DeleteValue')
    def test_set_autostart_off(self, mock_delete, mock_open, mock_close):
        config_service.set_autostart(False)
        mock_delete.assert_called_once_with(mock_open.return_value, config_service.APP_NAME)

if __name__ == '__main__':
    unittest.main()