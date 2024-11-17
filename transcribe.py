from audiobook.transcribe import OpenAIWhisperModel
from dotenv import load_dotenv
import os

load_dotenv()

if __name__ == '__main__':
    api_key = os.getenv("OPENAI_API_KEY")
    model = OpenAIWhisperModel(api_key)
    filepath_from = "data/book/aliceaupays_03_carroll_64kb.mp3"
    filepath_to = "data/book/aliceaupays_03_carroll_64kb.srt"
    model.transcribe_from_file_to_srt(filepath_from, filepath_to)
