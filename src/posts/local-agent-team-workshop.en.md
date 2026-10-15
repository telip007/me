---
title: A source checker failed to distinguish Markdown contexts
date: '2026-10-15'
lang: en
translationKey: local-agent-team-workshop
slug: markdown-source-checking-and-review
tags:
  - Markdown
  - software-engineering
  - quality-assurance
excerpt: >-
  A local test reproduced four false passes in a source-link checker.
  Independent review changed the outcome: the candidate was not adopted.
draft: true
---

A small checker was meant to ensure that German and English blog drafts each contained a source link. Its own tests passed. An independent review still found four cases where it accepted a document with no actual source link.

The checker searched the text for link-shaped patterns. That is not enough: Markdown distinguishes links from images, code blocks and HTML. The [CommonMark specification](https://spec.commonmark.org/0.31.2/) defines these forms separately. A link pattern inside a code example or an HTML comment does not support a claim in the article.

## The failed check

In a fresh local check on 15 October 2026, the candidate's own suite passed with nine tests. The independent review also expected rejection when the only apparent link was inside a tilde-fenced code block, indented code, an HTML comment or image syntax. In all four cases, the checker returned success instead.

Those results are reproducible in the local review copy. They establish a narrow defect in this candidate version; they say nothing about Markdown checkers in general. The candidate was not adopted after review. That decision does not demonstrate successful self-improvement. It shows that passing its own tests was not enough for acceptance.

## What this observation supports

An automated check can satisfy the wrong condition and still report success. Here, the real question was whether the article text contained an actual source link, not whether a link-shaped pattern appeared somewhere. The public specification helped distinguish the syntax; only the local counterexamples showed how the candidate behaved.

This is a small, local finding. It does not prove that the rejection was correct in every respect or that other review steps are reliable. Nor does it establish greater productivity or general quality of the agent team. It shows one useful boundary: a proposal can be reviewed and rejected before it becomes part of the tools in use.

This article was created with the help of AI. The described test results were rerun locally on 15 October 2026; publishing this observation does not turn it into a general quality claim.
