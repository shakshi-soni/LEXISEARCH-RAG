# LexiSearch RAG

[![Live Demo](https://img.shields.io/badge/🚀%20Live%20Demo-blue?style=for-the-badge)](https://lexisearch-rag-ajqgd6s57rxbg2teuj2hvq.streamlit.app/)

Upload a PDF, ask questions, get answers with exact page citations — or an honest "not found" instead of a guess.

A RAG system built around hybrid search (semantic + keyword), reciprocal rank fusion, and citation-forced generation. The point of the design was that every claim in an answer should trace back to a specific document and page, not just sound plausible.

## What it does

- Upload any PDF — reports, contracts, papers, regulations
- Hybrid retrieval: dense vector search for meaning, BM25 for exact keyword/jargon matches, merged with Reciprocal Rank Fusion so neither approach dominates
- Every answer is grounded with a document + page citation
- If retrieved context doesn't actually support an answer, it says so instead of guessing — this was a deliberate constraint, not something I settled for
- Nothing persists — documents and indexes live in `st.session_state` for the length of the session, nothing touches disk

## How it works

Document text comes in page-by-page via `chunker.py`, with filename and page number kept as metadata, then split into overlapping chunks so nothing gets cut off at a boundary (`chunker.py`).

Each chunk gets indexed two ways at once (`indexer.py`): dense embeddings via `all-MiniLM-L6-v2` (384-dim) for semantic meaning, and BM25 for exact terms — identifiers, jargon, anything dense search tends to miss.

A query hits both indexes, and the two ranked lists get merged with Reciprocal Rank Fusion before reranking (`retriever.py`) — this is the part that actually balances "sounds related" against "contains the exact term."

The fused top chunks go into a prompt sent to Llama 3.3 70B on Groq, instructed to answer only from the given context (`generator.py`). No outside knowledge allowed in the prompt, which is what makes the citation-or-refuse behavior enforceable rather than just hoped for.

## Tech stack

Streamlit for the UI, PyMuPDF for PDF parsing, `sentence-transformers` for dense embeddings, `rank-bm25` for sparse search, a custom numpy-based RRF implementation for fusion, Groq's Llama 3.3 70B for generation, and a GitHub Actions keep-alive job so the Streamlit app doesn't idle out.

## Running locally

```bash
git clone https://github.com/shakshi-soni/LEXISEARCH-RAG.git
cd LEXISEARCH-RAG
pip install -r requirements.txt

cp .env.example .env
# add GROQ_API_KEY

streamlit run src/app.py
```

## Project structure

```
lexisearch-rag/
├── .github/workflows/main.yml   # scheduled keep-alive job
├── src/
│   ├── app.py          # Streamlit UI + session state
│   ├── chunker.py       # PDF extraction + chunking
│   ├── indexer.py       # dense + sparse index builder
│   ├── retriever.py     # hybrid search + RRF fusion
│   └── generator.py     # citation-forced generation
├── .env.example
├── requirements.txt
└── wake_up.py            # keep-alive ping
```

## Design notes

No database, no persistence — everything lives in session state. That was a deliberate choice, not a shortcut I plan to fix: it keeps the tool privacy-friendly (nothing about someone's uploaded contract sits on a disk anywhere) and makes it trivial to deploy. The trade-off is obvious — close the tab, lose your indexed documents, re-upload next time.

## Limitations

- No persistence, by design — you lose your document index when the session ends
- No reranking step beyond RRF — a cross-encoder reranker would likely improve precision on ambiguous queries, it's just not built yet
- No formal evaluation — I've tested this on documents I fed it manually, there's no retrieval precision/recall or faithfulness scoring against a fixed test set
- Single-document reasoning only — it can't currently compare or reason across two uploaded documents at once
- Multi-part questions aren't decomposed — a compound question gets answered as one retrieval pass, which can miss part of it

## What I'd improve next

1. Cross-encoder reranking on top of the RRF-fused candidates
2. An actual evaluation harness — retrieval precision/recall plus faithfulness scoring, not just spot-checking
3. Query decomposition for multi-part questions
4. Multi-document comparison mode

## Why I built this

I kept running into the same problem with RAG demos — the answer sounds confident but there's no way to check if it's actually grounded in the source, and if the retrieval misses, the model just fills the gap with something plausible. I wanted to build the version where that's not possible by construction: force every answer to cite a page, and make refusal the default when the retrieved context doesn't back up a confident claim. The hybrid retrieval (dense + BM25) came out of testing single-method search and noticing it missed exact terms and identifiers a keyword search would've caught immediately.

## About

Shakshi Soni.

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=flat&logo=linkedin)](https://www.linkedin.com/in/shakshi-soni-961048411/)
