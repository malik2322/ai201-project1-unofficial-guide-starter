"""
RAG ingestion pipeline.

Pipeline: TXT files (JSON-shaped) -> Parser -> Cleaner -> Chunker -> chunks.jsonl

Each input .txt file in DOCUMENTS_DIR is expected to contain JSON of the form:
    {
        "documents": [
            {"source": "...", "content": "..."},
            ...
        ]
    }
"""

import json
import re
from pathlib import Path

DOCUMENTS_DIR = "documents"
OUTPUT_FILE = "chunks.jsonl"

CHUNK_SIZE_WORDS = 250
OVERLAP_WORDS = 50


def load_documents(documents_dir):
    """Read every .txt file in documents_dir and parse its `documents` array.

    Files that aren't valid JSON in the expected shape (e.g. notes, source
    lists) are skipped with a message rather than crashing the pipeline.
    """
    documents = []
    for path in sorted(Path(documents_dir).glob("*.txt")):
        try:
            with open(path, "r", encoding="utf-8") as f:
                raw = f.read()
        except UnicodeDecodeError:
            print(f"Skipping {path.name}: not UTF-8 text")
            continue

        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            # Source files sometimes have a missing comma between adjacent
            # objects (e.g. "}\n{"). Repair that one known issue and retry
            # before giving up on the file.
            repaired = re.sub(r"\}\s*\n\s*\{", "},\n{", raw)
            try:
                data = json.loads(repaired)
            except json.JSONDecodeError:
                print(f"Skipping {path.name}: not a JSON documents file")
                continue

        entries = data.get("documents", [])
        for i, entry in enumerate(entries):
            content = (entry.get("content") or "").strip()
            source = (entry.get("source") or f"{path.stem}_unknown_{i}").strip()
            if not content:
                continue
            documents.append({
                "parent_source": path.stem,
                "source": source,
                "content": content,
            })

    print(f"Loaded {len(documents)} document entries from {documents_dir}/")
    return documents


def clean_text(text):
    """Strip URLs, markdown noise, and [deleted]/[removed] markers, and
    collapse whitespace down to single spaces."""
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"\[deleted\]|\[removed\]", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)  # [label](url) -> label
    text = re.sub(r"[*_#>`~]+", "", text)  # markdown emphasis/heading/quote markers
    text = re.sub(r"\s+", " ", text).strip()
    return text


def split_sentences(text):
    """Split on sentence-ending punctuation followed by whitespace."""
    return [s for s in re.split(r"(?<=[.!?])\s+", text) if s]


def chunk_text(text, chunk_size=CHUNK_SIZE_WORDS, overlap=OVERLAP_WORDS):
    """Sliding-window chunking that prefers sentence boundaries.

    Sentences are accumulated into a chunk until adding the next sentence
    would exceed chunk_size words. The next chunk starts with the last
    `overlap` words of the previous chunk so context isn't lost at the seam.
    """
    chunks = []
    current_words = []

    for sentence in split_sentences(text):
        sentence_words = sentence.split()
        if current_words and len(current_words) + len(sentence_words) > chunk_size:
            chunks.append(" ".join(current_words))
            current_words = current_words[-overlap:] if overlap else []
        current_words.extend(sentence_words)

    if current_words:
        chunks.append(" ".join(current_words))

    # Edge case: a single sentence longer than chunk_size never gets broken
    # up by the loop above. Split any oversized chunk by raw word count.
    final_chunks = []
    for chunk in chunks:
        words = chunk.split()
        if len(words) <= chunk_size * 1.5:
            final_chunks.append(chunk)
        else:
            start = 0
            while start < len(words):
                final_chunks.append(" ".join(words[start:start + chunk_size]))
                start += chunk_size - overlap

    return final_chunks


def build_chunks(documents):
    """Clean and chunk each document, attaching chunk_id/source/parent_source metadata."""
    records = []
    for doc in documents:
        cleaned = clean_text(doc["content"])
        if not cleaned:
            continue

        slug = re.sub(r"[^a-zA-Z0-9]+", "_", doc["source"]).strip("_")[:40]
        for i, chunk in enumerate(chunk_text(cleaned)):
            records.append({
                "chunk_id": f"{doc['parent_source']}_{slug}_{i}",
                "source": doc["source"],
                "content": chunk,
                "parent_source": doc["parent_source"],
            })

    return records


def write_jsonl(records, output_file):
    with open(output_file, "w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def main():
    documents = load_documents(DOCUMENTS_DIR)
    records = build_chunks(documents)
    write_jsonl(records, OUTPUT_FILE)
    print(f"Wrote {len(records)} chunks to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
