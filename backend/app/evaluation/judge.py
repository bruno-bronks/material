from app.llm.client import get_llm
from app.prompts.loader import render_prompt
from app.schemas.evaluation import EvaluationScore


def judge_answer(question: str, report: str) -> EvaluationScore:
    """LLM-as-a-Judge: avalia qualidade intrínseca da resposta (sem gabarito de referência)."""
    prompt = render_prompt("evaluation_judge.jinja2", question=question, report=report)
    return get_llm(temperature=0).with_structured_output(EvaluationScore).invoke(prompt)
