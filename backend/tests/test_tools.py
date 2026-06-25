import pytest

from app.tools import aflow, arxiv, crossref, oqmd, pubchem

pytestmark = pytest.mark.network


def test_oqmd_search_by_composition():
    results = oqmd.search_by_composition("TiAl", limit=2)
    assert results
    assert results[0]["source"] == "oqmd"


def test_aflow_search_by_species():
    results = aflow.search_by_species(["Ti"], limit=2)
    assert results
    assert results[0]["source"] == "aflow"


def test_pubchem_search_by_name():
    results = pubchem.search_by_name("aspirin")
    assert results
    assert results[0]["composition"]


def test_crossref_search_works():
    results = crossref.search_works("titanium alloy corrosion", limit=2)
    assert results
    assert results[0]["source"] == "crossref"


def test_arxiv_search_papers():
    results = arxiv.search_papers("graphene", limit=2)
    assert results
    assert results[0]["source"] == "arxiv"
