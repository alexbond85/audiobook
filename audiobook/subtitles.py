from dataclasses import dataclass
from typing import List


@dataclass
class Subtitle:
    """
    Represents a single subtitle entry with its index, start time,
    end time, and text.

    Attributes
    ----------
    index : int
        The index of the subtitle entry.
    start_time : float
        The start time of the subtitle in seconds.
    end_time : float
        The end time of the subtitle in seconds.
    text : str
        The subtitle text.
    """

    index: int
    start_time: float
    end_time: float
    text: str

    def __post_init__(self):
        """Validate subtitle attributes after initialization."""
        if self.index < 0:
            raise ValueError("Index cannot be negative")
        if self.start_time < 0 or self.end_time < 0:
            raise ValueError("Timestamps cannot be negative")
        if self.start_time > self.end_time:
            raise ValueError("Start time cannot be greater than end time")


class Subtitles:
    """
    A container class for managing a list of subtitles with
    navigation capabilities.

    Attributes
    ----------
    subtitles_list : list[Subtitle]
        List of Subtitle objects.
    current_index : int
        Current position in the subtitles list.
    """

    def __init__(self, subtitles_list: List[Subtitle]):
        """
        Initialize the Subtitles container.

        Parameters
        ----------
        subtitles_list : list[Subtitle]
            List of Subtitle objects to manage.
        """
        self.subtitles_list = sorted(
            subtitles_list, key=lambda x: x.start_time
        )
        self.current_index = 0

    def length(self) -> int:
        """Return the number of subtitles."""
        return len(self.subtitles_list)

    def next(self) -> None:
        """Move to the next subtitle if not at the end."""
        if self.current_index < len(self.subtitles_list) - 1:
            self.current_index += 1

    def previous(self) -> None:
        """Move to the previous subtitle if not at the beginning."""
        if self.current_index > 0:
            self.current_index -= 1

    def set_to(self, index: int) -> None:
        """
        Set the current index to the given value.

        Parameters
        ----------
        index : int
            The index to set as the current index.

        Raises
        ------
        IndexError
            If the index is out of bounds.
        """
        if not self.subtitles_list:
            raise IndexError("No subtitles available")
        if index < 0 or index >= len(self.subtitles_list):
            raise IndexError("Index out of bounds")
        self.current_index = index

    def current_subtitle(self) -> Subtitle:
        """
        Get the current subtitle.

        Returns
        -------
        Subtitle
            The current subtitle object.

        Raises
        ------
        IndexError
            If the subtitles list is empty.
        """
        if not self.subtitles_list:
            raise IndexError("No subtitles available")
        return self.subtitles_list[self.current_index]

    def find_subtitle_at_time(self, time: float) -> int:
        """
        Find the subtitle that should be displayed at the given time.

        Parameters
        ----------
        time : float
            The time in seconds to find a subtitle for.

        Returns
        -------
        int
            The index of the subtitle that should be displayed at
            the given time, or -1 if no subtitle should be displayed.
        """
        for i, subtitle in enumerate(self.subtitles_list):
            if subtitle.start_time <= time <= subtitle.end_time:
                return i
        return -1

    def seek_to_time(self, time: float) -> None:
        """
        Set the current subtitle to the one that should be
        displayed at the given time.

        Parameters
        ----------
        time : float
            The time in seconds to seek to.
        """
        index = self.find_subtitle_at_time(time)
        if index != -1:
            self.set_to(index)

    def __len__(self):
        return len(self.subtitles_list)


class SubtitlesParser:
    """
    Parses SRT (SubRip Subtitle) text into a list of Subtitle objects.

    Methods
    -------
    value() -> List[Subtitle]
        Parses the SRT text and returns a list of Subtitle objects.
    from_file(path: str) -> Subtitles
        Creates a Subtitles instance from an SRT file.
    """

    def __init__(self, srt_text: str):
        """
        Initialize with raw SRT content as a string.

        Parameters
        ----------
        srt_text : str
            The raw content of an SRT file as a string.

        Raises
        ------
        ValueError
            If srt_text is empty or None.
        """
        if not srt_text:
            raise ValueError("SRT text cannot be empty")
        self.srt_text = srt_text

    def value(self) -> List[Subtitle]:
        """
        Parse the SRT text into a list of Subtitle objects.

        Returns
        -------
        List[Subtitle]
            A list of Subtitle objects parsed from the SRT text.
        """
        subtitles = []
        entries = self.srt_text.strip().split("\n\n")

        for entry in entries:
            lines = entry.strip().split("\n")
            if len(lines) >= 3:  # Minimum 3 lines: index, timestamp, and text
                try:
                    # Parse subtitle index
                    index = int(lines[0])

                    # Parse timestamp line
                    start_str, end_str = lines[1].split(" --> ")

                    # Combine all remaining lines as text (handles
                    # multi-line subtitles)
                    text = "\n".join(lines[2:])

                    # Convert timestamps to seconds
                    start_time = self._time_to_seconds(start_str)
                    end_time = self._time_to_seconds(end_str)

                    subtitles.append(
                        Subtitle(
                            index=index,
                            start_time=start_time,
                            end_time=end_time,
                            text=text,
                        )
                    )
                except Exception as e:
                    print(f"Error parsing entry:\n{entry}\nError: {e}")
                    continue
        return subtitles

    @staticmethod
    def _time_to_seconds(time_str: str) -> float:
        """
        Convert a time string in HH:MM:SS,ms format to seconds.

        Parameters
        ----------
        time_str : str
            The time string in HH:MM:SS,ms format.

        Returns
        -------
        float
            The time in seconds as a float.

        Raises
        ------
        ValueError
            If the time string format is invalid.
        """
        try:
            hours, minutes, seconds_milliseconds = time_str.strip().split(":")
            seconds, milliseconds = seconds_milliseconds.split(",")
            return (
                int(hours) * 3600
                + int(minutes) * 60
                + int(seconds)
                + int(milliseconds) / 1000.0
            )
        except ValueError as e:
            raise ValueError(
                f"Invalid time format. Expected HH:MM:SS,ms "
                f"but got: {time_str}"
            ) from e

    @classmethod
    def from_file(cls, path: str) -> "Subtitles":
        """
        Create a Subtitles instance from a file.

        Parameters
        ----------
        path : str
            The file path to the SRT file.

        Returns
        -------
        Subtitles
            A Subtitles instance initialized with the content of the SRT file.

        Raises
        ------
        FileNotFoundError
            If the specified file does not exist.
        UnicodeDecodeError
            If the file encoding is not UTF-8.
        """
        try:
            with open(path, "r", encoding="utf-8") as file:
                srt_text = file.read()
            parser = cls(srt_text)
            return Subtitles(parser.value())
        except FileNotFoundError:
            raise FileNotFoundError(f"SRT file not found: {path}")
