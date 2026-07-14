## 🛡️ VigiLo Pull Request Template

### Description
Please provide a brief description of the changes introduced by this pull request and the problems they solve.

### Motivation & Context
Why is this change required? What issue does it resolve? If it fixes an open issue, please link it here (e.g., `Closes #123`).

---

### 🧱 Type of Change
- [ ] 🐛 Bug fix (non-breaking change which fixes an issue)
- [ ] ✨ New feature (non-breaking change which adds functionality)
- [ ] 💥 Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] 🔒 Security hardening / Vulnerability patch
- [ ] 🧹 Refactoring / Tech Debt reduction
- [ ] 📝 Documentation update

---

### 🏗️ Architectural & Security Compliance
- [ ] **Clean Architecture**: Follows VigiLo's directory layout structure (`api/`, `core/`, `modules/`, `security/`, `services/`, `ui/`, `utils/`).
- [ ] **No Plaintext Credentials**: Sensitive tokens/configuration items are protected via DPAPI (`security/crypt.py`) or environment configurations.
- [ ] **No Unsanitized Script Droppers**: Avoids dropping scripts to disk (VBS, Batch); utilizes native API calls/COM interfaces instead.
- [ ] **Path Sanitization**: Direct filesystem references canonicalize paths via `os.path.realpath` and pass boundary safety checks.

---

### 🧪 Verification & Testing
How did you test your changes? Please describe the tests that you ran to verify your changes.

#### Automated Tests
- [ ] Run `python -m unittest discover -s tests` successfully.

#### Manual Verification
Please list details of your local testing setup:
- OS Version:
- Tested Scenarios:
- Captured Logs/Screenshots (if applicable):
