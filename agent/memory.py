class ConversationMemory:

    def __init__(
        self,
        max_messages=10
    ):

        self.max_messages = (
            max_messages
        )

        self.messages = []

    def add_user_message(
        self,
        content
    ):

        self.messages.append({
            "role": "user",
            "content": content
        })

        self._trim()

    def add_assistant_message(
        self,
        content
    ):

        self.messages.append({
            "role": "assistant",
            "content": content
        })

        self._trim()

    def get_messages(self):

        return list(
            self.messages
        )

    def clear(self):

        self.messages = []

    def _trim(self):

        if len(self.messages) > (
            self.max_messages
        ):

            self.messages = (
                self.messages[
                    -self.max_messages:
                ]
            )