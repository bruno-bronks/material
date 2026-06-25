from pydantic import BaseModel


class PaperSchema(BaseModel):
    title: str
    authors: list[str]
    year: int
    doi: str
    abstract: str


class PaperOutput(BaseModel):
    title: str
    authors: list[str]
    year: int
    doi: str
