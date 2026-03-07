# Windows Mobile Hotspot Manager

A lightweight, modern desktop utility designed to manage the built-in Mobile Hotspot functionality in Windows 11. 

## Features
- **Modern GUI:** Built with `customtkinter` for a native, responsive look and feel.
- **System Tray Integration:** Runs silently in the background with a dynamic tray icon and a quick-access context menu using `pystray`.
- **Advanced Automation:** Set a shutdown timer or enable the auto-restart feature to periodically reset the hotspot connection and prevent session hangs.
- **Native Integration:** Interacts directly with the Windows Network Operators API (`winsdk`) for reliable network control without opening system settings.
- **Memory Optimized:** Automatically manages memory with explicit garbage collection and resource caching when minimized to the tray.
![scr1](https://github.com/user-attachments/assets/e1fa60e9-b38a-44aa-9406-fedf94d60909)

## Installation

### From Source
1. Ensure you have **Python 3.11** installed.
2. Clone this repository.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   python src/hotspot_manager.py
   ```
   *(Note: The application will prompt for Administrator privileges as they are required to toggle the Windows Mobile Hotspot via the API).*

## Building the Executable

You can easily compile this project into a standalone `.exe` file using PyInstaller.

1. Install PyInstaller (usually included via `requirements.txt` or install via `pip install pyinstaller`).
2. Run the provided build script:
   ```bash
   .\build.bat
   ```
3. The standalone executable will be generated in the `dist/` folder as `HotspotManager.exe`.

For more details on building and avoiding false-positive Windows Defender flags, please refer to [BUILD_README.md](BUILD_README.md).

## Testing
This project uses `pytest` for automated testing.
To run the test suite:
```bash
pytest
```

## Technologies Used
- **Python 3**
- **CustomTkinter** (UI Framework)
- **Pystray & Pillow** (System Tray Integration)
- **WinSDK** (Windows Runtime API)
- **Pytest** (Testing)

- **PyInstaller** (Compilation)

