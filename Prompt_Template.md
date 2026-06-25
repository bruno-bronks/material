# MaterialGPT

# Parte 3 — Prompt Templates e Agent Graph

---

# 4. Prompt Templates

Os Prompt Templates representam a inteligência cognitiva do sistema.

Seu objetivo é transformar a intenção do usuário em tarefas científicas estruturadas.

---

# Arquitetura

```text
User
↓
Planner
↓
Context Builder
↓
Prompt Template
↓
LLM
↓
Structured Output
```

---

# Material Search Prompt

```jinja
Você é um cientista especialista em Ciência dos Materiais.

Objetivo:

{{ objective }}

Restrições:

{{ constraints }}

Considere:

- termodinâmica;
- estruturas cristalinas;
- propriedades mecânicas;
- química;
- estabilidade;
- aplicações industriais.

Produza:

1. materiais candidatos;
2. vantagens;
3. desvantagens;
4. aplicações;
5. papers relacionados;
6. nível de confiança.

Retorne JSON estruturado.
```

---

# Explain Material Prompt

```jinja
Explique o seguinte material para um engenheiro:

{{ material }}

Inclua:

- composição;
- estrutura cristalina;
- propriedades;
- vantagens;
- limitações;
- aplicações;
- referências.
```

---

# Compare Materials Prompt

```jinja
Compare:

{{ material_1 }}

vs

{{ material_2 }}

Avalie:

- temperatura máxima;
- densidade;
- resistência;
- custo;
- corrosão;
- aplicações.

Produza uma recomendação final.
```

---

# Paper Search Prompt

```jinja
Você é um pesquisador científico.

Pergunta:

{{ question }}

Recupere:

- artigos relevantes;
- DOI;
- resumo;
- aplicações;
- descobertas recentes.
```

---

# Property Prediction Prompt

```jinja
Analise o seguinte material:

{{ material }}

Prediga:

- dureza;
- densidade;
- condutividade;
- temperatura máxima;
- estabilidade.

Forneça um intervalo de confiança.
```

---

# Simulation Prompt

```jinja
Determine quais métodos de simulação são adequados.

Considere:

{{ material }}

Objetivo:

{{ objective }}

Escolha entre:

- DFT;
- Molecular Dynamics;
- Monte Carlo;
- Ab Initio.

Justifique a escolha.
```

---

# Planner Prompt

```jinja
Analise a pergunta do usuário.

Determine a intenção principal.

Possíveis intenções:

- material_search
- compare_materials
- explain_material
- paper_search
- simulation
- property_prediction

Retorne somente a intenção.
```

---

# Structured Outputs

## MaterialCandidate

```python
class MaterialCandidate(BaseModel):

    material_name: str

    confidence: float

    advantages: list

    disadvantages: list

    applications: list
```

---

## CompareOutput

```python
class CompareOutput(BaseModel):

    winner: str

    explanation: str

    confidence: float
```

---

# 5. Agent Graph

Framework:

LangGraph

---

# Arquitetura

```text
User
↓
Planner
↓
Intent Classifier
↓
────────────────────
│ Material Search  │
│ Paper Search     │
│ Compare          │
│ Explain          │
│ Simulation       │
│ Property Predict │
────────────────────
↓
Aggregator
↓
Report Generator
↓
User
```

---

# State Management

```python
class MaterialState(TypedDict):

    user_question: str

    intent: str

    constraints: dict

    objectives: list

    context: list

    materials: list

    papers: list

    simulations: list

    ranking: list

    report: str
```

---

# Node: Planner

Objetivo:

Determinar qual fluxo será executado.

Entrada:

```python
"Quero um material para baterias sem lítio."
```

Saída:

```python
material_search
```

---

# Node: Intent Classifier

Tipos:

```python
material_search

compare_materials

paper_search

explain_material

simulation

property_prediction
```

---

# Node: Material Search

Objetivo:

Encontrar candidatos.

Ferramentas:

* Materials Project;
* OQMD;
* AFLOW.

Saída:

```python
[
  material_1,
  material_2,
  material_3
]
```

---

# Node: Paper Search

Objetivo:

Encontrar artigos relevantes.

Ferramentas:

* Semantic Scholar;
* arXiv;
* Crossref.

Saída:

```python
papers
```

---

# Node: Explain Material

Objetivo:

Explicar propriedades.

Saída:

```python
summary
```

---

# Node: Compare Materials

Objetivo:

Comparar candidatos.

Entrada:

```python
Ti6Al4V

Inconel 718
```

Saída:

```python
winner
```

---

# Node: Property Prediction

Objetivo:

Predizer:

* densidade;
* dureza;
* condutividade;
* temperatura máxima.

---

# Node: Simulation

Objetivo:

Selecionar métodos de simulação.

Saída:

```python
DFT

Molecular Dynamics

Monte Carlo
```

---

# Node: Ranker

Objetivo:

Ordenar candidatos.

Critérios:

* estabilidade;
* custo;
* temperatura;
* confiança.

---

# Node: Aggregator

Objetivo:

Combinar:

* materiais;
* artigos;
* contexto;
* previsões.

---

# Node: Report Generator

Objetivo:

Gerar resposta final.

Formato:

```markdown
# Material Recomendado

## Candidato Principal

Ti6Al4V

## Temperatura Máxima

950°C

## Vantagens

...

## Desvantagens

...

## Papers

...
```

---

# Fluxo Material Search

```text
User
↓
Planner
↓
Intent Classifier
↓
RAG
↓
Material Search
↓
Ranker
↓
Report Generator
↓
User
```

---

# Fluxo Compare Materials

```text
User
↓
Planner
↓
Compare Node
↓
Paper Search
↓
Aggregator
↓
Report Generator
↓
User
```

---

# Fluxo Simulation

```text
User
↓
Planner
↓
Simulation Node
↓
Method Selection
↓
Report Generator
↓
User
```

---

# Multi-Agent Architecture

```text
Planner
↓
────────────────────
Material Agent

Paper Agent

Simulation Agent

Comparison Agent

Explanation Agent

Prediction Agent
────────────────────
↓
Aggregator
↓
Report Generator
```

---

# Supervisor Pattern

```text
Supervisor
↓
Workers
↓
Aggregator
```

Supervisor:

* coordena agentes;
* controla fluxo;
* evita loops.

---

# Future Scientific Agent

Arquitetura futura:

```text
User
↓
Planner
↓
Hypothesis Generator
↓
Material Generator
↓
Simulation
↓
Evaluation
↓
Knowledge Graph
↓
Learning
↓
Report
```

---

# Self-Reflective Agent

Capacidade futura:

```text
Resposta
↓
Crítica
↓
Revisão
↓
Melhoria
↓
Resposta Final
```

---

# Long-Term Vision

Transformar o MaterialGPT em um agente científico capaz de:

* gerar hipóteses;
* propor novos materiais;
* planejar experimentos;
* aprender com resultados;
* evoluir continuamente.

Este será o embrião do futuro AlphaFold para Materiais.
