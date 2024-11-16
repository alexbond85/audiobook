from io import BytesIO
from typing import Dict
from typing import Optional

from pydub import AudioSegment  # type: ignore

from .subtitles import Subtitle


class AudioManager:
    """Handles audio processing and caching for subtitle-aligned
    audio chunks."""

    def __init__(self, audio_path: str):
        """
        Initialize audio manager.

        Args:
            audio_path: Path to the audio file
        """
        self.audio_path = audio_path
        self.audio_chunks: Dict[int, bytes] = {}
        self._audio: Optional[AudioSegment] = None

    @property
    def audio(self) -> AudioSegment:
        """Lazy load the audio file."""
        if self._audio is None:
            self._audio = AudioSegment.from_mp3(self.audio_path)
        return self._audio

    def get_chunk(self, subtitle: Subtitle) -> Optional[bytes]:
        """
        Get audio chunk for the given subtitle.

        Args:
            subtitle: Subtitle object containing timing information

        Returns:
            Audio chunk as bytes, or None if processing fails
        """
        try:
            # Check cache first
            if subtitle.index in self.audio_chunks:
                return self.audio_chunks[subtitle.index]

            # Extract chunk using timing information
            start_ms = int(subtitle.start_time * 1000)
            end_ms = int(subtitle.end_time * 1000)
            chunk = self.audio[start_ms:end_ms]

            # Convert to bytes
            audio_buffer = BytesIO()
            chunk.export(audio_buffer, format="mp3")
            audio_bytes = audio_buffer.getvalue()

            # Cache the chunk
            self.audio_chunks[subtitle.index] = audio_bytes

            return audio_bytes

        except Exception as e:
            print(f"Error processing audio chunk: {e}")
            return None

    def clear_cache(self):
        """Clear the audio chunks cache."""
        self.audio_chunks.clear()

    def preload_chunks(self, subtitles: list[Subtitle]):
        """
        Preload audio chunks for a list of subtitles.

        Args:
            subtitles: List of subtitles to preload audio for
        """
        for subtitle in subtitles:
            if subtitle.index not in self.audio_chunks:
                self.get_chunk(subtitle)
