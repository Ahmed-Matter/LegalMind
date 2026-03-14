conversation_memory = {}


def add_message(session_id, role, text):

    if session_id not in conversation_memory:
        conversation_memory[session_id] = []

    conversation_memory[session_id].append({
        "role": role,
        "text": text
    })

    # keep last 6 messages only
    conversation_memory[session_id] = conversation_memory[session_id][-6:]


def get_memory(session_id):

    return conversation_memory.get(session_id, [])