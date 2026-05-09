from typing import Any


def extract_user_utterance(payload: dict[str, Any]) -> str:
    request = payload.get('request', {})
    request_type = request.get('type')

    if request_type == 'LaunchRequest':
        return 'Hello'

    if request_type == 'IntentRequest':
        intent = request.get('intent', {})
        slots = intent.get('slots', {})
        for key in ('SearchQuery', 'query', 'text'):
            slot = slots.get(key, {})
            value = slot.get('value')
            if value:
                return str(value)

        spoken = intent.get('name', '').replace('Intent', '').strip()
        return spoken or 'Help me'

    return 'Help me'
