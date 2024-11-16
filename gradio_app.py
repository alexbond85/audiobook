import gradio as gr

# JavaScript to explicitly set and debug the audio source
js = """
(() => {
    const audioElement = document.querySelector('#audio_player audio');
    if (audioElement) {
        console.log("Audio element found:", audioElement);

        // Check if the source is set
        console.log("Audio source URL (before):", audioElement.src);
        if (!audioElement.src || audioElement.src === '') {
            console.error("Audio source is empty. Setting source manually.");
            audioElement.src = '/file=data/book/premiere-partie.mp3'; // Update with the correct path
            audioElement.load();
        }

        // Log the updated source
        console.log("Audio source URL (after):", audioElement.src);

        // Attach a listener for ready state
        audioElement.addEventListener("canplay", () => {
            console.log("Audio is ready to play.");
        });

        // Attach an error listener
        audioElement.addEventListener("error", (e) => {
            console.error("Audio error detected:", e);
        });
    } else {
        console.error("Audio element not found.");
    }
})()
"""

# Gradio App
with gr.Blocks(js=js) as demo:
    # Audio player
    audio_player = gr.Audio(
        "data/book/premiere-partie.mp3",
        elem_id="audio_player",
        label="Audio Player",
        interactive=True
    )

# Launch the app
demo.launch()
