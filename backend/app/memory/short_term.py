"""Short-Term Memory: contexto da sessão atual, mantido em processo."""

_SHORT_TERM: dict[str, list[dict]] = {}


def append_turn(session_id: str, question: str, intent: str, report: str) -> None:
    _SHORT_TERM.setdefault(session_id, []).append(
        {"question": question, "intent": intent, "report": report}
    )


def get_history(session_id: str) -> list[dict]:
    return _SHORT_TERM.get(session_id, [])
