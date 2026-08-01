# VigiLo Release Engineering & Digital Signing Guide

## 1. Authenticode Digital Signing

All production binaries built for release must be signed using Windows SignTool:

```cmd
signtool.exe sign /f "VigiLo_Release_Cert.pfx" /p "SecretPassword" /tr http://timestamp.digicert.com /td sha256 "dist\VigiLo_Production_Installer.exe"
```

---

## 2. Release Verification & Release Manifest

Before publishing a new release version:
1. Run `python scripts/quality_gates.py` to evaluate release probes.
2. Run `python scripts/signing/verify_signature.py` to generate SHA-256 checksums.
3. Update `release_metadata.json` with version metadata and changelog.
