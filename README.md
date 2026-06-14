# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

<!-- What topic or category of knowledge does your system cover?
     Why is this knowledge valuable, and why is it hard to find through official channels?
     Example: "Student reviews of CS professors at [university] — useful because official
     course descriptions don't reflect teaching style, exam difficulty, or workload." -->

The Texas State University (TXST) "survival guide" — student life topics including on-campus housing requirements, parking enforcement, professor reviews, and computer science degree requirements. This knowledge is valuable because honest, first-hand student experiences (e.g., "this professor is a tough grader and mumbles through lectures," "everyone says parking near Old Main is free but enforcement will ticket you there") aren't reflected in official university pages, which describe policies and requirements but not how students actually experience them. It's hard to find through official channels because the university's own communications (housing office statements, course catalogs) describe the *intended* policy, not the lived reality that shows up scattered across Reddit threads and Rate My Professors reviews.

---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | r/txstate — "Miserable Parking Enforcement" thread (post + comments, cleaned into 5 themed entries: original rant, getting tickets forgiven, where free parking actually exists, disputing tickets, disabled placard issue) | Reddit thread | `documents/reddit_parking_thread.txt` |
| 2 | University Star — articles and reader commentary on the on-campus freshman housing requirement, the YAL protest against it, and satellite-campus proposals (12 entries) | Student newspaper articles + commentary | `documents/Source.txt` |
| 3 | TXST Housing & Residential Life — official housing requirement policy, contract/cancellation policy, benefits of living on campus | Official university policy text | `documents/Source.txt` |
| 4 | Rate My Professors — profiles and student reviews for 5 Computer Science professors (Isayas Adhanom, Moonis Ali, Vicki Almstrum, Tsz-Chiu Au, Keshav Bhandari, Xiaomin Li) | Professor ratings + reviews | `documents/prof_review.txt` |
| 5 | TXST Undergraduate Catalog — B.S. Computer Science degree overview, core courses, additional requirements, four-year plan, project course options | Official degree catalog | `documents/cs_degree_catalog.txt` |
| 6 | | | |
| 7 | | | |
| 8 | | | |
| 9 | | | |
| 10 | | | |

*Sources 6-10 are not yet collected — see planning.md's "Actually collected so far" note and the Failure Case Analysis below for the impact this has on retrieval for parking-during-peak-hours, Thompson Apartments, and international student questions.*

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:**
~250 words per chunk.

**Overlap:**
50 words.

**Why these choices fit your documents:**
Most source entries (Reddit comments, professor reviews, news article excerpts) are short, self-contained opinions — usually well under 250 words on their own, so they end up as a single chunk. `chunk_text()` is sentence-aware: it accumulates whole sentences until adding the next one would exceed 250 words, so chunks never get cut off mid-sentence. Before chunking, `clean_text()` strips URLs, `[deleted]`/`[removed]` markers, and markdown formatting (since several sources were pasted from Reddit and contain link syntax and emphasis markers that add noise to the embedding). The 50-word overlap matters for the few longer entries — like the CS degree catalog's "Additional Degree Requirements" section, which splits into 2 chunks — so a fact near a chunk boundary still has surrounding context in at least one chunk.

**Final chunk count:**
62 chunks across 4 source files (18 from `Source.txt`, 33 from `prof_review.txt`, 6 from `cs_degree_catalog.txt`, 5 from `reddit_parking_thread.txt`).

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:**
`all-MiniLM-L6-v2` via `sentence-transformers`. It was chosen because it's small and fast enough to run locally with no API cost or latency, and it performs well on short, single-topic text like reviews and comments, which makes up nearly all of this corpus.

**Production tradeoff reflection:**
If cost weren't a constraint, I'd weigh: (1) **context length** — all-MiniLM-L6-v2 truncates at 256 tokens, which is fine for individual reviews but would clip longer article excerpts; a model like OpenAI's `text-embedding-3-large` (8191 tokens) would let chunks be larger without losing information. (2) **domain-specific accuracy** — TXST-specific terms (building names, permit colors, professor nicknames) are out-of-vocabulary for a general-purpose model; a larger model trained on more web text would likely embed these more accurately, improving retrieval for niche questions. (3) **latency and privacy** — a local model has zero network latency and keeps student-generated review text from being sent to a third-party API, which matters since some of this content (e.g., professor reviews, personal financial details from the housing protest article) is sensitive. The tradeoff is API-hosted models generally embed nuanced/slang-heavy text better, at the cost of per-call latency, ongoing cost, and sending that data externally.

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:**
The system prompt sent with every query is:

> "You are a research assistant answering questions about student life at Texas State University, using ONLY the excerpts provided in the context below — never use outside knowledge or general assumptions about universities.
>
> Guidelines:
> - Base your answer strictly on the provided excerpts.
> - If the excerpts don't contain enough information to answer the question, respond with exactly: "I don't have enough information on that."
> - Keep answers concise and specific to what the excerpts say.
>
> Context:\n[retrieved chunks, each prefixed with `[Source: <source label>]`]"

The retrieved chunks are concatenated into this `Context` block, each one labeled with its source (`[Source: <source>]\n<chunk text>`), so the model can see exactly which chunk each piece of information came from while answering. If `retrieve()` returns zero chunks (empty collection), `generate_response()` short-circuits and returns the fallback message without even calling the LLM — no low-relevance filtering is applied beyond top-k=5, since cosine distance alone wasn't a reliable enough signal to threshold on for this corpus (on-topic distances ranged 0.33-0.59 and off-topic ones could still be under 0.6).

**How source attribution is surfaced in the response:**
Source attribution is built programmatically from ChromaDB's retrieval metadata — never parsed out of the LLM's text. For each retrieved chunk, `generate_response()` builds a label `f"{chunk['source']} ({chunk['parent_source']}.txt)"` (e.g., `"Eric Pinteralli (Source.txt)"`), deduplicates them, and returns them as a separate `sources` list alongside the `answer`. The Gradio UI displays these in a dedicated "Retrieved from" textbox below the answer, so the cited sources are guaranteed to be the actual chunks that were retrieved and shown to the model — they can't drift from what the model "claims" it used.

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What complaints do students most frequently mention about maintenance at The Thompson Apartments? | Slow maintenance response, delayed repairs, poor communication from management. | "I don't have enough information on that." Retrieved chunks (distances 0.537-0.592) were unrelated housing/professor-review content. | Off-target | Accurate (correct refusal — no Thompson Apartments source exists yet) |
| 2 | According to student discussions, what are the biggest challenges international students face at Texas State University? | Transportation without a car, affordable housing, adjusting to campus life, building social connections. | "I don't have enough information on that." Retrieved chunks (distances 0.474-0.529) were general housing/satellite-campus content, none specific to international students. | Off-target | Accurate (correct refusal — no international-student source exists yet) |
| 3 | What do students say about parking availability on campus during peak class hours? | Lots fill up quickly during peak hours, students arrive early or park farther away. | "I don't have enough information on that." Retrieved the parking Reddit thread (distances 0.475-0.516) plus unrelated housing content, but no chunk discusses peak-hour crowding specifically. | Partially relevant | Accurate (correct refusal — parking content exists but doesn't cover this specific angle) |
| 4 | What factors do students consider when recommending a professor on Rate My Professors and Reddit? | Teaching clarity, responsiveness, quality of feedback, exam fairness, workload. | "I don't have enough information on that." Retrieved 5 professor-related chunks (distances 0.480-0.513) — individual reviews and profile summaries, but none discuss "what factors students weigh" as a topic. | Partially relevant | Accurate (correct refusal — right domain, but no chunk frames this as a meta-discussion) |
| 5 | According to Reddit and student articles, why are some students dissatisfied with the on-campus housing lottery process? | Process feels non-transparent / outcomes unpredictable despite official claims of randomization. | "I don't have enough information on that." Retrieved housing-requirement and housing-protest chunks (distances 0.390-0.535) — relevant to housing policy broadly, but none mention a "lottery" or room-assignment process. | Partially relevant | Accurate (correct refusal — corpus covers the housing *requirement* but not the room-assignment *lottery*) |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

**Overall note:** None of the 5 evaluation questions could be fully answered by the current corpus, but the system correctly recognized this in all 5 cases and returned the grounded fallback message rather than hallucinating. This points to a documents/ *coverage* gap (see Failure Case Analysis), not a grounding failure — a separate spot-check question ("Why do some students oppose the requirement that freshmen live on campus?") *was* well-covered and produced a correct, cited answer (distances 0.332-0.432), confirming the retrieval → generation → citation pipeline works correctly when the topic is in the corpus.

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:**
"What factors do students consider when recommending a professor on Rate My Professors and Reddit?"

**What the system returned:**
"I don't have enough information on that." Retrieval returned 5 chunks from `prof_review.txt` (distances 0.480-0.513) — a mix of individual student reviews (e.g., "He listens very well to his students... I respect him a lot as a professor") and professor profile summaries (overall quality, difficulty, % would-take-again).

**Root cause (tied to a specific pipeline stage):**
This is a retrieval/corpus-mismatch issue, not a generation bug. The question asks for a *meta-level synthesis* — "what factors do students weigh when recommending a professor" — but every chunk in `prof_review.txt` is either a single review describing one professor's specific traits, or a numeric profile summary. No chunk explicitly enumerates "factors students consider" as its own topic, so even though the retrieved chunks are topically close (all about professor reviews, distance ~0.48-0.51), none of them individually contain a direct answer to *this* phrasing of the question. The grounding instruction correctly refused rather than synthesizing a generalization the source text doesn't explicitly state.

**What you would change to fix it:**
Either (a) add a source that explicitly discusses *how* students choose/recommend professors (e.g., a Reddit thread titled something like "how do you pick classes/professors"), which is exactly the kind of meta-discussion question 16 in the brainstormed question list points at, or (b) relax the system prompt slightly to allow the model to *synthesize* a pattern across multiple individual reviews (e.g., "the reviews above repeatedly mention X, Y, Z") rather than requiring an explicit statement of "factors" — though this would need to be done carefully to avoid drifting away from strict grounding.

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**
The Architecture section's five-stage breakdown (Ingestion → Chunking → Embedding/Vector Store → Retrieval → Generation) made it straightforward to hand each stage to Claude as a separate, well-scoped request — `ingest.py`, then `retriever.py`, then `generator.py`/`app.py` — rather than asking for "the whole RAG system" at once. Having the Evaluation Plan's 5 test questions written *before* implementation also made it obvious, once retrieval was working, that the corpus didn't actually cover several of the planned questions — which surfaced the documents/ coverage gap early rather than after a final demo.

**One way your implementation diverged from the spec, and why:**
The Chunking Strategy changed from the planned 200-250 *character* chunks to 250-*word* sentence-aware chunks with 50-word overlap. Character-based chunking would frequently cut sentences (and Reddit comments) in half mid-word, which both looks bad when displayed as a retrieved excerpt and gives the LLM a fragment instead of a complete thought. Word-based, sentence-aware chunking keeps each chunk as one or more complete sentences, which matches the actual structure of the corpus (mostly short, self-contained opinions/reviews) much better than an arbitrary character cutoff would have.

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:* A generic ingestion-pipeline prompt template (load docs → clean → chunk → write JSONL) along with the actual shape of the data in `documents/` — JSON files of `{"documents": [{"source", "content"}]}`, not the `SOURCE:`/`CONTENT:` line-pair format the template assumed.
- *What it produced:* `ingest.py` with `load_documents()`, `clean_text()`, `split_sentences()`, `chunk_text()`, `build_chunks()`, and `write_jsonl()`, using 250-word/50-word-overlap sentence-aware chunking.
- *What I changed or overrode:* After printing 5 random chunks for QA, two real bugs surfaced from actual data: (1) two source entries with similar names produced colliding 40-character chunk-ID slugs, causing a ChromaDB `DuplicateIDError` — fixed by adding each entry's index within its source file to `chunk_id`; (2) `documents/prof_review.txt` contained multiple concatenated top-level JSON objects (`{"documents":[...]}\n\n{"documents":[...]}\n...`) which `load_documents()` silently skipped as invalid JSON — I rewrote the file as one valid JSON document with a single `"documents"` array (merging and de-duplicating the entries), which brought the total from 29 to 62 chunks.

**Instance 2**

- *What I gave the AI:* The Milestone 5/6 instructions for the generation step and Gradio interface, plus the Grounded Generation requirements: a system prompt restricting the model to retrieved excerpts, a fixed fallback string for out-of-scope questions, and source citations built from retrieval metadata (not parsed from the LLM's text).
- *What it produced:* `generator.py` (`generate_response()` with the grounding system prompt and programmatic source-label deduplication) and `app.py` (a Gradio `Blocks` UI wiring `retrieve()` → `generate_response()` to Answer/Sources textboxes), including an asyncio event-loop workaround needed for Gradio to run on Python 3.14.
- *What I changed or overrode:* The first run failed with `ModuleNotFoundError: No module named 'gradio'` because `pip install -r requirements.txt` had been run against the system Python instead of the project's `.venv` — fixed by reinstalling with `.venv/Scripts/python.exe -m pip install -r requirements.txt`. I also ran the 5 planning.md evaluation questions end-to-end and found all 5 returned the "I don't have enough information" fallback due to a documents/ coverage gap (not a generation bug) — I verified the pipeline itself worked correctly with a spot-check question that *was* covered by the corpus, which returned a correctly grounded, cited answer.
