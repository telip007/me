# Editorial guide

Updated: 31 October 2026. For Talip Göksu's English engineering blog. Internal guidance for choosing, drafting, reviewing, and maintaining articles.

The two main references are [Gergely Orosz's writing process](https://blog.pragmaticengineer.com/becoming-a-better-writer-in-tech/) and [Piotr Sarna and Cynthia Dunlop's *Writing for Developers* repository](https://github.com/scynthiadunlop/WritingForDevelopersBook). Orosz informs the editing and feedback habits; the book's public roadmap, pattern index, and excerpts inform topic selection and article shapes. The workflow below is this blog's adaptation, not a summary of the entire book. See the [research notes](research/editorial.md) for source details and limits.

## Promise to the reader

Explain a concrete engineering question with enough evidence that a developer can act on the answer. Open with the finding, explain the mechanism, and preserve the conditions that make the conclusion true. A useful article can be short. An unresolved question can be useful when it establishes a meaningful limit or a reproducible next step.

Voice: professional, direct, curious, and restrained. Name the system, behavior, or decision. Let an interesting observation carry the piece. A modest finding explained precisely is enough; it does not need a dramatic failure or a breakthrough. Avoid sweeping technology predictions, self-praise, stock openings, and personal anecdotes without an evidentiary basis. A technical term is appropriate when it is the precise name; explain it at the point where the intended reader needs help.

Prefer “This check accepts a link inside a code block” to “This powerful example reveals a fundamental challenge.” Prefer “The benchmark covered these inputs” to an unqualified claim that an approach is faster. These are wording examples in documentation, not assertions about a tested project.

## Find the angle before drafting

Collect questions while the confusing details are fresh: an unexpected result, a hard tradeoff, a documentation gap, a failed hypothesis, or a paper whose result needs interpreting. Capture the question and its supporting artifact together. A topic names an area; an angle gives a particular reader a reason to spend time on it.

Before committing to a draft, answer three questions:

1. **Why this reader?** Identify the situation in which the question matters.
2. **Why this article?** Name the explanation, example, comparison, or evidence it adds beyond the existing sources. A clearer explanation can be a sufficient contribution; novelty is not mandatory.
3. **Why trust this answer?** Identify what can actually be demonstrated or attributed. If the evidence cannot support the proposed angle, narrow it or keep researching.

Avoid broad subjects such as “Thoughts on caching.” A more useful working question is “When does a cache key need to include response format?” This is a hypothetical angle, not a claim about a tested system. This approach adapts the book's emphasis on [topic selection and planning](https://github.com/scynthiadunlop/WritingForDevelopersBook/blob/main/excerpts/AboutTheBook.md).

### Write a short brief

Keep this brief outside the repository, normally under `/Users/tag/Developer/blog-drafts/`. The same applies to post research, collected sources, thoughts, editorial notes, and working drafts. Only the final article and its public media assets belong in the repository; supporting citations stay in the article. The brief is not additional required front matter.

| Question | Required answer |
| --- | --- |
| Who is reading? | A role plus relevant prior knowledge. |
| What is the reader trying to do? | One problem, task, or consequential choice. |
| What changes after reading? | A specific action or understanding, not general awareness. |
| What kind of piece is this? | Explanation, how-to, tutorial, decision analysis, or investigation. |
| What is the strongest evidence? | Primary source, actual artifact, reproducible observation, or explicitly attributed report. |
| What remains uncertain? | The nearest limitation that could change the reader's choice. |

Finish this sentence: “After reading, a developer facing ___ can ___ because ___.” Then sketch the section questions and attach the evidence each needs. Keep the brief proportional: a short explanation may need only a few lines.

Do not force every topic into a personal story. Source-based explanation is preferable to invented first-person experience. The distinction between task instruction and explanation follows [Diátaxis](https://www.diataxis.fr/start-here/); the audience brief follows [Google's audience guidance](https://developers.google.com/tech-writing/one/audience).

## Choose a useful article shape

Choose by the material available, not by the most impressive title. The book's [pattern index](https://github.com/scynthiadunlop/WritingForDevelopersBook/blob/main/links/README.md#featured-blog-posts) offers several shapes. These are this blog's working adaptations:

| Shape | Use when the material supports | What the article must earn |
| --- | --- | --- |
| Bug hunt | A puzzling symptom and an evidenced investigation | Show how observations changed the diagnosis. |
| How we built it | A real design with consequential constraints | Explain the decisions and alternatives, beyond listing components. |
| We rewrote it in X | A real migration with a reason and an outcome | Compare against the previous system; include migration costs and remaining drawbacks. |
| Lessons learned | An experience with a transferable consequence | Connect each lesson to the event or evidence that warrants it. |
| Thoughts on trends | A specific argument about an emerging practice | Separate observation, interpretation, and prediction; address the strongest objection. |
| Benchmarks and test results | Measurements that answer a defined question | State workload, baseline, method, variability, costs, and limits. |
| Product perspective | A tool reveals a useful engineering mechanism | Teach the mechanism; state where the tool fits and where it does not. |

Use first-person pattern names only when the underlying experience is real and attributable. Source-based explanations are equally welcome. The outlines below cover common needs; use them as scaffolding, not mandatory public headings.

### Explanation or technical decision

1. **Answer and stakes.** State what changes and when a reader should care, in one short opening paragraph.
2. **The necessary model.** Explain the mechanism using the smallest concrete example that preserves the important behavior.
3. **Evidence and alternatives.** Show what supports the answer, compare meaningful options, and explain the tradeoff.
4. **Conditions and limits.** Identify where the answer changes or what was not established.
5. **Next action.** Give the reader a specific check, choice, or follow-up question.

### Investigation or bug explanation

1. Intended behavior and observed symptom.
2. Minimal reproduction with relevant environment and version.
3. The decisive observation and any failed hypothesis that teaches a useful diagnostic lesson.
4. Fix or bounded finding, with a check showing what it changes.
5. Remaining limits and a transferable lesson.

The book's [bug-hunt excerpt](https://github.com/scynthiadunlop/WritingForDevelopersBook/blob/main/excerpts/TheBugHuntPattern.md) shows how diagnostic detours can help future debuggers. Select the useful turns; omit a terminal-by-terminal diary. Give the finding early, then make the reasoning worth following. Do not withhold a practical answer to manufacture suspense, or imply a successful fix if the only result was a rejected candidate. An unresolved investigation can end with what was ruled out and the next discriminating check.

### How-to or tutorial

1. Outcome, prerequisites, and relevant version.
2. Small steps in execution order.
3. Expected result after the important step.
4. Likely failure and recovery where the reader needs it.
5. Verification of the final outcome, then optional deeper explanation.

A how-to assumes relevant competence; a tutorial needs a guided learning path. Do not bury a runnable procedure inside unrelated background.

## Draft for a reader who can leave

Start with the part you understand best. Put unresolved points in private draft notes and return to them; do not polish every sentence while the argument is still changing. If explaining a step exposes a gap in understanding, investigate it before presenting it as settled. This follows the book's account of [writing as a way to examine technical understanding](https://github.com/scynthiadunlop/WritingForDevelopersBook/blob/main/excerpts/WhyWriteEngineeringBlogs.md#really-understanding-your-code).

### Title, opening, and excerpt

The title names the question, behavior, or result. Make it specific enough that the intended reader can judge relevance. Avoid universal claims, unexplained superlatives, and curiosity gaps. A measured number belongs in a title only when the article establishes its meaning and conditions.

The opening should establish the problem, the useful answer or direction, and the reason to continue. Begin at the concrete point of interest; cut generic industry history and “In this article, we will explore…” introductions. Include a limitation early when it changes who should use the answer.

The excerpt is a compact statement of the article's value that can stand alone in a list or feed. Add useful context instead of mechanically repeating the title. Finalize it after the argument is stable.

### Develop the explanation

Make each section answer the next question the reader is likely to have. Introduce a small concrete example before adding abstraction. Explain why a detail matters before asking the reader to inspect code or a diagram. Put prerequisites before their use and material qualifications beside the affected claim.

End with the consequence: a check to run, a condition for choosing an approach, or a question the evidence leaves open. Skip a concluding recap if it only repeats what the reader just learned.

### Keep the voice precise and natural

- Prefer a named object and a concrete verb: “The parser rejects duplicate keys” is clearer than “Robust validation is provided.” These are wording examples, not assertions about a tested project.
- Explain unfamiliar terms where they first become necessary. Avoid idioms that add work for readers using English as an additional language.
- Use “I” or “we” for attributable actions, judgments, or observations. Do not manufacture a personal narrative or use a collective voice to suggest a team that was not involved.
- Let personality come through a sharp observation, a well-chosen example, or occasional relevant humor. Remove jokes that interrupt the explanation or put the reader down.
- Keep necessary nuance. Shorter is useful when it reduces effort without changing the claim.

## Claims and evidence

Maintain a brief ledger for consequential claims while drafting:

| Claim | Evidence | Scope and qualification | Review action |
| --- | --- | --- | --- |
| The factual statement the reader will rely on | Direct primary URL and section, or local artifact and tested revision | Version, environment, date, inputs, and what was actually observed | Verify, narrow, attribute, or remove |

The row is a template; fill it with real evidence before using it. Do not publish empty ledgers or invented results.

- Link a factual claim to the primary source that supports it, near that claim. Use a descriptive source label rather than “here.” Distinguish an author's report from an independently reproduced observation.
- For an original setup or experiment, retain the command, revision, environment, and decisive result. A test run proves only the behavior its assertions cover. Record failures and contradictory observations that affect the conclusion.
- A local demo, successful build, remote response, deployment, and physical-device check are distinct results. Choose the corresponding verb accurately.
- Verify changing APIs, product capabilities, specifications, and time-sensitive claims against the relevant version. Include a date when it materially affects interpretation.
- Treat an inference as an inference. Support comparisons with comparable conditions; do not infer general superiority from a single local case.
- Never invent quotes, measurements, citations, customer outcomes, Talip's experience, or a human review that did not occur. Do not import private notes, contact details, or personal background into public copy.
- Summarize sources in original language; quote only a short passage when its exact wording matters. Credit the source and do not duplicate substantial portions of another author's work.

## Editing and review

Separate drafting, editing, and feedback. [Orosz's article](https://blog.pragmaticengineer.com/becoming-a-better-writer-in-tech/) emphasizes improving a draft for its reader, seeking directed feedback, and learning through repeated practice. The passes below adapt that process to this blog; they need not become separate documents or approval stages.

| Pass | Read for | Done when |
| --- | --- | --- |
| Answer and evidence | Unsupported claims, missing counterevidence, misleading scope | The conclusion follows from the evidence and answers the brief. |
| Structure and examples | Missing steps, repetition, distracting detours, poor sequence | Each section advances the explanation and each example earns its space. |
| Language | Vague phrasing, overloaded sentences, unexplained terms, inconsistent names | The prose is natural and precise when read aloud. |
| Rendered reading | Navigation, code, media, links, narrow-screen reading | The article works in its actual presentation. |

During the structural pass, read just the title, opening, headings, and ending. They should form a coherent path. Check this against the full text: a neat outline cannot compensate for a missing explanation. Sources support [putting key answers early](https://developers.google.com/tech-writing/one/documents); the exact outline remains an editorial choice.

During the language pass, use one main thought per paragraph and vary sentence rhythm naturally. Let headings and topic sentences support scanning; reserve bold for meaningful emphasis. Sentence-style headings and direct verbs are consistent with [Microsoft's style guidance](https://learn.microsoft.com/en-us/style-guide/top-10-tips-style-voice). Readability tools can flag awkward passages; accept a suggestion only if it preserves technical meaning and voice.

### Ask for feedback that can change the draft

Tell a reviewer who the piece is for and what kind of help it needs. Seek structural feedback while sections are still easy to move. A domain reviewer can challenge correctness; a representative reader can reveal missing context. One person may serve both roles.

Choose the questions relevant to the draft:

- What can the intended reader do or decide after reading?
- Which claim is unsupported, overstated, stale, or ambiguous?
- Which term, step, or diagram requires knowledge the reader may not have?
- Which paragraph can be removed without losing understanding?
- Can the stated reproduction produce the stated result?

Resolve substantive feedback before a final language edit. Keep an unresolved disagreement visible in private notes, check the evidence, and narrow or remove a claim when necessary. Record who or what actually reviewed the draft; do not manufacture a review to satisfy a checklist.

An agent's editorial pass may be recorded as an agent pass. It does not establish that Talip personally wrote or reviewed the piece. Do not add blanket AI-creation notices, replacement disclaimers, or a central disclosure page; preserve substantive source attribution and factual limits.

## Code, diagrams, and links

Introduce a code sample with its purpose. Include the file or command context and relevant dependencies. Execute runnable examples in the stated environment; make omissions explicit in partial examples. Never label an unexecuted snippet as tested. See [MDN's example guidance](https://developer.mozilla.org/en-US/docs/MDN/Writing_guidelines/Code_style_guide) and [Google's formatting guidance](https://developers.google.com/style/code-samples).

Use a table when the reader needs to compare the same attributes across options. Use a diagram when it makes a relationship, sequence, or boundary easier to understand. Give it a specific question to answer and remove decorative detail. For charts, label units, inputs, and the relevant baseline. A visual must agree with the evidence and nearby prose.

Keep code and terminal output as selectable text. Explain a diagram's meaning in prose, provide useful alt text for informative images, and use empty alt text for decoration. Use a logical heading hierarchy and meaningful link text. Do not rely on color, motion, or “the box on the right” to carry the explanation. These practices follow [Google's accessible documentation guidance](https://developers.google.com/style/accessibility).

## English publication

- Publish in English at `/articles/<slug>/`, with English tags, excerpts and metadata. Set `lang: en`; omitted language defaults to English.
- Explicit German posts are excluded from public output. Keep unpublished source drafts intact until intentionally edited or removed.
- Old `/en/` URLs redirect to existing canonical counterparts. There is no language switch.
- Preserve professional About links and keep `/privacy/` accurate for the deployed host.

## Publication checklist

- [ ] The piece answers one specific reader question and its opening delivers the title's promise.
- [ ] The title and excerpt are specific and honest; the chosen article shape fits the available material.
- [ ] Consequential claims have supporting evidence; original observations have actual artifacts and reproducible details.
- [ ] No invented personal experience, measurement, quote, citation, human review, or general outcome remains.
- [ ] Sources and code examples were checked in the relevant context, not merely found by a link checker.
- [ ] The explanation states material limits once, where they help interpret the claim.
- [ ] The rendered article has readable code, accessible headings and media, working meaningful links, and usable narrow-screen layout.
- [ ] Metadata, dates, language and slugs are consistent with routes, feeds, and sitemap.
- [ ] Draft status is intentional. Boolean `draft: true` stays excluded from all public outputs; a future date alone is not a publishing gate.
- [ ] No private working notes, credentials, unrelated user content, placeholder articles, blanket AI notices, or implementation bookkeeping appears publicly.
- [ ] The relevant content/build checks pass. Editorial judgment and publication authority are still separate from automated validation.

If no article meets these criteria, keep the empty homepage state. A design refresh does not justify publishing unfinished material.

## Maintenance

Correct a consequential factual error in the published article and describe a material correction plainly. Set a new update date only for a substantive change, if the content model supports it. Recheck articles when their central API or behavior changes; avoid implying an old result applies to a new version. Keep useful durable explanations available, with an explicit historical boundary when needed.

## Build the writing habit

Keep a small private queue of questions with their artifacts. Choose the next useful explanation from that queue. A regular practice session can produce a paragraph, a clarified example, or a revision; it does not need to produce a published article.

Save a few strong articles with a note on what works: the opening, sequence, example, visual, or ending. Study the technique and apply it to different material; do not copy another author's prose or experience. Use the book's [curated examples](https://github.com/scynthiadunlop/WritingForDevelopersBook/blob/main/links/README.md) as a starting collection, not a claim that every example fits this blog's voice.

After feedback, note one recurring weakness and practice correcting it in the next draft. Publication frequency, article length, readability scores, citation counts, and traffic do not substitute for reader value or factual accuracy. Useful reader questions and corrections are reasons to revisit an explanation; neither praise nor popularity establishes that it is correct.
