from contextlib import nullcontext as does_not_raise
from typing import ContextManager

import pytest

from audiobook.subtitles import Subtitle
from audiobook.subtitles import Subtitles
from audiobook.subtitles import SubtitlesParser


@pytest.fixture
def valid_srt_text():
    return """1
00:00:01,000 --> 00:00:04,000
Hello World!

2
00:00:05,000 --> 00:00:08,000
This is a test subtitle.
Second line of subtitle.

3
00:01:15,500 --> 00:01:20,750
Multi-line subtitle
with three
different lines.
"""


@pytest.fixture
def invalid_srt_text():
    return """1
00:00:01,000 --> 00:00:04,000
Hello World!

Invalid Entry

3
00:01:15,500 --> invalid_timestamp
This should be skipped.

4
00:01:20,000 --> 00:01:15,000
Invalid time range (end before start).
"""


@pytest.fixture
def sample_subtitles():
    return [
        Subtitle(
            index=1, start_time=5.0, end_time=8.0, text="Second subtitle"
        ),  # Intentionally out of order
        Subtitle(index=2, start_time=1.0, end_time=4.0, text="First subtitle"),
        Subtitle(
            index=3, start_time=10.0, end_time=13.0, text="Third subtitle"
        ),
    ]


class TestSubtitle:
    @pytest.mark.parametrize(
        "index,start_time,end_time,text,expectation",
        [
            (1, 0.0, 1.0, "Valid", does_not_raise()),
            (-1, 0.0, 1.0, "Invalid index", pytest.raises(ValueError)),
            (1, 2.0, 1.0, "Invalid time range", pytest.raises(ValueError)),
            (1, -1.0, 1.0, "Negative start time", pytest.raises(ValueError)),
            (1, 0.0, -1.0, "Negative end time", pytest.raises(ValueError)),
        ],
    )
    def test_subtitle_validation(
        self,
        index: int,
        start_time: float,
        end_time: float,
        text: str,
        expectation: ContextManager,
    ):
        with expectation:
            Subtitle(
                index=index,
                start_time=start_time,
                end_time=end_time,
                text=text,
            )


class TestSubtitles:
    def test_init_sorts_subtitles(self, sample_subtitles):
        subtitles = Subtitles(sample_subtitles)
        assert subtitles.current_index == 0
        assert subtitles.length() == 3
        # Check if subtitles are sorted by start_time
        assert subtitles.subtitles_list[0].start_time == 1.0
        assert subtitles.subtitles_list[1].start_time == 5.0
        assert subtitles.subtitles_list[2].start_time == 10.0

    def test_navigation(self, sample_subtitles):
        subtitles = Subtitles(sample_subtitles)

        # Test initial state
        assert subtitles.current_subtitle().start_time == 1.0

        # Test next()
        subtitles.next()
        assert subtitles.current_subtitle().start_time == 5.0

        # Test next() at end
        subtitles.next()
        subtitles.next()  # Try to go past the end
        assert subtitles.current_index == 2  # Should not move past the end

        # Test previous()
        subtitles.previous()
        assert subtitles.current_subtitle().start_time == 5.0

        # Test previous() at start
        subtitles.previous()
        subtitles.previous()  # Try to go past the start
        assert subtitles.current_index == 0  # Should not move past the start

    def test_set_to(self, sample_subtitles):
        subtitles = Subtitles(sample_subtitles)

        # Test valid index
        subtitles.set_to(1)
        assert subtitles.current_index == 1

        # Test invalid indices
        with pytest.raises(IndexError):
            subtitles.set_to(-1)
        with pytest.raises(IndexError):
            subtitles.set_to(len(sample_subtitles))

    def test_find_subtitle_at_time(self, sample_subtitles):
        subtitles = Subtitles(sample_subtitles)

        # Test finding subtitles at various times
        assert subtitles.find_subtitle_at_time(2.0) == 0  # First subtitle
        assert subtitles.find_subtitle_at_time(6.0) == 1  # Second subtitle
        assert subtitles.find_subtitle_at_time(11.0) == 2  # Third subtitle
        assert (
            subtitles.find_subtitle_at_time(0.0) == -1
        )  # Before first subtitle
        assert subtitles.find_subtitle_at_time(9.0) == -1  # Between subtitles
        assert (
            subtitles.find_subtitle_at_time(14.0) == -1
        )  # After last subtitle

    def test_seek_to_time(self, sample_subtitles):
        subtitles = Subtitles(sample_subtitles)

        # Test seeking to various times
        subtitles.seek_to_time(6.0)  # Should find second subtitle
        assert subtitles.current_subtitle().start_time == 5.0

        subtitles.seek_to_time(2.0)  # Should find first subtitle
        assert subtitles.current_subtitle().start_time == 1.0

        subtitles.seek_to_time(
            9.0
        )  # Time between subtitles, should stay at current position
        assert subtitles.current_subtitle().start_time == 1.0
