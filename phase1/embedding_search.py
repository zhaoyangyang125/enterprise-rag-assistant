import math
import os

import dashscope
from dotenv import load_dotenv


load_dotenv()


documents = [
    "有給休暇は年間20日付与されます。",
    "在宅勤務は週3日まで利用できます。",
    "交通費は月額5万円を上限として支給されます。",
    "社員食堂は平日の11時から14時まで営業しています。"
]

question = "家で仕事をすることはできますか？"


# 中文：把多条文本发送给 Embedding 模型
# 函数名：get_embeddings
# texts：需要转换成向量的文本列表
# 返回值：Embedding API 返回的完整响应
def get_embeddings(texts: list) -> object:
    response = dashscope.TextEmbedding.call(
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        model=os.getenv("EMBEDDING_MODEL"),
        input=texts,
        dimension=1024
    )

    return response


# 中文：计算两个向量的余弦相似度
# 函数名：cosine_similarity
# vector_a：第一个向量
# vector_b：第二个向量
# 返回值：两个向量的相似度分数
def cosine_similarity(vector_a: list, vector_b: list) -> float:
    dot_product = sum(
        a * b
        for a, b in zip(vector_a, vector_b)
    )

    magnitude_a = math.sqrt(
        sum(a * a for a in vector_a)
    )

    magnitude_b = math.sqrt(
        sum(b * b for b in vector_b)
    )

    return dot_product / (magnitude_a * magnitude_b)


# 中文：根据用户问题检索最相关的文档
# 函数名：search_similar_documents
# question：用户问题
# documents：待检索文档列表
# top_k：返回相似度最高的前几条
# 返回值：排序后的 Top-K 检索结果
def search_similar_documents(
    question: str,
    documents: list,
    top_k: int = 2
) -> list:
    document_response = get_embeddings(documents)
    document_embeddings = document_response.output["embeddings"]

    question_response = get_embeddings([question])
    question_vector = question_response.output["embeddings"][0]["embedding"]

    results = []

    for embedding_item in document_embeddings:
        document_vector = embedding_item["embedding"]
        text_index = embedding_item["text_index"]

        similarity = cosine_similarity(
            question_vector,
            document_vector
        )

        results.append({
            "text": documents[text_index],
            "similarity": similarity
        })

    results.sort(
        key=lambda item: item["similarity"],
        reverse=True
    )

    return results[:top_k]


search_results = search_similar_documents(
    question,
    documents,
    top_k=2
)

for result in search_results:
    print(result)