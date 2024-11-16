import pytest


def test_translation_config_initialization(translation_config):
    """Test TranslationConfig initialization."""
    from audiobook.translation import TranslationConfig

    config = TranslationConfig(translation_config["translation"])
    assert config.config["source_language"] == "French"
    assert config.config["target_language"] == "German"


def test_prompt_formatting(translation_config):
    """Test prompt formatting with different inputs."""
    from audiobook.translation import TranslationConfig

    config = TranslationConfig(translation_config["translation"])

    # Test system prompt
    system_prompt = config.system_prompt()
    assert "French" in system_prompt
    assert "German" in system_prompt

    # Test user prompt with sample text
    test_text = "Bonjour le monde"
    user_prompt = config.user_prompt(test_text)
    assert test_text in user_prompt
    assert "French" in user_prompt
    assert "German" in user_prompt


def test_format_prompt_with_additional_params(translation_config):
    """Test format_prompt with additional parameters."""
    from audiobook.translation import TranslationConfig

    config = TranslationConfig(translation_config["translation"])

    custom_template = (
        "Translate from {source_language} to {target_language}, style: {style}"
    )
    formatted = config.format_prompt(custom_template, style="formal")

    assert "French" in formatted
    assert "German" in formatted
    assert "formal" in formatted


def test_openai_translator_initialization(translation_config, openai_api_key):
    """Test OpenAITranslator initialization."""
    from audiobook.translation import OpenAITranslator

    translator = OpenAITranslator(translation_config, openai_api_key)

    assert translator.openai_settings == translation_config["openai"]
    assert translator.client.api_key == openai_api_key

    source, target = translator.from_to_languages()
    assert source == "French"
    assert target == "German"


@pytest.mark.skip(reason="This test requires a valid OpenAI API key.")
def test_translation_with_real_api(translation_config, openai_api_key):
    """Test actual translation using OpenAI API."""
    from audiobook.translation import OpenAITranslator

    translator = OpenAITranslator(translation_config, openai_api_key)
    result = translator.translate("Bonjour le monde")

    assert result is not None
    assert isinstance(result, str)
    assert len(result) > 0
    assert "Welt" in result  # "Welt" is "world" in German


def test_translation_error_handling(translation_config):
    """Test translation error handling with invalid API key."""
    from audiobook.translation import OpenAITranslator

    translator = OpenAITranslator(translation_config, "invalid_key")
    result = translator.translate("Test text")

    assert "Error" in result


def test_complex_prompt_formatting(translation_config):
    """Test formatting of complex prompts with multiple placeholders."""
    from audiobook.translation import TranslationConfig

    config = TranslationConfig(translation_config["translation"])

    complex_template = """
    From: {source_language}
    To: {target_language}
    Text: {text}
    Style: {style}
    Formality: {formality}
    """

    formatted = config.format_prompt(
        complex_template,
        text="Sample text",
        style="casual",
        formality="informal",
    )

    assert "French" in formatted
    assert "German" in formatted
    assert "Sample text" in formatted
    assert "casual" in formatted
    assert "informal" in formatted


def test_translation_config_languages_access(translation_config):
    """Test direct access to language configuration."""
    from audiobook.translation import TranslationConfig

    config = TranslationConfig(translation_config["translation"])
    assert config.config["source_language"] == "French"
    assert config.config["target_language"] == "German"


def test_prompt_templates_existence(translation_config):
    """Test that all required prompt templates exist."""
    from audiobook.translation import TranslationConfig

    config = TranslationConfig(translation_config["translation"])
    assert "system" in config.config["prompts"]
    assert "user" in config.config["prompts"]
