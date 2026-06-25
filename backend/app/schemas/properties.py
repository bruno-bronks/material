from pydantic import BaseModel


class PropertySchema(BaseModel):
    hardness: float
    density: float
    conductivity: float
    elastic_modulus: float
