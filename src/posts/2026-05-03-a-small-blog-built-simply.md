---
title: "A Small Blog, Built Simply"
date: "2026-05-03"
tags: ["engineering", "writing", "static-sites"]
excerpt: "An introduction to this blog: how it is built, why it stays small, and what I plan to write here."
featured: true
slug: a-small-blog-built-simply
---

This is the first post on this blog, so it feels right to start with the shape of the place itself: how it is built, why it is intentionally small, and what I want to use it for.

The short version: this is a static blog made from Markdown files, a small Node build script, and plain HTML. No CMS. No frontend framework. No database. No dashboard.

That is not minimalism for its own sake. It is a response to how I want to write now.

## How it is built

The source of the site lives in a few files:

- site metadata in `src/config.json`,
- page copy in `src/about.md`,
- articles in `src/posts/*.md`,
- styles in `src/styles.css`,
- and the generator in `scripts/build.js`.

The build script reads those inputs and writes static output: the homepage, article pages, tag pages, RSS, sitemap, robots, and CSS. The result is a `dist/` folder that can be served by almost anything.

There is very little magic here. That is the feature.

## Why no CMS or framework

A CMS is useful when people need a human-friendly interface for managing content. But with AI-assisted development, that assumption changes. I do not need to log into an admin screen, fill out forms, and hope the system maps my intent correctly.

I can describe the change I want:

> Write a short introduction post for the blog. Explain how it is built, why there is no CMS, and what readers can expect.

Then an agent can edit the Markdown, update metadata, rebuild the site, and show me the result. The interface is no longer a dashboard. The interface is the conversation, and the source files stay the source of truth.

The same is true for a frontend framework. There is nothing on this site that needs to be a client-side application. The writing should load quickly, remain inspectable, and avoid carrying more machinery than it needs.

## What still stays human

AI can remove the busywork around publishing, but it does not remove responsibility.

The important decisions are still mine:

- what is worth saying,
- what should stay private,
- how direct the tone should be,
- when a feature deserves to exist,
- and whether the final page feels honest.

The agent can help with the mechanics. It can edit, rebuild, and verify. But the intent still has to come from somewhere.

## What to expect here

I want this blog to be a place for thinking out loud about software engineering, leadership, product ideas, AI-assisted development, and the discipline of building useful things.

Some posts will be practical. Some will be reflective. Most should be short enough to respect the reader's time and specific enough to be useful later.

That is the goal: a small place on the web, easy to change, hard to overcomplicate, and clear enough to keep writing in.
