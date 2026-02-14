from collections import defaultdict

class ConversationMemory:
    def __init__(self):
        self.chat_history = defaultdict(list)
        self.facts = defaultdict(dict)

    def add_message(self, session_id, role, content):
        self.chat_history[session_id].append({
            "role": role,
            "content": content
        })

    def get_history(self, session_id):
        return self.chat_history[session_id]

    def store_facts(self, session_id, facts_dict):
        self.facts[session_id].update(facts_dict)

    def get_all_facts(self, session_id):
        return self.facts[session_id]

memory = ConversationMemory()
