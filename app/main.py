from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.agent import AgentRouter
from app.alexa import extract_user_utterance
from app.config import settings
from app.models import (
    AlexaOutputSpeech,
    AlexaReprompt,
    AlexaResponseBody,
    AlexaResponseEnvelope,
    ChatRequest,
    ChatResponse,
)

app = FastAPI(title='Echo Agent Bridge', version='0.1.0')
router = AgentRouter()


@app.get('/health')
async def health() -> dict[str, str]:
    return {'status': 'ok'}


@app.post('/v1/chat', response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    answer, route = await router.run(request.text)
    return ChatResponse(answer=answer, route=route)


@app.post('/alexa')
async def alexa_webhook(payload: dict) -> JSONResponse:
    utterance = extract_user_utterance(payload)
    answer, _route = await router.run(utterance)

    response = AlexaResponseEnvelope(
        response=AlexaResponseBody(
            outputSpeech=AlexaOutputSpeech(text=answer),
            reprompt=AlexaReprompt(outputSpeech=AlexaOutputSpeech(text='Anything else?')),
            shouldEndSession=False,
        )
    )
    return JSONResponse(content=response.model_dump())


if __name__ == '__main__':
    import uvicorn

    uvicorn.run('app.main:app', host=settings.host, port=settings.port, reload=False)
