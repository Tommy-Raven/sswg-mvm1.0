from generator.main import generate_workflow
from ai_memory.memory_store import MemoryStore

class Orchestrator:
    def __init__(self):
        self.memory = MemoryStore()

    def run(self, user_config):
        wf = generate_workflow(user_config)
        self.memory.save(wf)
        return wf
