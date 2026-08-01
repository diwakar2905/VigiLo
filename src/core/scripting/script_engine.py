import ast
import uuid
from dataclasses import dataclass
from typing import Dict, Any, List
from src.core.interfaces.i_service import IService
from src.core.events.event_bus import EventBus, VigiLoEvent
from src.core.exceptions.vigi_exceptions import SecurityException

@dataclass
class AutomationRule:
    rule_id: str
    rule_name: str
    trigger_event_type: str
    action_script: str
    enabled: bool = True

class ScriptEngine(IService):
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self._rules: Dict[str, AutomationRule] = {}
        self._event_sub_id: str = ""
        self._initialized = False

    def initialize(self) -> bool:
        self._event_sub_id = self.event_bus.subscribe("*", self._on_event_published)
        self._initialized = True
        return True

    def shutdown(self) -> None:
        if self._event_sub_id:
            self.event_bus.unsubscribe("*", self._event_sub_id)
        self._rules.clear()
        self._initialized = False

    def register_rule(self, name: str, trigger_event_type: str, action_script: str) -> str:
        self.validate_script_ast(action_script)
        rule_id = f"RULE-{uuid.uuid4().hex[:8].upper()}"
        self._rules[rule_id] = AutomationRule(
            rule_id=rule_id,
            rule_name=name,
            trigger_event_type=trigger_event_type,
            action_script=action_script
        )
        return rule_id

    def validate_script_ast(self, script_code: str) -> None:
        try:
            tree = ast.parse(script_code)
        except SyntaxError as e:
            raise SecurityException(f"Automation script syntax error: {e}")

        # AST Security Inspector: Prohibit Import, Call to eval/exec/open
        forbidden_nodes = (ast.Import, ast.ImportFrom)
        for node in ast.walk(tree):
            if isinstance(node, forbidden_nodes):
                raise SecurityException("Automation Script Security Violation: Imports are strictly prohibited in AST Sandbox.")
            if isinstance(node, ast.Name) and node.id in ["eval", "exec", "open", "__import__", "compile"]:
                raise SecurityException(f"Automation Script Security Violation: Call to restricted function '{node.id}' prohibited.")

    def _on_event_published(self, event: VigiLoEvent) -> None:
        for rule in self._rules.values():
            if rule.enabled and (rule.trigger_event_type in ["*", event.event_type]):
                self.execute_rule(rule, event)

    def execute_rule(self, rule: AutomationRule, event: VigiLoEvent) -> bool:
        safe_globals = {
            "__builtins__": {
                "print": print,
                "len": len,
                "range": range,
                "str": str,
                "int": int,
                "float": float,
                "dict": dict,
                "list": list
            },
            "event": {
                "id": event.event_id,
                "type": event.event_type,
                "timestamp": event.timestamp,
                "data": event.data
            }
        }

        try:
            compiled = compile(rule.action_script, filename=f"<rule_{rule.rule_id}>", mode="exec")
            exec(compiled, safe_globals)
            return True
        except Exception as e:
            print(f"[ERROR] ScriptEngine execution failed for rule '{rule.rule_id}': {e}")
            return False
