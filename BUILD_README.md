# Build Instructions and Release Notes

## Compiling the Project into an Executable (.exe)

This project uses `PyInstaller` to bundle the Python scripts and dependencies into a single, standalone Windows executable.

### Prerequisites
1. Ensure Python 3.11 is installed.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   *(Note: Ensure PyInstaller is also installed, usually via `pip install pyinstaller`)*

### Build Command
We have provided a batch script (`build.bat`) to automate the build process with the correct flags. 
To build the project, simply double-click `build.bat` or run it from the command line:

```cmd
.\build.bat
```

**Key PyInstaller Flags Used:**
- `--onefile`: Packages everything into a single `.exe` file.
- `--windowed` (or `--noconsole`): Hides the console window when running the GUI application.
- `--uac-admin`: Requests Administrator privileges upon launch (required for modifying Windows Hotspot settings).
- `--icon=app.ico`: Sets the application icon.
- `--hidden-import=...`: Explicitly includes libraries that PyInstaller might miss during static analysis (like `pystray._win32`, `winsdk`, `customtkinter`).

### Locating the Executable
Once the build script completes, the final executable will be located in the newly created `dist/` directory as `HotspotManager.exe`.

---

## Windows Defender Mitigations

When distributing standalone Python executables built with PyInstaller, it is common for Windows Defender or other antivirus software to falsely flag the `.exe` as a trojan or malware (often detected as "Win32/Wacatac" or "Trojan:Python/..."). This happens because the PyInstaller bootloader unpacks files into a temporary directory at runtime, a behavior that mimics some malicious payloads.

### Recommendations for Distribution and Users

**If you are the Developer:**
1.  **Code Signing (Best Solution):** Purchase a legitimate Code Signing Certificate (EV or Standard) and sign your compiled `.exe`. This builds trust with Microsoft SmartScreen and drastically reduces false positives.
2.  **Submit for Analysis:** Submit the false positive `.exe` directly to Microsoft via their [security intelligence portal](https://www.microsoft.com/en-us/wdsi/filesubmission). They usually analyze and whitelist clean PyInstaller files within 24-48 hours.
3.  **Build in a Clean Environment:** Ensure the environment where you run PyInstaller is completely clean of any actual malware. Compiling inside a fresh Virtual Machine or a CI/CD pipeline (like GitHub Actions) can sometimes produce slightly different file hashes that avoid certain heuristic signatures.

**If you are the User (Workarounds):**
If Windows Defender blocks `HotspotManager.exe` immediately after building or downloading:
1.  **Add an Exclusion:** 
    - Open Windows Security -> Virus & threat protection -> Manage settings.
    - Scroll down to **Exclusions** and click "Add or remove exclusions".
    - Add the specific folder where the `.exe` is located, or add the `HotspotManager.exe` file directly.
2.  **Unblock via Protection History:**
    - Open Windows Security -> Virus & threat protection -> Protection history.
    - Find the blocked threat, click on it, select "Actions" and choose "Allow on device".