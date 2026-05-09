from pydantic import BaseModel


class ChatRequest(BaseModel):
    text: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    answer: str
    route: str


class AlexaOutputSpeech(BaseModel):
    type: str = 'PlainText'
    text: str


class AlexaReprompt(BaseModel):
    outputSpeech: AlexaOutputSpeech


class AlexaResponseBody(BaseModel):
    outputSpeech: AlexaOutputSpeech
    shouldEndSession: bool = False
    reprompt: AlexaReprompt | None = None


class AlexaResponseEnvelope(BaseModel):
    version: str = '1.0'
    response: AlexaResponseBody
