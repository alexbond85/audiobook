# audiobook/app.py
import os
from pathlib import Path

import gradio as gr
import yaml
from dotenv import load_dotenv

from audiobook.audio import AudioManager
from audiobook.subtitles import SubtitlesParser
from audiobook.translation import OpenAITranslator


def load_yaml_config(config_path: str = "config.yaml") -> dict:
    """Return configuration from YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def initialize_core_services(config: dict) -> tuple:
    """Return essential services for audiobook playback and translation."""
    data_dir = Path(config['paths']['data_dir'])
    chapter = config['paths']['chapter']

    srt_path = data_dir / f"{chapter}.srt"
    audio_path = data_dir / f"{chapter}.mp3"

    load_dotenv()
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if not openai_api_key:
        raise ValueError("OpenAI API key not set in environment")

    subtitles = SubtitlesParser.from_file(str(srt_path))
    audio_manager = AudioManager(str(audio_path))
    translator = OpenAITranslator(config, openai_api_key)

    return subtitles, audio_manager, translator


def extract_phrase_content(index: int, subtitles, audio_manager) -> tuple[str, bytes]:
    """Return formatted subtitle text and corresponding audio segment."""
    if index < 1 or index > len(subtitles):
        raise ValueError(f"Invalid index: {index}")

    subtitles.set_to(index - 1)  # Convert 1-based index to 0-based
    current_sub = subtitles.current_subtitle()

    audio_bytes = audio_manager.get_chunk(current_sub)
    if not audio_bytes:
        raise RuntimeError("Failed to extract audio segment")

    return f"**{current_sub.text}**", audio_bytes


def render_player_state(index: int, subtitles, audio_manager, max_index: int) -> tuple:
    """Return updated interface state for the given index."""
    # Ensure index is within bounds
    bounded_index = max(1, min(index, max_index))
    text, audio = extract_phrase_content(bounded_index, subtitles, audio_manager)
    return text, audio, bounded_index, bounded_index, ""


def build_player_interface(config: dict, subtitles, audio_manager, translator) -> gr.Blocks:
    """Return configured Gradio interface for audiobook playback."""
    initial_text, initial_audio = extract_phrase_content(1, subtitles, audio_manager)
    max_index = len(subtitles)

    with gr.Blocks(css=CSS) as demo:
        with gr.Column(elem_classes="player"):
            # Book header - only if title or cover is provided
            if config['paths'].get('book_title') or config['paths'].get('book_cover'):
                if config['paths'].get('book_title'):
                    gr.Markdown(
                        f"# {config['paths']['book_title']}",
                        elem_classes="book-title"
                    )
                if config['paths'].get('book_cover'):
                        gr.Image(
                            config['paths']['book_cover'],
                            show_label=False,
                            elem_classes="book-cover",
                            show_download_button=False,
                            show_fullscreen_button=False,
                            render=True
                        )


            # Rest of the interface remains the same...
            phrase_display = gr.Markdown(initial_text, elem_id="phrase_display")
            audio_output = gr.Audio(
                value=initial_audio,
                format='mp3',
                autoplay=True,
                elem_classes="audio-player"
            )
            phrase_slider = gr.Slider(
                1, max_index, value=1, step=1,
                label="",
                elem_classes="phrase-slider",
                interactive=True
            )

            with gr.Row(elem_classes="nav-row"):
                prev_button = gr.Button("←")
                next_button = gr.Button("→")

            translate_button = gr.Button("Translate")
            translation_display = gr.Markdown("")
            phrase_index = gr.State(value=1)

            # Wire up
            outputs = [phrase_display, audio_output, phrase_index, phrase_slider, translation_display]

            prev_button.click(
                lambda x: render_player_state(x - 1, subtitles, audio_manager, max_index),
                inputs=[phrase_index],
                outputs=outputs
            )
            next_button.click(
                lambda x: render_player_state(x + 1, subtitles, audio_manager, max_index),
                inputs=[phrase_index],
                outputs=outputs
            )
            phrase_slider.change(
                lambda x: render_player_state(x, subtitles, audio_manager, max_index),
                inputs=[phrase_slider],
                outputs=outputs
            )
            translate_button.click(
                translator.translate,
                inputs=[phrase_display],
                outputs=[translation_display]
            )

    return demo

CSS = """
.player {
    max-width: 600px;
    margin: 10px auto;
    font-family: -apple-system, BlinkMacSystemFont, sans-serif;
}

#phrase_display {
    font-size: 34px;
    margin: 10px 0;
    text-align: center;
}

.nav-row {
    display: flex !important;
    justify-content: space-between !important;
    width: 100% !important;
    margin: 10px 0 !important;
}

.nav-row button {
    min-width: 80px !important;
    margin: 0 !important;
}

/* Minimal slider */
.phrase-slider {
    margin: 0 !important;
    padding: 0 !important;
}

.phrase-slider > div:first-child {
    height: 8px !important;
}

.phrase-slider input[type="range"] {
    height: 1px !important;
    background: #e0e0e0 !important;
}

.phrase-slider .handle {
    width: 8px !important;
    height: 8px !important;
    background: #666 !important;
    border: none !important;
    box-shadow: none !important;
    margin-top: -4px !important;
}

.gradio-container .gr-form > div > div > div {
    border: none !important;
    box-shadow: none !important;
}

button {
    min-width: 60px;
    margin: 0 5px;
}

/* Audio player fixes */
.audio-player audio {
    width: 100% !important;
    height: 50px !important;
}

.audio-player > div:first-child {
    height: 50px !important;
}

.audio-player button {
    height: 22px !important;
    width: 22px !important;
    min-width: unset !important;
}

/* Hide unnecessary UI elements */
.audio-feedback, label, .progress {
    display: none !important;
}
.book-cover {
    width: 360px !important;  /* Reduced from default size */
}

.book-cover > div {
    height: auto !important;
    border: none !important;  /* Remove border */
    background: none !important;  /* Remove background */
}

.book-cover img {
    width: 100% !important;
    height: auto !important;
    object-fit: contain !important;
    border: none !important;  /* Remove image border */
    border-radius: 0 !important;  /* Remove border radius */
    box-shadow: none !important;  /* Remove shadow if any */
}

.book-title h1 {
    margin: 0 !important;
    font-size: 24px !important;
    font-weight: 500 !important;
    color: #1a1a1a !important;
}
"""

def render_player_state(index: int, subtitles, audio_manager, max_index: int) -> tuple:
    """Return updated interface state for the given index."""
    bounded_index = max(1, min(index, max_index))
    text, audio = extract_phrase_content(bounded_index, subtitles, audio_manager)
    return text, audio, bounded_index, bounded_index, ""  # Fixed: Return 5 values to match outputs

def main():
    """Launch the audiobook player application."""
    try:
        config = load_yaml_config()
        subtitles, audio_manager, translator = initialize_core_services(config)
        demo = build_player_interface(config, subtitles, audio_manager, translator)
        demo.launch(
            server_name=config['server']['host'],
            server_port=config['server']['port']
        )
    except Exception as e:
        print(f"Error starting application: {e}")


if __name__ == "__main__":
    main()