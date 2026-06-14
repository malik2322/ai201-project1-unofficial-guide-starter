import asyncio

# Gradio builds its queue's lock/stop-event via asyncio.get_event_loop() while
# gr.Blocks() is constructed — before uvicorn's loop exists. On newer Python,
# get_event_loop() raises RuntimeError instead of creating one. Pre-registering
# a loop restores the behavior Gradio expects.
try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

import gradio as gr

from generator import generate_response
from retriever import embed_and_store, get_collection, load_chunks, retrieve


def run_ingestion():
    """Embed and store chunks.jsonl into ChromaDB, if not already done."""
    collection = get_collection()

    if collection.count() > 0:
        print(f"Vector store already populated ({collection.count()} chunks). Skipping ingestion.")
        print("To re-ingest, delete the ./chroma_db folder and restart.")
        return

    chunks = load_chunks()
    if chunks:
        embed_and_store(chunks)
        print(f"Ingestion complete. {len(chunks)} chunks stored.")
    else:
        print(
            "\n⚠️  No chunks found in chunks.jsonl.\n"
            "    Run ingest.py first to generate chunks from documents/.\n"
        )


def ask(question):
    retrieved = retrieve(question)
    result = generate_response(question, retrieved)
    return result["answer"], result["sources"]


def handle_query(question):
    if not question.strip():
        return "", ""
    answer, sources = ask(question)
    sources_text = "\n".join(f"• {s}" for s in sources) if sources else "(none)"
    return answer, sources_text


with gr.Blocks(title="The Unofficial Guide — TXST") as demo:
    gr.Markdown(
        "# 🎓 The Unofficial Guide to Texas State University\n"
        "Ask a question about student life at TXST — answers are grounded "
        "in collected student reviews and articles, with sources cited below."
    )

    inp = gr.Textbox(
        label="Your question",
        placeholder="e.g. Why are some students unhappy with the on-campus housing requirement?",
    )
    btn = gr.Button("Ask")
    answer = gr.Textbox(label="Answer", lines=8)
    sources = gr.Textbox(label="Retrieved from", lines=4)

    btn.click(handle_query, inputs=inp, outputs=[answer, sources])
    inp.submit(handle_query, inputs=inp, outputs=[answer, sources])


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("  The Unofficial Guide — starting up")
    print("=" * 50 + "\n")
    run_ingestion()
    demo.launch()
