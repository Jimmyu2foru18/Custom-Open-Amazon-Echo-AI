from __future__ import annotations

import re
from typing import Literal

import httpx
from duckduckgo_search import DDGS

from app.config import settings

try:
    import google.generativeai as genai
except Exception:  # pragma: no cover - optional at runtime
    genai = None

Route = Literal['openclaw_remote', 'web_search+gemini', 'gemini', 'ollama', 'fallback']


class AgentRouter:
    """OpenClaw-style orchestration: tool selection + model routing."""

    WEB_SEARCH_HINTS = {
        'search',
        'look up',
        'lookup',
        'find',
        'latest',
        'news',
        'current',
        'today',
        'weather',
        'price',
    }

    HARD_HINTS = {
        'explain',
        'compare',
        'analyze',
        'strategy',
        'plan',
        'pros and cons',
        'tradeoffs',
    }

    def __init__(self) -> None:
        if settings.google_api_key and genai:
            genai.configure(api_key=settings.google_api_key)

    async def run(self, query: str) -> tuple[str, Route]:
        cleaned_query = ' '.join(query.split())

        if settings.openclaw_base_url:
            external = await self._call_openclaw_remote(cleaned_query)
            if external:
                return external, 'openclaw_remote'

        needs_search = settings.enable_web_search and self._needs_search(cleaned_query)
        hard = self._is_hard_query(cleaned_query)

        if needs_search:
            snippets = self._search_web(cleaned_query)
            prompt = self._build_search_prompt(cleaned_query, snippets)
            answer = await self._ask_gemini(prompt)
            if answer:
                return answer, 'web_search+gemini'

        if hard:
            answer = await self._ask_gemini(cleaned_query)
            if answer:
                return answer, 'gemini'

        answer = await self._ask_ollama(cleaned_query)
        if answer:
            return answer, 'ollama'

        fallback = await self._ask_gemini(cleaned_query)
        if fallback:
            return fallback, 'fallback'

        return (
            'Sorry, I could not reach either local or cloud models right now. '
            'Please check Ollama and Gemini settings and try again.',
            'fallback',
        )

    async def _call_openclaw_remote(self, query: str) -> str | None:
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.post(
                    f"{settings.openclaw_base_url.rstrip('/')}/chat",
                    json={'text': query},
                )
                response.raise_for_status()
            data = response.json()
            return data.get('answer') or data.get('response')
        except Exception:
            return None

    def _needs_search(self, query: str) -> bool:
        lowered = query.lower()
        if any(hint in lowered for hint in self.WEB_SEARCH_HINTS):
            return True
        return bool(re.search(r'\b(who|what|when|where)\b', lowered))

    def _is_hard_query(self, query: str) -> bool:
        lowered = query.lower()
        word_count = len(lowered.split())
        has_hard_hint = any(hint in lowered for hint in self.HARD_HINTS)
        return has_hard_hint or word_count >= settings.hard_query_word_threshold

    def _search_web(self, query: str) -> list[str]:
        snippets: list[str] = []
        try:
            with DDGS() as ddgs:
                for result in ddgs.text(query, max_results=settings.search_results_limit):
                    title = result.get('title', 'Untitled')
                    body = result.get('body', '')
                    href = result.get('href', '')
                    snippets.append(f"- {title}: {body} ({href})")
        except Exception:
            return []
        return snippets

    async def _ask_ollama(self, query: str) -> str | None:
        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                response = await client.post(
                    f"{settings.ollama_base_url.rstrip('/')}/api/generate",
                    json={
                        'model': settings.ollama_model,
                        'prompt': query,
                        'stream': False,
                    },
                )
                response.raise_for_status()
            data = response.json()
            return data.get('response', '').strip() or None
        except Exception:
            return None

    async def _ask_gemini(self, query: str) -> str | None:
        if not settings.google_api_key or not genai:
            return None

        try:
            model = genai.GenerativeModel(settings.gemini_model)
            response = await model.generate_content_async(query)
            text = getattr(response, 'text', None)
            return text.strip() if text else None
        except Exception:
            return None

    def _build_search_prompt(self, query: str, snippets: list[str]) -> str:
        if not snippets:
            return query
        joined = '\n'.join(snippets)
        return (
            'You are helping an Alexa voice assistant. Use the web snippets to answer clearly in under 3 short sentences. '
            'If uncertainty exists, say so.\n\n'
            f'User question: {query}\n\n'
            f'Web snippets:\n{joined}'
        )
