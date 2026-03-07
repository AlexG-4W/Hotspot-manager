import logging
import asyncio

try:
    from winsdk.windows.networking.networkoperators import TetheringOperationalState
    from winsdk.windows.networking.connectivity import NetworkInformation
    try:
        from winsdk.windows.networking.networkoperators import TetheringManager
    except ImportError:
        # For some versions of winsdk, it is named NetworkOperatorTetheringManager
        from winsdk.windows.networking.networkoperators import NetworkOperatorTetheringManager as TetheringManager
except ImportError as e:
    import ctypes
    import sys
    ctypes.windll.user32.MessageBoxW(0, f"winsdk library is required or import error occurred: {e}\nInstall with: pip install winsdk", "Error", 16)
    sys.exit(1)

def get_tethering_manager():
    try:
        profile = NetworkInformation.get_internet_connection_profile()
        if not profile:
            raise Exception("Internet connection profile not found.")
        return TetheringManager.create_from_connection_profile(profile)
    except Exception as e:
        logging.error(f"Error getting manager: {e}")
        return None

def get_hotspot_status():
    try:
        manager = get_tethering_manager()
        if manager:
            state = manager.tethering_operational_state
            return state == TetheringOperationalState.ON
    except Exception as e:
        logging.error(f"Error checking status: {e}")
    return False

async def _set_hotspot_async(enable: bool):
    try:
        manager = get_tethering_manager()
        if manager:
            if enable:
                result = await manager.start_tethering_async()
                logging.info("TURN ON command sent.")
            else:
                result = await manager.stop_tethering_async()
                logging.info("TURN OFF command sent.")
            return True
        else:
            logging.error("Failed to get TetheringManager.")
            return False
    except Exception as e:
        logging.error(f"Error changing hotspot status: {e}")
        return False

def set_hotspot(enable: bool):
    return asyncio.run(_set_hotspot_async(enable))