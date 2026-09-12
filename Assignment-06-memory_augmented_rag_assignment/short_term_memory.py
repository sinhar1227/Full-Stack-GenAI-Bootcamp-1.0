from config import MAX_RECENT_MESSAGES


class ShortTermMemory:
    """
    Session-level memory.
    Keeps only the latest N raw messages.
    """

    def __init__(
        self,
        max_messages=MAX_RECENT_MESSAGES,
    ):
        self.max_messages = max_messages
        self.sessions = {}


    def add_message(
        self,
        session_key: str,
        role: str,
        content: str,
    ):
        self.sessions.setdefault(
            session_key,
            []
        )

        self.sessions[
            session_key
        ].append(
            {
                "role": role,
                "content": content,
            }
        )

        self.sessions[
            session_key
        ] = self.sessions[
            session_key
        ][-self.max_messages:]


    def get_messages(
        self,
        session_key: str,
    ):
        return list(
            self.sessions.get(
                session_key,
                []
            )
        )


    def clear(
        self,
        session_key: str,
    ):
        self.sessions.pop(
            session_key,
            None
        )


short_term_memory = ShortTermMemory()
