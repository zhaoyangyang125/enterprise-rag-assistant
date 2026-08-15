import os
import hashlib
import chromadb
import dashscope
from dotenv import load_dotenv

from phase2.document_loader import load_txt
from phase2.chunking import (
    chunk_by_section,
    build_section_documents
)


load_dotenv()

# 中文：计算文件内容的 SHA-256 Hash
# 函数名：calculate_file_hash
# file_path：文件路径
# 返回值：代表文件内容的 Hash 字符串
def calculate_file_hash(file_path: str) -> str:
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        while True:
            data = file.read(8192)

            if not data:
                break

            sha256.update(data)

    return sha256.hexdigest()


# 中文：把文本列表转换成 Embedding
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


# 中文：创建持久化 Chroma
client = chromadb.PersistentClient(
    path="data/chroma"
)

collection = client.get_or_create_collection(
    name="company_documents"
)
# 中文：取得数据库中某个文件保存的 Hash
# 函数名：get_stored_file_hash
# collection：Chroma Collection
# source：文件名
# 返回值：数据库中的 Hash；找不到返回 None
def get_stored_file_hash(
    collection,
    source: str
) -> str | None:

    result = collection.get(
        where={
            "source": source
        }
    )

    if len(result["ids"]) == 0:
        return None

    metadata = result["metadatas"][0]

    return metadata.get("file_hash")


# 中文：检查某个文件是否已经存在于 Chroma
# 函数名：document_exists
# collection：Chroma Collection
# source：文件名
# 返回值：存在返回 True，不存在返回 False
def document_exists(
    collection,
    source: str
) -> bool:

    result = collection.get(
        where={
            "source": source
        }
    )

    return len(result["ids"]) > 0



# 中文：删除指定 source 的所有 Chunk
# 函数名：delete_document
# collection：Chroma Collection
# source：文件名
def delete_document(
    collection,
    source: str
) -> None:

    collection.delete(
        where={
            "source": source
        }
    )


# 中文：把 Chunk 加入 Chroma
def add_documents(
    documents: list,
    collection,
    file_hash: str
) -> None:
    texts = []
    metadatas = []
    ids = []

    for document in documents:
        texts.append(document["text"])

        metadatas.append({
            "source": document["source"],
            "title": document["title"],
            "chunk_index": document["chunk_index"],
            "file_hash": file_hash
        })

        ids.append(
            f'{document["source"]}_{document["chunk_index"]}'
        )

    vectors = get_embeddings(texts)

    collection.add(
        ids=ids,
        embeddings=vectors,
        documents=texts,
        metadatas=metadatas
    )


file_path = "phase2/sample_documents/company_rules.txt"

file_hash = calculate_file_hash(file_path)

text = load_txt(file_path)

sections = chunk_by_section(text)

documents = build_section_documents(
    sections=sections,
    source="company_rules.txt"
)

source = "company_rules.txt"

stored_hash = get_stored_file_hash(
    collection=collection,
    source=source
)


if stored_hash is None:
    # 中文：数据库里完全没有这个文件
    print(f"{source} is not indexed. Start indexing...")

    add_documents(
        documents=documents,
        collection=collection,
        file_hash=file_hash
    )

    print("Indexing completed.")


elif stored_hash == file_hash:
    # 中文：文件存在，而且内容没有变化
    print(f"{source} has not changed. Skip indexing.")


else:
    # 中文：文件存在，但是内容已经发生变化
    print(f"{source} has changed. Reindexing...")

    delete_document(
        collection=collection,
        source=source
    )

    add_documents(
        documents=documents,
        collection=collection,
        file_hash=file_hash
    )

    print("Reindexing completed.")

print("Stored count:", collection.count())



print("File hash:", file_hash)


