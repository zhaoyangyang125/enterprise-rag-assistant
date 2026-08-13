### Phase 1 - Basic Vector Search

Status: **COMPLETED**

已完成：

- 使用 `text-embedding-v4` 将文本转换为 1024 维向量
- 将用户问题转换为 Embedding
- 手写 Cosine Similarity
- 计算问题与各文档之间的相似度
- 按 similarity 从高到低排序
- 实现 Top-K Retrieval
- 将检索流程封装为 `search_similar_documents()`
- 使用不同问题验证 Semantic Search

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


## Current Task

Phase 2 - Document Loading & Chunking

下一步：

1. 准备真实 TXT 文档
2. 读取文件内容
3. 理解为什么长文档需要 Chunking
4. 实现最基础文本切分
5. 学习 chunk_size
6. 学习 chunk_overlap
7. 为 Chunk 保存 metadata