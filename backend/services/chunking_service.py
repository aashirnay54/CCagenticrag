CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200


def chunk_text(text: str) -> list[str]:
    separators = ["\n\n", "\n", ". ", " "]

    def _split(text: str, seps: list[str]) -> list[str]:
        if not seps:
            return [text[i:i + CHUNK_SIZE] for i in range(0, len(text), CHUNK_SIZE - CHUNK_OVERLAP)]
        parts = [s.strip() for s in text.split(seps[0]) if s.strip()]
        result = []
        for part in parts:
            if len(part) <= CHUNK_SIZE:
                result.append(part)
            else:
                result.extend(_split(part, seps[1:]))
        return result

    raw = _split(text, separators)
    merged, current = [], ""
    for piece in raw:
        if not current:
            current = piece
        elif len(current) + len(piece) + 1 <= CHUNK_SIZE:
            current += " " + piece
        else:
            merged.append(current)
            current = current[-CHUNK_OVERLAP:] + " " + piece
    if current:
        merged.append(current)
    return [c for c in merged if c.strip()]
