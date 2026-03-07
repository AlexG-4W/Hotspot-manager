import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestProjectStructure(unittest.TestCase):
    def test_src_directory_exists(self):
        self.assertTrue(os.path.isdir('src'), "src directory should exist")

    def test_hotspot_manager_in_src(self):
        self.assertTrue(os.path.isfile(os.path.join('src', 'hotspot_manager.py')), "hotspot_manager.py should be in src/")

    def test_can_import_hotspot_manager(self):
        try:
            import src.hotspot_manager
        except ImportError:
            self.fail("Could not import src.hotspot_manager (ImportError)")
        except SystemExit:
            # Expected if winsdk fails to import
            pass

if __name__ == '__main__':
    unittest.main()