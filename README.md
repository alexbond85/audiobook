# AudioReader App

An application that combines audiobook playback with synchronized text display and translation capabilities.

[Description and AudioReader screenshots](https://www.linkedin.com/pulse/audioreader-app-alexander-bondarenko-hvloe/)

## Features

- Text display synchronized with audio playback
- Translation between languages using ChatGPT
- Navigation through audio/text phrases 
- Simple web interface
- Support for multiple languages
- SRT subtitle generation from audio using OpenAI's Whisper

[Rest of the README remains exactly the same...]

## Prerequisites

- Python 3.11 or higher
- Poetry (Python package manager)
- OpenAI API key
- [Task](https://taskfile.dev) (task runner)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/alexbond85/audiobook.git
cd audiobook
```

2. Initialize the project:
```bash
task init
```
This command will:
- Configure poetry to use local virtualenv
- Set Python version to 3.11
- Install all dependencies

3. Create a `.env` file in the project root and add your OpenAI API key:
```bash
OPENAI_API_KEY=your_api_key_here
```

## Configuration

Configure the application through `config.yaml`:

```yaml
paths:
  data_dir: "data/book"  # Directory containing audio and subtitle files
  chapter: "chapter_name"  # Base name for audio and subtitle files
  book_title: "Book Title"  # Optional book title
  book_cover: "cover.png"  # Optional book cover image

server:
  host: "0.0.0.0"
  port: 7860

translation:
  source_language: "French"  # Source language for translation
  target_language: "German"  # Target language for translation
```

## Usage

1. Prepare your files:
   - Place your audio file (MP3 format) in the configured data directory
   - If you don't have subtitles, generate them:
     ```bash
     python transcribe.py
     ```

2. Start the application:
   ```bash
   python gradio_app.py
   ```gradio_app.py

3. Access the interface:
   - Open `http://localhost:7860`
   - Navigate between phrases
   - Use translate button for translations

## Development

The project uses Task for workflow automation. Available commands:

### Project Setup
```bash
task init              # Initialize project and install dependencies
```

### Code Quality
```bash
task format           # Format code using isort and black
task lint             # Run all linters
```

Individual linting tasks:
```bash
task linters:black    # Check code formatting
task linters:mypy     # Run type checker
task linters:flake8   # Check code style
task linters:isort    # Check import sorting
```

### Testing
```bash
task tests                        # Run unit tests
task tests:run_integration_tests  # Run integration tests
task tests:run_pytest            # Run all tests
```

### Maintenance
```bash
task clean            # Remove cache files and directories
```

### Default Workflow
```bash
task                  # Run format, lint, and tests
```

## Technical Details

- Built with Gradio for web interface
- OpenAI's Whisper API for transcription
- GPT models for translations
- Audio chunk caching for playback
- SRT subtitle format support

## Why AudioReader

Traditional audiobooks lack synchronized text features. While some platforms attempted to introduce this (like Audible Captions), they faced legal challenges from publishers.

AudioReader provides:
1. AI transcription (OpenAI's Whisper)
2. Real-time translation (ChatGPT)
3. Synchronized reading-listening experience

## Contributing

Contributions are welcome:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI for Whisper and GPT APIs
- Gradio team for web interface framework
- All contributors and users
