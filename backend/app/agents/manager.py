import os
import json
from typing import Optional

import google.genai as genai
from google.genai import types

from app.agents.prompts import SYSTEM_PROMPT, CODE_GENERATION_TEMPLATE


class AIAgentManager:
    """
    Manages communication with the Google Gemini API. Handles prompt construction,
    API calls, and parsing raw model outputs into executable Python scripts.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initializes the Gemini client using an explicitly provided API key
        or falls back to the GEMINI_API_KEY environment variable.
        """
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Gemini API key is missing. Please set GEMINI_API_KEY in your environment or .env file."
            )

        self.client = genai.Client(api_key=self.api_key)

    def _clean_response(self, raw_text: str) -> str:
        """
        Strips markdown code block formatting (e.g., ```python ... ```)
        from the generated response to ensure pure Python code execution.
        """
        text = raw_text.strip()

        if text.startswith("```python"):
            text = text[9:]
        elif text.startswith("```"):
            text = text[3:]

        if text.endswith("```"):
            text = text[:-3]

        return text.strip()

    def generate_preprocessing_code(
            self, data_profile: dict, user_preferences: dict
    ) -> str:
        """
        Injects the dataset metadata and user options into the prompt template,
        sends the request to Gemini, and returns sanitized executable Python code.
        """
        prompt = CODE_GENERATION_TEMPLATE.format(
            data_profile=json.dumps(data_profile, indent=2),
            user_preferences=json.dumps(user_preferences, indent=2)
        )

        try:
            response = self.client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT
                )
            )
            return self._clean_response(response.text)
        except Exception as e:
            raise RuntimeError(
                f"Failed to generate preprocessing code via Gemini API: {str(e)}"
            ) from e