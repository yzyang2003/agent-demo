"""
RAG (Retrieval-Augmented Generation) module for the Streamlit AI Agent Demo.

Provides document loading, chunking, vectorization, FAISS indexing,
similarity search, and prompt construction for knowledge-grounded QA.

Usage:
    from rag import search, build_prompt

    chunks = search("长沙有什么好吃的", "tourism.txt", top_k=3)
    prompt = build_prompt("长沙有什么好吃的", chunks)
"""

import logging
import os
from pathlib import Path

import faiss
import numpy as np
import streamlit as st
from sentence_transformers import SentenceTransformer

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
EMBEDDING_MODEL_NAME: str = "paraphrase-multilingual-MiniLM-L12-v2"
CHUNK_MIN_SIZE: int = 200   # minimum characters per chunk
CHUNK_MAX_SIZE: int = 500   # maximum characters per chunk
DATA_DIR: Path = Path(__file__).parent / "data"

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Document Loading & Chunking
# ---------------------------------------------------------------------------
def load_and_chunk(filepath: str) -> list[dict]:
    """Load a text file and split it into paragraph-based chunks.

    Chunking strategy:
    1. Split document by double newlines (``\\n\\n``) to get paragraphs.
    2. Merge consecutive small paragraphs (< ``CHUNK_MIN_SIZE`` chars).
    3. Split oversized paragraphs (> ``CHUNK_MAX_SIZE`` chars) by single
       newlines, then by sentence punctuation if still too large.

    Args:
        filepath: Absolute or project-relative path to a ``.txt`` file.

    Returns:
        A list of dicts, each with keys ``content``, ``source``, ``index``.

    Raises:
        FileNotFoundError: If *filepath* does not exist.
        ValueError: If the file is empty after stripping whitespace.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Knowledge file not found: {filepath}")

    text = path.read_text(encoding="utf-8").strip()
    if not text:
        raise ValueError(f"File is empty: {filepath}")

    # Step 1: split by double-newline paragraph boundaries
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    # Step 2 & 3: merge small / split large
    chunks: list[str] = []
    for para in paragraphs:
        if len(para) <= CHUNK_MAX_SIZE:
            # Paragraph fits – try merging with the previous chunk if small
            if chunks and len(chunks[-1]) < CHUNK_MIN_SIZE and len(chunks[-1]) + len(para) + 1 <= CHUNK_MAX_SIZE:
                chunks[-1] = chunks[-1] + "\n" + para
            else:
                chunks.append(para)
        else:
            # Paragraph too large – split by single newlines first
            sub_chunks = _split_text(para, sep="\n")
            chunks.extend(sub_chunks)

    # Final merge pass: combine any remaining undersized trailing chunks
    merged: list[str] = []
    for chunk in chunks:
        if (merged
                and len(merged[-1]) < CHUNK_MIN_SIZE
                and len(merged[-1]) + len(chunk) + 1 <= CHUNK_MAX_SIZE):
            merged[-1] = merged[-1] + "\n" + chunk
        else:
            merged.append(chunk)

    return [
        {"content": c, "source": path.name, "index": i}
        for i, c in enumerate(merged)
    ]


def _split_text(text: str, sep: str = "\n") -> list[str]:
    """Recursively split *text* until every piece is within ``CHUNK_MAX_SIZE``.

    Tries *sep* first (e.g. newlines), then falls back to sentence-ending
    punctuation (``。！？.!?``), then to hard character splits.

    Args:
        text: The text block to split.
        sep: The separator to try first.

    Returns:
        A list of text chunks, each <= ``CHUNK_MAX_SIZE`` chars.
    """
    if len(text) <= CHUNK_MAX_SIZE:
        return [text]

    parts = [p.strip() for p in text.split(sep) if p.strip()]

    # If split produced nothing useful, try sentence punctuation
    if len(parts) <= 1:
        for punct in ("。", "！", "？", ".", "!", "?"):
            parts = [p.strip() for p in text.split(punct) if p.strip()]
            if len(parts) > 1:
                # Re-attach punctuation
                parts = [p + punct if not p.endswith(punct) else p for p in parts]
                break

    # If still a single giant blob, hard-split by character count
    if len(parts) <= 1 and len(text) > CHUNK_MAX_SIZE:
        parts = []
        for i in range(0, len(text), CHUNK_MAX_SIZE):
            parts.append(text[i : i + CHUNK_MAX_SIZE])

    # Recursively handle any remaining oversized pieces
    result: list[str] = []
    for part in parts:
        if len(part) <= CHUNK_MAX_SIZE:
            result.append(part)
        else:
            result.extend(_split_text(part, sep="。"))

    # Merge small adjacent pieces
    final: list[str] = []
    for chunk in result:
        if (final
                and len(final[-1]) < CHUNK_MIN_SIZE
                and len(final[-1]) + len(chunk) + 1 <= CHUNK_MAX_SIZE):
            final[-1] = final[-1] + "\n" + chunk
        else:
            final.append(chunk)

    return final


# ---------------------------------------------------------------------------
# Embedding Model (cached)
# ---------------------------------------------------------------------------
@st.cache_resource
def _get_model() -> SentenceTransformer:
    """Load and cache the HuggingFace sentence-transformer model.

    Uses ``@st.cache_resource`` so the model is loaded only once per
    Streamlit server process.
    """
    logger.info("Loading embedding model: %s", EMBEDDING_MODEL_NAME)
    return SentenceTransformer(EMBEDDING_MODEL_NAME)


def get_embeddings(chunks: list[str]) -> np.ndarray:
    """Vectorize a list of text strings into L2-normalized embeddings.

    Args:
        chunks: Plain text strings to encode.

    Returns:
        A ``(len(chunks), dim)`` float32 NumPy array of normalized embeddings.
    """
    model = _get_model()
    embeddings = model.encode(
        chunks,
        show_progress_bar=False,
        normalize_embeddings=True,
    )
    return np.asarray(embeddings, dtype="float32")


# ---------------------------------------------------------------------------
# FAISS Index
# ---------------------------------------------------------------------------
def build_index(chunks: list[dict], embeddings: np.ndarray) -> faiss.Index:
    """Build a FAISS inner-product index from chunk metadata and embeddings.

    Because embeddings are L2-normalized, inner-product search is equivalent
    to cosine similarity.

    Args:
        chunks: Chunk dicts (unused here but kept for API consistency).
        embeddings: ``(n, dim)`` float32 array of normalized vectors.

    Returns:
        A populated ``faiss.IndexFlatIP`` instance.
    """
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)
    return index


# ---------------------------------------------------------------------------
# Cached Knowledge Base Loader
# ---------------------------------------------------------------------------
@st.cache_resource
def _load_knowledge_base(
    filepath: str,
) -> tuple[list[dict], list[str], np.ndarray, faiss.Index]:
    """End-to-end pipeline: load → chunk → embed → index.

    Results are cached by *filepath* so repeated calls with the same
    knowledge file skip all heavy work.

    Returns:
        Tuple of ``(chunks_meta, chunk_texts, embeddings, faiss_index)``.
    """
    chunks_meta = load_and_chunk(filepath)
    chunk_texts = [c["content"] for c in chunks_meta]
    embeddings = get_embeddings(chunk_texts)
    index = build_index(chunks_meta, embeddings)
    return chunks_meta, chunk_texts, embeddings, index


# ---------------------------------------------------------------------------
# Public Search API
# ---------------------------------------------------------------------------
def search(query: str, knowledge_file: str, top_k: int = 3) -> list[str]:
    """Return the most relevant text chunks for *query* from a knowledge file.

    Args:
        query: The user's natural-language question.
        knowledge_file: Filename inside ``data/`` (e.g. ``"tourism.txt"``)
            **or** an absolute path.
        top_k: Maximum number of chunks to return.

    Returns:
        A list of up to *top_k* relevant text chunks, or an empty list on
        error (file not found, empty index, etc.).
    """
    try:
        # Resolve path: prefer DATA_DIR-relative, fall back to absolute
        if os.path.isabs(knowledge_file):
            filepath = knowledge_file
        else:
            filepath = str(DATA_DIR / knowledge_file)

        if not os.path.exists(filepath):
            logger.error("Knowledge file not found: %s", filepath)
            return []

        _chunks_meta, chunk_texts, _embeddings, index = _load_knowledge_base(filepath)

        if index.ntotal == 0:
            logger.warning("FAISS index is empty for %s", filepath)
            return []

        # Encode query with the same model
        model = _get_model()
        query_vec = model.encode([query], normalize_embeddings=True).astype("float32")

        # Retrieve top-k (clamp to available count)
        k = min(top_k, index.ntotal)
        _scores, indices = index.search(query_vec, k)

        results: list[str] = []
        for idx in indices[0]:
            if 0 <= idx < len(chunk_texts):
                results.append(chunk_texts[idx])

        return results

    except FileNotFoundError:
        logger.error("Knowledge file not found: %s", knowledge_file)
        return []
    except Exception as exc:
        logger.error("Search error for query=%r file=%r: %s", query, knowledge_file, exc)
        return []


# ---------------------------------------------------------------------------
# Prompt Construction
# ---------------------------------------------------------------------------
def build_prompt(query: str, context_chunks: list[str]) -> str:
    """Build a Chinese-language prompt that injects retrieved context.

    If *context_chunks* is non-empty the context is formatted into numbered
    reference blocks; otherwise the prompt asks the LLM to answer from
    general knowledge.

    Args:
        query: The user's question.
        context_chunks: Relevant text snippets returned by :func:`search`.

    Returns:
        A ready-to-send prompt string (Chinese).
    """
    if context_chunks:
        context = "\n\n".join(
            f"[参考资料{i+1}] {chunk}" for i, chunk in enumerate(context_chunks)
        )
        return (
            "请根据以下参考资料回答用户的问题。"
            "如果参考资料中没有相关信息，请说明并尝试给出一般性建议。\n\n"
            f"参考资料：\n{context}\n\n"
            f"用户问题：{query}\n\n"
            "请用中文回答："
        )

    return (
        "请回答以下问题。"
        "注意：未找到相关的参考资料，请根据你的知识给出回答。\n\n"
        f"用户问题：{query}\n\n"
        "请用中文回答："
    )
