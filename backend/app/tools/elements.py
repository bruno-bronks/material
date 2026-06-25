import re

ELEMENT_SYMBOLS = {
    "H", "He", "Li", "Be", "B", "C", "N", "O", "F", "Ne", "Na", "Mg", "Al", "Si",
    "P", "S", "Cl", "Ar", "K", "Ca", "Sc", "Ti", "V", "Cr", "Mn", "Fe", "Co",
    "Ni", "Cu", "Zn", "Ga", "Ge", "As", "Se", "Br", "Kr", "Rb", "Sr", "Y", "Zr",
    "Nb", "Mo", "Tc", "Ru", "Rh", "Pd", "Ag", "Cd", "In", "Sn", "Sb", "Te", "I",
    "Xe", "Cs", "Ba", "La", "Ce", "Hf", "Ta", "W", "Re", "Os", "Ir", "Pt", "Au",
    "Hg", "Tl", "Pb", "Bi",
}

# Termos comuns em português que mapeiam para o elemento predominante.
# Cobertura intencionalmente pequena (apenas o suficiente para acionar
# Materials Project / OQMD / AFLOW em consultas em linguagem natural);
# não substitui um NER científico de fato.
PT_KEYWORDS = {
    "titânio": "Ti", "titanio": "Ti",
    "alumínio": "Al", "aluminio": "Al",
    "aço": "Fe", "aco": "Fe", "ferro": "Fe",
    "níquel": "Ni", "niquel": "Ni",
    "cromo": "Cr",
    "cobre": "Cu",
    "lítio": "Li", "litio": "Li",
    "sódio": "Na", "sodio": "Na",
    "silício": "Si", "silicio": "Si",
    "grafeno": "C", "carbono": "C", "diamante": "C",
    "zinco": "Zn",
    "magnésio": "Mg", "magnesio": "Mg",
    "vanádio": "V", "vanadio": "V",
    "tungstênio": "W", "tungstenio": "W",
    "molibdênio": "Mo", "molibdenio": "Mo",
    "cobalto": "Co",
    "manganês": "Mn", "manganes": "Mn",
    "estanho": "Sn",
    "ouro": "Au",
    "prata": "Ag",
    "platina": "Pt",
    "oxigênio": "O", "oxigenio": "O",
    "nitrogênio": "N", "nitrogenio": "N",
    "hidrogênio": "H", "hidrogenio": "H",
    "enxofre": "S",
    "boro": "B",
    "zircônio": "Zr", "zirconio": "Zr",
    "chumbo": "Pb",
}

_FORMULA_TOKEN_RE = re.compile(r"\b(?:[A-Z][a-z]?\d*){2,6}\b")
_ELEMENT_TOKEN_RE = re.compile(r"[A-Z][a-z]?")


def extract_formula(text: str) -> str | None:
    """Encontra algo que pareça uma fórmula química explícita (ex: Ti6Al4V)."""
    for candidate in _FORMULA_TOKEN_RE.findall(text):
        tokens = _ELEMENT_TOKEN_RE.findall(candidate)
        if tokens and all(token in ELEMENT_SYMBOLS for token in tokens):
            return candidate
    return None


def extract_elements(text: str) -> list[str]:
    """Extrai elementos citados por nome (PT) ou por fórmula explícita."""
    lowered = text.lower()
    found = {symbol for keyword, symbol in PT_KEYWORDS.items() if keyword in lowered}

    formula = extract_formula(text)
    if formula:
        found.update(_ELEMENT_TOKEN_RE.findall(formula))

    return sorted(found)
