import openai  # type: ignore


class OpenAIWhisperModel:
    """
    Whisper model implementation for transcribing audio files via OpenAI API.

    Attributes
    ----------
    client : openai.OpenAI
        OpenAI client for accessing Whisper API.

    Methods
    -------
    transcribe_from_file_to_srt(file_path_from: str, file_path_to: str) -> Dict[str, str]
        Transcribes an audio file using OpenAI's Whisper API.
    """

    def __init__(self, api_key: str):
        """
        Initializes the OpenAIWhisperModel by creating an OpenAI API client.
        """
        self.client = openai.OpenAI(api_key=api_key)

    def transcribe_from_file_to_srt(
        self, filepath_from: str, filepath_to: str
    ) -> None:
        """
        Transcribes an audio file using OpenAI's Whisper API.

        Parameters
        ----------
        filepath_from : str
            Path to the audio file.
        filepath_to : str
            Path to save transcription.
        """
        with open(filepath_from, "rb") as audio_file:
            transcription = self.client.audio.transcriptions.create(
                model="whisper-1", file=audio_file, response_format="srt"
            )
        with open(filepath_to, "w") as f:
            f.write(transcription)
