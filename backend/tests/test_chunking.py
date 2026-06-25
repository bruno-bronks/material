from app.rag.chunking import chunk_text


def test_chunk_text_empty():
    assert chunk_text("", kind="paper") == []


def test_chunk_text_short_single_chunk():
    text = "Ti6Al4V é uma liga de titânio amplamente usada em turbinas."
    chunks = chunk_text(text, kind="material")
    assert len(chunks) == 1


def test_chunk_text_paper_splits_long_text():
    text = "palavra cientifica sobre materiais " * 1000
    chunks = chunk_text(text, kind="paper")
    assert len(chunks) > 1


def test_chunk_text_respects_overlap_config():
    from app.rag.chunking import CHUNK_CONFIG

    assert CHUNK_CONFIG["paper"] == {"chunk_size": 1500, "overlap": 300}
    assert CHUNK_CONFIG["material"] == {"chunk_size": 500, "overlap": 0}
    assert CHUNK_CONFIG["summary"] == {"chunk_size": 300, "overlap": 0}
