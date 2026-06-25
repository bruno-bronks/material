export type RankingItem = {
  source?: string;
  material_id?: string;
  material_name?: string;
  composition?: string;
  density?: number;
  band_gap?: number;
  crystal_structure?: string;
  energy_above_hull?: number;
  stability?: number;
  formation_energy?: number;
  gnn_formation_energy_ev_atom?: number;
};

const SOURCE_LABELS: Record<string, string> = {
  materials_project: "Materials Project",
  oqmd: "OQMD",
  aflow: "AFLOW",
};

function stabilityInfo(material: RankingItem): { label: string; value: number; predicted: boolean } | null {
  // Mesma ordem de prioridade do node_ranker: dado real do banco antes de previsão de GNN,
  // nunca apresentados como se tivessem o mesmo nível de confiança.
  if (typeof material.energy_above_hull === "number") {
    return { label: "Energia acima do hull", value: material.energy_above_hull, predicted: false };
  }
  if (typeof material.stability === "number") {
    return { label: "Estabilidade (OQMD)", value: material.stability, predicted: false };
  }
  if (typeof material.formation_energy === "number") {
    return { label: "Energia de formação", value: material.formation_energy, predicted: false };
  }
  if (typeof material.gnn_formation_energy_ev_atom === "number") {
    return { label: "Energia de formação (previsão GNN)", value: material.gnn_formation_energy_ev_atom, predicted: true };
  }
  return null;
}

export default function MaterialCard({ material, highlighted }: { material: RankingItem; highlighted?: boolean }) {
  const stability = stabilityInfo(material);

  return (
    <div className={`material-card${highlighted ? " highlighted" : ""}`}>
      <div className="material-card-header">
        <span className="material-card-name">{material.material_name ?? material.composition ?? "?"}</span>
        {material.source && (
          <span className="source-badge">{SOURCE_LABELS[material.source] ?? material.source}</span>
        )}
      </div>
      <div className="material-card-body">
        {stability && (
          <div className="material-card-row">
            <span>
              {stability.label}
              {stability.predicted ? " *" : ""}
            </span>
            <span>{stability.value.toFixed(3)} eV/átomo</span>
          </div>
        )}
        {typeof material.band_gap === "number" && (
          <div className="material-card-row">
            <span>Band gap</span>
            <span>{material.band_gap.toFixed(2)} eV</span>
          </div>
        )}
        {typeof material.density === "number" && (
          <div className="material-card-row">
            <span>Densidade</span>
            <span>{material.density.toFixed(2)} g/cm³</span>
          </div>
        )}
        {material.crystal_structure && (
          <div className="material-card-row">
            <span>Estrutura</span>
            <span>{material.crystal_structure}</span>
          </div>
        )}
      </div>
      {stability?.predicted && (
        <p className="material-card-note">* previsão de modelo de ML, não dado experimental/DFT do banco</p>
      )}
    </div>
  );
}
