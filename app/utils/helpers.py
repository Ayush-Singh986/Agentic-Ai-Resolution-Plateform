import uuid


def generate_incident_id():

    return str(uuid.uuid4())


def format_context(context):

    if isinstance(context, list):
        return "\n".join(context)

    return str(context)