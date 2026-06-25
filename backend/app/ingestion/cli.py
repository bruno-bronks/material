import argparse

from app.ingestion.pipeline import ingest_materials, ingest_papers


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingestão de dados no RAG do MaterialGPT")
    parser.add_argument("--query", required=True, help="Termo de busca, ex: 'titanium alloy corrosion'")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--kind", choices=["papers", "materials", "both"], default="both")
    args = parser.parse_args()

    if args.kind in ("papers", "both"):
        n = ingest_papers(args.query, limit=args.limit)
        print(f"papers: {n} chunks indexados")

    if args.kind in ("materials", "both"):
        n = ingest_materials(args.query, limit=args.limit)
        print(f"materials: {n} chunks indexados")


if __name__ == "__main__":
    main()
