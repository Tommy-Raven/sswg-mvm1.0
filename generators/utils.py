import uuid
from datetime import datetime

def generate_workflow_id():
    return f"workflow_{uuid.uuid4().hex[:8]}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

def log(message):
    print(f"[LOG] {message}")