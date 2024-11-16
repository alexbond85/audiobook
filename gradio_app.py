import gradio as gr
from io import BytesIO
from pydub import AudioSegment
import os
import openai
from dotenv import load_dotenv
from audiobook.subtitles import SubtitlesParser, Subtitles

# Load API key from .env file
load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')

# Initialize OpenAI client
client = openai.OpenAI(api_key=openai_api_key)

# Read subtitles from the file
chapter = 'audio_files/premiere-partie'
srt_file_path = chapter + '.srt'
audio_file_path = chapter + '.mp3'

# Load subtitles using our SubtitlesParser class
subtitles = SubtitlesParser.from_file(srt_file_path)

# Global dictionary to store audio chunks for future use
audio_chunks = {}


def get_audio_chunk_and_phrase(index: int):
    """Get the audio chunk and subtitle text for a given index."""
    if index < 1 or index > len(subtitles):
        print(f"Invalid index: {index}")
        return "", None

    try:
        # Set the current subtitle
        subtitles.set_to(index - 1)  # Convert 1-based index to 0-based
        current_sub = subtitles.current_subtitle()

        # Check if audio chunk is already in cache
        if index in audio_chunks:
            audio_bytes = audio_chunks[index]
        else:
            # Load the audio file if needed
            audio = AudioSegment.from_mp3(audio_file_path)

            # Extract the chunk (convert times to milliseconds)
            start_time = int(current_sub.start_time * 1000)
            end_time = int(current_sub.end_time * 1000)
            chunk = audio[start_time:end_time]

            # Export to raw bytes
            audio_buffer = BytesIO()
            chunk.export(audio_buffer, format='mp3')
            audio_bytes = audio_buffer.getvalue()

            # Store audio_bytes for future use
            audio_chunks[index] = audio_bytes

        return f"Phrase {index}: **{current_sub.text}**", audio_bytes

    except Exception as e:
        print(f"Error processing audio chunk: {e}")
        return f"Phrase {index}: **{current_sub.text}**", None


def increment_index(current_index: int) -> int:
    """Increment the current index within bounds."""
    new_index = int(current_index) + 1
    return min(new_index, len(subtitles))


def decrement_index(current_index: int) -> int:
    """Decrement the current index within bounds."""
    new_index = int(current_index) - 1
    return max(new_index, 1)


def translate_phrase(phrase_text: str) -> str:
    """Translate the current phrase using OpenAI API."""
    if not client.api_key:
        return "OpenAI API key not set. Please set your API key."

    messages = [
        {"role": "system",
         "content": "You are a helpful assistant that translates French to Russian and explains words that might be unfamiliar to a Russian learner. You speak only russian and french."},
        {"role": "user", "content": f"""Translate the following French phrase into Russian, and then list the words that a Russian learner might not know, providing short translations for each, don't translate all words, only difficult ones. for example: Se promener - Гулять.

Phrase: "{phrase_text}"."""}
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            max_tokens=1250,
            temperature=0.5,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error in translation: {e}"


def update_phrase_and_audio(index: int):
    """Update the display with new phrase and audio."""
    text, audio_bytes = get_audio_chunk_and_phrase(index)
    return text, audio_bytes, index, index, ""  # Reset translation when phrase changes


def create_interface():
    """Create and configure the Gradio interface with compact layout."""
    with gr.Blocks(css="""
        .container {
            max-width: 800px !important;
            margin: auto !important;
            padding: 20px !important;
        }
        #phrase_display {
            font-size: 24px;
            margin: 20px 0;
            text-align: center;
        }
        #translation_display {
            margin-top: 20px;
            padding: 15px;
            background: #f5f5f5;
            border-radius: 8px;
        }
        .navigation-buttons {
            display: flex;
            justify-content: center;
            gap: 10px;
            margin: 10px 0;
        }
    """) as demo:
        with gr.Column(elem_classes="container"):
            gr.Markdown("# Phrase Navigator")

            # Phrase display
            phrase_display = gr.Markdown("", elem_id="phrase_display")

            # Navigation buttons in a centered row
            with gr.Row(elem_classes="navigation-buttons"):
                prev_button = gr.Button("Previous", size="lg")
                next_button = gr.Button("Next", size="lg")

            # Slider
            phrase_slider = gr.Slider(
                1,
                len(subtitles),
                value=1,
                step=1,
                label="Select Phrase",
                interactive=True
            )

            # Audio player
            audio_output = gr.Audio(
                label="Audio Playback",
                elem_id="audio_output",
                format='mp3',
                autoplay=True
            )

            # Translation section
            translate_button = gr.Button("Translate", size="lg")
            translation_display = gr.Markdown("", elem_id="translation_display")

            # State management
            phrase_index = gr.State(value=1)

        # (Component connections remain the same)
        outputs = [phrase_display, audio_output, phrase_index, phrase_slider, translation_display]

        phrase_slider.change(update_phrase_and_audio, inputs=phrase_slider, outputs=outputs)

        prev_button.click(
            fn=lambda idx: update_phrase_and_audio(decrement_index(idx)),
            inputs=phrase_index,
            outputs=outputs
        )
        next_button.click(
            fn=lambda idx: update_phrase_and_audio(increment_index(idx)),
            inputs=phrase_index,
            outputs=outputs
        )

        translate_button.click(
            fn=lambda text: translate_phrase(text),
            inputs=phrase_display,
            outputs=translation_display
        )

    return demo


if __name__ == "__main__":
    demo = create_interface()
    demo.launch(server_name="0.0.0.0", server_port=7860)