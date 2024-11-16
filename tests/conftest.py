from pathlib import Path

import pytest


@pytest.fixture
def path_subtitles_file():
    current_directory = Path(__file__).parent
    path_to_input_file = current_directory / "data" / "premiere-partie.srt"
    return path_to_input_file
