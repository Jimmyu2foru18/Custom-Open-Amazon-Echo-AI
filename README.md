# Custom Open Amazon Echo AI (Prototype) WIP

A working starter prototype that lets an Amazon Echo/Alexa skill send speech requests to your own Python backend, route the request through an OpenClaw-style agent flow, and return spoken answers.

## What this prototype does

- Accepts Alexa requests at `POST /alexa`
- Provides a direct test API at `POST /v1/chat` (no Alexa required)
- Routes tasks with an OpenClaw-style orchestration policy:
  - **Simple / fast** tasks → local **Ollama + Phi-3**
  - **Hard reasoning** tasks → **Gemini 1.5 Flash**
  - **Voice-activated web search** → DuckDuckGo snippets + Gemini synthesis
- Supports an optional external OpenClaw service endpoint (`OPENCLAW_BASE_URL`) if you have one

---

## 1) Prerequisites

- Python 3.11+
- [Ollama](https://ollama.com/download)
- Amazon Developer account (for Alexa skill)
- [ngrok](https://ngrok.com/) (or similar tunnel)

Pull a small local model for ~4GB VRAM setups:

```bash
ollama pull phi3:mini
```

---

## 2) Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env`:

- Set `GOOGLE_API_KEY` for Gemini
- Confirm `OLLAMA_MODEL=phi3:mini`
- Optional: set `OPENCLAW_BASE_URL` if you run OpenClaw elsewhere

Start backend:

```bash
python -m app.main
```

Health check:

```bash
curl http://localhost:5000/health
```

---

## 3) Test without Alexa first

### Option A: curl

```bash
curl -X POST http://localhost:5000/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"text":"Search latest updates on reusable rockets and summarize"}'
```

### Option B: helper script

```bash
python scripts/test_backend.py "Explain the difference between TLS 1.2 and TLS 1.3"
```

---

## 4) Expose backend to Alexa (ngrok)

In another terminal:

```bash
ngrok http 5000
```

Copy the HTTPS forwarding URL (for example `https://abc123.ngrok-free.app`) and use:

- Alexa endpoint URL: `https://abc123.ngrok-free.app/alexa`

---

## 5) Alexa Skill quick wiring

In Amazon Developer Console:

1. Create a custom skill.
2. Add an intent (example: `ChatIntent`) with a slot (example: `SearchQuery`) and sample utterances like:
   - `ask agent {SearchQuery}`
   - `search for {SearchQuery}`
   - `tell me {SearchQuery}`
3. In Endpoint settings, set HTTPS endpoint to your ngrok URL + `/alexa`.
4. Save/build and test in developer console.

The backend reads slot values from `SearchQuery`, `query`, or `text`.

---

## 6) Routing behavior (OpenClaw-style)

- Search-style requests (`search`, `latest`, `news`, etc.) trigger web tool usage.
- Longer or analysis-heavy prompts route to Gemini 1.5 Flash.
- Short/simple prompts prefer local Ollama Phi-3 for speed.
- If one model is unavailable, the backend falls back where possible.

---

## Notes

- This is a prototype. For production Alexa skills, add request signature/certificate validation and tighter auth/rate-limits.
- If Gemini is not configured, hard/cloud routes will be skipped.
