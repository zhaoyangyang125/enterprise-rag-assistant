## Phase 3 - Vector Store & Basic RAG

状态：已完成

### 已完成功能

- 安装并使用 ChromaDB
- 创建 `company_documents` Collection
- 使用 DashScope Embedding 将文档 Chunk 转换为 1024 维向量
- 向 Chroma 中保存以下内容：
  - id
  - embedding
  - document text
  - metadata
- 实现 `add_documents()`
- 实现 `search_documents()`
- 实现 Top-K 向量检索
- 理解以下数据之间的对应关系：
  - `texts[0]`
  - `vectors[0]`
  - `metadatas[0]`
  - `ids[0]`
  - 它们共同代表同一个 Chunk
- 将 Chroma 原始查询结果整理成 `list[dict]`
- 实现 `build_context()`
- 实现 `generate_answer()`
- 打通 Phase 2 文档读取 / Chunking 与 Phase 3 Vector Store
- 完成最小可运行 RAG 流程：

```text
Document
↓
Chunk
↓
Embedding
↓
Chroma
↓
Retrieval
↓
Context
↓
LLM
↓
Answer

当前 Chunk 数据结构：

```python
{
    "text": "第2章 在宅勤務...",
    "source": "company_rules.txt",
    "title": "社員就業規則",
    "chunk_index": 1
}

验证示例：

- `家で仕事をすることはできますか？`
  → `在宅勤務は週3日まで利用できます。`

- `会社までの電車代は支給されますか？`
  → `交通費は月額5万円を上限として支給されます。`

- `休暇は何日ありますか？`
  → `有給休暇は年間20日付与されます。`

理解要点：

- Embedding 不是把文本切成 1024 份，而是把整段文本转换成 1024 维向量
- 相似度高表示两个向量在语义空间中更接近
- Top-K 表示返回相似度最高的前 K 条结果
- Top-K 结果不代表每一条都真正相关，后续需要进一步学习 threshold 和 Retriever 策略


```markdown
## Current Task

Phase 3 - Embedding & Vector Database

下一步：

1. 将 Phase 2 生成的 Chunk 转换为 Embedding
2. 理解 Vector DB 为什么存在
3. 安装并使用 Chroma
4. 将 Vector + Text + Metadata 保存到 Vector DB
5. 将用户问题转换为 Embedding
6. 使用 Vector Search 检索 Top-K Chunks
7. 对比 Phase 1 手写检索与 Vector DB 检索