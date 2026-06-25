# MaterialGPT

# AI for Materials Discovery

## Visão Geral

O objetivo do MaterialGPT é construir um **AlphaFold para materiais**, capaz de descobrir novos materiais para:

* baterias;
* supercondutores;
* semicondutores;
* ligas metálicas;
* catalisadores;
* células solares;
* hidrogênio verde.

---

# Arquitetura

```text
Design Doc
↓
Spec
↓
Context Engineering
↓
Prompt Templates
↓
Agent Graph
↓
Tool Calling
↓
Memory/RAG
↓
Harness
↓
Evaluation
↓
Observability
↓
Feedback Loop
↓
Continuous Improvement
↓
Production
```

---

# 1. Design Doc

## Problema

A descoberta de novos materiais pode levar décadas e bilhões de dólares.

Grande parte dos experimentos falha.

A IA deve reduzir drasticamente o espaço de busca e acelerar o processo científico.

---

## Objetivo

Receber:

```text
"Quero um material barato, reciclável e que suporte 1200°C."
```

E retornar:

* candidatos;
* propriedades previstas;
* explicações;
* artigos relacionados;
* nível de confiança;
* resultados de simulações.

---

## Usuários

### Pesquisadores

Universidades e centros de pesquisa.

---

### Indústrias

#### Baterias

* baterias de lítio;
* baterias de sódio;
* baterias de estado sólido.

#### Aeroespacial

* turbinas;
* ligas metálicas;
* materiais leves.

#### Química

* polímeros;
* catalisadores.

#### Petróleo e Gás

* corrosão;
* alta temperatura.

#### Semicondutores

* chips;
* eletrônica avançada.

---

### Startups DeepTech

Empresas focadas em materiais avançados e AI for Science.

---

# Casos de Uso

## Descoberta de materiais

Entrada:

```text
Material resistente à corrosão para ambiente marinho.
```

Saída:

* candidatos;
* propriedades;
* artigos relacionados.

---

## Comparação de materiais

Entrada:

```text
Titânio vs Inconel para alta temperatura.
```

Saída:

* vantagens;
* desvantagens;
* recomendação.

---

## Explicação

Entrada:

```text
Explique o grafeno.
```

Saída:

* estrutura;
* aplicações;
* propriedades.

---

## Busca por artigos

Entrada:

```text
Pesquisas recentes sobre supercondutores.
```

Saída:

* papers;
* DOI;
* resumo.

---

## Predição de propriedades

Entrada:

```text
Liga metálica para operar acima de 1000°C.
```

Saída:

* materiais candidatos;
* estabilidade;
* propriedades previstas.

---

# 2. Spec

## Inputs

### Linguagem Natural

Exemplo:

```text
Material resistente à corrosão para ambiente marinho.
```

---

### Restrições

```python
temperatura > 800°C

baixo custo

densidade < 3 g/cm³

alta resistência mecânica

baixa toxicidade
```

---

### Objetivos

```python
leve

reciclável

alta condutividade

baixo peso

alta resistência
```

---

## Outputs

Exemplo:

```json
{
    "material": "Ti6Al4V",
    "densidade": "4.43",
    "temperatura_max": "950°C",
    "confianca": "91%",
    "papers_relacionados": []
}
```

---

# Estado do Sistema

```python
class MaterialState(TypedDict):

    user_question: str

    intent: str

    constraints: dict

    objectives: list

    retrieved_materials: list

    papers: list

    candidates: list

    ranking: list

    final_report: str
```

---

# Tipos de Intenção

## Material Search

Busca de materiais.

---

## Compare Materials

Comparação entre candidatos.

---

## Explain Material

Explicação de propriedades.

---

## Paper Search

Busca de literatura científica.

---

## Simulation

Execução de simulações.

---

## Property Prediction

Predição de propriedades.

---

# MVP V1

Construir inicialmente um sistema semelhante a:

```text
Perplexity
+
ChatGPT
+
Ciência dos Materiais
```

Capaz de:

* responder perguntas;
* buscar materiais;
* consultar papers;
* explicar propriedades;
* gerar relatórios técnicos.

Posteriormente, evoluir para um verdadeiro agente científico capaz de propor novos materiais.
