import os, json, base64, re
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI

app = FastAPI(title='Vocal Coach Studio AI API')
origins = [x.strip() for x in os.getenv('ALLOWED_ORIGINS','*').split(',') if x.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=False, allow_methods=['GET','POST'], allow_headers=['*'])
MAX_BYTES = 20 * 1024 * 1024
MODEL = os.getenv('OPENAI_AUDIO_MODEL','gpt-audio-1.5')

@app.get('/health')
def health():
    return {'status':'ok','service':'Vocal Coach Studio AI','model':MODEL,'api_key_configured':bool(os.getenv('OPENAI_API_KEY'))}

async def read_audio(file: UploadFile):
    data = await file.read()
    if not data: raise HTTPException(400, f'{file.filename} is empty')
    if len(data) > MAX_BYTES: raise HTTPException(413, f'{file.filename} exceeds 20 MB')
    ext = (file.filename or '').lower().rsplit('.',1)[-1]
    formats = {'wav':'wav','mp3':'mp3','mpeg':'mp3','mpga':'mp3'}
    fmt = formats.get(ext)
    if fmt is None: raise HTTPException(415, 'Unsupported audio type. Use WAV, MP3, M4A or MP4.')
    # This starter sends WAV/MP3 directly as input_audio; other containers need transcoding first.
    return data, fmt

SYSTEM_PROMPT = '''You are a demanding but constructive professional singing coach. You are listening to the singer's actual audio, not merely reading a transcript. Give evidence-based feedback, never invent note names, timestamps, lyrics, vocal diagnoses, or technical faults. Separate what you can hear confidently from what is uncertain. The user wants BOTH independent vocal assessment and comparison with the supplied reference audio when present. The reference may contain accompaniment and/or a singer; say when that makes exact melody comparison uncertain. If no reference is supplied, set reference_comparison to null and do not claim note-by-note accuracy. Assess each section of the performance, with approximate timestamps in mm:ss. Score only when there is enough audible evidence; otherwise use null and explain low confidence. A sung lyric transcription may be uncertain: compare against user-supplied lyrics when present and flag unclear words. Do not diagnose vocal injury or strain; describe audible warning signs cautiously. Return ONLY valid JSON, no markdown, with this shape:
{
 "scores":{"pitch":{"score":0-10 or null,"confidence":"high|medium|low","note":""},"rhythm":{"score":0-10 or null,"confidence":"","note":""},"tone":{"score":0-10 or null,"confidence":"","note":""},"diction":{"score":0-10 or null,"confidence":"","note":""},"breath":{"score":0-10 or null,"confidence":"","note":""},"technique":{"score":0-10 or null,"confidence":"","note":""},"expression":{"score":0-10 or null,"confidence":"","note":""},"overall":{"score":0-10 or null,"confidence":"","note":""}},
 "overall_feedback":"string",
 "reference_comparison":{"available":true,"summary":"","melody_and_pitch":"","timing":"","lyrics_and_diction":"","confidence":"high|medium|low"} or null,
 "sections":[{"name":"Verse/chorus/phrase label","start":"mm:ss","end":"mm:ss","score":0-10 or null,"confidence":"high|medium|low","observation":"specific audible evidence","evidence":"what in audio supports this; timestamps approximate","corrections":"actionable correction","exercise":"targeted exercise"}],
 "technical_findings":[{"category":"","finding":"","evidence":"","confidence":"high|medium|low"}],
 "priority":"the single most important improvement",
 "exercises":[{"name":"","instructions":"","dose":""}],
 "next_session_target":"one measurable goal"
}
Use 3–8 meaningful sections depending on recording length. Be strict: praise only specific strengths. Do not fabricate numeric accuracy percentages or exact cents. For scores, 5 means developing, 7 means solid, 9 means excellent; explain evidence and uncertainty.''' 

@app.post('/api/analyze')
async def analyze(performance: UploadFile = File(...), reference: Optional[UploadFile] = File(None), song_title: str = Form(''), lyrics: str = Form(''), assessment_mode: str = Form('both')):
    key = os.getenv('OPENAI_API_KEY')
    if not key: raise HTTPException(503, 'AI server is not configured: add OPENAI_API_KEY as a server environment variable.')
    perf_data, perf_fmt = await read_audio(performance)
    content = [{'type':'text','text':f'''Assess this singer. Song/exercise: {song_title or 'not specified'}. Assessment mode: {assessment_mode}. User-supplied target lyrics (may be incomplete): {lyrics[:7000] if lyrics else 'not supplied'}. First audio is the singer performance. If a second audio follows, it is the reference/original recording. Listen carefully. Provide the required JSON report with section-by-section observations and confidence. Do not claim exact note-level comparison if the reference is a dense mix or the evidence is unclear.'''}]
    content.append({'type':'input_audio','input_audio':{'data':base64.b64encode(perf_data).decode('ascii'),'format':perf_fmt}})
    if reference is not None:
        ref_data, ref_fmt = await read_audio(reference)
        content.append({'type':'text','text':'The following audio is the reference/original recording for comparison.'})
        content.append({'type':'input_audio','input_audio':{'data':base64.b64encode(ref_data).decode('ascii'),'format':ref_fmt}})
    client = OpenAI(api_key=key)
    try:
        result = client.chat.completions.create(
            model=MODEL,
            modalities=['text'],
            messages=[{'role':'system','content':SYSTEM_PROMPT},{'role':'user','content':content}],
            store=False,
        )
        text = result.choices[0].message.content or ''
        match = re.search(r'\{.*\}', text, re.S)
        if not match: raise ValueError('Model did not return the expected JSON report.')
        report = json.loads(match.group(0))
        if reference is None: report['reference_comparison'] = None
        report['model_used'] = MODEL
        report['notice'] = 'AI listening feedback is an aid, not a certified vocal diagnosis. Verify timestamped findings by replaying the recording.'
        return report
    except Exception as exc:
        raise HTTPException(502, f'Audio analysis failed: {str(exc)[:500]}')
