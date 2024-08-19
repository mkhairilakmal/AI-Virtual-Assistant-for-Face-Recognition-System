import whisper
import pyttsx3
import sounddevice as sd
import numpy as np
import tempfile
import os

# Initialize the text-to-speech engine
engine = pyttsx3.init()

# Load Whisper model
model = whisper.load_model("base")

def capture_audio(duration=5, samplerate=16000):
    print("Recording...")
    audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
    sd.wait()
    print("Recording completed.")
    
    # Save the audio to a temporary WAV file
    temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    write(temp_wav.name, samplerate, audio)
    return temp_wav.name

def transcribe_audio(audio_path):
    # Transcribe audio using Whisper
    result = model.transcribe(audio_path)
    return result['text']

def respond(response):
    engine.say(response)
    engine.runAndWait()

def process_command(command):
    if "open slides" in command or "open powerpoint" in command:
        respond("Opening PowerPoint.")
        # Insert the code to open PowerPoint here
    elif "open presentation" in command:
        respond("Opening your presentation.")
        # Insert the code to open a specific presentation here
    else:
        # Process the command using QA system
        response = qa.invoke(command)
        respond(response["result"])

def main():
    while True:
        audio_file = capture_audio(duration=5)
        command = transcribe_audio(audio_file)
        print(f"Transcribed Command: {command}")
        
        if command:
            process_command(command)
        else:
            respond("Sorry, I didn't understand that.")
        
        # Clean up temporary audio file
        os.remove(audio_file)

        # Break the loop if user says 'exit'
        if "exit" in command or "quit" in command:
            respond("Goodbye!")
            break

if __name__ == "__main__":
    main()