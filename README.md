# Gemini-Talk

Gemini-Talk is an empathetic voice assistant powered by Google's Gemini 1.5 Pro AI model. It provides a command-line interface for natural, voice-based interactions with advanced AI capabilities. 

## Key Features

1. **Empathetic Responses**: Utilizes Gemini Native Audio for more natural and context-aware interactions.
2. **Multilingual Support**: Capable of understanding and responding in multiple languages.
3. **Efficient Audio Processing**: Streams output from Gemini to ElevenLabs for real-time text-to-speech conversion.
4. **Intelligent Turn-Taking**: Employs a local endpointer model to manage conversation flow.
5. **Persona Support**: Supports multiple personas with different voices and personalities.
6. **Interruptable**: Can be interrupted by the user by pressing `space`.

## Technologies Used

- Gemini 1.5 Pro: Advanced AI model for natural language processing and generation
- ElevenLabs TTS: High-quality text-to-speech conversion
- Local Endpointer Model: Manages conversation turn-taking

## Prerequisites

- Python 3.7+
- `mpv` media player
- Gemini API key
- ElevenLabs API key

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/Gemini-Talk.git
   cd Gemini-Talk
   ```

2. Create and activate a Python virtual environment:
   ```
   python3 -m venv myenv
   source myenv/bin/activate
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Install the `mpv` media player:
   - macOS: `brew install mpv`
   - Linux: Use your distribution's package manager (e.g., `sudo apt-get install mpv` for Ubuntu)

5. Set up your API keys:
   ```
   cp .env.example .env
   ```
   Edit the `.env` file and add your Gemini API key and ElevenLabs API key.

## Usage

Run the assistant:
```
python assistant.py
```

Follow the on-screen prompts to interact with the Gemini-Talk voice assistant.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
