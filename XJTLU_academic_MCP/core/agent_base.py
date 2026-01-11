from typing import Dict, Any
from datetime import datetime

class AcademicAgent:
    def __init__(self, name: str):
        self.name = name
        self.state: Dict[str, Any] = {}
        self.last_updated: datetime | None = None

    def validate_task(self, task: Dict[str, Any]) -> bool:
        if not isinstance(task, dict):
            return False
        return True

    def preprocess(self, task: Dict[str, Any]) -> Dict[str, Any]:
        task["timestamp"] = datetime.utcnow().isoformat()
        return task

    def handle(self, task: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    def postprocess(self, result: Dict[str, Any]) -> Dict[str, Any]:
        self.last_updated = datetime.utcnow()
        self.state.update(result)
        return result

    def run(self, task: Dict[str, Any]) -> Dict[str, Any]:
        if not self.validate_task(task):
            return {"error": f"Invalid task for {self.name}"}
        task = self.preprocess(task)
        result = self.handle(task)
        return self.postprocess(result)
