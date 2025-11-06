from jsonschema import validate, ValidationError

WORKFLOW_SCHEMA = {
    "type": "object",
    "properties": {
        "workflow_id": {"type": "string"},
        "version": {"type": "string"},
        "metadata": {"type": "object"},
        "phases": {"type": "array"},
        "dependency_graph": {"type": "object"},
    },
    "required": ["workflow_id", "metadata", "phases"]
}

def validate_workflow(wf):
    try:
        validate(instance=wf, schema=WORKFLOW_SCHEMA)
        return True, None
    except ValidationError as e:
        return False, str(e)
