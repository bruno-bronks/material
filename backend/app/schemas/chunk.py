from pydantic import BaseModel


class ChunkMetadata(BaseModel):
    source: str = ""
    material: str = ""
    application: str = ""
    temperature_range: str = ""
    year: str = ""
    authors: str = ""
    doi: str = ""
    keywords: list[str] = []
