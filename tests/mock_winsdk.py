import sys
from unittest.mock import MagicMock

def patch_winsdk():
    """
    Patches sys.modules with a mock of the winsdk library.
    This ensures that tests run in a predictable environment without
    actually calling Windows APIs.
    """
    mock_winsdk = MagicMock()
    
    # Mock specific enums and classes
    class MockTetheringOperationalState:
        UNKNOWN = 0
        ON = 1
        OFF = 2
        IN_TRANSITION = 3

    class MockNetworkOperatorTetheringManager:
        @classmethod
        def create_from_connection_profile(cls, profile):
            manager = MagicMock()
            manager.tethering_operational_state = MockTetheringOperationalState.OFF
            return manager

    class MockNetworkInformation:
        @classmethod
        def get_internet_connection_profile(cls):
            return MagicMock()

    # Create the mocked module structure
    network_operators = MagicMock()
    network_operators.TetheringOperationalState = MockTetheringOperationalState
    network_operators.NetworkOperatorTetheringManager = MockNetworkOperatorTetheringManager
    network_operators.TetheringManager = MockNetworkOperatorTetheringManager

    connectivity = MagicMock()
    connectivity.NetworkInformation = MockNetworkInformation

    mock_winsdk.windows.networking.networkoperators = network_operators
    mock_winsdk.windows.networking.connectivity = connectivity

    # Patch sys.modules
    sys.modules['winsdk'] = mock_winsdk
    sys.modules['winsdk.windows'] = mock_winsdk.windows
    sys.modules['winsdk.windows.networking'] = mock_winsdk.windows.networking
    sys.modules['winsdk.windows.networking.networkoperators'] = network_operators
    sys.modules['winsdk.windows.networking.connectivity'] = connectivity

    return mock_winsdk
