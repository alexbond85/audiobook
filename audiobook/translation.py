from string import Formatter
from typing import Any
from typing import Dict

import openai


class TranslationConfig:
    """Handles translation-specific configuration and template formatting."""

    def __init__(self, config_dict: Dict[str, Any]):
        """
        Initialize translation configuration.

        Args:
            config_dict: Dictionary containing translation configuration
        """
        self.config = config_dict
        self.formatter = Formatter()

    def format_prompt(self, prompt_template: str, **kwargs) -> str:
        """
        Format a prompt template with given parameters.

        Args:
            prompt_template: The template string to format
            **kwargs: Keywords arguments to use in formatting

        Returns:
            Formatted prompt string
        """
        # Get default values from config
        default_values = {
            "source_language": self.config["source_language"],
            "target_language": self.config["target_language"],
        }

        # Combine default values with provided kwargs
        format_values = {**default_values, **kwargs}

        return prompt_template.format(**format_values)

    def system_prompt(self) -> str:
        """Get formatted system prompt."""
        return self.format_prompt(self.config["prompts"]["system"])

    def user_prompt(self, text: str) -> str:
        """Get formatted user prompt."""
        return self.format_prompt(self.config["prompts"]["user"], text=text)


class OpenAITranslator:
    """Handles translation services using OpenAI API."""

    def __init__(self, config: dict, api_key: str):
        """
        Initialize translator with configuration.

        Args:
            config: Application configuration instance
        """
        self.openai_settings = config["openai"]
        self.client = openai.OpenAI(api_key=api_key)
        self.translation_config = TranslationConfig(config["translation"])

    def translate(self, phrase_text: str) -> str:
        """
        Translate phrase using configured languages and prompts.

        Args:
            phrase_text: Text to translate

        Returns:
            Translated text with explanations
        """
        if not self.client.api_key:
            return "OpenAI API key not set. Please set your API key."

        try:
            response = self.client.chat.completions.create(
                model=self.openai_settings["model"],
                messages=[
                    {
                        "role": "system",
                        "content": self.translation_config.system_prompt(),
                    },
                    {
                        "role": "user",
                        "content": self.translation_config.user_prompt(
                            phrase_text
                        ),
                    },
                ],
                max_tokens=self.openai_settings["max_tokens"],
                temperature=self.openai_settings["temperature"],
            )
            content = response.choices[0].message.content
            if not content:
                return "No translation provided."
            return content
        except Exception as e:
            return f"Error in translation: {e}"

    def from_to_languages(self) -> tuple:
        """Get configured source and target languages."""
        config = self.translation_config.config
        return config["source_language"], config["target_language"]
