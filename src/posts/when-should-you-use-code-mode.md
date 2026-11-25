---
title: "When should you use Code Mode?"
date: 2026-11-24
updated: 2026-11-25
slug: when-should-you-use-code-mode
lang: en
tags: [AI, Agents, MCP]
excerpt: "Code Mode moves deterministic work out of the inference loop. Here's where that saves context, time and effort, and where ordinary tool calls are enough."
featured: false
---

Code Mode allows an agent to write a program that calls its tools rather than the language model having to do every single step itself. That means the LLM doesn't have to spend all its time on things that code can do quite easily.

Use Code Mode when an agent can use a program to fetch, filter or combine several tool results before the model reads them. For a single call whose result the model needs to read in full, a direct tool call is usually enough. The decision depends on the work the agent needs to do with the tools.

## What changes with Code Mode?

Suppose you ask the agent to look at a CI pipeline (find the failed jobs, get their logs, work out which tests are failing most often).

With regular tool calling the model gets the job list, asks for the logs and gets the logs back. It then needs to parse and group the failures. Even if the logs are fetched in parallel their contents will take up a significant amount of the context window.

With Code Mode the agent can create code that does all the retrieval and aggregation and just returns a simple result.

```terminal-diagram direct-tool-calls
```

```terminal-diagram code-mode
```

The program might look like this. The tool names are illustrative, and the example counts matching log lines that start with `FAIL `.

```javascript
const jobs = await tools.listFailedJobs({
  runId: 42,
});

const logReads = jobs.map(async ({ id }) => {
  const log = await tools.getJobLog({ id });
  return log.match(/^FAIL .+$/gm) ?? [];
});

const results = await Promise.allSettled(logReads);

const counts = {};
const errors = [];

for (const [index, result] of results.entries()) {
  if (result.status === "rejected") {
    errors.push(jobs[index].id);
    continue;
  }

  for (const line of result.value) {
    counts[line] = (counts[line] ?? 0) + 1;
  }
}

return { counts, errors };
```

Now the model can just focus on the most common failures rather than using its context on every log. That's the principle behind [Cloudflare's Code Mode](https://blog.cloudflare.com/code-mode/).

## Why it matters

**Context:** suppose 20 jobs each return 50KB of logs (so about 1MB total). If you only need the failure counts then you're probably only interested in a very small amount of structured output. You can leave the rest out of the model's context and have more space for the actual investigation, and you reduce the risk of running out of context too quickly.

**Latency:** Each dependent tool call may require another model inference. You could get the job IDs and then immediately go and fetch the logs from them, rather than waiting for the model to make the next call.

**Reliability:** Things like counting, sorting, joining records and applying known conditions are all very predictable. You can write that code once and it will just do the required processing on the raw data without having to go through that process repeatedly. You can also validate and test the logic.

Another good feature is on-demand tool discovery. Rather than load up a massive MCP tool catalog at the outset you can discover the tools that you need as you go. [Cloudflare's MCP server for its API](https://blog.cloudflare.com/code-mode-mcp/) does this with separate search and execution tools. Tool discovery and programmatic execution work very well in tandem, but you don't necessarily need both at the same time.

## Why not just use Bash?

For local files or services that have a suitable CLI a shell script can achieve pretty much the same outcome. Coding agents already make use of tools such as `rg` and `jq` to filter the information before returning it to the model.

Code Mode is particularly useful when the tools are part of the agent harness rather than the shell. The agent could for instance pick up a GitHub issue, go and find the relevant Sentry errors and then combine those results without needing to set up a separate CLI.

[Armin Ronacher's article on Codemode](https://lucumr.pocoo.org/2026/10/6/codemode/) makes this distinction very clearly using Pi. Its runtime also has access to session storage and a range of model APIs so the generated programs can persist intermediate data or hand off certain tasks. That's taking it a lot further than just batching tool calls.

## Does the implementation matter?

Yes in particular when you're deciding whether to turn it on. [Claude Code](https://code.claude.com/docs/en/code-mode) offers an experimental mode for making tool calls from JavaScript. [OpenClaw](https://docs.openclaw.ai/tools/code-mode) combines program execution with tool discovery and can enable Code Mode based on the selected model. The available tools and runtime guarantees vary across implementations.

Code Mode is ideal for scenarios with large tool responses, multiple steps that are repeated or where there are several dependent lookups. It's particularly useful for cross-service investigations, CI triage and issue reporting.

It's not so compelling when the agent has to interpret some unfamiliar information before it can decide what its next step is. A generated filter can in fact filter out the very evidence the model needs. For a small edit or a single lookup direct calls may actually be simpler. Workflows that are going to modify external systems need to be treated with care as a failed script may well have already done some of its writes.

Start with a recurring read only task. Run it with and without Code Mode using the same model and inputs. Check correctness first, then elapsed time, token usage, and cost. Where appropriate include the parallel direct calls or shell commands in the baseline.

The question we should be asking is not how many tool calls Code Mode removes, but how many model decisions the task actually requires. If the bulk of the work that's left is data processing, then deterministic code is probably the better place to do that.
