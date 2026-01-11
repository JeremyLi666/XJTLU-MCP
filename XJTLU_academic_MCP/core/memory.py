class AcademicMemory:
    def __init__(self):
        self.storage = {}

    def update(self, agent_name: str, data: dict):
        self.storage[agent_name] = data

    def snapshot(self) -> dict:
        return self.storage.copy()
