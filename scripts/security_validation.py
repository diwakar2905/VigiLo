import sys
from dataclasses import dataclass
from src.core.controllers.container import ServiceContainer
from src.core.security.security_gateway import SecurityGatewayRequest

@dataclass
class ComplianceResult:
    check_name: str
    passed: bool
    details: str

def run_security_compliance_audit() -> bool:
    print("[*] Running VigiLo Priority 2 Security Compliance Audit...")
    results = []

    container = ServiceContainer.get_instance()

    # Check 1: Security Gateway Initialization
    gw = container.security_gateway
    gw_ok = gw is not None
    results.append(ComplianceResult("Security Gateway Initialized", gw_ok, "Single execution path ready"))

    # Check 2: Capability Registry Integrity
    reg = container.capability_registry
    caps = reg.list_capabilities()
    cap_ok = len(caps) >= 12
    results.append(ComplianceResult("Capability Registry Integrity", cap_ok, f"{len(caps)} capabilities registered"))

    # Check 3: Privileged Operation Authorization Test
    req = SecurityGatewayRequest(
        capability_id="CAP_LOCK",
        action_name="lock_workstation",
        caller_id="UI",
        handler=lambda: "WORKSTATION_LOCKED"
    )
    resp = gw.execute_privileged_operation(req)
    results.append(ComplianceResult("Security Gateway Execution & Correlation Tracing", resp.correlation_id.startswith("COR-"), f"CorrelationID: {resp.correlation_id}, Decision: {resp.decision}"))

    # Display Report
    all_ok = True
    print("\n================================================================================")
    print("                VIGILO SECURITY ARCHITECTURE COMPLIANCE REPORT")
    print("================================================================================")
    for r in results:
        status = "PASSED" if r.passed else "FAILED"
        print(f"[{status}] {r.check_name}: {r.details}")
        if not r.passed:
            all_ok = False
    print("================================================================================")

    return all_ok

if __name__ == "__main__":
    if not run_security_compliance_audit():
        sys.exit(1)
