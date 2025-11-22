<h1 align="center">SEESENSE-AI</h1>

<p align="center">
  Empowering Vision, Enabling Freedom Through AI Assistance
</p>

<p align="center">
  <img src="https://img.shields.io/github/last-commit/hannahjan06/SeeSense-AI" alt="last commit">
  <img src="https://img.shields.io/github/languages/top/hannahjan06/SeeSense-AI?color=2b7489&label=top%20language" alt="CSS">
  <img src="https://img.shields.io/github/languages/count/hannahjan06/SeeSense-AI?label=languages" alt="languages">
</p>

<p align="center">
  Built with the tools and technologies:
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask">
  <img src="https://img.shields.io/badge/Python-3572A5?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Google%20Gemini-7b1fa2?style=for-the-badge&logo=google&logoColor=white" alt="Google Gemini">
</p>

---

## Overview

SeeSense-AI is a browser-based assistive vision tool designed for blind and low-vision users.  
Using a camera feed, AI vision models, and text-to-speech, it turns visual information into spoken feedback so users can:

- Understand their surroundings
- Read printed text in the environment
- Identify everyday objects

All of this is driven through simple voice commands such as:

> “Nova, describe”  
> “Nova, read”  
> “Nova, identify”  

The goal is not to be a generic AI demo, but a focused accessibility tool that gives users more independence in unfamiliar or visually complex environments.

---

## Core Features

- **Voice-activated assistant (Nova)**  
  Hands-free interaction using speech recognition to trigger actions:
  - `describe` – scene description
  - `read` – text reading
  - `identify` – object identification
  - `repeat` – repeat the last response

- **Scene Description**  
  Captures a frame from the camera and sends it to a vision model, which returns a concise spoken description of what is in front of the user.

- **Text Reading**  
  Reads menus, signs, labels or other printed text visible to the camera and speaks it back to the user.

- **Object Identification**  
  Identifies the main object in view and provides details like type, color and context.

- **Lighting Awareness**  
  Detects when the scene is too dark or too bright for reliable analysis and gives spoken guidance on how to adjust.

- **Accessible Interaction Design**  
  - Full-screen “tap anywhere to start” onboarding
  - Large, high-contrast controls
  - Voice-first flow so users never need to rely on precise mouse/trackpad interaction

---

## How It Works

1. The user opens the web app and grants camera and microphone access.
2. The browser listens for wake phrases such as:  
   `“Nova, describe”`
3. JavaScript captures a frame from the camera and sends it to the Flask backend.
4. The Flask backend forwards the image to a Google Gemini vision endpoint with a task-specific prompt.
5. The model response (scene description / text / object info) is returned as JSON.
6. The frontend:
   - Displays the result in the “AI Analysis” panel
   - Uses the Web Speech API to speak the result aloud
7. Users can say `“Nova, repeat”` to hear the last response again.

---

## Tech Stack

- **Backend:** Python, Flask
- **AI:** Google Gemini Vision API (via HTTP requests)
- **Frontend:** HTML, CSS, JavaScript
- **Speech Input:** Web Speech API (speech recognition)
- **Speech Output:** Web Speech API (text-to-speech)
- **Environment:** `.env`-based config, `requirements.txt` for dependencies

---

## Project Structure

```bash
SeeSense-AI/
├── app.py                # Main Flask application and routes
├── config.py             # Configuration and environment variable loading
├── pp1.py                # AI / Gemini integration and helper functions
├── requirements.txt      # Python dependencies
├── .env                  # Local environment variables (not committed)
├── static/
│   ├── index/
│   │   ├── index.html    # Main UI for the assistant
│   │   └── style.css     # Main styles
│   └── demo/
│       ├── demo.html     # Optional demo/experimental view
│       └── demo.css
└── venv/                 # Local virtual environment (ignored in git)

---

## Getting Started

### Prerequisites

* Python 3.9+
* A Google Gemini API key
* Git

### 1. Clone the repository

```bash
git clone https://github.com/hannahjan06/SeeSense-AI.git
cd SeeSense-AI
```

### 2. Create and activate a virtual environment (recommended)

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```bash
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=your_preferred_model_name   # optional, if used in config.py
FLASK_ENV=development
```

### 5. Run the application

```bash
python app.py
```

By default, the app should be available at:

```
http://127.0.0.1:5000
```

Open it in Chrome for best support of camera and speech APIs.

---

## Usage

1. Open the web page and allow camera and microphone access when prompted.
2. Wait for Nova to indicate that it is listening.
3. Use one of the voice commands:

   * `"Nova, describe"`
   * `"Nova, read"`
   * `"Nova, identify"`
   * `"Nova, repeat"`
4. Listen to the spoken response. The same text will also appear in the “AI Analysis” panel.
5. If the lighting is too dark or bright, Nova will inform you and suggest adjustments.

---

## Current Limitations

* Requires a stable internet connection for Gemini API access.
* Accuracy depends on camera quality, lighting and model performance.
* Works best in Chrome or Chromium-based browsers with full support for Web Speech and media APIs.
* Not a medical or safety-certified device; intended as a proof-of-concept assistive tool.

---

## Roadmap / Future Work

* Continuous “explore” mode with periodic scene updates
* Improved alignment guidance for framing objects and text
* Dedicated modes for:

  * Reading menus
  * Reading medicine labels
  * Locating specific objects
* Multi-language support for output
* Mobile-first layout and PWA packaging
* Option to swap Gemini with self-hosted open models for offline/edge use

---

## Contributing

This project started as a hackathon prototype.
If you have ideas around accessibility, voice interaction, or multimodal AI and want to iterate on it:

1. Fork the repo
2. Create a feature branch
3. Submit a pull request with a clear description of your changes

---

## Acknowledgements

* Google Gemini for multimodal AI capabilities
* The broader accessibility community for continual advocacy and design principles
* Horizon Hacks for the theme “AI for Accessibility and Equity” that inspired this build