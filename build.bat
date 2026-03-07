@echo off
echo Building Hotspot Manager Executable...

:: Ensure you have pyinstaller installed
:: pip install pyinstaller

:: We need to include hidden imports that PyInstaller might miss.
:: customtkinter requires explicitly importing its theme and base components sometimes, though recent versions are better.
:: pystray can sometimes lose its backend imports.

pyinstaller --noconfirm ^
    --onefile ^
    --windowed ^
    --uac-admin ^
    --icon=app.ico ^
    --name="HotspotManager" ^
    --hidden-import=pystray._win32 ^
    --hidden-import=PIL._tkinter_finder ^
    --hidden-import=customtkinter ^
    --hidden-import=winsdk.windows.networking.networkoperators ^
    src\hotspot_manager.py

echo Build completed! Check the "dist" folder.
pause