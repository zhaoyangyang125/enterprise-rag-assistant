import os
import math
import dashscope
from dotenv import load_dotenv


load_dotenv()

print("API KEY loaded:", bool(os.getenv("DASHSCOPE_API_KEY")))
print("Embedding model:", os.getenv("EMBEDDING_MODEL"))

results = []

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
    

response = get_embeddings(documents)
question_response = get_embeddings([question])
embeddings = response.output["embeddings"]

print("向量数量:", len(embeddings))
print("第一个向量维度:", len(embeddings[0]["embedding"]))
print("第一个向量前5个数字:", embeddings[0]["embedding"][:5])

question_vector = question_response.output["embeddings"][0]["embedding"]
print("问题向量维度:", len(question_vector))
print("问题向量前5个数字:", question_vector[:5])

for embedding_item in embeddings:
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

top_k = results[:2]

for result in top_k:
    print(result)