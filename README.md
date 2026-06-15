# chunking-system

A hybrid document-chunking pipeline for RAG, in Python. I built this early in my crossing
from infrastructure into AI — to learn document preprocessing properly rather than reach for
a one-line splitter. It's structured and heavily tested, but **it has no production users**:
treat it as a learning build I keep in the open, not a product.

## What it does

- **Hybrid chunking** — header-based, recursive, and code-aware splitting for markdown.
- **Adaptive strategy** — analyzes content (code density, structure) and picks a chunking
  strategy, with a quality score to compare runs.
- **Quality evaluation** — size distribution, coherence, structure-preservation metrics,
  written to a report.
- **Multi-LLM token counting** — OpenAI, Anthropic, Jina, Google, with a `tiktoken` fallback;
  swappable via a provider factory.
- **Docling integration** — for multi-format document parsing.
- Supporting layers: caching, input/path validation, structured logging, health endpoints,
  and Prometheus-style metrics. Built to practice production patterns — not load-tested at scale.

## Install

```bash
pip install -r requirements.txt   # Python 3.11+
```

## Usage

```bash
# Basic
python main.py --input-file data/input/markdown_files/your_book.md

# Adaptive strategy + quality enhancement
python main.py --input-file your_book.md --auto-enhance --output-dir data/output
```

```python
from src.chunkers.adaptive_chunker import AdaptiveChunker
from src.chunkers.evaluators import ChunkQualityEvaluator

chunker = AdaptiveChunker(auto_optimize=True, chunk_size=800, chunk_overlap=150)

with open("your_document.md") as f:
    chunks = chunker.chunk_document_adaptive(f.read(), {"source_file": "your_document.md"})

metrics = ChunkQualityEvaluator().evaluate_chunks(chunks)
print(f"Quality: {metrics['overall_score']:.1f}/100")
```

## Configuration

Pydantic settings in `src/config/settings.py`; provider keys via `.env`:

```bash
LLM_PROVIDER=google          # google | openai | anthropic | jina | local
GOOGLE_API_KEY=...
OPENAI_API_KEY=...
ANTHROPIC_API_KEY=...
JINA_API_KEY=...             # enables Jina embeddings when set
```

## Layout

```
src/
├── chunkers/      # hybrid, adaptive, strategy optimizer, evaluators, docling, markdown
├── llm/           # provider factory + OpenAI / Anthropic / Jina / Google
├── utils/         # cache, security, validators, monitoring, observability, file handling
├── api/           # health / metrics endpoints
└── orchestration/ # production pipeline
tests/             # 43 test files (unit, integration, security, observability)
```

## Tests

```bash
pytest tests/ -v
pytest tests/ --cov=src --cov-report=html
```

## Status & honesty

Architecturally complete, well-tested, runs locally. **Unproven in production — no users.**
An early build from learning RAG preprocessing, kept public as a receipt of the work, not
a pitch. Part of [ai.rio.br](https://ai.rio.br) — crossing into AI, the engineer's way.

## License

MIT — see [LICENSE](LICENSE).
