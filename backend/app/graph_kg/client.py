from functools import lru_cache

from neo4j import GraphDatabase

from app.config import get_settings


@lru_cache
def get_driver():
    settings = get_settings()
    if not settings.neo4j_enabled:
        return None
    return GraphDatabase.driver(settings.neo4j_uri, auth=(settings.neo4j_user, settings.neo4j_password))


def query_related(material_name: str) -> list[dict]:
    """Graph RAG: Material -> Element -> Structure -> Properties -> Applications -> Paper.

    Sem NEO4J_URI configurado, este node é um no-op (retorna lista vazia) —
    o Knowledge Graph é tratado como infraestrutura opcional no V1.
    """
    driver = get_driver()
    if driver is None:
        return []

    cypher = """
    MATCH (m:Material {name: $name})-[*1..4]-(related)
    RETURN DISTINCT labels(related) AS labels, related.name AS name
    LIMIT 25
    """
    with driver.session() as session:
        records = session.run(cypher, name=material_name)
        return [{"labels": record["labels"], "name": record["name"]} for record in records]
