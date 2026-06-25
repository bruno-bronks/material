import json
import time
from datetime import datetime, timezone
from pathlib import Path

from app.agent.graph import build_graph
from app.evaluation.judge import judge_answer

DATASET_PATH = Path(__file__).resolve().parent / "golden_dataset.json"
RESULTS_DIR = Path(__file__).resolve().parents[2] / "data" / "eval_runs"


def load_dataset() -> list[dict]:
    return json.loads(DATASET_PATH.read_text(encoding="utf-8"))


def run_golden_dataset(dataset: list[dict] | None = None) -> dict:
    """Harness: Question -> MaterialGPT -> Answer -> Judge LLM -> Metrics -> Score."""
    graph = build_graph()
    dataset = dataset if dataset is not None else load_dataset()

    results = []
    for item in dataset:
        t0 = time.time()
        report, intent, error = "", "", None
        try:
            state = graph.invoke({"session_id": "eval", "user_question": item["question"]})
            report = state.get("report", "")
            intent = state.get("intent", "")
        except Exception as exc:  # noqa: BLE001 - harness não deve parar no primeiro erro
            error = str(exc)
        elapsed = time.time() - t0

        score = None
        if report:
            try:
                score = judge_answer(item["question"], report).model_dump()
            except Exception as exc:  # noqa: BLE001
                error = f"judge falhou: {exc}"

        results.append(
            {
                "id": item["id"],
                "category": item["category"],
                "question": item["question"],
                "intent": intent,
                "elapsed_s": round(elapsed, 1),
                "error": error,
                "score": score,
            }
        )

        verdict = score.get("passed") if score else "ERRO"
        print(f"[{item['id']:14s}] intent={intent or '-':20s} {elapsed:5.1f}s  passed={verdict}")

    summary = _summarize(results)
    path = _save_run(results, summary)
    print(f"\nRelatório salvo em {path}")
    return summary


def _summarize(results: list[dict]) -> dict:
    scored = [r for r in results if r["score"]]
    passed = sum(1 for r in scored if r["score"]["passed"])

    def avg(key: str) -> float | None:
        if not scored:
            return None
        return round(sum(r["score"][key] for r in scored) / len(scored), 2)

    return {
        "total": len(results),
        "scored": len(scored),
        "errors": len(results) - len(scored),
        "passed": passed,
        "pass_rate": round(passed / len(scored), 2) if scored else None,
        "avg_relevance": avg("relevance"),
        "avg_faithfulness": avg("faithfulness"),
        "avg_hallucination_risk": avg("hallucination_risk"),
        "avg_confidence_calibration": avg("confidence_calibration"),
    }


def _save_run(results: list[dict], summary: dict) -> Path:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = RESULTS_DIR / f"{timestamp}.json"
    path.write_text(
        json.dumps({"summary": summary, "results": results}, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    summary = run_golden_dataset()
    print(json.dumps(summary, indent=2, ensure_ascii=False))
