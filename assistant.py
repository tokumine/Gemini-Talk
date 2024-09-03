import warnings
warnings.filterwarnings("ignore", category=UserWarning)

import pyaudio
import wave
import numpy as np
import torch
import google.generativeai as genai
from elevenlabs import stream
import io
import queue
import threading
import time
import os
from elevenlabs.client import ElevenLabs
from elevenlabs import Voice, VoiceSettings
import tempfile  
import sys
import google.api_core.exceptions
from google.api_core import retry, exceptions
from dotenv import load_dotenv
import select
import termios
import tty
import yaml

# Load environment variables from .env file
load_dotenv()

# Get API keys from environment variables
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')

# Check if API keys are present
if not GEMINI_API_KEY or not ELEVENLABS_API_KEY:
    print("Error: API keys not found.")
    print("Please make sure you have a .env file in the project root with the following content:")
    print("GEMINI_API_KEY=your_gemini_api_key")
    print("ELEVENLABS_API_KEY=your_elevenlabs_api_key")
    print("You can copy the .env.example file and fill in your actual API keys.")
    exit(1)

# VAD model (speech endpointer)
vad_model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad',
                                  model='silero_vad',
                                  force_reload=True)

(get_speech_timestamps,
 save_audio,
 read_audio,
 VADIterator,
 collect_chunks) = utils

# Initialize PyAudio
p = pyaudio.PyAudio()

# Audio recording parameters
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000

# Gemini and ElevenLabs setup
genai.configure(api_key=GEMINI_API_KEY)
# Rename the Gemini model
gemini_model = genai.GenerativeModel('gemini-1.5-pro-exp-0827')
elevenlabs_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
safe_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]

# Conversation history
conversation = []

def record_audio():
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("Listening... (Press Ctrl+C to stop manually)")

    frames = []
    vad_iterator = VADIterator(vad_model)
    window_size_samples = 512  # for 16000 Hz
    speech_started = False
    silence_threshold = 0.8  # 1.5 seconds of silence
    max_duration = 5 * 60  # 5 minutes max recording

    start_time = time.time()
    last_speech_time = None
    silence_start_time = None
    audio_buffer = np.array([], dtype=np.float32)

    try:
        while True:
            current_time = time.time()
            data = stream.read(CHUNK)
            frames.append(data)
            
            # Convert data to numpy array and add to buffer
            float_data = np.frombuffer(data, np.int16).astype(np.float32) / 32768.0
            audio_buffer = np.concatenate((audio_buffer, float_data))
            
            # Process VAD in window_size_samples chunks
            while len(audio_buffer) >= window_size_samples:
                chunk = audio_buffer[:window_size_samples]
                audio_buffer = audio_buffer[window_size_samples:]
                
                # Process VAD
                speech_detected = vad_iterator(torch.from_numpy(chunk), return_seconds=False)
                
                if speech_detected:
                    last_speech_time = current_time
                    silence_start_time = None  # Reset silence start time
                    if not speech_started:
                        speech_started = True
                        #print("\nSpeech detected, recording started.")
                elif speech_started and silence_start_time is None:
                    silence_start_time = current_time

            # Calculate silence duration
            if silence_start_time is not None:
                silence_duration = current_time - silence_start_time
            else:
                silence_duration = 0

            # Check if speech has paused
            if speech_started and silence_duration > 0:
                speech_started = False
                #print("\nSpeech paused.")

            # Debug information
            elapsed_time = current_time - start_time
            sys.stdout.write(f'\rTime: {elapsed_time:.2f}s, Silence: {silence_duration:.2f}s, Speech active: {speech_started}')
            sys.stdout.flush()

            vad_iterator.reset_states()

            # End conditions
            if not speech_started and silence_duration >= silence_threshold:
                print("\nRecording ended due to prolonged silence.")
                break
            
            if current_time - start_time > max_duration:
                print("\nMaximum recording time reached.")
                break

    except KeyboardInterrupt:
        print("\nRecording stopped manually.")

    print("\nRecording finished.")
    stream.stop_stream()
    stream.close()
    p.terminate()
    vad_iterator.reset_states()  # Reset VAD states after recording

    # Save the recorded audio to a temporary WAV file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio_file:
        with wave.open(temp_audio_file.name, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
        
        return temp_audio_file.name

def text_to_speech_stream(text_queue, persona):
    def text_generator():
        while True:
            text = text_queue.get()
            if text is None:
                break
            yield text + " "  # Add a space to ensure proper streaming

    audio_stream = elevenlabs_client.generate(
        text=text_generator(),
        voice=persona['elevenlabs_voice'],
        model=persona['elevenlabs_model'],
        stream=True
    )

    stop_event = threading.Event()

    def check_for_interrupt():
        # Save the current terminal settings
        old_settings = termios.tcgetattr(sys.stdin)
        try:
            # Set the terminal to raw mode
            tty.setraw(sys.stdin.fileno())
            while not stop_event.is_set():
                rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
                if rlist:
                    key = sys.stdin.read(1)
                    if key == ' ':
                        stop_event.set()
                        break
        finally:
            # Restore the terminal settings
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

    interrupt_thread = threading.Thread(target=check_for_interrupt)
    interrupt_thread.start()

    def custom_stream():
        try:
            for chunk in audio_stream:
                if stop_event.is_set():
                    break
                yield chunk
        finally:
            stop_event.set()
            interrupt_thread.join()

    stream(custom_stream())

    # Ensure the terminal is reset after streaming
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, termios.tcgetattr(sys.stdin))

def load_personas():
    personas = {}
    for filename in os.listdir('persona'):
        if filename.endswith('.yaml') or filename.endswith('.yml'):
            with open(os.path.join('persona', filename), 'r') as f:
                persona = yaml.safe_load(f)
                personas[persona['name']] = persona
    return personas

def main():
    print("Welcome to Gemini-Talk-CLI. Let's start a conversation!")
    
    personas = load_personas()
    print("Available personas:")
    # Sort the personas by name
    for i, (name, persona) in enumerate(sorted(personas.items()), 1):
        print(f"{i}. {name}: {persona['description']}")
    
    choice = int(input("Choose a persona (enter the number): ")) - 1
    # Use the sorted list of personas to select the chosen one
    selected_persona = list(dict(sorted(personas.items())).values())[choice]
    
    model = genai.GenerativeModel(
        model_name=selected_persona['gemini_model'],
        system_instruction=selected_persona['persona']
    )
    
    chat = model.start_chat()

    while True:
        print("\nListening for your input...")
        audio_file_path = record_audio()
        if audio_file_path is None:
            print("No audio data recorded. Please try again.")
            continue
        
        print("Processing audio...")
        try:
            uploaded_file = genai.upload_file(path=audio_file_path)
            
            response = chat.send_message(["", uploaded_file], safety_settings=safe_settings, stream=True)
            
            print("Gemini response:")
            text_queue = queue.Queue()
            
            tts_thread = threading.Thread(target=text_to_speech_stream, args=(text_queue, selected_persona))
            tts_thread.start()
            
            full_response = ""
            for chunk in response:
                if chunk.text:
                    print(chunk.text, end='', flush=True)
                    full_response += chunk.text
                    text_queue.put(chunk.text)
            
            text_queue.put(None)  # Signal end of text
            tts_thread.join()
            
            print("\n")
            
        except google.api_core.exceptions.InternalServerError:
            print("Gemini API is currently experiencing issues. Please try again.")
        except exceptions.DeadlineExceeded:
            print("Request to Gemini API timed out. Please try again.")
        except Exception as e:
            print(f"An unexpected error occurred: {type(e).__name__}: {e}")
        finally:
            os.unlink(audio_file_path)

    print("Thank you for using the Gemini-Talk-CLI. Goodbye!")

if __name__ == "__main__":
    main()
