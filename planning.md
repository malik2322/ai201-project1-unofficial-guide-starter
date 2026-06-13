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

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:**
I will documents into 200 - 250 character chunks.
**Overlap:**
40 - 50 characters
**Reasoning:**
As documents are opinion based which mostly depend upon the context so limiting chunk size will help to reduce the chunks and

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:**
Review
↓
Extract metadata
↓
One opinion/comment per chunk
↓
Metadata-enriched embedding
↓
Vector DB
↓
Retrieve top-k
↓
LLM answer with citations
**Top-k:**
It will retrieve top 5-8 K
**Production tradeoff reflection:**
high recall initially
high precision in the final context

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

1. It could mixed the words

2.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

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

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**
