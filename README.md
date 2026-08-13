# 🔍 LexiSearch RAG

**Upload documents. Ask questions. Get answers with exact page citations — or an honest "not found" instead of a guess.**

A Retrieval-Augmented Generation system built around hybrid search (semantic + keyword), reciprocal rank fusion, and citation-forced generation — designed so every claim in every answer traces back to a specific document and page.


[![Live Demo](https://img.shields.io/badge/🚀%20Live%20Demo-Streamlit-FF4B4B?style=for-the-badge)](https://lexisearch-rag-ajqgd6s57rxbg2teuj2hvq.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![LLM Powered](https://img.shields.io/badge/LLM-Powered-8A2BE2?style=for-the-badge&logo=openai&logoColor=white)]()

---

## ✨ Features

- 📄 **Upload any PDF** — reports, contracts, research papers, regulations
- 🧠 **Hybrid retrieval** — dense vector search (semantic) + BM25 (exact keyword) fused via Reciprocal Rank Fusion
- 📌 **Citation-forced answers** — every claim is grounded in a specific document + page number
- 🚫 **Confidence-gated refusal** — if the answer isn't in the documents, the system says so instead of hallucinating
- ⚡ **Zero-persistence sessions** — documents are processed entirely in memory, nothing touches disk, nothing is stored after your session ends
- 🎨 **Custom reading-room UI** — answers rendered as index cards with a call number and a "sourced" stamp, citations rendered as catalogue entries

---

## 🏗️ How It Works

**1. Document Ingestion & Chunking** — `chunker.py`
Raw PDF text is extracted page-by-page (preserving filename + page number as metadata) and split into overlapping chunks, so context isn't lost at chunk boundaries.

**2. Dual Indexing** — `indexer.py`
Every chunk is indexed two ways in parallel:
- **Dense:** embedded into 384-dimensional vectors via `all-MiniLM-L6-v2` — captures meaning, not just words
- **Sparse:** indexed with BM25 — catches exact terms, jargon, and identifiers dense search can miss

**3. Hybrid Retrieval & Fusion** — `retriever.py`
A query hits both indexes independently. The two ranked result lists are merged with **Reciprocal Rank Fusion**, balancing conceptual relevance against exact keyword matches before reranking.

**4. Grounded Generation** — `generator.py`
The top fused chunks are injected into a prompt sent to **Llama 3.3 70B via the Groq API**, with strict instructions to answer using *only* the provided context — no outside knowledge, no fabrication.

**5. UI Rendering** — `app.py`
Questions render as call slips, answers render as index cards with a citation stamp (`SOURCED ✓` / `NOT ON SHELF`), and every citation is expandable to show the exact source text.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| UI | Streamlit |
| PDF parsing | PyMuPDF |
| Dense embeddings | `sentence-transformers` (`all-MiniLM-L6-v2`) |
| Sparse search | `rank-bm25` |
| Fusion | Reciprocal Rank Fusion (custom implementation, `numpy`) |
| Generation | Groq API — Llama 3.3 70B |
| Uptime | GitHub Actions keep-alive workflow |

---

## 📁 Project Structure

```
lexisearch-rag/
├── .github/
│   └── workflows/
│       └── main.yml          # scheduled keep-alive job
├── src/
│   ├── app.py                 # Streamlit UI + session state
│   ├── chunker.py              # PDF extraction + chunking
│   ├── indexer.py              # dense + sparse index builder
│   ├── retriever.py            # hybrid search + RRF fusion
│   └── generator.py            # citation-forced LLM generation
├── .env.example                # required environment variables
├── .gitignore
├── README.md
├── requirements.txt
└── wake_up.py                  # keep-alive ping script
```

---

## 🚀 Running Locally

```bash
git clone https://github.com/shakshi-soni/LEXISEARCH-RAG.git
cd LEXISEARCH-RAG

pip install -r requirements.txt

cp .env.example .env
# add your GROQ_API_KEY inside .env

streamlit run src/app.py
```

---

## 🔑 Environment Variables

| Variable | Description |
|---|---|
| `GROQ_API_KEY` | Your Groq API key, used for answer generation |

---

## 🧭 Design Notes

- **No database, no persistence.** All indexing happens in `st.session_state` — documents and indexes exist only for the duration of a browser session, which keeps the tool privacy-friendly and simple to deploy.
- **Confidence over completeness.** The system is designed to refuse rather than guess when retrieved context doesn't support a confident answer — this is a deliberate constraint, not a limitation.

---

## 🗺️ Roadmap

- [ ] Cross-encoder reranking on top of RRF-fused candidates
- [ ] Evaluation harness — retrieval precision/recall + faithfulness scoring against a fixed test set
- [ ] Query decomposition for multi-part questions
- [ ] Multi-document comparison mode

---
## 🙋‍♂️ About the Developer

Built with ❤️ by **[SHAKSHI SONI]**

I'm a developer passionate about building practical AI applications that solve real-world problems. This project explores agentic AI design — where an LLM doesn't just chat, but *acts*, by calling tools, remembering context, and making decisions autonomously.
---

📫 **Connect with me:**
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=flat&logo=linkedin)](https://linkedin.com/in/yourprofile)


<div align="center">

**⭐ If you found this project interesting, please give it a star! It helps a lot.**
## 📄 License

MIT
