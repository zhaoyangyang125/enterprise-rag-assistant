# Enterprise Document QA Assistant

社内文書を対象とした RAG（Retrieval-Augmented Generation）型 QA アシスタントです。

複数の TXT 文書を自動的に読み込み、Embedding を生成して Chroma に保存し、ユーザーの質問に対して関連する文書 Chunk を検索します。

取得した文書を Context として LLM に渡すことで、社内文書に基づいた回答を生成します。

また、回答とは別に metadata から参照元ファイル・章情報を生成し、Source Citation を表示します。

## Demo

https://enterprise-rag-assistant-kc4v.onrender.com/

質問例：

```text
出張中の食事代はいくらまで支給されますか？
```

回答例：

```text
出張中の食事代は1日3000円を上限として支給されます。
```

Sources:

```text
- expense_rules.txt / 第2章 食事代
- expense_rules.txt / 第1章 出張費
```

---

## Features

* TXT 文書の読み込み
* Section 単位の Chunking
* DashScope Embedding
* Chroma Vector Database
* Semantic Search
* Top-K Retrieval
* Persistent Vector Store
* 複数文書の自動 Indexing
* SHA-256 による文書変更検知
* 未変更文書の Embedding Skip
* 更新文書の Reindex
* Metadata 管理
* Source Citation
* FastAPI Backend
* Web UI
* Docker
* Render Deployment

---

## Architecture

### Indexing Flow

```text
TXT Documents
    ↓
Load
    ↓
Section-based Chunking
    ↓
Build Metadata
    ↓
Embedding
    ↓
Chroma Vector Store
```

各 Chunk には以下の情報を保存します。

```text
document
embedding
metadata
id
```

Metadata:

```text
source
title
section
chunk_index
file_hash
```

---

### Query Flow

```text
User Question
    ↓
Question Embedding
    ↓
Chroma Top-K Search
    ↓
Retrieved Documents
    ↓
Build Context
    ↓
Context + Question
    ↓
LLM
    ↓
Answer
```

同時に、取得した metadata から Source 情報を生成します。

```text
metadata
    ↓
source + section
    ↓
Sources
```

Source Citation は LLM に生成させず、検索結果の metadata からプログラム側で生成しています。

---

## Incremental Indexing

文書を毎回すべて Embedding するのではなく、SHA-256 Hash を使用してファイル変更を検知します。

```text
New File
→ ADD

Unchanged File
→ SKIP

Modified File
→ Delete old chunks
→ Re-Embedding
→ Reindex
```

これにより、変更されていない文書に対する不要な Embedding API 呼び出しを防ぎます。

---

## Multi-Document Retrieval

現在のサンプルデータ：

```text
company_rules.txt
expense_rules.txt
```

Indexing 結果：

```text
company_rules.txt : 4 chunks
expense_rules.txt : 2 chunks

Total : 6 chunks
```

複数文書は同一 Chroma Collection に保存し、metadata の `source` で文書を識別しています。

---

## API

### Health Check

```http
GET /health
```

Response:

```json
{
  "status": "ok"
}
```

### Ask

```http
POST /ask
```

Request:

```json
{
  "question": "出張中の食事代はいくらまで支給されますか？"
}
```

Response:

```json
{
  "answer": "出張中の食事代は1日3000円を上限として支給されます。",
  "sources": "- expense_rules.txt / 第2章 食事代"
}
```

---

## Tech Stack

### Backend

* Python 3.12
* FastAPI
* Pydantic
* Uvicorn

### AI / RAG

* DashScope
* Embedding API
* LLM API
* ChromaDB

### Infrastructure

* Docker
* Render

### Frontend

* HTML
* CSS
* JavaScript
* Fetch API

---

## Project Structure

```text
enterprise-rag-assistant/
│
├── phase1/
│   └── Vector similarity search
│
├── phase2/
│   ├── document_loader.py
│   ├── chunking.py
│   └── sample_documents/
│
├── phase3/
│   └── Vector Store / Minimal RAG
│
├── phase4/
│   ├── index_documents.py
│   └── rag_query.py
│
├── phase6/
│   ├── main.py
│   ├── rag_service.py
│   └── static/
│       └── index.html
│
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## Local Setup

仮想環境を作成します。

```bash
python -m venv .venv
```

Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

依存ライブラリをインストールします。

```bash
pip install -r requirements.txt
```

`.env` を作成します。

```text
DASHSCOPE_API_KEY=your_api_key
EMBEDDING_MODEL=your_embedding_model
LLM_MODEL=your_llm_model
```

文書を Indexing します。

```bash
python -m phase4.index_documents
```

FastAPI を起動します。

```bash
uvicorn phase6.main:app --reload
```

ブラウザ：

```text
http://127.0.0.1:8000/
```

Swagger UI：

```text
http://127.0.0.1:8000/docs
```

---

## Docker

Build:

```bash
docker build -t enterprise-rag-assistant .
```

Run:

```bash
docker run --rm -p 8000:8000 --env-file .env enterprise-rag-assistant
```

Container 起動時に文書 Indexing を行った後、FastAPI を起動します。

---

## Key Design Decisions

### Document と Embedding を別々に管理

Embedding は検索用の数値表現であり、元の Text に逆変換するものではありません。

Chroma には以下を一緒に保存します。

```text
Embedding
Document
Metadata
ID
```

検索時には Vector を使用して関連 Chunk を見つけ、取得した Document を LLM の Context として使用します。

### Source Citation を metadata から生成

LLM に出典を推測させるのではなく、検索結果に保存されている metadata を利用します。

これにより、回答と参照元の追跡性を高めています。

### Indexing と Query を分離

文書の Embedding は Indexing 時に生成し、文書が変更されない限り再利用します。

ユーザーの Question は毎回異なるため、Query 時に新しい Embedding を生成します。

---

## Status

Project completed and deployed.

* RAG pipeline: Completed
* Multi-document retrieval: Completed
* Incremental indexing: Completed
* Source Citation: Completed
* FastAPI: Completed
* Web UI: Completed
* Docker: Completed
* Render Deployment: Completed
