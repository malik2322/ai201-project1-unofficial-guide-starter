from groq import Groq

from config import GROQ_API_KEY, LLM_MODEL

_client = Groq(api_key=GROQ_API_KEY)

NO_INFO_MESSAGE = "I don't have enough information on that."


def generate_response(query, retrieved_chunks):
    """Generate a grounded answer from retrieved chunks.

    Returns a dict with:
      - "answer"  : the LLM's response (str)
      - "sources" : list of source labels the retrieved chunks came from,
                     built directly from retrieval metadata — not parsed
                     out of the LLM's response.
    """
    if not retrieved_chunks:
        return {"answer": NO_INFO_MESSAGE, "sources": []}

    context = "\n\n".join(
        f"[Source: {chunk['source']}]\n{chunk['text']}" for chunk in retrieved_chunks
    )

    system_prompt = (
        "You are a research assistant answering questions about student life "
        "at Texas State University, using ONLY the excerpts provided in the "
        "context below — never use outside knowledge or general assumptions "
        "about universities.\n\n"
        "Guidelines:\n"
        "- Base your answer strictly on the provided excerpts.\n"
        "- If the excerpts don't contain enough information to answer the "
        f"question, respond with exactly: \"{NO_INFO_MESSAGE}\"\n"
        "- Keep answers concise and specific to what the excerpts say.\n\n"
        f"Context:\n{context}"
    )

    response = _client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ],
        temperature=0.2,
    )

    answer = response.choices[0].message.content

    sources = []
    for chunk in retrieved_chunks:
        label = f"{chunk['source']} ({chunk['parent_source']}.txt)"
        if label not in sources:
            sources.append(label)

    return {"answer": answer, "sources": sources}
