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


# 中文：取得指定目录下所有 TXT 文件
# 函数名：get_txt_files
# directory：文件夹路径
# 返回值：TXT 文件路径列表
def get_txt_files(directory: str) -> list:
    file_paths = []

    for file_name in os.listdir(directory):
        if file_name.endswith(".txt"):
            file_path = os.path.join(
                directory,
                file_name
            )

            file_paths.append(file_path)

    return file_paths


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
# 函数名：get_embeddings
# texts：需要转换的文本列表
# 返回值：Embedding 向量列表
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
        vectors.append(
            item["embedding"]
        )

    return vectors


# 中文：创建持久化 Chroma Client
client = chromadb.PersistentClient(
    path="data/chroma"
)


# 中文：取得或创建文档 Collection
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
# 函数名：add_documents
# documents：Chunk 列表
# collection：Chroma Collection
# file_hash：当前文件 Hash
def add_documents(
    documents: list,
    collection,
    file_hash: str
) -> None:

    texts = []
    metadatas = []
    ids = []

    for document in documents:
        texts.append(
            document["text"]
        )

        metadatas.append({
            "source": document["source"],
            "title": document["title"],
            "section": document["section"],
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


# =========================
# 中文：多文档索引流程
# =========================

directory = "phase2/sample_documents"

file_paths = get_txt_files(directory)


for file_path in file_paths:

    # 中文：取得文件名
    # 例如：
    # phase2/sample_documents/company_rules.txt
    # ↓
    # company_rules.txt
    source = os.path.basename(file_path)

    # 中文：计算当前文件 Hash
    file_hash = calculate_file_hash(
        file_path
    )

    # 中文：读取 TXT 文档
    text = load_txt(
        file_path
    )

    # 中文：按章节切分文档
    sections = chunk_by_section(
        text
    )

    # 中文：生成带 metadata 的 Chunk
    documents = build_section_documents(
        sections=sections,
        source=source
    )

    # 中文：取得数据库里的旧 Hash
    stored_hash = get_stored_file_hash(
        collection=collection,
        source=source
    )

    # 中文：数据库里没有这个文件
    if stored_hash is None:
        print(
            f"{source} is not indexed. "
            f"Start indexing..."
        )

        add_documents(
            documents=documents,
            collection=collection,
            file_hash=file_hash
        )

        print("Indexing completed.")

    # 中文：文件存在，而且内容没有变化
    elif stored_hash == file_hash:
        print(
            f"{source} has not changed. "
            f"Skip indexing."
        )

    # 中文：文件存在，但是内容发生了变化
    else:
        print(
            f"{source} has changed. "
            f"Reindexing..."
        )

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


print(
    "Stored count:",
    collection.count()
)