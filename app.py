# backend/app.py

from flask import Flask, request, jsonify, send_file
import os
import google.generativeai as genai
from dotenv import load_dotenv
from gtts import gTTS
import speech_recognition as sr
from pydub import AudioSegment
import random
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Initialize Flask
app = Flask(__name__)
CORS(app)

# Load environment variables
load_dotenv()

# You should use environment variable in production
API_KEY = "AIzaSyB3N9BHeIWs_8sdFK76PU-v9N6prcIq2Hw"
genai.configure(api_key=API_KEY)
gemini_model = genai.GenerativeModel('gemini-1.5-pro')

# Paths
UPLOAD_FOLDER = 'uploads'
AUDIO_RESPONSE_FOLDER = 'audio'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(AUDIO_RESPONSE_FOLDER, exist_ok=True)

def predict_emotion_from_eeg():
    # Placeholder for EEG model inference
    return random.choice(['positive', 'neutral', 'negative'])

def transcribe_audio(audio_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio_data = recognizer.record(source)
    try:
        return recognizer.recognize_google(audio_data)
    except sr.UnknownValueError:
        return None

@app.route('/chat', methods=['POST'])
def chat():
    user_text = None

    if 'audio' in request.files:
        audio_file = request.files['audio']
        audio_filename = secure_filename("uploaded_audio.wav")
        audio_path = os.path.join(UPLOAD_FOLDER, audio_filename)
        audio_file.save(audio_path)

        user_text = transcribe_audio(audio_path)
        if not user_text:
            return jsonify({"error": "Could not transcribe audio."}), 400

    elif request.is_json:
        data = request.get_json()
        user_text = data.get('user_input')

    if not user_text:
        return jsonify({"error": "No user input received."}), 400

    # Predict emotion (stub)
    user_emotion = predict_emotion_from_eeg()
    emotion_prompt = f"The user is feeling {user_emotion}. Respond appropriately and kindly.\nUser said: {user_text}"

    # Gemini response
    response = gemini_model.generate_content(emotion_prompt)
    bot_reply = response.text.strip()

    # Generate audio
    audio_filename = 'response.mp3'
    audio_path = os.path.join(AUDIO_RESPONSE_FOLDER, audio_filename)
    tts = gTTS(bot_reply, lang='en', tld='com.ng')
    tts.save(audio_path)

    return jsonify({
        "emotion": user_emotion,
        "response_text": bot_reply,
        "audio_url": f"/audio/{audio_filename}"
    })

@app.route('/audio/<filename>')
def serve_audio(filename):
    filepath = os.path.join(AUDIO_RESPONSE_FOLDER, secure_filename(filename))
    if not os.path.exists(filepath):
        return jsonify({"error": "File not found"}), 404
    return send_file(filepath, mimetype='audio/mpeg')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
