from pydantic import BaseModel


class MaterialSchema(BaseModel):
    material_name: str
    composition: str
    density: float
    max_temperature: float
    conductivity: float
    confidence: float


class MaterialOutput(BaseModel):
    material_name: str
    composition: str
    density: float
    confidence: float


class MaterialCandidate(BaseModel):
    material_name: str
    confidence: float
    advantages: list[str]
    disadvantages: list[str]
    applications: list[str]


class CompareOutput(BaseModel):
    winner: str
    explanation: str
    confidence: float
