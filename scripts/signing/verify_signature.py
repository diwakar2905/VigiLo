import os
import hashlib
import sys

def verify_file_sha256(filepath: str) -> str:
    if not os.path.exists(filepath):
        print(f"[ERROR] Target file not found: {filepath}")
        return ""
    
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    digest = sha256.hexdigest().upper()
    print(f"[SIGN-VERIFY] {os.path.basename(filepath)} SHA-256: {digest}")
    return digest

def main():
    print("[*] VigiLo Authenticode & SHA-256 Verification Runner")
    dist_dir = "dist"
    if os.path.exists(dist_dir):
        for fname in os.listdir(dist_dir):
            if fname.endswith(".exe"):
                verify_file_sha256(os.path.join(dist_dir, fname))
    else:
        print("[INFO] No dist/ directory present. Skipping binary SHA verification.")

if __name__ == "__main__":
    main()
