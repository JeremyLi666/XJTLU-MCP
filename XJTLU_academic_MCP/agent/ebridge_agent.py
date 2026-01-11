from core.agent_base import AcademicAgent

class EBridgeAgent(AcademicAgent):
    def __init__(self):
        super().__init__("EBridgeAgent")

    def _load_grades(self):
        return {
            "ECO201": 72,
            "ECO309": 68,
            "STA200": 81
        }

    def _load_rules(self):
        return {
            "ECO401": {"ECO309": 65},
            "FIN308": {"ECO201": 70}
        }

    def handle(self, task: dict) -> dict:
        return {
            "grades": self._load_grades(),
            "enrollment_rules": self._load_rules()
        }
