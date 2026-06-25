from app.schemas.discovery import CriticVerdict, SubstitutionTarget
from app.schemas.materials import CompareOutput, MaterialCandidate, MaterialSchema
from app.schemas.papers import PaperSchema
from app.schemas.properties import PropertySchema


def test_material_schema():
    schema = MaterialSchema(
        material_name="Ti6Al4V",
        composition="Ti6Al4V",
        density=4.43,
        max_temperature=950.0,
        conductivity=7.2,
        confidence=0.91,
    )
    assert schema.material_name == "Ti6Al4V"
    assert schema.confidence == 0.91


def test_material_candidate_lists():
    candidate = MaterialCandidate(
        material_name="Ti6Al4V",
        confidence=0.9,
        advantages=["leve"],
        disadvantages=["caro"],
        applications=["aeroespacial"],
    )
    assert candidate.advantages == ["leve"]


def test_compare_output():
    result = CompareOutput(winner="Ti6Al4V", explanation="melhor relação peso/resistência", confidence=0.8)
    assert result.winner == "Ti6Al4V"


def test_paper_schema():
    paper = PaperSchema(title="X", authors=["A", "B"], year=2024, doi="10.1/x", abstract="...")
    assert paper.year == 2024


def test_property_schema():
    props = PropertySchema(hardness=120.0, density=4.5, conductivity=7.2, elastic_modulus=110.0)
    assert props.hardness == 120.0


def test_substitution_target():
    target = SubstitutionTarget(element_from="Au", rationale="caro e pesado")
    assert target.element_from == "Au"


def test_critic_verdict():
    verdict = CriticVerdict(accepted=False, reasons=["instável"])
    assert verdict.accepted is False
    assert verdict.reasons == ["instável"]
