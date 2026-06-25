"use client";

import { useEffect, useRef } from "react";
import type { GLViewer } from "3dmol";

// 3Dmol manipula WebGL/canvas direto no DOM — só pode rodar no navegador, nunca durante o
// build/SSR do Next.js. Import dinâmico dentro do useEffect evita isso (o import de tipo acima
// é apagado em tempo de compilação, não tem efeito em runtime).
export default function CrystalViewer({ cif }: { cif: string }) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;
    let cancelled = false;
    let viewer: GLViewer | undefined;

    import("3dmol").then(($3Dmol) => {
      if (cancelled || !containerRef.current) return;
      viewer = $3Dmol.createViewer(containerRef.current, { backgroundColor: "#131c2e" });
      const model = viewer.addModel(cif, "cif");
      viewer.addUnitCell(model, { box: { color: "#4f9dff" } });
      viewer.setStyle({}, { sphere: { scale: 0.3 }, stick: { radius: 0.1 } });
      viewer.zoomTo();
      viewer.render();
    });

    return () => {
      cancelled = true;
      viewer?.clear();
    };
  }, [cif]);

  return <div ref={containerRef} className="crystal-viewer" />;
}
