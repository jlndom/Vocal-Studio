# Vocal Coach Studio — PWA starter

Phone-first installable Progressive Web App starter. Includes live single-note pitch monitoring, audio recording/upload, and basic in-browser acoustic measurements.

## Publish free with GitHub Pages
1. Create/sign in to GitHub.
2. Create a **public** repository named `vocal-coach-studio`.
3. Extract this ZIP on your computer. Upload the five files (`index.html`, `app.js`, `manifest.webmanifest`, `sw.js`, `icon.svg`) to the repository root using Add file → Upload files.
4. Repository Settings → Pages → Build and deployment → Deploy from a branch → `main` → `/(root)` → Save.
5. Wait for the published URL shown on the Pages screen.
6. Open that HTTPS URL in Chrome on your Samsung → ⋮ menu → Install app or Add to Home screen.

GitHub Pages is available for public repositories on GitHub Free. The published site is public. Do not upload private audio, API keys, passwords or personal information to the repository.

## Important limitations
This starter runs its basic analysis locally in the browser. It is not yet connected to an AI audio-perception service or cloud account/history. It cannot reliably grade emotion, diction, full tone quality, vocal strain or note accuracy against the original song. Those require a secure backend, reference melody and an audio-capable evaluation workflow. Never put an OpenAI API key in `app.js` or any frontend file.

## Later secure AI integration
A Supabase Edge Function can act as the private backend for audio uploads and AI calls. Store API credentials in Supabase Edge Function secrets, not in browser code. Add authentication, storage limits, consent and deletion controls before storing recordings.
