## Phase 4 - Persistent Vector Store / Index Lifecycle

Status: COMPLETED

Implemented:

- Added Chroma PersistentClient with local persistence.
- Split document indexing and RAG querying into separate modules:
  - phase4/index_documents.py
  - phase4/rag_query.py
- Added source-based document existence check.
- Added SHA-256 file hash calculation.
- Stored file hash in Chroma metadata.
- Added document update detection.
- Reindexing flow:
  - New document → index
  - Existing unchanged document → skip
  - Existing changed document → delete old chunks and rebuild index
- Verified that updated document content is reflected in RAG answers.
- Added data/chroma/ to .gitignore.

Next:

- Improve multi-document indexing flow.
- Add source citation to final answer.
- Start FastAPI integration.