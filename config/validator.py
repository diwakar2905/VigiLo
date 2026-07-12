# config/validator.py
from config.exceptions import ValidationError

class ValidationIssue:
    def __init__(self, field: str, value, reason: str, severity: str = "CRITICAL", suggested_fix: str = ""):
        self.field = field
        self.value = value
        self.reason = reason
        self.severity = severity
        self.suggested_fix = suggested_fix

    def to_dict(self):
        return {
            "field": self.field,
            "value": str(self.value),
            "reason": self.reason,
            "severity": self.severity,
            "suggested_fix": self.suggested_fix
        }

class ValidationReport:
    def __init__(self):
        self.issues = []

    def add_issue(self, issue: ValidationIssue):
        self.issues.append(issue)

    def is_valid(self) -> bool:
        return not any(issue.severity == "CRITICAL" for issue in self.issues)

    def raise_on_critical(self):
        critical_issues = [issue for issue in self.issues if issue.severity == "CRITICAL"]
        if critical_issues:
            msg = "\n".join(f"- [{issue.field}] Value '{issue.value}' invalid: {issue.reason} (Fix: {issue.suggested_fix})" for issue in critical_issues)
            raise ValidationError(f"Configuration validation failed:\n{msg}")

class ConfigValidator:
    @staticmethod
    def validate(app_config, raise_exception: bool = True) -> ValidationReport:
        """Validates configuration and returns a structured validation report."""
        report = ValidationReport()

        # 1. Validate Telegram Configuration
        if not hasattr(app_config, 'telegram') or app_config.telegram is None:
            report.add_issue(ValidationIssue("telegram", None, "Telegram configuration block is missing."))
        else:
            tg = app_config.telegram
            if not isinstance(tg.bot_token, str):
                report.add_issue(ValidationIssue("telegram.bot_token", type(tg.bot_token), "bot_token must be a string.", suggested_fix="Ensure bot_token is a valid string representation."))
            elif not tg.bot_token.strip():
                report.add_issue(ValidationIssue("telegram.bot_token", tg.bot_token, "bot_token cannot be empty.", suggested_fix="Set your Telegram Bot Token."))
                
            if not isinstance(tg.chat_id, str):
                report.add_issue(ValidationIssue("telegram.chat_id", type(tg.chat_id), "chat_id must be a string.", suggested_fix="Ensure chat_id is a valid string representation."))
            elif not tg.chat_id.strip():
                report.add_issue(ValidationIssue("telegram.chat_id", tg.chat_id, "chat_id cannot be empty.", suggested_fix="Set your Telegram Chat ID."))

        # 2. Validate Security Configuration
        if not hasattr(app_config, 'security') or app_config.security is None:
            report.add_issue(ValidationIssue("security", None, "Security configuration block is missing."))
        else:
            sec = app_config.security
            if not isinstance(sec.failed_attempt_threshold, int) or sec.failed_attempt_threshold < 1:
                report.add_issue(ValidationIssue("security.failed_attempt_threshold", sec.failed_attempt_threshold, "failed_attempt_threshold must be >= 1.", suggested_fix="Set an integer >= 1."))
            if not isinstance(sec.event_id, int) or sec.event_id <= 0:
                report.add_issue(ValidationIssue("security.event_id", sec.event_id, "event_id must be a positive integer.", suggested_fix="Use standard Windows Event IDs, e.g. 4625."))
            if not isinstance(sec.check_interval_seconds, (int, float)) or sec.check_interval_seconds <= 0:
                report.add_issue(ValidationIssue("security.check_interval_seconds", sec.check_interval_seconds, "check_interval_seconds must be a positive float.", suggested_fix="Set a decimal value representing seconds, e.g., 0.1."))

        # 3. Validate Camera Configuration
        if not hasattr(app_config, 'camera') or app_config.camera is None:
            report.add_issue(ValidationIssue("camera", None, "Camera configuration block is missing."))
        else:
            cam = app_config.camera
            if not isinstance(cam.device_index, int) or cam.device_index < 0:
                report.add_issue(ValidationIssue("camera.device_index", cam.device_index, "device_index must be >= 0.", suggested_fix="Set to 0 for primary device or a positive index."))

        if raise_exception:
            report.raise_on_critical()

        return report
