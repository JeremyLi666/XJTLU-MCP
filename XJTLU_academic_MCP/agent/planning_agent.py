from core.agent_base import AcademicAgent

class PlanningAgent(AcademicAgent):
    def __init__(self):
        super().__init__("PlanningAgent")

    def _check_eligibility(self, grades, rules):
        eligible = []
        for course, reqs in rules.items():
            ok = True
            for prereq, min_grade in reqs.items():
                if grades.get(prereq, 0) < min_grade:
                    ok = False
            if ok:
                eligible.append(course)
        return eligible

    def _estimate_workload(self, courses):
        weights = {"ECO401": 4, "FIN308": 5}
        return sum(weights.get(c, 3) for c in courses)

    def handle(self, task: dict) -> dict:
        academic_state = task.get("academic_state", {})
        grades = academic_state.get("EBridgeAgent", {}).get("grades", {})
        rules = academic_state.get("EBridgeAgent", {}).get("enrollment_rules", {})

        eligible = self._check_eligibility(grades, rules)
        workload = self._estimate_workload(eligible)

        return {
            "recommended_courses": eligible,
            "workload_score": workload,
            "risk_level": "High" if workload > 8 else "Moderate"
        }
