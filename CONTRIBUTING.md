# Contributing to VigiLo

Thank you for your interest in contributing to **VigiLo — Privacy-First Windows Device Recovery Platform**!

VigiLo is committed to building a trusted, commercial-grade open-source security platform. To maintain high code quality, security standards, and platform reliability, please follow these guidelines.

---

## 📜 Core Architectural Principles

All contributions must adhere strictly to VigiLo's core design rules:

1. **Privacy-First & Local-First**: No third-party cloud data transmission, external tracking servers, or telemetry analytics.
2. **Layered Architecture (C-S-R-M)**:
   - `Controller` -> `Service` -> `Repository` -> `Model` -> `UI`.
   - Direct cross-layer imports or circular imports are strictly prohibited.
3. **Service Interface Protocol**: Every new business service must implement `IService` (`initialize()`, `shutdown()`).
4. **Deterministic Device State Gating**: Features must be registered and evaluated against `FeaturePermissionMatrix`.

---

## 🛠️ Development Setup

### 1. Prerequisites
- **Windows 10/11**
- **Python 3.10+**
- **Git**

### 2. Fork and Clone
```bash
git clone https://github.com/YOUR-USERNAME/VigiLo.git
cd VigiLo
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
pip install pytest pytest-cov
```

### 4. Running the Desktop Dashboard
```bash
python -m src.ui.dashboard_app
```

---

## 🧪 Testing & Verification

Every pull request requires automated test coverage:

```bash
# Run all unit and integration tests
python -m pytest tests/
```

- Target coverage: **>= 95%** for new core services.
- Ensure zero breaking changes for existing Win32 background service loops.

---

## 📬 Pull Request Process

1. **Create a Feature Branch**:
   ```bash
   git checkout -b feature/amazing-new-feature
   ```
2. **Commit Your Changes**: Follow conventional commit messages (`feat:`, `fix:`, `docs:`, `test:`).
3. **Run Code Formatting & Linters**: Ensure code is cleanly typed and documented.
4. **Push & Open a Pull Request**: Provide a detailed description of changes, architectural impact, and manual verification steps.

---

## 🔒 Security Vulnerability Reporting

Please **DO NOT** publicly disclose security vulnerabilities on GitHub Issues.
Report security vulnerabilities privately via email to the security team or open a confidential GitHub Security Advisory.

---

## 📄 License
By contributing to VigiLo, you agree that your contributions will be licensed under the project's [MIT License](file:///c:/Users/diwak/Downloads/WatchDog-61675e7fe6254baf87bd0b158efba4b9e6192b34/WatchDog-61675e7fe6254baf87bd0b158efba4b9e6192b34/LICENSE).
