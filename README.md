# Kopi Debate Chatbot API

FastAPI service that hosts a persuasive debate bot which maintains a consistent stance for the entire conversation.

## Quickstart

```bash
make install
make run
# API at http://localhost:8000
```

### Endpoints
- `GET /healthz` → `{ "status": "ok" }`
- `POST /chat` → per challenge spec.

**Start conversation:**
```bash
curl -s localhost:8000/chat -H 'content-type: application/json'   -d '{"conversation_id": null, "message": "hello"}' | jq
```
**Continue:**
```bash
curl -s localhost:8000/chat -H 'content-type: application/json'   -d '{"conversation_id": "<the id>", "message": "I disagree"}' | jq
```

## Environment
- `ENGINE_BACKEND` (default: `local`). Set to `openai` to use OpenAI.
- `OPENAI_API_KEY` (required if `ENGINE_BACKEND=openai`).
- `OPENAI_MODEL` (default: `gpt-4o-mini`).
- `REDIS_URL` (default: `redis://redis:6379/0`).
- `RESPONSE_TIMEOUT` seconds (default: `25`).

## Make targets
See `make`.

## Tests
```bash
make test
```

## Deployment
- Build & run with Docker Compose (see `make run`). For a public URL, deploy behind a reverse proxy or use a PaaS (Fly.io, Railway, Render). Expose port 8000.
