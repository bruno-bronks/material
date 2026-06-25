from pydantic import BaseModel, Field

# Categorias combinadas dos exemplos de "Aplicações" em Context_Engineering.md e Design_docs.md.
APPLICATION_CATEGORIES = [
    "baterias",
    "aeroespacial",
    "semicondutores",
    "química e catalisadores",
    "petróleo e gás",
    "energia solar",
    "automotivo",
    "biomédico",
    "outro",
]


class ContentEnrichment(BaseModel):
    keywords: list[str] = Field(description="3 a 6 termos científicos-chave do texto")
    application: str = Field(description="uma das categorias controladas fornecidas no prompt")
    summary: str = Field(description="resumo objetivo em 2-3 frases, só com informação do texto original")
