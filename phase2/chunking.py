import re

from phase2.document_loader import load_txt


# 中文：为 Chunk 添加来源等 Metadata
# 函数名：add_metadata
# chunks：切分后的文本列表
# source：原始文件名
# 返回值：包含 text / source / chunk_index 的字典列表
def add_metadata(
    chunks: list,
    source: str
) -> list:
    documents = []

    for index, chunk in enumerate(chunks):
        documents.append({
            "text": chunk,
            "source": source,
            "chunk_index": index
        })

    return documents


# 中文：按照“第X章”拆分文档
# 函数名：chunk_by_section
# text：完整文档文本
# 返回值：章节列表
def chunk_by_section(text: str) -> list:
    sections = re.split(
        r"(?=第\d+章\s)",
        text
    )

    chunks = []

    for section in sections:
        section = section.strip()

        if not section:
            continue

        chunks.append(section)

    return chunks


# 中文：优先按照段落边界切分文本
# 函数名：chunk_by_paragraph
# text：需要切分的长文本
# chunk_size：每个 Chunk 的目标最大字符数
# 返回值：多个尽量保持段落完整的 Chunk
def chunk_by_paragraph(
    text: str,
    chunk_size: int = 100
) -> list:
    paragraphs = text.split("\n\n")

    chunks = []
    current_chunk = ""

    for paragraph in paragraphs:
        if not paragraph.strip():
            continue

        candidate = (
            current_chunk + "\n\n" + paragraph
            if current_chunk
            else paragraph
        )

        if len(candidate) <= chunk_size:
            current_chunk = candidate
        else:
            if current_chunk:
                chunks.append(current_chunk)

            current_chunk = paragraph

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


# 中文：把章节列表转换成带 Metadata 的文档列表
# 函数名：build_section_documents
# sections：按章节切分后的文本列表
# source：来源文件名
# 返回值：带 text / source / title / section / chunk_index 的列表
def build_section_documents(
    sections: list,
    source: str
) -> list:

    if not sections:
        return []

    # 中文：第一个元素是整个文档标题
    title = sections[0]

    documents = []

    for index, section in enumerate(sections[1:]):

        # 中文：章节文本第一行就是章节标题
        # 例如：
        # 第2章 食事代
        section_title = section.splitlines()[0]

        documents.append({
            "text": section,
            "source": source,
            "title": title,
            "section": section_title,
            "chunk_index": index
        })

    return documents

# 中文：只有直接运行 chunking.py 时才执行下面测试代码
if __name__ == "__main__":
    file_path = "phase2/sample_documents/company_rules.txt"

    text = load_txt(file_path)

    sections = chunk_by_section(text)

    documents = build_section_documents(
        sections=sections,
        source="company_rules.txt"
    )

    for document in documents:
        print(document)