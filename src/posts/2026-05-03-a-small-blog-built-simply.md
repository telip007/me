---
title: "A Small Blog, Built Simply"
date: "2026-05-03"
tags: ["engineering", "writing", "static-sites"]
excerpt: "An introduction to this blog: how it is built, why it stays small, and what I plan to write here."
featured: true
slug: a-small-blog-built-simply
---

This is the first post, so I'll start with the place itself: how it's built, why I kept it small, and what I want to use it for.

The short version: Markdown files, a tiny Node script, and plain HTML. No CMS, no framework, no database, no dashboard.

That's not minimalism for its own sake. It's just how I want to write now.

### How it's built

The site is a handful of files. Site metadata in `src/config.json`. The about page is `src/about.md`. Posts in `src/posts/*.md`. Styles in `src/styles.css`. The generator is `scripts/build.js`.

The build script reads those, clears `dist/`, and writes static HTML: homepage, article pages, tag pages, RSS, sitemap, robots, CSS. You get a `dist/` folder that almost any server can handle.

Very little magic. That's the point.

### Why no CMS or framework

A CMS makes sense when non-technical people need to edit content. That's not my situation. I don't want to log into an admin screen, click through forms, and hope the system understood what I meant.

I can just say:

> Write a short intro post. Explain how the blog is built, why there's no CMS, and what readers can expect.

Then an agent edits the Markdown, updates metadata, rebuilds the site, and shows me the result. No dashboard. The interface is the conversation. The files are the source of truth.

Same for frontend frameworks. Nothing here needs to be a client-side app. The writing should load fast, stay inspectable, and not carry more machinery than it needs.

### What stays human

AI can handle the publishing busywork, but not the responsibility. The decisions are still mine: what's worth saying, what stays private, how direct the tone should be, when a feature actually deserves to exist, and whether the final thing feels honest.

The agent does the editing, rebuilding, and checking. But the intent has to come from somewhere.

### What to expect

I want this to be a place for thinking out loud about engineering, leadership, product ideas, AI-assisted development, and the discipline of building useful things.

Some posts will be practical. Some will be more reflective. Most should be short enough to respect your time and specific enough that they're still useful when I come back to them later.

That's the goal: a small place, easy to change, hard to overcomplicate, and clear enough that I actually keep writing in it.
