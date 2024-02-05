class ChatHistory:
    def __init__(self, capacity):
        self.capacity = capacity
        self.messages = []

    def tail(self):
        if self.messages:
            return self.messages[-1]
        else:
            return None

    def put(self, message):
        if len(self.messages) >= self.capacity:
            self.messages.pop(0)
        self.messages.append(message)

    def get_all(self):
        return self.messages

    def string(self):
        return ' '.join(self.messages)

