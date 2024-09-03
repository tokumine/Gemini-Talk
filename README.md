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
- Local silero-vad Endpointer Model: Manages conversation turn-taking

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
Note: You can press `space` to interrupt the assistant, but it's pretty laggy.

## Available personas
1. Alice: A confident British news anchor with a penchant for precision and clarity.
2. Bill: A wise and trustworthy American storyteller with years of experience to share.
3. Brian: A deep-voiced American narrator with a commanding presence and soothing tone.
4. Callum: An intense Transatlantic voice actor specializing in dynamic character portrayals.
5. Callum (NSFW): An NSFW Transatlantic voice actor specializing in dynamic character portrayals.
6. Charlie: A natural and friendly Australian voice for engaging conversational interactions.
7. Charlie-DE: A natural and friendly Australian voice for engaging conversational interactions.
8. Charlie-ES: A natural and friendly Australian voice for engaging conversational interactions.
9. Charlie-JP: A natural and friendly Australian voice for engaging conversational interactions.
10. Charlie-ZH: A natural and friendly Australian voice for engaging conversational interactions.
11. Charlotte: A charming and seductive Swedish character actress with a flair for the dramatic.
12. Chris: A casual and relatable American conversationalist with a knack for putting people at ease.
13. Daniel: An authoritative British news presenter with a commanding presence.
14. Eric: A friendly American conversationalist with a knack for making complex topics accessible.
15. George: A warm British narrator with a comforting presence and storytelling prowess.
16. Jessica: An expressive American conversationalist with a vibrant and engaging personality.
17. Laura: An upbeat American social media personality with a finger on the pulse of trends.
18. Liam: An articulate American narrator with a talent for clear and engaging storytelling.
19. Lily: A warm British narrator with a soothing presence and storytelling finesse.
20. Matilda: A friendly American narrator with a knack for making complex topics accessible and engaging.
21. Sarah: A soft-spoken American news presenter with a calming presence and clear delivery.
22. Will: A friendly American social media personality with an engaging and relatable style.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
