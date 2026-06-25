"""Rótulos amigáveis por node, usados só para exibir progresso em tempo real no frontend."""

NODE_LABELS = {
    "planner": "Identificando a intenção da pergunta",
    "material_search": "Buscando materiais (Materials Project, OQMD, AFLOW)",
    "paper_search": "Buscando artigos científicos",
    "explain_material": "Reunindo informações para explicar o material",
    "compare_materials": "Comparando candidatos",
    "property_prediction": "Prevendo propriedades (GNN + simulação)",
    "simulation": "Selecionando e executando simulação",
    "ranker": "Ordenando candidatos por estabilidade",
    "aggregator": "Consolidando resultados",
    "report_generator": "Gerando relatório final",
    "node_hypothesis": "Buscando material base e decidindo onde intervir",
    "node_material_generator": "Gerando candidato hipotético (substituição de elemento)",
    "node_simulation_planner": "Simulando candidato (GNN + relaxação)",
    "node_critic": "Avaliando se o candidato atende ao objetivo",
    "node_reflection": "Tentativa rejeitada — avançando para o próximo candidato",
}
