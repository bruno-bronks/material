import tiktoken

_ENCODING = tiktoken.get_encoding("cl100k_base")

# Tamanhos conforme Context_Engineering.md / ToolCalling_Memory_RAG.md
CHUNK_CONFIG = {
    "paper": {"chunk_size": 1500, "overlap": 300},
    "material": {"chunk_size": 500, "overlap": 0},
    "summary": {"chunk_size": 300, "overlap": 0},
}


def chunk_text(text: str, kind: str = "paper") -> list[str]:
    config = CHUNK_CONFIG[kind]
    chunk_size = config["chunk_size"]
    overlap = config["overlap"]

    tokens = _ENCODING.encode(text)
    if not tokens:
        return []

    chunks = []
    step = chunk_size - overlap
    for start in range(0, len(tokens), step):
        chunk_tokens = tokens[start : start + chunk_size]
        chunks.append(_ENCODING.decode(chunk_tokens))
        if start + chunk_size >= len(tokens):
            break
    return chunks
