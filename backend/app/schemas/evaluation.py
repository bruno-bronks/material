from pydantic import BaseModel, Field


class EvaluationScore(BaseModel):
    relevance: int = Field(ge=1, le=5, description="A resposta de fato responde à pergunta feita?")
    faithfulness: int = Field(
        ge=1, le=5, description="A resposta é internamente consistente com os dados/fontes que ela mesma cita?"
    )
    hallucination_risk: int = Field(
        ge=1,
        le=5,
        description="1 = afirmações fundamentadas em dados citados; 5 = números/fatos sem fonte aparente",
    )
    confidence_calibration: int = Field(
        ge=1, le=5, description="Quando a resposta declara confiança, ela é coerente com a evidência apresentada?"
    )
    passed: bool = Field(description="Veredito geral: atende ao padrão mínimo de qualidade científica?")
    reasoning: str = Field(description="Justificativa breve e objetiva do veredito")
