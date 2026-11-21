# Vocal Coach Studio — AI Edition

This is an upgraded PWA front end plus a separate FastAPI backend. It supports BOTH assessment modes:
- Independent vocal assessment (pitch, rhythm, tone, diction, breath/phrasing, technique, expression)
- Comparison with an optional reference recording

Reports are structured by section with approximate timestamps, evidence, confidence, corrections and exercises.

## Important architecture note
GitHub Pages only hosts static files. It cannot run `server.py`. The AI assessment endpoint must be deployed separately to a Python hosting service, and the front end must be configured to call that service. Never put `OPENAI_API_KEY` in `app.js`, GitHub Pages files, or a public repository.

## Backend setup (recommended: Render)

1. Push the files in this folder to the root of your existing GitHub repository (`jindom/Vocal-Studio`). Keep `index.html`, `app.js`, `server.py`, and `requirements.txt` at repository root.
2. In Render, create a **New Web Service** and connect the `Vocal-Studio` GitHub repository.
3. Use these settings: Runtime `Python`; Build command `pip install -r requirements.txt`; Start command `uvicorn server:app --host 0.0.0.0 --port $PORT`.
4. Add environment variables in Render: `OPENAI_API_KEY` (your secret API key), `OPENAI_AUDIO_MODEL` = `gpt-audio-1.5`, and `ALLOWED_ORIGINS` = `https://jindom.github.io`.
5. Deploy. Open `https://YOUR-RENDER-SERVICE.onrender.com/health`; it should return `status: ok` and `api_key_configured: true`.
6. Open the PWA, scroll to **AI server connection**, paste your Render service URL (without a trailing slash), and save.

Render free services may sleep when idle; the first request after inactivity can take longer. Check current hosting limits and pricing before choosing a plan.

## Alternative: run locally on Windows
1. Install Python 3.11+ from python.org.
2. Open Command Prompt in this folder.
3. Run: `py -m venv .venv`
4. Activate: `.venv\\Scripts\\activate`
5. Run: `pip install -r requirements.txt`
6. Set the key in the current terminal: `set OPENAI_API_KEY=your_key_here`
7. Run: `uvicorn server:app --host 0.0.0.0 --port 8000`
8. Test `http://127.0.0.1:8000/health`.

For public use, deploy the backend to a secure HTTPS host and set environment variables there. Set `ALLOWED_ORIGINS` to your GitHub Pages origin. The server is not publicly accessible until deployed.

## Connect the PWA to the backend
The front end includes an **AI server connection** field. Paste the backend HTTPS URL there and save.

## Audio input
The starter backend accepts WAV and MP3 (up to 20 MB per file). If a mobile recorder creates WebM/M4A, convert to WAV or MP3 before upload. For best reference comparison, use a clean vocal stem or instrumental/reference with a clearly audible melody. Full commercial mixes can obscure the lead melody.

## Accuracy and limitations
The AI model listens to the submitted audio and provides perceptual coaching. It is not a calibrated pitch-tracking laboratory or a certified singing teacher. Scores and timestamps are approximate; confidence must be reviewed. Exact note-by-note scoring, cents deviation, vocal range tracking and robust phrase alignment require a dedicated DSP pipeline (e.g. pitch extraction + source separation + dynamic time warping) and validation against labelled recordings. Do not use the feedback as medical advice.

## API privacy and cost
Audio is sent to the configured OpenAI API through your backend. `store=False` is requested for the model call, but review the provider's current API data controls and pricing before use. API usage is billed separately from ChatGPT subscriptions. Add billing limits and rate limits before making the endpoint public.


## API billing
An OpenAI API key and API billing are separate from a ChatGPT subscription. Audio analysis calls can incur usage charges. Set a usage budget/rate limit in your API account before using the service. Never send your secret key to anyone or commit it to GitHub.
