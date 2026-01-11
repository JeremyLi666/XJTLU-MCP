from core.memory import AcademicMemory

class AcademicOrchestrator:
    def __init__(self, agents, planner):
        self.agents = agents
        self.planner = planner
        self.memory = AcademicMemory()

    def collect_contexts(self, query: str):
        for agent in self.agents:
            result = agent.run({"query": query})
            self.memory.update(agent.name, result)

    def run_planning(self):
        academic_state = self.memory.snapshot()
        return self.planner.run({
            "academic_state": academic_state
        })

    def run(self, query: str):
        self.collect_contexts(query)
        return self.run_planning()
