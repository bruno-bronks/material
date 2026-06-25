# MaterialGPT

# Parte 4 — Tool Calling, Memory e RAG

---

# 6. Tool Calling

A camada de Tool Calling é responsável por conectar o agente científico ao mundo externo.

Objetivos:

* consultar bancos de materiais;
* recuperar literatura científica;
* executar simulações;
* enriquecer contexto;
* produzir respostas fundamentadas.

---

# Arquitetura

```text id="5h0d5f"
Agent
↓
Tool Router
↓
────────────────────
Literature Tools
Material Tools
Simulation Tools
Graph Tools
Memory Tools
────────────────────
↓
Results
↓
Aggregator
↓
LLM
```

---

# Literature Tools

---

## Semantic Scholar

Objetivo:

Recuperar artigos científicos.

Retorna:

* título;
* autores;
* resumo;
* citações;
* DOI.

---

## Crossref

Objetivo:

Consultar:

* DOI;
* metadados;
* revistas.

---

## arXiv

Objetivo:

Recuperar preprints.

Áreas:

* Materials Science;
* Physics;
* Quantum Physics;
* Condensed Matter.

---

## Springer

Objetivo:

Literatura científica.

---

## Nature

Objetivo:

Artigos revisados.

---

# Material Databases

---

## Materials Project API

Principal ferramenta do sistema.

Informações:

* composição;
* estrutura cristalina;
* band gap;
* energia de formação;
* estabilidade;
* densidade.

---

## OQMD

Open Quantum Materials Database.

Informações:

* termodinâmica;
* energia;
* estabilidade.

---

## AFLOW API

Informações:

* propriedades eletrônicas;
* estruturas cristalinas;
* parâmetros de rede.

---

## PubChem

Informações:

* moléculas;
* propriedades químicas;
* identificadores.

---

# Simulation Tools

---

## ASE

Atomic Simulation Environment.

Objetivo:

Construção e manipulação de estruturas atômicas.

Funções:

* criação de células unitárias;
* interfaces para DFT;
* otimizações.

---

## Quantum ESPRESSO

Objetivo:

DFT (Density Functional Theory).

Usado para:

* energia total;
* estrutura eletrônica;
* estabilidade.

---

## LAMMPS

Objetivo:

Dinâmica Molecular.

Usado para:

* temperatura;
* pressão;
* difusão;
* deformação.

---

## pymatgen

Objetivo:

Manipulação de materiais.

Funções:

* parsing;
* análise;
* geração de estruturas.

---

# Future Tools

---

## Graph Neural Networks

Predição de propriedades.

---

## Crystal Graph Networks

Representação cristalina.

---

## Transformer Models

Foundation Models para materiais.

---

## Quantum Computing

Simulações quânticas futuras.

---

# Tool Router

Objetivo:

Selecionar automaticamente ferramentas.

Fluxo:

```text id="n0vzph"
Question
↓
Intent
↓
Tool Router
↓
Tool Execution
↓
Aggregation
```

---

# Tool Selection

## Material Search

Ferramentas:

```python id="e4e90e"
Materials Project

OQMD

AFLOW
```

---

## Paper Search

Ferramentas:

```python id="cg5plu"
Semantic Scholar

Crossref

arXiv
```

---

## Simulation

Ferramentas:

```python id="pkh7p2"
ASE

Quantum ESPRESSO

LAMMPS
```

---

## Explanation

Ferramentas:

```python id="4e2aez"
RAG

Knowledge Graph
```

---

# Structured Tool Outputs

## MaterialOutput

```python id="abv9hl"
class MaterialOutput(BaseModel):

    material_name: str

    composition: str

    density: float

    confidence: float
```

---

## PaperOutput

```python id="7a2n7n"
class PaperOutput(BaseModel):

    title: str

    authors: list

    year: int

    doi: str
```

---

# 7. Memory / RAG

Objetivo:

Construir uma memória científica persistente.

---

# Arquitetura

```text id="4a5e4o"
User
↓
Retriever
↓
──────────────────
Papers
Materials
Knowledge Graph
Memory
──────────────────
↓
Context Builder
↓
LLM
```

---

# Banco Vetorial

## Pinecone

Responsável por:

* embeddings;
* similaridade semântica;
* recuperação de contexto.

---

Alternativas:

* Qdrant;
* Weaviate;
* pgvector.

---

# Knowledge Graph

Banco:

Neo4j

---

Relacionamentos:

```text id="jgv81e"
Material
↓
Element
↓
Structure
↓
Properties
↓
Applications
↓
Paper
```

---

# Banco Relacional

## PostgreSQL

Armazenará:

* usuários;
* sessões;
* feedback;
* resultados;
* rankings;
* histórico.

---

# Embeddings

---

## OpenAI Embeddings

---

## Qwen3-Embedding

---

## BGE-M3

---

# Chunking

---

## Papers

```python id="bb8nyl"
chunk_size = 1500
overlap = 300
```

---

## Materiais

```python id="a1vjfo"
chunk_size = 500
```

---

## Summaries

```python id="a7kqz5"
chunk_size = 300
```

---

# Metadata

```json id="m1sv0v"
{
    "source": "",
    "authors": [],
    "year": "",
    "doi": "",
    "material": "",
    "application": "",
    "temperature_range": "",
    "keywords": []
}
```

---

# Hierarchical RAG

```text id="opn53h"
User
↓
Question Understanding
↓
Paper Retriever
↓
Material Retriever
↓
Graph Retriever
↓
Summaries
↓
LLM
```

---

# Multi-RAG

---

## Literature RAG

Busca artigos.

---

## Material RAG

Busca materiais.

---

## Property RAG

Busca propriedades.

---

## Application RAG

Busca aplicações.

---

## Graph RAG

Busca relações no Neo4j.

---

# Context Builder

Objetivo:

Montar o contexto final.

Fluxo:

```text id="gh7ujl"
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

# Short-Term Memory

Objetivo:

Memória da sessão atual.

Armazena:

* pergunta atual;
* contexto recente;
* materiais encontrados.

---

# Long-Term Memory

Persistência de:

* perguntas;
* materiais pesquisados;
* respostas;
* feedback;
* histórico.

---

# Episodic Memory

Memória por sessão.

```text id="e3tthd"
Session
↓
Questions
↓
Answers
↓
Feedback
```

---

# Semantic Memory

Conhecimento científico.

```text id="jwy83g"
Papers
↓
Properties
↓
Materials
↓
Applications
```

---

# Procedural Memory

Conhecimento operacional.

Exemplos:

* como comparar materiais;
* como selecionar ferramentas;
* como interpretar resultados.

---

# Future Experimental Memory

```text id="j72az9"
Experiments
↓
Results
↓
Failures
↓
Learning
↓
Knowledge Graph
```

---

# Memory Compression

Pipeline:

```text id="d7fms7"
Raw Context
↓
Summaries
↓
Compression
↓
Ranking
↓
Prompt
```

---

# Retrieval Pipeline

```text id="wlj5hp"
User
↓
Embedding
↓
Vector Search
↓
Graph Search
↓
Re-ranking
↓
Context Builder
↓
Prompt
↓
LLM
```

---

# Future Vision

A camada Memory/RAG deverá evoluir para uma verdadeira memória científica capaz de integrar:

* literatura;
* materiais;
* propriedades;
* aplicações;
* resultados experimentais;
* hipóteses geradas pelo sistema.

Essa memória será a fundação do futuro agente científico do MaterialGPT e, posteriormente, do AlphaFold para Materiais.
