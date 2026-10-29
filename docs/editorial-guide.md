# Editorial guide

Policy date: 29 October 2026. For Talip Göksu's German and English engineering blog. This guide turns the [source research](research/editorial.md) into repeatable decisions. It is internal documentation, not public article copy.

## Promise to the reader

Explain a concrete engineering question with enough evidence that a developer can act on the answer. Open with the finding, explain the mechanism, and preserve the conditions that make the conclusion true. A useful article can be short. An unresolved question can be useful when it establishes a meaningful limit or a reproducible next step.

Voice: professional, direct, curious, and restrained. Name the system, behavior, or decision. Avoid sweeping technology predictions, self-praise, stock openings, and personal anecdotes without an evidentiary basis. A technical term is appropriate when it is the precise name; explain it at the point where the intended reader needs help.

Prefer “This check accepts a link inside a code block” to “This powerful example reveals a fundamental challenge.” Prefer “The benchmark covered these inputs” to an unqualified claim that an approach is faster. These are wording examples in documentation, not assertions about a tested project.

## Before drafting

Keep this brief in `drafts/` or another private working document. It is not additional required front matter.

| Question | Required answer |
| --- | --- |
| Who is reading? | A role plus relevant prior knowledge. |
| What is the reader trying to do? | One problem, task, or consequential choice. |
| What changes after reading? | A specific action or understanding, not general awareness. |
| What kind of piece is this? | Explanation, how-to, tutorial, decision analysis, or investigation. |
| What is the strongest evidence? | Primary source, actual artifact, reproducible observation, or explicitly attributed report. |
| What remains uncertain? | The nearest limitation that could change the reader's choice. |

Do not force every topic into a personal story. Source-based explanation is preferable to invented first-person experience. The distinction between task instruction and explanation follows [Diátaxis](https://www.diataxis.fr/start-here/); the audience brief follows [Google's audience guidance](https://developers.google.com/tech-writing/one/audience).

## Choose a useful structure

Use these as working outlines, not mandatory public headings. Omit a section that adds no value; preserve the answer and its evidence.

### Explanation or technical decision

1. **Answer and stakes.** State what changes and when a reader should care, in one short opening paragraph.
2. **The necessary model.** Explain the mechanism using the smallest concrete example that preserves the important behavior.
3. **Evidence and alternatives.** Show what supports the answer, compare meaningful options, and explain the tradeoff.
4. **Conditions and limits.** Identify where the answer changes or what was not established.
5. **Next action.** Give the reader a specific check, choice, or follow-up question.

### Investigation or bug explanation

1. Intended behavior and observed symptom.
2. Minimal reproduction with relevant environment and version.
3. The decisive observation and why earlier explanations failed.
4. Fix or bounded finding, with a check showing what it changes.
5. Remaining limits and a transferable lesson.

Write from actual artifacts. Do not imply a successful fix if the only result was a rejected candidate. Specific difficulties can reveal useful subjects, as [Julia Evans explains](https://jvns.ca/blog/2021/05/24/blog-about-what-you-ve-struggled-with/).

### How-to or tutorial

1. Outcome, prerequisites, and relevant version.
2. Small steps in execution order.
3. Expected result after the important step.
4. Likely failure and recovery where the reader needs it.
5. Verification of the final outcome, then optional deeper explanation.

A how-to assumes relevant competence; a tutorial needs a guided learning path. Do not bury a runnable procedure inside unrelated background.

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

Use distinct passes: answer and evidence; structure and examples; language; bilingual parity; rendered reading. This adapts the draft/edit/feedback process in [Orosz's writing article](https://blog.pragmaticengineer.com/becoming-a-better-writer-in-tech/).

During the structural pass, check that the introduction answers the question the title raises. Move prerequisites before their use. Remove repeated conclusions and unrelated history. Use a table for a real comparison and a diagram for relationships that prose makes difficult. Sources support [putting key answers early](https://developers.google.com/tech-writing/one/documents); the exact outline remains an editorial choice.

During the language pass, read the opening aloud. Replace vague nouns and ornamental verbs with the object and action. Keep one main thought per paragraph, vary rhythm naturally, and use headings that explain their section. Prefer plain international English and natural German. Sentence-style headings and direct verbs are consistent with [Microsoft's style guidance](https://learn.microsoft.com/en-us/style-guide/top-10-tips-style-voice).

Ask a reviewer specific questions:

- What can the intended reader do or decide after reading?
- Which claim is unsupported, overstated, stale, or ambiguous?
- Which term, step, or diagram requires knowledge the reader may not have?
- Which paragraph can be removed without losing understanding?
- Can the stated reproduction produce the stated result?

An agent's editorial pass may be recorded as an agent pass. It does not establish that Talip personally wrote or reviewed the piece. Do not add blanket AI-creation notices, replacement disclaimers, or a central disclosure page; preserve substantive source attribution and factual limits.

## Code, diagrams, and links

Introduce a code sample with its purpose. Include the file or command context and relevant dependencies. Execute runnable examples in the stated environment; make omissions explicit in partial examples. Never label an unexecuted snippet as tested. See [MDN's example guidance](https://developer.mozilla.org/en-US/docs/MDN/Writing_guidelines/Code_style_guide) and [Google's formatting guidance](https://developers.google.com/style/code-samples).

Keep code and terminal output as selectable text. Explain a diagram's meaning in prose, provide useful alt text for informative images, and use empty alt text for decoration. Use a logical heading hierarchy and meaningful link text. Do not rely on color, motion, or “the box on the right” to carry the explanation. These practices follow [Google's accessible documentation guidance](https://developers.google.com/style/accessibility).

## German and English parity

- Preserve established German URLs; English content lives under `/en/`.
- Use `lang: de` or `lang: en`, an explicit date, locale-specific `slug`, and one shared `translationKey` for counterparts. Missing `lang` keeps its existing German meaning.
- Translate the reasoning and intended action, not English sentence structure. Check acronyms, quotation context, terminology, units, dates, and linked source versions.
- Compare each locale's title, excerpt, evidence, conclusion, and limitations. Neither locale may gain an unsupported claim or lose a material uncertainty.
- Show an article's language alternative only when its published counterpart exists. Never link a reader to a draft or an unrelated page as though it were the translation.
- About pages preserve the current professional links. The existing German privacy text stays intact; English navigation identifies it as German.

## Publication checklist

- [ ] The piece answers one specific reader question and its opening delivers the title's promise.
- [ ] Consequential claims have supporting evidence; original observations have actual artifacts and reproducible details.
- [ ] No invented personal experience, measurement, quote, citation, human review, or general outcome remains.
- [ ] Sources and code examples were checked in the relevant context, not merely found by a link checker.
- [ ] The explanation states material limits once, where they help interpret the claim.
- [ ] Both language versions preserve the same conclusion and evidence boundary, when both are intended for release.
- [ ] The rendered article has readable code, accessible headings and media, working meaningful links, and usable narrow-screen layout.
- [ ] Metadata, dates, locale, slugs, and translations are consistent with routes, feeds, and sitemap.
- [ ] Draft status is intentional. Boolean `draft: true` stays excluded from all public outputs; a future date alone is not a publishing gate.
- [ ] No private working notes, credentials, unrelated user content, placeholder articles, blanket AI notices, or implementation bookkeeping appears publicly.
- [ ] The relevant content/build checks pass. Editorial judgment and publication authority are still separate from automated validation.

If no article meets these criteria, keep the empty homepage state. A design refresh does not justify publishing unfinished material.

## Maintenance

Correct a consequential factual error in both locales and describe a material correction plainly. Set a new update date only for a substantive change, if the content model supports it. Recheck articles when their central API or behavior changes; avoid implying an old result applies to a new version. Keep useful durable explanations available, with an explicit historical boundary when needed.

Practice can mean a small draft, a clarified example, or feedback on one paragraph. Choose the next topic from real unanswered engineering questions. Publication frequency, article length, readability scores, and numbers of citations are signals; none substitutes for reader value or factual accuracy.
