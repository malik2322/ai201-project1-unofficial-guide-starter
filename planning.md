# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->

## I have choose the Texas state university survival guide as a domain, and it hard to find on official channels because it not possible to find honest reviews and real life experience of students with the university facilities.

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| #   | Source | Description | URL or location |
| --- | ------ | ----------- | --------------- |

| 1 | r/txstate main subreddit | Largest unofficial community for TXST students; discussions on housing, classes, professors, parking, dining, jobs, and campus life. | [https://www.reddit.com/r/txstate/](https://www.reddit.com/r/txstate/) |
| 2 | r/TexasStateUniversity | Smaller community with student, alumni, and staff discussions; useful for freshman and transfer student experiences. | [https://www.reddit.com/r/TexasStateUniversity/](https://www.reddit.com/r/TexasStateUniversity/) |
| 3 | Rate My Professors | Student reviews and ratings of TXST professors; valuable for course and instructor feedback. | [https://www.ratemyprofessors.com](https://www.ratemyprofessors.com) |
| 4 | University Star | Official student-run newspaper covering campus news, housing, safety, events, and student opinions. | [https://universitystar.com](https://universitystar.com) |
| 5 | RateMyApartments | Reviews and ratings of apartments near Texas State University from current and former residents. | [https://www.ratemyapartments.com/ratings/tx/texas-state-university-san-marcos](https://www.ratemyapartments.com/ratings/tx/texas-state-university-san-marcos) |
| 6 | Storage Scholars Housing Guide | Student-focused housing recommendations and comparisons of popular apartment complexes. | [https://www.storagescholars.com/blog/top-housing-picks-for-texas-state-students](https://www.storagescholars.com/blog/top-housing-picks-for-texas-state-students) |
| 7 | TXST Housing & Residential Life | Official housing policies, dorm information, room assignments, and residence hall resources. | [https://www.reslife.txst.edu](https://www.reslife.txst.edu) |
| 8 | TXST Dining Services | Official information about dining halls, meal plans, campus restaurants, and food services. | [https://www.dineoncampus.com/txstate](https://www.dineoncampus.com/txstate) |
| 9 | The Thompson Apartments Reviews | Student apartment information and resident testimonials near campus. | [https://livethethompson.com](https://livethethompson.com) |
| 10 | YouTube Student Experience Videos | Dorm tours, apartment reviews, freshman advice, and day-in-the-life videos created by TXST students. | Search: "Texas State University dorm tour", "Texas State freshman advice", "Texas State apartment review" on YouTube |

**Actually collected so far (4 of the 10 planned sources):**
- `documents/Source.txt` — University Star articles + reader commentary on the on-campus housing requirement and satellite campus proposals (12 entries, source #4/#7).
- `documents/cs_degree_catalog.txt` — Official TXST B.S. Computer Science degree catalog (source #similar to official catalog info, not in original list — added for academic/registration questions).
- `documents/prof_review.txt` — Rate My Professors profiles + reviews for 5 CS professors (source #3).
- `documents/reddit_parking_thread.txt` — r/txstate "Miserable Parking Enforcement" thread, cleaned into 5 themed entries (source #1).

Remaining planned sources (RateMyApartments, Storage Scholars, TXST Housing/Dining official pages, Thompson Apartments, international student threads, YouTube) are not yet collected — see Anticipated Challenges and the README Failure Case Analysis for the impact on evaluation.

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:**
~250 words per chunk (changed from the originally planned 200-250 characters — see note below).
**Overlap:**
50 words.
**Reasoning:**
Most source entries are individual reviews, comments, or short article excerpts that are already self-contained "opinions," so a 250-word window is large enough to keep a full opinion together while still being short enough to embed a single topic per chunk. Chunking is sentence-aware: sentences are accumulated until adding the next one would exceed 250 words, so chunks don't cut off mid-sentence. The 50-word overlap preserves context across chunk boundaries for the few entries (like the CS degree catalog) that are long enough to be split into multiple chunks.

**Note on change from original plan:** the original plan specified 200-250 *character* chunks. During implementation this was switched to *word*-based chunking (250 words / 50-word overlap) because character-based splitting would cut sentences and reviews apart awkwardly, and word counts map more directly to "roughly one paragraph of context" for an LLM.

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:**
all-MiniLM-L6-v2 (via sentence-transformers) — a small, fast local embedding model that's free to run, has no API latency or cost, and is accurate enough for short review/comment-style text.

**Pipeline:**
```
Document (JSON: source + content)
        ↓
   Clean text (strip URLs, [deleted]/[removed], markdown)
        ↓
   Chunk (250 words, 50-word overlap, sentence-aware)
        ↓
   Embed chunk (all-MiniLM-L6-v2)
        ↓
   Store in ChromaDB (with source + parent_source metadata)
        ↓
   Retrieve top-k by cosine distance
        ↓
   LLM answer grounded in retrieved chunks, with citations
```

**Top-k:**
5 (N_RESULTS = 5) — narrowed down from the originally planned 5-8 since most source entries are already short, single-topic chunks, so 5 chunks gives enough coverage without diluting the context with marginally-relevant results.

**Production tradeoff reflection:**
all-MiniLM-L6-v2 is fast and free but has a short context window (256 tokens) and weaker performance on nuanced or domain-specific phrasing (e.g., TXST-specific slang, building/permit names). For a real deployment without cost constraints, I'd consider a larger API-hosted embedding model (e.g., OpenAI text-embedding-3-large or Cohere embed-v3) for better accuracy on slang-heavy student text and longer context per chunk, at the cost of per-call latency, ongoing API cost, and sending student-generated content to a third party.

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| #   | Question                                                                                                                 | Expected Correct Answer                                                                                                                                                           |
| --- | ------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | What complaints do students most frequently mention about maintenance at The Thompson Apartments?                        | Students frequently mention slow maintenance response times, delayed repairs, and poor communication from management.                                                             |
| 2   | According to student discussions, what are the biggest challenges international students face at Texas State University? | International students commonly mention difficulties with transportation without a car, finding affordable housing, adjusting to campus life, and building social connections.    |
| 3   | What do students say about parking availability on campus during peak class hours?                                       | Students frequently report that parking lots fill up quickly during peak hours, making it difficult to find spots and causing some students to arrive early or park farther away. |
| 4   | What factors do students consider when recommending a professor on Rate My Professors and Reddit?                        | Students primarily evaluate professors based on teaching clarity, responsiveness to questions, quality of feedback, fairness of exams, and workload.                              |
| 5   | According to Reddit and student articles, why are some students dissatisfied with the on-campus housing lottery process? | Some students feel the process lacks transparency and believe outcomes are unpredictable, even though official university information states that the lottery is randomized.      |
|  |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. **Inconsistent/malformed source files.** Several `.txt` source files contain JSON copy-pasted from different AI tools, and the formatting wasn't always valid as a single JSON document (missing commas between objects, multiple top-level `{"documents": [...]}` blocks concatenated in one file). If `ingest.py` can't parse a file, it silently skips it — meaning entire sources (e.g., the professor review data) could be missing from the vector store without an obvious error, which would make retrieval for those topics fail with "I don't have enough information" even though the data exists on disk.

2. **Off-topic / unsupported evaluation questions.** Several of the planned evaluation questions (Thompson Apartments maintenance, international student challenges, on-campus housing lottery) assume sources that aren't in the corpus yet (RateMyApartments, Thompson Apartments reviews, international-student threads). Because the system is grounded ("answer ONLY from the provided excerpts"), it correctly refuses to answer ("I don't have enough information on that.") rather than hallucinating — but this means retrieval quality looks poor for those questions purely because of a documents/ coverage gap, not a retrieval or generation bug.

3. **Duplicate/colliding chunk IDs.** Two different source entries with similar `source` labels (truncated to the same 40-character slug) produced the same `chunk_id`, which ChromaDB rejects as a `DuplicateIDError`. Fixed by including the document's index within its parent file in the `chunk_id`.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

```
documents/*.txt (JSON: {"documents": [{"source","content"}]})
        │
        ▼
[1. Ingestion]  ingest.py — load_documents()
        │  parses each file's JSON, repairs minor JSON formatting issues
        ▼
[2. Chunking]   ingest.py — clean_text() + chunk_text()
        │  strip URLs/markdown/[deleted], sentence-aware 250-word
        │  chunks with 50-word overlap → chunks.jsonl
        ▼
[3. Embedding + Vector Store]  retriever.py — embed_and_store()
        │  sentence-transformers (all-MiniLM-L6-v2) → ChromaDB
        │  PersistentClient, cosine distance, ./chroma_db
        ▼
[4. Retrieval]  retriever.py — retrieve()
        │  _collection.query(query_texts=[q], n_results=5)
        │  returns text + source + parent_source + distance
        ▼
[5. Generation]  generator.py — generate_response()
        │  Groq llama-3.3-70b-versatile, grounded system prompt,
        │  programmatic source citations from chunk metadata
        ▼
   Gradio UI (app.py) — question in, answer + sources out
```

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**
I gave Claude this planning.md's Chunking Strategy section along with a description of the actual data format (JSON `{"documents": [{"source","content"}]}` files in `documents/`, instead of the `SOURCE:`/`CONTENT:` line-pair format a generic prompt assumed). I asked for a full `ingest.py`: parse the JSON files, clean the text (strip URLs, markdown, `[deleted]`/`[removed]`), chunk with the word-based sentence-aware strategy, and write `chunks.jsonl`. Claude produced the script; I verified it by printing 5 random chunks and checking they were readable and self-contained, then fixed two real bugs that surfaced from real data: a `DuplicateIDError` from colliding chunk IDs (fixed by adding a per-file document index to `chunk_id`), and silently-skipped files due to malformed concatenated JSON (fixed by repairing the JSON in `documents/prof_review.txt`).

**Milestone 4 — Embedding and retrieval:**
I gave Claude the config (`all-MiniLM-L6-v2`, ChromaDB `PersistentClient`, cosine distance, top-k=5) and asked for `retriever.py` with `embed_and_store()` and `retrieve()`. It produced a `retrieve()` that returns `text`, `source`, `parent_source`, and `distance` per chunk, built from ChromaDB's nested `results["documents"][0]` / `["metadatas"][0]` / `["distances"][0]` lists via `zip()`. I verified it by running real queries and checking the returned distances were lower for on-topic questions (~0.33-0.43) than off-topic ones (~0.8+).

**Milestone 5 — Generation and interface:**
I gave Claude the Grounded Generation requirements (system prompt that restricts the model to the provided excerpts, a fixed fallback message, and programmatic source citation instead of parsing citations out of the model's text) plus the Milestone 5 Gradio interface spec. It produced `generator.py` and `app.py` (including an asyncio event-loop workaround needed for Gradio on Python 3.14). I verified by running test queries end-to-end through the Gradio UI and confirming both grounded answers with correct citations and the "I don't have enough information on that." fallback for out-of-scope questions.
