from core.agent_base import AcademicAgent

class LearningMallAgent(AcademicAgent):
    def __init__(self):
        super().__init__("LearningMallAgent")

    def _load_courses(self):
        return ["ECO201", "ECO309", "STA200"]

    def _load_materials(self, course):
        return [
            f"{course} Lecture Slides",
            f"{course} Assignment Brief"
        ]

    def handle(self, task: dict) -> dict:
        courses = self._load_courses()
        materials = {c: self._load_materials(c) for c in courses}

        return {
            "courses": courses,
            "materials": materials
        }
