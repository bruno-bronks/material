import os
import shutil
import tempfile

import pytest

_tmp_dir: str | None = None


def pytest_configure(config):
    """Roda antes de qualquer import de módulo de teste — isola Chroma/SQLite num
    diretório temporário, pra testes não escreverem nos dados de desenvolvimento
    em backend/data/. Precisa rodar antes de qualquer chamada a get_settings()."""
    global _tmp_dir
    _tmp_dir = tempfile.mkdtemp(prefix="materialgpt_test_")
    os.environ["CHROMA_PERSIST_DIR"] = os.path.join(_tmp_dir, "chroma")
    os.environ["DATABASE_URL"] = f"sqlite:///{os.path.join(_tmp_dir, 'test.db')}"


def pytest_unconfigure(config):
    if _tmp_dir:
        shutil.rmtree(_tmp_dir, ignore_errors=True)


@pytest.fixture()
def client():
    # Import local (não no topo do módulo): app.main importa app.memory.db, que
    # constrói a engine do SQLite no import — precisa rodar depois do
    # pytest_configure já ter setado DATABASE_URL.
    from fastapi.testclient import TestClient

    from app.main import app

    with TestClient(app) as test_client:
        yield test_client
