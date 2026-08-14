import os

import chromadb
import dashscope
from dotenv import load_dotenv

from phase2.document_loader import load_txt


from phase2.chunking import (
    chunk_by_section,
    build_section_documents
)


# 中文：读取 .env 文件
load_dotenv()


# 中文：调用 DashScope，把文本列表转换成 Embedding
# 函数名：get_embeddings
# texts：文本列表
# 返回值示例：
# [
#     [第0条文本的1024维向量],
#     [第1条文本的1024维向量]
# ]
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


# 中文：创建 Chroma Client
client = chromadb.Client()


# 中文：创建 / 获取 Collection
# 可以暂时理解成“向量表”
collection = client.get_or_create_collection(
    name="company_documents"
)


# 中文：把 Chunk 转成向量，并加入 Chroma
# 函数名：add_documents
# documents：Chunk 列表
# collection：保存数据的 Collection
def add_documents(documents: list, collection) -> None:
    texts = []
    metadatas = []
    ids = []

    # 中文：把 documents 拆成 Chroma 需要的三组数据
    for document in documents:
        texts.append(document["text"])

        metadatas.append({
            "source": document["source"],
            "title": document["title"],
            "chunk_index": document["chunk_index"]
        })

        ids.append(
            f'{document["source"]}_{document["chunk_index"]}'
        )

    # 中文：每条文本转换成一个1024维向量
    vectors = get_embeddings(texts)

    # 中文：真正存入 Chroma
    collection.add(
        ids=ids,
        embeddings=vectors,
        documents=texts,
        metadatas=metadatas
    )


# 中文：根据用户问题搜索最相关的文档
# 函数名：search_documents
# question：用户问题
# collection：搜索的 Chroma Collection
# top_k：返回几个结果
# 返回值：
# [
#     {
#         "text": "...",
#         "source": "...",
#         "title": "...",
#         "chunk_index": 1,
#         "distance": 1.02
#     }
# ]
def search_documents(
    question: str,
    collection,
    top_k: int = 2
) -> list:

    # 中文：用户问题 → 1024维向量
    question_vector = get_embeddings([question])[0]

    # 中文：从 Chroma 搜索 Top-K
    query_result = collection.query(
        query_embeddings=[question_vector],
        n_results=top_k
    )

    # 中文：取出“第一个问题”的所有结果
    result_documents = query_result["documents"][0]
    result_metadatas = query_result["metadatas"][0]
    result_distances = query_result["distances"][0]

    results = []

    # 中文：把 document / metadata / distance
    # 按相同 index 重新组合成一条记录
    for index in range(len(result_documents)):
        metadata = result_metadatas[index]

        results.append({
            "text": result_documents[index],
            "source": metadata["source"],
            "title": metadata["title"],
            "chunk_index": metadata["chunk_index"],
            "distance": result_distances[index]
        })

    return results


# 中文：把搜索结果整理成给 LLM 使用的参考资料
# 函数名：build_context
# results：search_documents 返回的结果列表
# 返回值：拼接好的参考资料字符串
def build_context(results: list) -> str:
    context_parts = []

    for index, result in enumerate(results):
        context_parts.append(
            f"【参考資料{index + 1}】\n"
            f"{result['text']}"
        )

    context = "\n\n".join(context_parts)

    return context


# 中文：根据 Context 和用户问题生成最终回答
# 函数名：generate_answer
# question：用户问题
# context：检索到的参考资料
# 返回值：LLM 生成的回答
def generate_answer(question: str, context: str) -> str:

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

    # 中文：请求成功时
    if response.status_code == 200:
        return response.output.choices[0].message.content

    # 中文：请求失败时打印错误信息
    print("LLM request failed")
    print("Status code:", response.status_code)
    print("Error code:", response.code)
    print("Error message:", response.message)

    return ""


# =========================
# 中文：下面开始真正执行程序
# =========================


# 中文：读取 Phase 2 的真实 TXT 文档
file_path = "phase2/sample_documents/company_rules.txt"

text = load_txt(file_path)


# 中文：按照“第X章”拆分文档
#
# 返回示例：
#
# [
#     "社員就業規則",
#     "第1章 有給休暇...",
#     "第2章 在宅勤務...",
#     "第3章 交通費...",
#     "第4章 社員食堂..."
# ]
sections = chunk_by_section(text)


# 中文：把 sections 整理成带 metadata 的 Chunk
#
# 返回示例：
#
# [
#     {
#         "text": "第1章 有給休暇...",
#         "source": "company_rules.txt",
#         "title": "社員就業規則",
#         "chunk_index": 0
#     },
#     ...
# ]
documents = build_section_documents(
    sections=sections,
    source="company_rules.txt"
)


# 中文：把真正从 TXT 读取、切分出来的 Chunk 存进 Chroma
add_documents(
    documents=documents,
    collection=collection
)


print("Collection:", collection.name)
print("Stored count:", collection.count())


# 中文：用户问题
question = "家で仕事をすることはできますか？"


# 中文：搜索 Top-2
results = search_documents(
    question=question,
    collection=collection,
    top_k=2
)


# 中文：打印检索结果
for result in results:
    print("-----")
    print("Document:", result["text"])
    print("Source:", result["source"])
    print("Title:", result["title"])
    print("Chunk Index:", result["chunk_index"])
    print("Distance:", result["distance"])


# 中文：把检索结果整理成 Context
context = build_context(results)


print("\n===== Context =====")
print(context)


# 中文：把 Context + 用户问题交给 LLM
answer = generate_answer(
    question=question,
    context=context
)


print("\n===== Answer =====")
print(answer)