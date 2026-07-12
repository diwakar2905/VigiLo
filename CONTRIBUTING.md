# Contributing to WatchDog

First off, thank you for taking the time to contribute! We welcome contributions that improve WatchDog's reliability, security, maintainability, and user trust.

---

## 🏗️ Architectural Standards

WatchDog adheres to a **Clean Architecture** directory layout. Please place your files in the correct package structures:
*   `api/` - Outbound API request clients (e.g. Telegram client).
*   `config/` - Schema validation and configuration file manager.
*   `core/` - System event monitors, lifecycle coordinators, and installer/uninstaller engines.
*   `modules/` - Executable feature modules (e.g. camera, audio, screenshot, locate).
*   `security/` - Encryption wrappers (DPAPI), privilege validation, and sanitizers.
*   `services/` - Long-running background processes (Telegram poll loop, offline queue).
*   `ui/` - Tkinter frames and UI stylesheet specifications.
*   `utils/` - Global system and network helper utilities.

---

## 🔒 Security Principles
1.  **No Plaintext Credentials**: Never save secrets in plaintext. Use DPAPI (`security/crypt.py`) to encrypt configurations on disk.
2.  **No Script Droppers**: Do not drop script files (VBS, Batch) to disk. Call native COM objects or ctypes Windows APIs directly to reduce AV/EDR false positives.
3.  **Strict Path Sanitization**: Always canonicalize path inputs via `os.path.realpath` and run directory boundary checks (`is_safe_path` in `security/sanitizer.py`) before executing file system actions.

---

## 🛠️ Development & Build Pipeline

1.  **Clone and Install Dependencies**:
    ```bash
    pip install -r requirements.txt pyinstaller
    ```
2.  **Run in Development Mode**:
    *   To test the service background worker:
        ```bash
        python main.py --service
        ```
    *   To test the Telegram polling commander:
        ```bash
        python main.py --commander
        ```
3.  **Re-Compile Executables**:
    Always run the compilation pipeline script to verify that spec files parse and compile without errors:
    ```bash
    python setup/install_startup.py
    ```

---

## 🤝 Code of Conduct
Please review and adhere to our [Code of Conduct](CODE_OF_CONDUCT.md) when interacting with the project.
