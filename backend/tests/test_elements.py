from app.tools.elements import extract_elements, extract_formula


def test_extract_formula_explicit():
    assert extract_formula("Ti6Al4V") == "Ti6Al4V"


def test_extract_formula_none_for_plain_text():
    assert extract_formula("um material resistente à corrosão") is None


def test_extract_elements_from_pt_keyword():
    assert "Ti" in extract_elements("preciso de titânio para uma turbina")


def test_extract_elements_from_formula():
    elements = set(extract_elements("Ti6Al4V é uma liga aeroespacial"))
    assert {"Ti", "Al", "V"}.issubset(elements)


def test_extract_elements_empty_for_unrelated_text():
    assert extract_elements("qual o clima hoje") == []
