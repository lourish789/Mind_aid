
#pip install flask google-generativeai python-dotenv gtts speechrecognition pydub


# backend/app.py
from flask import Flask, request, jsonify, send_file
import os
import google.generativeai as genai
from dotenv import load_dotenv
from gtts import gTTS
import speech_recognition as sr
from pydub import AudioSegment
import random

# Load environment variables
load_dotenv()
#API_KEY = os.getenv('GEMINI_API_KEY')

API_KEY = "AIzaSyB3N9BHeIWs_8sdFK76PU-v9N6prcIq2Hw"

# Initialize Gemini API
genai.configure(api_key=API_KEY)
gemini_model = genai.GenerativeModel('gemini-1.5-pro')

# Initialize Flask
app = Flask(__name__)


def predict_emotion_from_eeg():
    #EEG_model = mind_aid_model.pkl
    return random.choice(['positive', 'neutral', 'negative'])

def transcribe_audio(audio_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio_data = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio_data)
        return text
    except sr.UnknownValueError:
        return None

@app.route('/chat', methods=['POST'])
def chat():
    # Check if audio was sent
    if 'audio' in request.files:
        audio_file = request.files['audio']
        audio_path = "uploaded_audio.wav"
        audio_file.save(audio_path)

        # Transcribe audio to text
        user_text = transcribe_audio(audio_path)
        if not user_text:
            return jsonify({"error": "Could not transcribe audio."}), 400
    else:
        # Otherwise expect JSON text input
        data = request.get_json()
        user_text = data.get('user_input')

    if not user_text:
        return jsonify({"error": "No user input received."}), 400

    # Predict Emotion
    user_emotion = predict_emotion_from_eeg()

    # Modify prompt based on emotion
    emotion_prompt = f"The user is feeling {user_emotion}. Respond appropriately and kindly.\nUser said: {user_text}"

    # Call Gemini
    response = gemini_model.generate_content(emotion_prompt)
    bot_reply = response.text

    # Generate Nigerian accent audio
    tts = gTTS(bot_reply, lang='en', tld='com.ng')
    audio_response_path = "response.mp3"
    tts.save(audio_response_path)

    return jsonify({
        "emotion": user_emotion,
        "response_text": bot_reply,
        "audio_url": "/audio/response.mp3"
    })

@app.route('/audio/<filename>')
def serve_audio(filename):
    return send_file(filename, mimetype='audio/mpeg')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)

