# MaterialGPT — V1-V6 lite + Harness/Evaluation (Parte 5) + Quantum Chemistry & Optimization (QRA)

Implementação do MaterialGPT a partir da documentação em `*.md` na raiz do projeto
(`Design_docs.md`, `Context_Engineering.md`, `Prompt_Template.md`, `ToolCalling_Memory_RAG.md`,
`Harness_Evaluation_Observability.md`, `materialgpt_part6_roadmap_v1_v7.md`).

* **V1 — Scientific RAG**: um "Perplexity + ChatGPT especializado em Ciência dos Materiais",
  capaz de buscar materiais, comparar candidatos, explicar propriedades, buscar papers e sugerir
  métodos de simulação.
* **V2 — Graph Neural Networks**: adiciona inteligência preditiva (não só recuperar o que já é
  conhecido) — candidatos do Materials Project ganham uma energia de formação **prevista por um
  modelo de GNN pré-treinado**, em vez de depender só de dados já calculados.
* **V3 — Property Prediction Engine**: na intenção `property_prediction`, o candidato principal
  do Materials Project ganha também um **módulo de compressibilidade estimado por simulação**
  (M3GNet + equação de estado), cobrindo a categoria "mecânica" do roadmap.
* **V4 — DFT Automático**: na intenção `simulation`, o node deixa de só *sugerir* um método em
  texto e passa a **executar de fato** uma relaxação estrutural (otimização de geometria), usando
  M3GNet como potencial interatômico no lugar de DFT real (Quantum ESPRESSO).
* **V5 — Scientific Agent**: nova intenção `material_discovery` — o sistema deixa de só responder
  sobre materiais existentes e passa a **propor candidatos hipotéticos** (substituição de elemento
  numa estrutura real), simulá-los (V2+V4) e **criticar o próprio resultado**, tentando de novo se
  rejeitado (até um limite de iterações). Primeiro ciclo com loop real no grafo.
* **V6 lite — Active Learning**: o V6 real (Self-Driving Lab) precisa de robô/sensores físicos —
  fora de alcance aqui. A parte de V6 que é só matemática/algoritmo entrou: em vez do LLM
  "chutar" uma substituição por vez, o sistema gera um **pool de candidatos quimicamente
  plausíveis** (por grupo/eletronegatividade/raio atômico) e os ranqueia por estabilidade
  prevista pelo GNN (barato) **antes** de gastar com relaxação completa + julgamento do LLM
  (caro) — só os mais promissores chegam a ser testados de fato.

## Decisões de escopo

* **LLM padrão:** GPT (OpenAI) — configurável em `backend/.env`.
* **Infra paga → substitutos locais/gratuitos**, para rodar sem contas pagas:
  * Pinecone → **Chroma** (vetorial local, persistido em `backend/data/chroma`);
  * PostgreSQL → **SQLite** (`backend/data/materialgpt.db`, troque `DATABASE_URL` para usar Postgres real);
  * Neo4j → **opcional**. Sem `NEO4J_URI` configurado, o node de Graph RAG é um no-op.
  * CGCNN/ALIGNN/M3GNet treinados do zero → **MEGNet/M3GNet pré-treinados via `matgl`** (CPU,
    sem GPU, sem dataset próprio — ver seções V2/V3 abaixo).
* **V3 só cobre módulo de compressibilidade.** O roadmap pede 4 categorias (mecânica, térmica,
  elétrica, química); dureza, condutividade, expansão térmica e corrosão não têm modelo
  pré-treinado gratuito que dê o valor direto sem treinar algo do zero ou rodar DFT real — então
  não inventei número pra essas (o LLM ainda responde com conhecimento geral pra elas, mas sem
  rótulo de "previsto por GNN").
* **V4 não usa Quantum ESPRESSO de verdade.** DFT real exige WSL2/conda no Windows, banco de
  pseudopotenciais e minutos por cálculo. Em vez disso, a "simulação" executada é uma relaxação
  estrutural de fato (ASE + M3GNet como potencial), rotulada claramente como aproximação, não DFT.
* **V5 não gera estrutura cristalina do zero.** Isso seria um modelo generativo (diffusion/VAE),
  explicitamente V7 no roadmap. O "Material Generator" do V5 parte de uma estrutura **real** do
  Materials Project e aplica substituição de elemento — gera candidatos plausíveis, não inéditos.
* **V5/V6 lite tem limite de 3 iterações** (`MAX_ITERATIONS` em `node_hypothesis.py`). Com o
  ranking por GNN (V6 lite), cada iteração depois da primeira não chama mais o LLM pra propor
  substituição (só pop do pool já ranqueado) — só o `node_critic` ainda chama LLM quando o gate
  físico passa. Mais barato que antes, mas ainda soma ~10-20s por iteração extra.
* **Não é Bayesian Optimization formal.** Não ajustamos um modelo probabilístico (Gaussian
  Process) entre iterações — é um ranking guloso por um substituto barato (GNN) sobre um pool
  gerado por regras de química (grupo/eletronegatividade/raio). Funciona bem aqui porque já temos
  exatamente a estrutura de "modelo barato + validação cara" que justifica essa técnica, mas é
  menos sofisticado que uma BO de verdade com função de aquisição.
* **Fora de escopo nesta entrega** (V6 real/V7 no roadmap, ou Harness/Eval/Observability como
  camada futura): laboratório físico de verdade (robôs/sensores), Tree of Thoughts / Monte Carlo
  Tree Search formais, fônons, golden dataset / LLM-as-judge, LangSmith/Phoenix/Grafana, DFT real
  via Quantum ESPRESSO, geração de estrutura cristalina do zero (modelos generativos).

## Estrutura

```text
backend/   FastAPI + LangGraph (agente científico) + RAG + tool calling + memória
frontend/  Next.js — chat mínimo que consome a API
```

### Backend (`backend/app`)

* `agent/` — Agent Graph em LangGraph: `planner` (intent classifier) → node por intenção
  (`material_search`, `paper_search`, `explain_material`, `compare_materials`,
  `property_prediction`, `simulation`) → `ranker` → `aggregator` → `report_generator`.
* `tools/` — clientes reais para Materials Project, OQMD, AFLOW, PubChem, Semantic Scholar,
  Crossref e arXiv, com um `router.py` que decide quais chamar por intenção.
* `rag/` — chunking (tamanhos de `Context_Engineering.md`: papers 1500/300, materiais 500,
  summaries 300), vetorstore Chroma + embeddings BGE-M3, re-ranking leve, context builder.
* `memory/` — sessões/perguntas/feedback/ranking em SQLite (SQLAlchemy) + memória de curto prazo
  em processo.
* `graph_kg/` — wrapper opcional para Neo4j (Knowledge Graph / Graph RAG).
* `ingestion/` — pipeline ETL (Extract → Transform → Validate → Enrich → Store) que popula o
  Chroma a partir das próprias tools.
* `prompts/templates/*.jinja2` — os prompts de `Prompt_Template.md`, fiéis ao documento original.

### Frontend (`frontend/app`)

Chat de uma página (`app/page.tsx`). Consome `POST /api/chat/stream` (SSE) em vez do `/api/chat`
original — mostra o progresso de cada node do grafo em tempo real (relevante sobretudo pro loop
de descoberta do V5/V6, que pode levar ~1min: sem isso, a tela ficava parada e sem feedback).
A conversa (mensagens + `session_id`) persiste em `localStorage`, sobrevivendo a reload de
página; tem um botão "Limpar conversa" pra resetar.

#### Streaming de progresso (SSE)

```text
graph.stream(state, stream_mode="updates") → 1 evento SSE por node concluído → frontend renderiza lista de etapas em tempo real
```

* `POST /api/chat/stream` (`backend/app/api/routes.py`) usa `graph.stream(...)` do LangGraph em
  vez de `graph.invoke(...)` — emite um evento a cada node que termina, em vez de só no final.
* `backend/app/agent/node_labels.py` mapeia cada nome de node (`node_critic`,
  `material_search` etc.) para um texto amigável em português, incluindo os nodes do loop de
  descoberta do V5/V6.
* Cada evento inclui `iteration` (de `discovery_iteration`) quando aplicável — o frontend mostra
  "Avaliando se o candidato atende ao objetivo (tentativa 2)" enquanto o loop tenta de novo.
* **Trade-off da resposta de erro:** como o streaming já começou a responder com `200 OK` antes
  de qualquer node rodar, não é possível trocar pra `503` no meio do caminho como o `/api/chat`
  original faz. Erros (ex: sem `OPENAI_API_KEY`) vêm como um evento `{"type": "error", ...}`
  dentro do próprio stream — o frontend trata isso explicitamente, não só checa o status HTTP.
* Frontend lê o corpo da resposta via `response.body.getReader()` (não dá pra usar
  `EventSource` nativo do browser porque ele só suporta GET, e aqui precisamos enviar a
  pergunta no corpo de um POST).
* Validado com Playwright: screenshot capturado **durante** o streaming mostra o passo atual com
  indicador pulsante (ex: "● Identificando a intenção da pergunta"); sem erros de console.

### V2 — GNN (`backend/app/gnn`)

```text
Structure (Materials Project) → Graph → GNN (MEGNet pré-treinado) → Property Prediction
```

* `predictor.py` — carrega `MEGNet-Eform-MP-2018.6.1` (via `matgl`) e prevê energia de formação
  (eV/átomo) a partir de uma `pymatgen.Structure`. Validado com uma estrutura sintética de
  NaCl (rock-salt): previsão de **-1.76 eV/átomo**, na faixa fisicamente plausível.
* `enrich.py` — para cada material que vem do Materials Project (único com `material_id`),
  busca a estrutura cristalina completa (`tools/materials_project.get_structure`, via `mp-api`)
  e anexa `gnn_formation_energy_ev_atom` ao dict do material. Plugado direto em
  `tools/router.search_materials`, então todo node que já usava essa função (material_search,
  explain_material, compare_materials, property_prediction) passa a receber o dado sem mudança
  de assinatura.
* **Band gap (resolvido na consolidação):** o checkpoint `MEGNet-BandGap-mfi-MP-2019.4.1` é
  multi-fidelidade — eu estava passando o `state_attr` errado (tensor one-hot float). A camada
  de embedding interna (`layer_state_embedding`, um `torch.nn.Embedding(4, 16)`) espera um
  **índice de classe inteiro** (`torch.tensor([0..3], dtype=torch.long)` para
  PBE/GLLB-SC/HSE/SCAN), não um vetor one-hot. Corrigido em `predict_band_gap()` — validado contra
  NaCl (isolante de gap largo, ~8.5 eV experimental): GLLB-SC previu 8.03 eV, PBE 4.59 eV (DFT-PBE
  é sabidamente subestimado), ordem PBE < HSE < GLLB-SC fisicamente coerente.
* Em `materials_project`-sourced materials (que já sempre trazem `band_gap` real do banco), o GNN
  só prevê quando esse campo está ausente. O uso que realmente importa é no **V5/V6** (seção
  abaixo), onde o candidato hipotético não tem valor real em nenhum banco.
* Sem `MP_API_KEY`, este passo simplesmente não roda (nenhum material tem `material_id`) — o
  resto do pipeline (OQMD/AFLOW/RAG/LLM) continua funcionando normalmente.

### V3 — Property Prediction Engine (`backend/app/gnn/elastic.py`)

```text
Structure → relaxações em volumes vizinhos (M3GNet-PES) → curva E×V → ajuste Birch-Murnaghan → B₀ (GPa)
```

* `estimate_bulk_modulus()` carrega `M3GNet-PES-MatPES-PBE-2025.2`, relaxa a estrutura em 5
  volumes (94%–106% do volume original, célula fixa) e ajusta uma equação de estado de
  Birch-Murnaghan (`pymatgen.analysis.eos`) para extrair o módulo de compressibilidade B₀.
* Plugado só em `node_property_prediction` (via `enrich.enrich_with_bulk_modulus`, `limit=1`) —
  **não** no `tools/router` global, porque é muito mais caro que a energia de formação do V2
  (várias relaxações por material, não uma inferência só).
* **Guard de custo:** estruturas com mais de 40 átomos são puladas (`MAX_ATOMS`). Testado com uma
  estrutura real de 100 átomos: ~73s para o cálculo completo — inviável para o chat, por isso o
  corte.
* **O ajuste de EOS pode falhar** para estruturas que não estão bem relaxadas no banco de dados
  (`EOSError`) — nesse caso retorna `None` silenciosamente, igual ao resto do V2.
* Validado contra valores conhecidos:
  * NaCl sintético: **22.7 GPa** previsto vs. ~24–25 GPa experimental.
  * Si real (`mp-aaaditqj`, Materials Project): **105.2 GPa** previsto vs. ~97–98 GPa experimental.
  * Ti real (`mp-aaacsmow`): EOS falhou (estrutura não bem comportada) → `None`, sem alucinar valor.

### V4 — Simulação Automática (`backend/app/simulation/relax.py`)

```text
Structure → ASE + M3GNet (potencial) → relaxação (posições + célula) → energia/força/volume finais
```

* `relax_structure()` reaproveita o mesmo potencial M3GNet do V3 (`app/gnn/potential.py`, agora
  compartilhado entre `elastic.py` e `relax.py`) e roda uma otimização de geometria completa
  (`relax_cell=True`) via `matgl.ext.ase.Relaxer` — isso **executa** uma simulação, não só prediz
  um número como o V2/V3.
* Plugado em `node_simulation`: além de pedir ao LLM para sugerir um método (DFT/MD/Monte
  Carlo/Ab Initio, como já fazia desde o V1), agora busca um candidato do Materials Project pela
  pergunta e relaxa a estrutura de fato, anexando energia inicial/final, força residual máxima e
  variação de volume à lista de `simulations`.
* **Guard de custo:** até 120 átomos (`MAX_ATOMS`) — testado com estrutura real de 100 átomos:
  ~14s (bem mais barato que o V3, que faz 5 relaxações em vez de 1).
* Validado com Si real (`mp-aaaditqj`): convergiu em 53 passos, energia caiu de -4.9243 para
  -5.0987 eV/átomo (rumo a configuração mais estável, como esperado fisicamente), força residual
  0.0264 eV/Å, variação de volume +0.81%. Relatório final citou os números corretamente como
  "substituto rápido de DFT (Quantum ESPRESSO)", não um cálculo de primeiros princípios real.

### V5 + V6 lite — Scientific Agent com Active Learning (`backend/app/agent/nodes/{hypothesis,material_generator,simulation_planner,critic,reflection,discovery_common}.py`)

```text
node_hypothesis → node_material_generator → node_simulation_planner → node_critic
   (LLM: só          ↑                                                       │
   escolhe ONDE      └──────────── node_reflection ◄──────────────────────┘ (sem LLM: só pop
   intervir;                                                                  do pool ranqueado)
   "o quê" vem do                                                             │
   ranking GNN)                                                    report_generator (aceito ou
                                                                     esgotou iterações/pool)
```

* **Primeiro grafo com ciclo real** no projeto — todos os outros fluxos (V1-V4) são DAGs lineares.
* `node_hypothesis` busca um material real (Materials Project) como "semente" e pede ao LLM
  **só qual elemento da estrutura é o ponto de intervenção** (`SubstitutionTarget`, via
  `with_structured_output`) — não pede mais o substituto.
* `discovery_common.rank_candidate_pool` (V6 lite) gera um pool de elementos quimicamente
  parecidos (mesmo grupo, eletronegatividade e raio atômico próximos —
  `_chemically_similar_elements`, sem LLM) e roda o GNN do V2 (barato, ~1-3s) em cada um pra
  ranquear por estabilidade prevista **antes** de relaxar/julgar nada. Só o candidato top do
  ranking é testado de verdade.
* `node_material_generator` aplica a substituição na estrutura real via
  `pymatgen.Structure.replace_species` e serializa o resultado como **string CIF** no estado do
  grafo — nunca guardamos o objeto `Structure` no `MaterialState` (precisa ser JSON-serializável
  pra API/persistência); cada node que precisa da estrutura a reconstrói a partir do CIF.
* `node_simulation_planner` roda a relaxação (V4) no candidato, **reaproveita** a energia de
  formação já calculada na etapa de ranking (em vez de recomputar), e também prevê o **band gap**
  (V2, agora corrigido) — esse é o caso onde o band gap do GNN realmente importa: o candidato
  hipotético não existe em nenhum banco, então não há valor real disponível. O `node_critic` usa
  esse número pra fundamentar rejeição (ex: "band gap previsto 0 eV → comportamento metálico, não
  semicondutor"), em vez de inferir qualitativamente sem dado nenhum.
* `node_critic` aplica primeiro um **gate físico determinístico** (relaxação não convergiu, ou
  força residual alta → rejeita sem nem chamar o LLM) e só então usa o LLM como juiz para o
  julgamento mais qualitativo (custo, toxicidade etc. vs. o objetivo do usuário).
* `node_reflection` (V6 lite) **não chama mais o LLM** — só avança pro próximo candidato do pool
  já ranqueado. O grafo volta para `node_material_generator`.
* **Validado end-to-end nos dois caminhos do loop, e comparado antes/depois do V6 lite:**
  * **Caminho de rejeição** — "Proponha um substituto para o silício em semicondutores": tentou
    Si→Ge (rejeitado: energia de formação positiva = instável, e Ge é caro), depois Si→Sn
    (rejeitado: estrutura colapsou — variação de volume de ~91% — e Sn é metálico, não
    semicondutor), esgotou as iterações, e **o relatório final admitiu honestamente que nenhum
    candidato foi aceito**, narrando as duas tentativas e os motivos — sem fingir uma descoberta
    que não aconteceu.
  * **Caminho de aceite, antes do V6 lite** (LLM chutava o substituto) — "substituto mais barato
    pro ouro": tentou Au→Cu (rejeitado), depois Au→Pd (**aceito**). 2 iterações, ~58s.
  * **Mesmo caso, depois do V6 lite** (ranking por GNN decide o substituto): o pool já colocou
    **Pd em 1º lugar** (mesma química real: Cu, Ag, Pt, Pd, Ni são os metais mais parecidos com
    Au) — **acertou de primeira**, sem precisar testar e rejeitar o Cu. 1 iteração em vez de 2,
    mesmo resultado final (Pd), relatório citando explicitamente que o substituto "não foi um
    palpite do assistente" e veio da busca química + ranking.
  * Regressão das intenções V1-V4 confirmada (continuam funcionando após a mudança no grafo).

## Consolidação (pós-V6 lite)

Depois de empilhar V1→V6 lite, parei pra fortalecer o que já existia em vez de seguir pro V7
(que bateria no mesmo limite de compute/hardware do V6 real). O que entrou:

* **Bug do band gap corrigido** (ver seção V2 acima) — não era incompatibilidade de checkpoint,
  era o `state_attr` passado no formato errado.
* **`node_ranker` corrigido e melhorado** (`backend/app/agent/nodes/ranker.py`):
  * Bug pré-existente: candidatos do AFLOW guardam energia de formação em `formation_energy`,
    mas o ranker só olhava `energy_above_hull` (Materials Project) e `stability` (OQMD) — todo
    material do AFLOW caía no fallback `0` (tratado como "perfeitamente estável"), ignorando o
    dado real que já estava ali. Corrigido.
  * Agora também cai pra `gnn_formation_energy_ev_atom` (V2) quando não há **nenhum** dado real
    de estabilidade — sempre como último recurso, nunca misturado com dado real na mesma
    comparação.
* **Suite de testes automatizados** (`backend/tests/`, 37 testes, `pytest`):
  * Unitários (rápidos, sem rede): schemas, chunking, heurística de elementos, ranker, busca de
    elementos quimicamente similares (V6 lite), grafo compila.
  * Integração com APIs reais (`@pytest.mark.network`): OQMD, AFLOW, PubChem, Crossref, arXiv —
    sem precisar de chave.
  * Lentos (`@pytest.mark.slow`): inferência GNN (energia de formação + band gap, validados
    contra NaCl), ingestão real, `/api/chat` ponta a ponta (pulado automaticamente sem
    `OPENAI_API_KEY`).
  * `tests/conftest.py` isola `CHROMA_PERSIST_DIR`/`DATABASE_URL` num diretório temporário via
    hook `pytest_configure` — os testes não tocam nos dados de desenvolvimento em `backend/data/`.
  * Rodar tudo: `pytest`. Só os rápidos: `pytest -m "not slow and not network"`.

## Harness, Evaluation & Observability (`Harness_Evaluation_Observability.md`, Parte 5)

Até aqui (V1-V6 lite) o projeto fazia o sistema *funcionar*. Esta parte é sobre *medir se ele
funciona bem* — o doc pede golden dataset (1000+ perguntas), métricas como Faithfulness/
Hallucination Rate/Recall/Precision, LLM-as-a-Judge, e observability via LangSmith/Phoenix/
OpenTelemetry. Implementação realista (`backend/app/evaluation/`):

* **Golden dataset** (`golden_dataset.json`) — 16 perguntas-semente cobrindo as 5 categorias do
  doc (baterias, supercondutores, ligas metálicas, corrosão, semicondutores) **e** todas as 7
  intenções do agente (`material_search` até `material_discovery`). Escala reduzida do "1000+"
  do doc, mas fácil de expandir — é só adicionar entradas no JSON.
* **LLM-as-a-Judge** (`judge.py` + `evaluation_judge.jinja2`) — sem gabarito de referência
  (nenhum especialista humano curou respostas corretas), o juiz avalia qualidade **intrínseca**:
  `relevance`, `faithfulness`, `hallucination_risk`, `confidence_calibration` (1-5 cada) +
  veredito `passed`. Recall/Precision/Citation Accuracy do doc original exigiriam respostas de
  referência que não temos — não inventei isso.
  * Usa o mesmo provider (GPT) que gera as respostas — risco conhecido de viés de
    autoavaliação. LangSmith/Phoenix ficaram de fora por exigirem conta externa (mesma lógica
    de "local/free" do resto do projeto); ficam documentados como alternativa real no doc.
* **Runner** (`runner.py`, `python -m app.evaluation.runner`) — roda cada pergunta pelo grafo
  completo, manda a resposta pro juiz, salva um relatório JSON em `backend/data/eval_runs/`.
  **Não rodar em paralelo com o backend ligado** — os dois processos disputam o lock do SQLite
  do Chroma e o segundo trava com *segmentation fault* (achado durante o desenvolvimento desta
  própria feature).

### O harness encontrou bugs reais — e eles foram corrigidos

Primeira rodada: **12/16 (75%)**. As 4 reprovações revelaram um padrão real:

| Pergunta | Problema encontrado pelo juiz |
|---|---|
| "material para bateria de estado sólido" | Resposta focou em titânio (irrelevante) em vez de eletrólitos sólidos |
| "material resistente a ácido sulfúrico" | Citou uma liga sem nenhuma base real de resistência a ácido |
| "materiais para chips de próxima geração" | Focou em metais estruturais, não em semicondutores emergentes |
| "Pesquisas recentes sobre supercondutores" | Único paper citado era de 2015 — não é "recente" |

**Causa raiz das 3 primeiras**: a heurística de extração de elementos (`tools/elements.py`) não
tem cobertura pra perguntas conceituais sem elemento/fórmula explícito. Sem isso, nenhuma tool
real (Materials Project/OQMD/AFLOW) era acionada, e o sistema caía pro RAG local — que, fora do
tópico perguntado, ainda tinha bastante dado de titânio de sessões de teste anteriores. O LLM
ancorava a resposta nesse contexto irrelevante em vez de admitir que não tinha boa base.

**Correção**: `suggest_elements()` (`tools/elements.py`) — quando a extração por palavra-chave
falha, pede ao LLM exatamente 2 elementos plausíveis (AFLOW exige todos os elementos pedidos
presentes simultaneamente, então mais que isso torna a busca rara demais) antes de desistir.
Resultado real: "bateria de estado sólido" → Li+P (eletrólitos Li-P-S, uma família real); "ácido
sulfúrico" → Ni+Cr (a mesma química do Inconel/Hastelloy); "chips de próxima geração" → Si+Ge
(SiGe, material real usado em chips avançados).

**Correção da recência**: `arxiv.py`/`crossref.py` agora misturam resultados por relevância com
uma busca extra ordenada por data — antes só havia ranking por relevância, que pode trazer um
artigo antigo bem casado por palavra-chave. Semantic Scholar ficou de fora dessa correção (rate
limit impediu validar o parâmetro de ordenação com confiança).

**Segunda rodada, após as correções: 16/16 (100%)**. Todas as métricas melhoraram:

| Métrica | Antes | Depois |
|---|---|---|
| Pass rate | 75% | **100%** |
| Relevância média | 4.44/5 | 4.81/5 |
| Fidelidade média | 4.88/5 | 4.94/5 |
| Risco de alucinação médio | 2.62/5 | **1.94/5** |
| Calibração de confiança média | 4.31/5 | 4.62/5 |

Achado residual menor (passou, mas vale registrar): ao explicar grafeno, a resposta citou um
material com estrutura "monoclínica" como se fosse grafeno (que é hexagonal) — provavelmente
outro alótropo de carbono do banco de dados sendo confundido. `explain_material` não trata bem
materiais 2D nos bancos de dados focados em estruturas 3D (AFLOW/MP/OQMD). Não corrigido ainda.

## Enrich real no pipeline de ingestão — de `Context_Engineering.md`

Revisitando o doc mais antigo do projeto (Parte 2), cruzei o pipeline ETL descrito (Extract →
Transform → **Validate** → **Enrich** → Store) com `backend/app/ingestion/pipeline.py` real.
Achado: o "Enrich" nunca existia — chunks iam direto do dado da tool pra o Chroma, com metadado
raso (`source`/`doi`/`year`/`authors`). E a coleção `summaries` (declarada em
`vectorstore.py`/`context_builder.py`, consultada em **toda** pergunta do chat) nunca era
populada por nada — sempre vazia, sempre um round-trip ao Chroma sem retorno.

* `backend/app/ingestion/enrich.py` — uma chamada de LLM por paper/material (não por chunk)
  extrai `keywords` e classifica `application` numa categoria controlada (baterias,
  aeroespacial, semicondutores etc. — as mesmas categorias citadas no próprio doc), e gera um
  resumo curto, tudo a partir do texto real, via `with_structured_output`.
* O resumo passa a popular a coleção `summaries` de verdade; `keywords`/`application` passam a
  fazer parte do metadado de cada chunk em `papers`/`materials`.
* Deixei `temperature_range` (que está no schema de metadado do doc) de fora deliberadamente —
  não tem como extrair isso de um abstract de paper sem risco real de inventar um número que não
  está lá.
* Validado na VPS: `POST /api/ingest` com "titanium alloy aerospace" indexou 8 papers + 4
  materiais, e a coleção `summaries` (antes sempre com `count=0`) passou a ter 12 entradas, com
  `application: "aeroespacial"` corretamente classificada e `keywords` reais extraídas do texto
  (não fabricadas). `/api/chat` confirmado funcionando normalmente depois da mudança.

## Quantum Chemistry & Optimization — de `Quantum_Research_Assistant.md` (`backend/app/quantum/`)

Documento separado (QRA), descrevendo um sistema de 10 agentes pra pesquisa em computação
quântica/química quântica (VQE, QAOA, hardware quântico real). Antes de implementar qualquer
coisa, cruzei com o roadmap original: `materialgpt_part6_roadmap_v1_v7.md` já cita exatamente
isso (NISQ, VQE, QAOA) numa seção chamada **"Beyond V7"** — ou seja, o próprio projeto já
considerava isso além até da fase mais especulativa (AlphaFold para Materiais).

### O que foi verificado antes de decidir o escopo (não assumido)

* `qiskit`, `qiskit-aer`, `qiskit-nature`, `pyscf` são reais e mantidos ativamente
  (`qiskit-nature` teve release em 01/06/2026).
* **Testei instalar `pyscf` neste Windows: falhou** (sem compilador C/C++; o próprio
  `qiskit-nature` já declara `pyscf; sys_platform != "win32"` nas suas dependências — PySCF não
  tem suporte oficial a Windows). No Linux (VPS), instala em segundos via wheel pré-compilado.
* **Rodei um VQE real pra H₂** (geometria 0.735 Å — valor *default* do próprio
  `PySCFDriver`, não escolhido por nós) na VPS: energia bateu com o valor exato (FCI) com erro de
  **5.7×10⁻¹¹ Hartree**, em 0.33s.
* **Tentei o exemplo principal do próprio documento — "qual a energia da molécula de água"**:
  mesmo após `FreezeCoreTransformer` (congelar os orbitais internos do oxigênio, prática padrão),
  o problema fica em 12 qubits / **92 parâmetros** no ansatz UCCSD — não convergiu em mais de
  280s num simulador clássico. **O exemplo-bandeira do documento não é viável em tempo de chat**
  com uma abordagem cientificamente rigorosa.

### O que entrou (escopo deliberadamente restrito)

* Nova intenção `quantum_chemistry`: roda um **VQE real** (não aproximação de ML) só pra **H₂**
  — único caso verificado como rápido (4 qubits, <1s) e com geometria que não inventamos.
* Qualquer outra molécula recebe uma resposta honesta explicando a limitação (testado com água:
  recusa rápida, sem travar, sem fabricar número).
* `backend/requirements-quantum.txt` — **separado** do `requirements.txt` principal, porque
  `pyscf` quebra a instalação no Windows. Sem essas libs instaladas, o node detecta `ImportError`
  e explica que a funcionalidade não está disponível no ambiente atual, em vez de quebrar o
  resto do app.
* Validado em produção: `https://material.bronks.ia.br` respondendo "qual a energia do H2 via
  VQE?" com o cálculo real, e recusando educadamente quando perguntado sobre água.

### Prós e contras de ter integrado isso

**Prós**: cobre uma lacuna real e documentada do roadmap; é genuinamente um cálculo quântico
(não é "mais um" modelo de ML como V2-V6); reaproveita a infraestrutura existente (grafo,
report_generator, planner) sem duplicar agentes que o MaterialGPT já tem (Research Agent ≈
`paper_search`, Knowledge RAG Agent ≈ `rag/`, Report Agent ≈ `report_generator`).

**Contras**: dependência pesada nova e exclusiva de Linux (não testável neste Windows local —
só na VPS); valor científico genuíno limitado a moléculas com poucos qubits, o que **não inclui**
o próprio exemplo principal do documento (água); não serve para o caso de uso central do
MaterialGPT (descoberta de materiais sólidos/ligas — VQE molecular não substitui M3GNet pra
isso); superfície pequena hoje (1 molécula suportada) — expandir exige ou geometrias
verificadas uma a uma, ou aceitar o risco de o LLM "chutar" geometria molecular errada, o que
decidimos não fazer.

### Cobertura do QRA, agente por agente (status real)

Cruzando os 10 agentes do documento com o que existe hoje:

| Agente do QRA | Status |
|---|---|
| 1. Intent Agent | Parcial — planner classifica intenção, não extrai domain/task/target estruturado |
| 2. Research Agent | Parcial — arXiv/Semantic Scholar/Crossref (V1); PubMed/Google Scholar/Nature/Science fora |
| 3. Knowledge RAG Agent | Já existia (Chroma do V1), reaproveitado |
| 4. Scientific Planner Agent | Não implementado |
| 5. Hamiltonian Generator Agent | Parcial — gerado internamente no VQE, não exposto separado; Qiskit Nature em vez de OpenFermion |
| 6. Quantum Algorithm Agent | **VQE + QAOA implementados.** QPE, Quantum Neural Networks, Trotterization — fora |
| 7. Simulation Agent | Parcial — só simulador local (Aer/CPU). GPU (CUDA-Q) e hardware real (IBM/Braket/IonQ/Rigetti) — fora |
| 8. Analysis Agent | Parcial — erro vs. exato reportado; Fidelidade formal e profundidade de circuito não |
| 9. Visualization Agent | Não implementado — nenhum gráfico, frontend só renderiza markdown |
| 10. Report Agent | Parcial — só markdown, sem PDF/DOCX/PPTX |

### QAOA (Quantum Algorithm Agent, parte 2) — `backend/app/quantum/qaoa.py`

* Diferente do VQE: **não depende de PySCF**, então roda em qualquer SO — desenvolvido e
  testado direto neste Windows local, sem precisar da VPS.
* Resolve **Max-Cut** (particionar nós de um grafo maximizando arestas entre os grupos) — o
  exemplo padrão de "Problemas de Otimização" do documento. Escopo restrito a um grafo fixo de
  demonstração (ciclo de 4 nós), mesma cautela do VQE: evitar extrair uma estrutura de grafo
  arbitrária de texto livre.
* Validação embutida: a solução exata é calculada por força bruta (viável até ~12 nós) e
  comparada com o resultado do QAOA a cada execução — não é "confiar no quântico", é checar.
* Testado localmente: encontrou o corte ótimo exato (4 de 4 arestas) em ~3.6s, via
  `/api/chat` completo (intent classificado corretamente, relatório explicando o resultado e as
  limitações de escala).
* Nova intenção `quantum_optimization` no planner, mesma lógica do `quantum_chemistry`
  (resposta do especialista reaproveitada pelo `report_generator`, sem reformatar como material).

## Como rodar

### 1. Backend

```bash
cd backend
python -m venv .venv
./.venv/Scripts/activate        # Windows (PowerShell: .venv\Scripts\Activate.ps1)
pip install -r requirements.txt
pip install -r requirements-quantum.txt  # opcional, só Linux/Mac — ver seção Quantum Chemistry
cp .env.example .env            # depois edite o .env
```

Edite `backend/.env`:

* `OPENAI_API_KEY` — obrigatório, sem ele `/api/chat` responde 503 com mensagem explicativa.
* `OPENAI_MODEL` — padrão `gpt-5`, troque se quiser outro modelo da OpenAI.
* `MP_API_KEY` — gratuito em https://next-gen.materialsproject.org/api. Opcional para o V1 (sem
  ele o sistema usa OQMD/AFLOW/PubChem normalmente), mas **necessário para o V2**: é a única
  fonte de estrutura cristalina completa usada para alimentar a predição por GNN.
* `SEMANTIC_SCHOLAR_API_KEY` — opcional, evita HTTP 429 por rate limit.

Suba a API:

```bash
python -m uvicorn app.main:app --reload --port 8000
```

> Na primeira chamada que usa o RAG (`/api/ingest` ou `/api/chat`), o `sentence-transformers`
> baixa o modelo de embeddings `BAAI/bge-m3` (~2 GB) do Hugging Face. Para um primeiro teste mais
> rápido, troque `EMBEDDING_MODEL` no `.env` por algo menor, ex.
> `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`.

Popule o RAG com alguns dados reais antes de perguntar (a base começa vazia):

```bash
curl -X POST http://localhost:8000/api/ingest \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"titânio liga aeroespacial\", \"kind\": \"both\", \"limit\": 5}"
```

ou via CLI:

```bash
python -m app.ingestion.cli --query "titanium alloy corrosion resistance" --kind both
```

Rodar a suite de testes (cobre tudo: unitários, integração com APIs reais, GNN, API):

```bash
pytest                                  # tudo (~2min, baixa modelos GNN na primeira vez)
pytest -m "not slow and not network"    # só os unitários rápidos (~10s)
```

### 2. Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

Abra http://localhost:3000 com o backend em http://localhost:8000.

## Produção

Rodando em **https://material.bronks.ia.br** (VPS compartilhada com outros projetos —
`leao`/`ligas`/`maya`.bronks.ia.br — mesmo IP, sem conflito de porta).

* **Backend**: `/opt/material/backend`, venv nativo, `systemd` (`material-backend.service`),
  escutando só em `127.0.0.1:8002` (nunca exposto direto).
* **Frontend**: Docker (`frontend/Dockerfile`, multi-stage), container `material-frontend` em
  `127.0.0.1:3011`, `NEXT_PUBLIC_API_BASE_URL=/api` (caminho relativo — mesma origem do backend
  via nginx, sem CORS).
* **nginx**: `/etc/nginx/sites-available/material.bronks.ia.br` roteia `/api/` → backend
  (`proxy_buffering off` — obrigatório pro streaming SSE funcionar atrás do proxy) e `/` →
  frontend. Certificado Let's Encrypt via `certbot --nginx`, renovação automática já agendada.
* **Rate limit** (`/etc/nginx/conf.d/material-ratelimit.conf`): 10 req/min por IP em `/api/`,
  rajada de 5 sem delay — `/api/chat` e `/api/chat/stream` chamam a OpenAI a cada requisição
  (custo real), e o endpoint é público sem autenticação. Validado: ~6 requisições passam, depois
  `429` até o limite renovar; não afeta os outros sites na mesma VPS (zona isolada por nome).
* Deploy via `git pull` em `/opt/material` + restart do service/container — sem CI/CD automático
  ainda.
* Cópias de referência das configs (nginx, systemd) em [`deploy/`](deploy/) — a config real fica
  na VPS; se o servidor precisar ser recriado, regenere o certificado com `certbot --nginx` em
  vez de copiar os caminhos de certificado literalmente.

## Endpoints da API

* `GET  /api/health`
* `POST /api/chat` `{ "question": str, "session_id": str | null }` — resposta única, igual desde o V1.
* `POST /api/chat/stream` — mesmo corpo, mas resposta em SSE com progresso por node (usado pelo frontend).
* `POST /api/feedback` `{ "question_id": int, "rating": str, "comment": str }`
* `POST /api/ingest` `{ "query": str, "kind": "papers"|"materials"|"both", "limit": int }`

## Validado neste ambiente

* Grafo LangGraph compila e executa.
* `uvicorn` sobe e `/api/health` responde.
* `/api/ingest` indexou papers reais (Semantic Scholar/Crossref/arXiv) e materiais reais (AFLOW)
  no Chroma usando BGE-M3.
* `/api/chat` end-to-end com `OPENAI_API_KEY` real: relatório completo em markdown, citando
  candidatos do AFLOW e papers reais (`gpt-5-chat-latest`, ~35s por pergunta; sem a chave,
  retorna 503 com mensagem clara).
* `npm run build` do frontend compila sem erros; testado também com Playwright (render +
  interação real do chat).
* **GNN end-to-end com `MP_API_KEY` real**: `/api/chat` com "titânio para turbina" → Materials
  Project retornou `mp-aaacsmow` (Ti), a estrutura completa foi buscada via `mp-api`, o MEGNet
  pré-treinado previu **0.0104 eV/átomo** de energia de formação (fisicamente coerente para um
  elemento puro), e o relatório final citou esse valor explicitamente como "previsão de modelo
  de rede neural (MEGNet), não um dado experimental nem calculado por DFT" — sem confundir com
  os valores reais de energia de formação que já vinham do AFLOW para os outros candidatos.
* **V3 end-to-end**: `/api/chat` com "Preveja as propriedades mecânicas do silício" → candidato
  do Materials Project (`mp-aaaditqj`) recebeu `gnn_bulk_modulus_gpa = 105.17`, e o relatório
  final citou "módulo de compressibilidade estimado por M3GNet ≈ 105 GPa" como estimativa de
  simulação, coerente com valores típicos de materiais covalentes. Em ~37s.
* **V4 end-to-end**: `/api/chat` com "Quais métodos de simulação são adequados para o silício?"
  → relaxação estrutural real rodou no candidato do Materials Project, convergiu em 53 passos, e
  o relatório citou energia inicial/final, força residual e variação de volume, identificando
  corretamente o M3GNet como substituto de DFT. Em ~48s.
* **V5/V6 lite end-to-end**: ver seção acima — loop de hipótese/crítica/reflexão validado nos
  caminhos de rejeição e aceite, e a melhoria do ranking por GNN confirmada lado a lado (mesmo
  caso de teste, 2 iterações → 1 iteração, mesmo resultado correto). Regressão das intenções
  V1-V4 confirmada após a mudança estrutural no grafo (de DAG linear para grafo com ciclo).
* **Consolidação**: band gap corrigido e validado (NaCl, ordem PBE < HSE < GLLB-SC fisicamente
  coerente), candidato hipotético sem semicondutividade agora rejeitado com base em band gap
  previsto (não só inferência qualitativa), bug do `node_ranker` ignorando dado real do AFLOW
  corrigido, e suite de 37 testes automatizados passando (`pytest`, ~2min completo).
* **UX (streaming + persistência)**: `/api/chat/stream` testado direto (httpx) nos fluxos
  simples e de descoberta — `iteration` aparece corretamente nos eventos do loop V5/V6. No
  navegador via Playwright: screenshot durante o streaming mostra o passo atual com indicador
  pulsante; conversa sobrevive a reload de página (2 mensagens antes → 2 depois) via
  `localStorage`; botão "Limpar conversa" funciona; `npm run build` sem erros.
* **Quantum Chemistry (QRA)**: VQE de H₂ validado em produção via `/api/chat` real
  ("qual a energia do H2 via VQE?") — relatório citou HF/VQE/FCI corretamente, identificou o
  cálculo como quântico real (não ML), explicou energia de correlação eletrônica. Pergunta sobre
  água testada também: recusa rápida e honesta, sem travar nem fabricar energia. Testado pelo
  navegador de verdade via Playwright em `https://material.bronks.ia.br` (não só pela API).
* **Quantum Optimization (QAOA)**: testado localmente (Windows, sem precisar da VPS) via
  `/api/chat` completo — intenção `quantum_optimization` classificada corretamente, QAOA achou o
  corte máximo exato (4 de 4 arestas) no grafo-ciclo de 4 nós, confirmado por força bruta no
  próprio código, relatório final explicando o resultado e as limitações de escala.

## Próximos passos sugeridos

* Expandir o `quantum_chemistry` pra LiH e HeH⁺ (mesma classe de 4 qubits do H2, então
  provavelmente rápidos) — exige verificar a geometria de cada um com a mesma cautela usada pro
  H2 antes de adicionar (não vale a pena adicionar molécula com geometria não confirmada).
* `qchem-1`/`qopt-1` já estão no golden dataset (`backend/app/evaluation/golden_dataset.json`),
  mas ainda não rodamos a avaliação completa de novo incluindo elas — `qchem-1` só roda de
  verdade na VPS (precisa de `pyscf`), `qopt-1` roda em qualquer lugar.
* QAOA hoje só resolve o grafo-ciclo de 4 nós fixo — aceitar grafos diferentes do usuário
  exigiria parsear estrutura de grafo de texto livre, com risco real de inventar uma topologia
  que ele não pediu. Não fizemos por isso.
* Avaliar PennyLane (já confirmado que instala no Windows) como alternativa ao Qiskit pra
  comparar resultados — não testado ainda.
* `explain_material` não trata bem materiais 2D (achado pelo harness: grafeno citado com
  estrutura "monoclínica" — provavelmente outro alótropo de carbono do AFLOW/MP/OQMD, bancos
  focados em estruturas 3D).
* Expandir o golden dataset além das 16 perguntas-semente, e cobrir o parâmetro de ordenação por
  data do Semantic Scholar (não validado por causa de rate limit sem `SEMANTIC_SCHOLAR_API_KEY`).
* Observability real (LangSmith/Phoenix/OpenTelemetry) ou ao menos latência/tokens/custo por
  pergunta no SQLite — hoje só salvamos pergunta/resposta, sem métricas.
* Rodar `estimate_bulk_modulus` para mais de 1 candidato quando a latência permitir (hoje
  `limit=1` em `enrich_with_bulk_modulus`).
* Fônons via M3GNet + `phonopy` (citado no roadmap V4, ainda não implementado — exige nova
  dependência e várias avaliações de força em supercélulas deslocadas).
* Mais testes de regressão ponta a ponta pra cada intent do V1-V6 (hoje só `material_search` e
  o golden dataset cobrem isso de forma automatizada).
* Botões de feedback (👍/👎) no frontend — o endpoint `POST /api/feedback` já existe desde o V1,
  mas a UI nunca chamou ele.
* DFT real via Quantum ESPRESSO, se algum dia precisão importar mais que velocidade (exigiria
  WSL2/conda no Windows e pseudopotenciais).
* Trocar Chroma → Pinecone e SQLite → PostgreSQL quando for para produção (`DATABASE_URL` e o
  módulo `rag/vectorstore.py` foram escritos para essa troca ser pontual).
* Bayesian Optimization de verdade (Gaussian Process + função de aquisição) no lugar do ranking
  guloso atual, se quiser uma busca mais formal sobre o espaço químico.
* Self-Driving Lab real (V6 completo): fecharia o ciclo entre o que o V5/V6-lite propõe e
  experimentos físicos reais — fora de alcance sem laboratório/hardware real, mas a interface
  entre "hipótese aceita" e "próximo experimento" já existe em `discovery_verdict`.
* V7 do roadmap: AlphaFold para Materiais (modelos generativos de estrutura — MatterGen, diffusion
  models) — substituiria a substituição de elemento do V5 por geração de estrutura cristalina do
  zero. Provavelmente bate no mesmo limite de compute/treinamento que o V6 bateu em hardware.
