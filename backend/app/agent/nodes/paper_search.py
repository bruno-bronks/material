from app.agent.state import MaterialState
from app.llm.client import get_llm
from app.prompts.loader import render_prompt
from app.rag.context_builder import build_context, context_to_prompt_text
from app.tools.router import search_papers


def node_paper_search(state: MaterialState) -> dict:
    question = state["user_question"]

    papers = search_papers(question)
    rag_context = build_context(question)
    context_text = context_to_prompt_text(rag_context)

    if papers:
        papers_block = "\n".join(
            f"- {paper.get('title')} ({paper.get('year')}) DOI:{paper.get('doi')}"
            for paper in papers[:10]
        )
        context_text = f"{context_text}\n\n### tools (Semantic Scholar / Crossref / arXiv)\n{papers_block}"

    prompt = render_prompt("paper_search.jinja2", question=question, context=context_text)
    response = get_llm().invoke(prompt)

    return {"papers": papers, "context": rag_context, "raw_answer": response.content}
