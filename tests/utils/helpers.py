import json


class MatchAny:
    def __eq__(self, _: object) -> bool:
        return True


def parse_sse_events(text: str) -> list[dict]:
    """Parse SSE response text into a list of events with 'event' and 'data' keys."""
    events = []
    current: dict = {}
    for line in text.splitlines():
        if line.startswith("event:"):
            current["event"] = line[len("event:") :].strip()
        elif line.startswith("data:"):
            current["data"] = json.loads(line[len("data:") :].strip())
        elif line == "" and current:
            events.append(current)
            current = {}
    if current:
        events.append(current)
    return events
