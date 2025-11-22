import base64
from io import BytesIO
from PIL import Image
import traceback
import sys
import os
import dotenv

from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS

import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

from gtts import gTTS

dotenv.load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    print("Error: GEMINI_API_KEY not found in .env file.")
    sys.exit(1)

genai.configure(api_key=API_KEY)

MODEL_ID = os.getenv("MODEL_ID")

app = Flask(__name__, static_folder='static', template_folder='static')
CORS(app)

print(f"Loading Gemini model: {MODEL_ID}...")
sys.stdout.flush()
gemini_model = None
try:
    gemini_model = genai.GenerativeModel(MODEL_ID)
    print(f"Gemini model {MODEL_ID} loaded.")
    sys.stdout.flush()
except Exception:
    print(f"Failed to load Gemini model {MODEL_ID} at startup:")
    traceback.print_exc()
    gemini_model = None

"""Renders the main home page (index.html)."""
@app.route('/')
def home():
    try:
        return render_template('index/index.html')
    except Exception as e:
        print(f"Error rendering index.html: {e}")
        # printing full error details
        traceback.print_exc()
        # Shows an error message to the user
        return jsonify({"error": "Failed to load home page."}), 500

"""Renders the demo page (demo.html)."""
@app.route('/demo.html')
def demo_page():
    try:
        return render_template('demo/demo.html')
    except Exception as e:
        print(f"Error rendering demo.html: {e}")
        traceback.print_exc()
        return jsonify({"error": "Failed to load demo page."}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"ok": True, "model_loaded": gemini_model is not None}), 200

last_gemini_response_text = ""

@app.route('/get-last-spoken-text', methods=['GET'])
def get_last_spoken_text():
    global last_gemini_response_text
    return jsonify({"text": last_gemini_response_text})

@app.route('/analyze-image', methods=['POST'])
def analyze_image():
    global last_gemini_response_text # Declare global to modify the variable

    if gemini_model is None:
        return jsonify({"error": f"Gemini model {MODEL_ID} not loaded. Check server logs."}), 500

    data = request.json
    if not data or 'image' not in data:
        return jsonify({"error": "No image data provided in the request body."}), 400

    command_type = data.get('command', 'describe')
    print(f"Received command type: {command_type}")

    try:
        image_data_url = data['image']
        header, encoded = image_data_url.split(',', 1)
        image_bytes = base64.b64decode(encoded)
        img = Image.open(BytesIO(image_bytes)).convert("RGB")

        prompt = ""
        if command_type == 'describe':
            prompt = (
                "You are an assistive AI for a visually impaired user and take the picture as the pov of what they see. "
                "Give a short, direct, safety-focused description of the scene in **1–3 sentences only**."
                "Requirements:"
                "- Prioritize hazards, obstacles, and anything close enough to touch, bump into, or trip over."
                "- Mention only the most important objects and their **relative direction** (left, right, center) and **approximate distance** (very close / one step away / a few steps away)."
                "- If unsure about something, say “unclear” instead of guessing."
                "- Do NOT use sections, headings, lists, or long explanations."
                "- Keep it fast, concise, and immediately useful for navigation."
                "- If u find text in the image, read it out loud. (DONT FORGET THIS STEP)"
            )
        elif command_type == 'identify':
            prompt = (
                "You are an assistive AI for a visually impaired user. "
                "Identify the main objects and people in the image. List them concisely, stating their general location "
                "(e.g., 'a person on the left', 'a chair in the center'). If you recognize a specific brand or item, mention it. "
                "Focus on distinct entities rather than a broad scene description. If u find text in the image, read it out loud. (DONT FORGET THIS STEP)"
            )
        elif command_type == 'read':
            prompt = (
                "You are an assistive AI for a visually impaired user. "
                "Carefully examine the image for any text. If text is present, read it out loud exactly as it appears. "
                "If there is no text, simply state 'No discernible text found in the image.' "
                "Prioritize legibility and accuracy. (DONT FORGET THIS STEP)"
            )
        else:
            prompt = (
                "You are an assistive AI for a visually impaired user and take the picture as the pov of what they see. "
                "Give a short, direct, safety-focused description of the scene in **1–3 sentences only**."
                "Requirements:"
                "- Prioritize hazards, obstacles, and anything close enough to touch, bump into, or trip over."
                "- Mention only the most important objects and their **relative direction** (left, right, center) and **approximate distance** (very close / one step away / a few steps away)."
                "- If unsure about something, say “unclear” instead of guessing."
                "- Do NOT use sections, headings, lists, or long explanations."
                "- Keep it fast, concise, and immediately useful for navigation."
                "- If u find text in the image, read it out loud. (DONT FORGET THIS STEP)"
            )

        contents = [prompt, img]

        print(f"Calling Gemini API with model: {MODEL_ID}")
        # Flush stdout to ensure logs appear in order and cause no delays
        sys.stdout.flush()

        response = gemini_model.generate_content(
            contents,
            generation_config=genai.GenerationConfig(max_output_tokens=500),
            safety_settings={
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
        )

        analysis = ""
        if response.candidates:
            first_candidate = response.candidates[0]

            print(f"Raw finish_reason value: {first_candidate.finish_reason}")
            sys.stdout.flush()

            if first_candidate.finish_reason == 2: # 2 is the integer value for FinishReason.SAFETY
                safety_ratings_info = []
                if first_candidate.safety_ratings:
                    for rating in first_candidate.safety_ratings:
                        safety_ratings_info.append(f"{rating.category.name}: {rating.probability.name}")
                error_message = (
                    f"Gemini API generated a candidate, but it was blocked due to safety. "
                    f"Finish reason: {first_candidate.finish_reason}. "
                    f"Safety ratings: {', '.join(safety_ratings_info) if safety_ratings_info else 'None provided.'}"
                )
                print(f"Gemini Blocking Details: {error_message}")
                last_gemini_response_text = ""
                return jsonify({
                    "error": "Image analysis blocked by safety filters. Please try a different image.",
                    "details": error_message
                }), 400

            for part in first_candidate.content.parts:
                if hasattr(part, 'text'):
                    analysis += part.text

            if analysis:
                print(f"Generated analysis: {analysis}")
                last_gemini_response_text = analysis

                tts = gTTS(text=analysis, lang='en')
                audio_buffer = BytesIO()
                tts.write_to_fp(audio_buffer)
                audio_buffer.seek(0)

                return send_file(audio_buffer, mimetype='audio/mpeg', as_attachment=False, download_name='analysis.mp3')

            else:
                error_message = (
                    "Gemini API returned candidates with no text content. "
                    f"Finish reason of first candidate: {first_candidate.finish_reason}."
                )
                print(f"Gemini Unexpected No Text: {error_message}")
                last_gemini_response_text = ""
                return jsonify({
                    "error": "Image analysis failed: No text content generated.",
                    "details": error_message
                }), 500
        else:
            feedback = response.prompt_feedback
            safety_ratings_info = []
            if feedback and feedback.safety_ratings:
                for rating in feedback.safety_ratings:
                    safety_ratings_info.append(f"{rating.category.name}: {rating.probability.name}")

            error_message = (
                f"Gemini API did not return any candidates. This is likely due to prompt-level safety filters. "
                f"Prompt feedback: {feedback}. "
                f"Safety ratings: {', '.join(safety_ratings_info) if safety_ratings_info else 'None provided.'}"
            )
            print(f"Gemini Blocking Details (Prompt-level): {error_message}")
            last_gemini_response_text = ""
            return jsonify({
                "error": "Image analysis blocked by safety filters (prompt-level). Please try a different image.",
                "details": error_message
            }), 400

    except Exception as e:
        tb = traceback.format_exc()
        print("Error in /analyze-image:", tb)
        last_gemini_response_text = ""
        return jsonify({"error": f"An unexpected error occurred during image analysis: {str(e)}", "trace": tb}), 500

if __name__ == '__main__':
    cwd = os.getcwd()
    print(f"Starting Flask server. CWD={cwd}. Listening on http://0.0.0.0:8000")
    sys.stdout.flush()
    app.run(host='0.0.0.0', port=8000, debug=True, threaded=True)