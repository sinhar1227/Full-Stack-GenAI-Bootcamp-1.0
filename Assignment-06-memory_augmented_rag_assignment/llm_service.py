import re

from config import (
    OPENAI_MODEL,
    USE_FAKE_MODE,
)


class LLMService:
    """
    Real mode uses OpenAI Responses API.
    Fake mode is only for the included offline self-test.
    """

    def __init__(self):
        self.fake_mode = USE_FAKE_MODE

        if self.fake_mode:
            self.client = None
            return

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ImportError(
                "openai is not installed. "
                "Run: pip install -r requirements.txt"
            ) from exc

        self.client = OpenAI()


    def _fake_generate(self, prompt: str):
        """
        Small deterministic response generator used only
        so the project can be tested without an API key.
        """
        knowledge_match = re.search(
            r"RETRIEVED KNOWLEDGE\n-+\n(.*?)\n\n-+\nCURRENT QUESTION",
            prompt,
            flags=re.S,
        )

        memory_match = re.search(
            r"LONG-TERM USER MEMORY\n-+\n(.*?)\n\n-+\nRELEVANT PAST MEMORIES",
            prompt,
            flags=re.S,
        )

        question_match = re.search(
            r"CURRENT QUESTION\n-+\n(.*?)\n\nAnswer",
            prompt,
            flags=re.S,
        )

        knowledge = (
            knowledge_match.group(1).strip()
            if knowledge_match
            else ""
        )

        long_term = (
            memory_match.group(1).strip()
            if memory_match
            else ""
        )

        question = (
            question_match.group(1).strip().lower()
            if question_match
            else ""
        )

        if "probation" in question and "six months" in knowledge.lower():
            return "The probation period is six months."

        if "leave" in question and "20 paid leaves" in knowledge.lower():
            return "Employees receive 20 paid leaves per year after completing probation."

        if (
            ("prefer" in question or "preference" in question)
            and long_term
            and long_term != "None."
        ):
            return f"Based on your saved memory: {long_term}"

        if question.startswith("remember:"):
            return "Understood. I will save that as a long-term memory."

        return (
            "I can answer using the available memory and retrieved knowledge."
        )


    def generate(
        self,
        prompt: str,
    ):
        if self.fake_mode:
            return self._fake_generate(
                prompt
            )

        response = self.client.responses.create(
            model=OPENAI_MODEL,
            input=prompt,
        )

        return response.output_text.strip()


llm_service = LLMService()
