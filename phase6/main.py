from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import FileResponse


from phase6.rag_service import (
    collection,
    search_documents,
    build_context,
    generate_answer,
    build_sources
)


# 中文：用户请求数据
class AskRequest(BaseModel):
    question: str


app = FastAPI(
    title="Enterprise Document QA Assistant"
)


@app.get("/health")
def health():
    return {
        "status": "ok"
    }

@app.get("/")
def home():
    return FileResponse("phase6/static/index.html")


@app.post("/ask")
def ask(request: AskRequest):

    # 中文：根据问题检索最相关文档
    results = search_documents(
        question=request.question,
        collection=collection,
        top_k=2
    )

    # 中文：把检索结果整理成 LLM Context
    context = build_context(results)

    # 中文：生成回答
    answer = generate_answer(
        question=request.question,
        context=context
    )

    # 中文：从 metadata 生成来源信息
    sources = build_sources(results)

    return {
        "answer": answer,
        "sources": sources
    }