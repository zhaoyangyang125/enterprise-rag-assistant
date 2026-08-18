import os

import chromadb
import dashscope
from dotenv import load_dotenv


# 中文：读取 .env
load_dotenv()


# 中文：把文本列表转换成 Embedding
# 函数名：get_embeddings
# texts：需要转换的文本列表
# 返回值：向量列表
def get_embeddings(texts: list) -> list:
    response = dashscope.TextEmbedding.call(
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        model=os.getenv("EMBEDDING_MODEL"),
        input=texts,
        dimension=1024
    )

    embeddings = response.output["embeddings"]

    vectors = []

    for item in embeddings:
        vectors.append(item["embedding"])

    return vectors


# 中文：连接已经持久化保存的 Chroma
client = chromadb.PersistentClient(
    path="data/chroma"
)


# 中文：取得已经存在的 Collection
collection = client.get_or_create_collection(
    name="company_documents"
)


# 中文：根据用户问题搜索最相关的文档
# 函数名：search_documents
# question：用户问题
# collection：查询的 Collection
# top_k：返回几个最相关 Chunk
# 返回值：整理后的检索结果列表
def search_documents(
    question: str,
    collection,
    top_k: int = 2
) -> list:

    # 中文：
    # Question
    # ↓
    # Embedding
    # ↓
    # Question Vector
    question_vector = get_embeddings([question])[0]

    # 中文：使用问题向量查询已经存在的向量数据库
    query_result = collection.query(
        query_embeddings=[question_vector],
        n_results=top_k
    )

    # 中文：取第一个问题的 Top-K 查询结果
    result_documents = query_result["documents"][0]
    result_metadatas = query_result["metadatas"][0]
    result_distances = query_result["distances"][0]

    results = []

    # 中文：重新整理成我们自己的统一结构
    for index in range(len(result_documents)):
        metadata = result_metadatas[index]

        results.append({
            "text": result_documents[index],
            "source": metadata["source"],
            "title": metadata["title"],
            "section": metadata["section"],
            "chunk_index": metadata["chunk_index"],
            "distance": result_distances[index]
        })

    return results


# 中文：从检索结果中整理来源信息
# 函数名：build_sources
# results：Top-K 检索结果
# 返回值：包含文件名和 Chunk 信息的来源字符串
def build_sources(results: list) -> str:
    sources = []

    for result in results:
        source_text = (
            f'{result["source"]} / '
            f'{result["section"]}'
        )

        if source_text not in sources:
            sources.append(source_text)

    return "\n".join(
        f"- {source}"
        for source in sources
    )
# 中文：把 Top-K 文档整理成给 LLM 使用的 Context
# 同时加入来源文件名
def build_context(results: list) -> str:
    context_parts = []

    for index, result in enumerate(results):
        context_parts.append(
            f"【参考資料{index + 1}】\n"
            f"出典: {result['source']}\n"
            f"{result['text']}"
        )

    return "\n\n".join(context_parts)


# 中文：根据 Context 和 Question 生成最终回答
# 函数名：generate_answer
def generate_answer(
    question: str,
    context: str
) -> str:

    messages = [
        {
            "role": "system",
            "content": (
                "あなたは社内文書QAアシスタントです。"
                "必ず参考資料だけを使用して回答してください。"
                "参考資料に答えがない場合は、"
                "「参考資料からは確認できません」と回答してください。"
            )
        },
        {
            "role": "user",
            "content": (
                f"【参考資料】\n"
                f"{context}\n\n"
                f"【質問】\n"
                f"{question}"
            )
        }
    ]

    response = dashscope.Generation.call(
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        model=os.getenv("LLM_MODEL"),
        messages=messages,
        result_format="message"
    )

    if response.status_code == 200:
        return response.output.choices[0].message.content

    print("LLM request failed")
    print("Status code:", response.status_code)
    print("Error code:", response.code)
    print("Error message:", response.message)

    return ""

