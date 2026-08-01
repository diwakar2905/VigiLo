import sys
import subprocess
from dataclasses import dataclass

@dataclass
class QualityGateResult:
    probe_name: str
    passed: bool
    details: str

def run_quality_gates() -> bool:
    print("[*] Running VigiLo Production Quality Gates...")
    gates = []

    # Gate 1: Test Suite execution
    try:
        res = subprocess.run(["python", "-m", "pytest", "tests/"], capture_output=True, text=True)
        passed = res.returncode == 0
        gates.append(QualityGateResult("Automated PyTest Suite", passed, "All tests passed" if passed else res.stderr))
    except Exception as e:
        gates.append(QualityGateResult("Automated PyTest Suite", False, str(e)))

    # Display Quality Gate Report
    all_ok = True
    print("\n================================================================================")
    print("                    VIGILO RELEASE QUALITY GATE REPORT")
    print("================================================================================")
    for g in gates:
        status = "PASSED" if g.passed else "FAILED"
        print(f"[{status}] {g.probe_name}: {g.details}")
        if not g.passed:
            all_ok = False
    print("================================================================================")

    return all_ok

if __name__ == "__main__":
    if not run_quality_gates():
        sys.exit(1)
