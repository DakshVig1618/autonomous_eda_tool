import os
import json
import google.genai as genai
from google.genai import types

from app.agents.prompts import SYSTEM_PROMPT, CODE_GENERATION_TEMPLATE


class AIAgentManager:
    """
    Handles orchestration between the application and the Google Gemini API.
    Converts dataset profiles and user configuration into production-ready Python code.
    """

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")

        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is missing. Ensure it is defined in your environment or .env file.")

        self.client = genai.Client(api_key=self.api_key)

    def _clean_response(self, raw_text: str) -> str:
        """
        Strips markdown backticks and language identifiers from the LLM output
        to ensure only raw, executable Python text is returned.
        """
        text = raw_text.strip()

        if text.startswith("```python"):
            text = text[9:]
        elif text.startswith("```"):
            text = text[3:]

        if text.endswith("```"):
            text = text[:-3]

        return text.strip()

    def generate_preprocessing_code(self, data_profile: dict, user_preferences: dict) -> str:
        """
        Sends formatted dataset metadata and user options to Gemini,
        returning the extracted Python script for sandbox execution.
        """
        prompt = CODE_GENERATION_TEMPLATE.format(
            data_profile=json.dumps(data_profile, indent=2),
            user_preferences=json.dumps(user_preferences, indent=2)
        )

        try:
            response = self.client.models.generate_content(
                model='gemini-3.6-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT
                )
            )

            if not response.text:
                raise ValueError("Model returned an empty text response.")

            return self._clean_response(response.text)

        except Exception as e:
            raise RuntimeError(f"Failed to generate transformation script: {str(e)}")