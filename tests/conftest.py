import os

from pathlib import Path

import pytest

from audiobook.subtitles import Subtitle
from audiobook.subtitles import SubtitlesParser


@pytest.fixture
def test_data_dir():
    """Fixture providing the path to test data directory."""
    current_directory = Path(__file__).parent
    return current_directory


@pytest.fixture
def audio_file_path(test_data_dir):
    """Fixture providing the path to test audio file."""
    return test_data_dir / "data" / "book" / "premiere-partie.mp3"


@pytest.fixture
def srt_file_path(test_data_dir):
    """Fixture providing the path to test SRT file."""
    return test_data_dir / "data" / "book" / "premiere-partie.srt"


@pytest.fixture
def subtitles(srt_file_path):
    """Fixture providing parsed subtitles from the test file."""
    return SubtitlesParser.from_file(str(srt_file_path))


@pytest.fixture
def sample_subtitle():
    """Fixture providing a sample subtitle."""
    return Subtitle(
        index=1, start_time=0.0, end_time=2.0, text="Sample subtitle text"
    )


@pytest.fixture
def translation_config():
    """Fixture providing complete translation configuration."""
    return {
        "openai": {"model": "gpt-4", "max_tokens": 1250, "temperature": 0.5},
        "translation": {
            "source_language": "French",
            "target_language": "German",
            "prompts": {
                "system": "You are a helpful assistant that translates {source_language} to {target_language} and explains words that might be unfamiliar to a {target_language} learner. You speak only {source_language} and {target_language}.",
                "user": 'Translate the following {source_language} phrase into {target_language}, and then list the words that a {target_language} learner might not know, providing short translations for each, don\'t translate all words, only difficult ones.\n\nPhrase: "{text}"',
            },
        },
    }


@pytest.fixture
def openai_api_key():
    """Fixture providing OpenAI API key from environment."""
    from dotenv import load_dotenv

    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OpenAI API key not set")
    return api_key
