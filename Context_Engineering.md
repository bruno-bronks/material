# MaterialGPT

# Parte 2 — Context Engineering

---

# 3. Context Engineering

O Context Engineering é a camada responsável por fornecer conhecimento científico ao sistema.

Seu objetivo é garantir que as respostas sejam fundamentadas em:

* bases de materiais;
* artigos científicos;
* estruturas cristalinas;
* propriedades físico-químicas;
* conhecimento acumulado em ciência dos materiais.

---

# Objetivos

Fornecer contexto para:

* descoberta de materiais;
* comparação entre materiais;
* explicação de propriedades;
* busca de literatura;
* predição de propriedades;
* futuras simulações.

---

# Fontes de Dados

## Materials Project

Principal fonte do sistema.

Contém aproximadamente:

* 150 mil materiais.

Informações disponíveis:

* estrutura cristalina;
* energia de formação;
* band gap;
* densidade;
* estabilidade;
* composição química.

---

## OQMD

Open Quantum Materials Database.

Possui:

* aproximadamente 1 milhão de estruturas.

Informações:

* termodinâmica;
* energia;
* estabilidade.

---

## AFLOW

Automatic Flow for Materials Discovery.

Contém:

* milhões de composições.

Informações:

* propriedades eletrônicas;
* estruturas cristalinas;
* parâmetros de rede.

---

## PubChem

Base química.

Contém:

* mais de 111 milhões de compostos.

Informações:

* moléculas;
* propriedades químicas;
* identificadores.

---

## arXiv

Pré-publicações científicas.

Áreas:

* Materials Science;
* Condensed Matter;
* Physics;
* Quantum Physics.

---

## Nature

Artigos científicos revisados.

---

## Springer

Literatura científica.

---

## Semantic Scholar

Papers e referências.

---

## Crossref

DOIs e metadados.

---

# Estratégia de Ingestão

```text id="0bmxn0"
APIs
↓
Raw Data
↓
Normalization
↓
Chunking
↓
Embeddings
↓
Vector Database
↓
RAG
```

---

# Pipeline ETL

```text id="2lh0u9"
Extract
↓
Transform
↓
Validate
↓
Enrich
↓
Store
```

---

# Estrutura do Conhecimento

## Knowledge Graph

Banco:

Neo4j

---

### Entidades

#### Material

Exemplo:

```text id="0otuj8"
Ti6Al4V
```

---

#### Elemento

Exemplo:

```text id="evw2j9"
Ti
Al
V
```

---

#### Estrutura Cristalina

Exemplo:

```text id="m5h0zl"
FCC
BCC
Hexagonal
```

---

#### Propriedades

Exemplo:

* densidade;
* dureza;
* módulo de elasticidade;
* condutividade;
* temperatura máxima.

---

#### Aplicações

Exemplo:

* baterias;
* turbinas;
* células solares;
* semicondutores.

---

#### Papers

Artigos relacionados.

---

# Relacionamentos

```text id="7i4jtp"
Material
↓
Elemento
↓
Estrutura Cristalina
↓
Propriedades
↓
Aplicações
↓
Artigos
```

---

# Exemplo

```text id="m4tw2v"
Ti6Al4V
↓
Titânio
↓
Hexagonal
↓
Alta resistência
↓
Aeroespacial
↓
Papers
```

---

# Banco Vetorial

## Pinecone

Responsável por:

* embeddings;
* recuperação semântica;
* busca por similaridade.

---

Alternativas:

* Qdrant;
* Weaviate;
* pgvector.

---

# Memória Estruturada

## PostgreSQL

Armazenará:

* perguntas;
* resultados;
* histórico;
* feedback;
* rankings.

---

# Embeddings

## OpenAI Embeddings

ou

## Qwen3-Embedding

ou

## BGE-M3

---

# Estratégia de Chunking

## Papers

Chunk size:

```python id="g8y36x"
1500 tokens
```

Overlap:

```python id="svr0i0"
300 tokens
```

---

## Materiais

Chunk size:

```python id="6w6b06"
500 tokens
```

---

## Summaries

Chunk size:

```python id="xk0u0w"
300 tokens
```

---

# Metadados

Cada chunk armazenará:

```json id="4rjlwm"
{
    "source": "",
    "material": "",
    "application": "",
    "temperature_range": "",
    "year": "",
    "authors": "",
    "doi": "",
    "keywords": []
}
```

---

# RAG Hierárquico

```text id="3bxr9v"
User
↓
Question Understanding
↓
Papers
↓
Materials
↓
Knowledge Graph
↓
Summaries
↓
LLM
```

---

# Multi-RAG

## Literature RAG

Busca artigos científicos.

---

## Materials RAG

Busca materiais.

---

## Property RAG

Busca propriedades.

---

## Application RAG

Busca aplicações.

---

## Graph RAG

Consulta relações do Neo4j.

---

# Context Builder

Responsável por montar o contexto final.

```text id="2k9v5m"
Question
↓
Material RAG
↓
Paper RAG
↓
Graph RAG
↓
Merge
↓
Ranking
↓
Prompt
```

---

# Schemas

## MaterialSchema

```python id="nq0c0m"
class MaterialSchema(BaseModel):

    material_name: str

    composition: str

    density: float

    max_temperature: float

    conductivity: float

    confidence: float
```

---

## PaperSchema

```python id="6x8vut"
class PaperSchema(BaseModel):

    title: str

    authors: list

    year: int

    doi: str

    abstract: str
```

---

## PropertySchema

```python id="pq03kq"
class PropertySchema(BaseModel):

    hardness: float

    density: float

    conductivity: float

    elastic_modulus: float
```

---

# Context Compression

Objetivo:

Reduzir tokens.

Pipeline:

```text id="2t1a7y"
Documents
↓
Summaries
↓
Compression
↓
Re-ranking
↓
Prompt
```

---

# Re-ranking

Modelos:

* Cohere Rerank;
* BGE Reranker;
* Cross Encoder.

---

# Long-Term Memory

Persistência de:

* perguntas;
* materiais pesquisados;
* feedback do usuário;
* histórico de sessões.

---

# Short-Term Memory

Contexto atual da conversa.

---

# Future Memory

No futuro:

```text id="r5tx8w"
Experimentos
↓
Resultados
↓
Aprendizado
↓
Knowledge Graph
↓
Novas Hipóteses
```

---

# Objetivo Final

Construir uma memória científica capaz de integrar:

* materiais;
* literatura;
* propriedades;
* aplicações;
* conhecimento estrutural.

Essa memória será a base do futuro agente científico do MaterialGPT.
