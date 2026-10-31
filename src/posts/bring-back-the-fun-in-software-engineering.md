---
title: Bring back the fun in software engineering
slug: bring-back-the-fun-in-software-engineering
date: 2026-10-31
lang: en
tags: [Software engineering, AI, Agents]
excerpt: "How to keep the problem solving and satisfaction in everyday development when an agent writes more of the code."
draft: false
---

When I talk to engineers who hesitate to use AI for coding, one concern keeps coming up: they enjoy writing code and don't want to lose that. Others have already adopted it and miss the fun they used to have. They spend more time describing a problem and reviewing a solution, and less time working through it themselves.

I understand the concern. Figuring out why something breaks, finding a good abstraction, and finally getting an implementation right are satisfying parts of this job. A workflow of prompt, wait, accept can feel like handing those parts away.

But I think there's still plenty of fun to be had. The problem solving, engineering, and coding shift when you work with an agent. You can stay involved in deciding how a feature should behave, trying competing designs, and figuring out why the implementation fails. You can also build the tools and feedback loops that make the agent useful. There is more to this way of working than describing a task and waiting for the result.

Let me start with the least ambitious example and work up to the more interesting ones.

## Engineering p*rn

Remember wondering what your project would look like in Rust? Or wanting to try a new JavaScript framework, while knowing that rebuilding a working application would be hard to justify?

An agent gives you another way to explore that question. You can ask for a small port, inspect the result, change the design, and see where the new language makes things easier or more awkward. The interesting part is comparing the implementations and understanding the differences.

This blog is my example. Before its first post, it went through Svelte, a custom static build pipeline, and then FastAPI with HTMX. Those rewrites weren't about attracting traffic. They satisfied my curiosity about different ways to build the same small site.

I wouldn't have spent the same effort on all those versions by hand. With an agent, I was willing to try them.

That's a modest argument, though. If you miss solving problems yourself, having an agent produce another implementation may still leave you watching from the sidelines. The more interesting question is how you stay involved in the work you already do.

## Keep shaping what you build

Take something as ordinary as adding search to a screen. An agent can write the input component and request handler. You still have to work out what happens while a request is pending, whether old results should remain visible, and how a keyboard user chooses a result. If an earlier request finishes after a later one, which response reaches the screen?

You can work through those questions with the agent: try two approaches, use them, inspect where they break, and change the design. Instead of spending the whole session implementing your first idea, you can spend more of it finding out whether the idea is any good. That can be a satisfying way to build.

The same involvement matters when a webhook is delivered twice or an offline edit meets a newer server version. There are choices about transactions, retries, and conflict resolution. You can ask for an implementation while keeping hold of the reasoning about what must remain true.

And when you want to implement a particular part yourself, you can. Delegation can be selective. Perhaps the agent prepares the surrounding plumbing while you work through the state transition that's caught your interest.

## Build the tooling

Suppose your agent needs information from a service you operate. Today you open a dashboard, find the relevant deployment, copy some logs, and paste them into the conversation. Every time.

You could build a small CLI that returns the deployment status and relevant errors. Or expose that capability through an [MCP server](https://modelcontextprotocol.io/).

It could just as well be a command that opens a particular screen with known test data, captures its state, or reproduces a troublesome request. The tool gives both you and the agent a better way to investigate the feature you're working on.

Now you have an interface-design problem. Does the tool accept a deployment ID, a service name, or both? How does it distinguish an unknown service from a failed deployment? How much log output should it return? What does the agent need to know to take a useful next step?

Returning everything is easy. Returning enough information to diagnose the problem without burying the useful signal takes more thought. You can experiment with [tool boundaries, descriptions, and results](https://www.anthropic.com/research/writing-tools-for-agents), then check whether the agent can complete the task with what you've given it. An ambiguous error or a missing identifier gives you something concrete to investigate and improve.

You still have APIs to design, errors to handle, and code to debug. The user of some of that software happens to be an agent.

## Build an agent

If you want to understand the tool you're working with more deeply, you can also build a small agent yourself. This is an optional project; you can apply the loop and coordination ideas below using an existing coding agent.

For this discussion, a coding agent is a program that lets a language model choose actions, executes the allowed actions, and feeds the results back so it can decide what to do next. It might read a file, edit it, run a command, inspect the result, and try again. The core can be a simple `while` loop.

Thorsten Ball's [“How to Build an Agent”](https://ampcode.com/notes/how-to-build-an-agent) develops a small code-editing agent in Go. Geoffrey Huntley's [coding-agent workshop](https://ghuntley.com/agent/) takes a similarly direct route through the underlying mechanics. Both are useful starting points for seeing what a minimal agent contains. Their examples don't establish what it takes to make a production system reliable.

[ReAct](https://arxiv.org/abs/2210.03629) is an early research example of this pattern: reasoning and actions are interleaved, with observations from the environment informing subsequent steps.

Once the first loop works, the design questions start multiplying. What happens if you cancel halfway through a tool call? Which events should the interface display? What state survives a restart? How do you preserve a conversation when switching model providers?

For a concrete implementation, [Zechner's account of building Pi](https://mariozechner.at/posts/2025-11-30-pi-coding-agent/) works through these kinds of decisions, from context handoffs to cancellation and terminal rendering.

That is where this gets interesting to me. Understanding the loop gives you something you can inspect, change, and reason about. You can form a hypothesis about a failure, modify the implementation, and check whether your explanation was right.

### Loop engineering

The loop inside the agent handles model calls and tool results. You can also design a loop around a larger piece of work: find the next task, give it to an agent, check the result, record what happened, and decide whether to continue.

Huntley's [“everything is a ralph loop”](https://ghuntley.com/loop/) describes this shift as programming the loop and watching for failures to address. The interesting engineering question is what makes repeated attempts produce useful progress.

Return to the search feature. A concrete task might be to keep a slow response from replacing newer results. You reproduce the failure by controlling the order in which two requests finish, let the agent attempt a fix, and run the check again. If it passes, you inspect the behavior and the change. If it fails, the observed result becomes feedback for another attempt, within a fixed retry limit.

![A feature-work loop: define one observable behavior, let the agent attempt a change, and check the result. A pass leads to inspecting the change and recording progress. A failure provides feedback for a bounded retry or stops for investigation.](/static/images/posts/bring-back-the-fun-in-software-engineering/repair-loop.png)

*A loop around an ordinary development task. You can run it interactively or automate selected steps.*

Even this small example contains a real puzzle: a check that passes when the result list stays empty would miss the point. You need evidence that the latest results appear and stale results cannot replace them. Deciding what to observe is part of solving the feature, and the agent's claim that it fixed the race isn't that evidence.

Then there is diagnosis. If the same failure appears after three attempts, is the agent editing the wrong layer? Is the test controlling the race you intended? What should the next attempt know about the previous failures? You still get to investigate, form a better explanation, and change the approach.

The [autoresearch repository](https://github.com/karpathy/autoresearch) offers a different concrete example: an agent changes training code, runs a time-bounded experiment, evaluates a metric, and keeps or discards the change. Its fixed scope and evaluation make the control loop easy to examine, even though a feature like our search interaction needs different checks.

If you enjoy debugging state machines or designing feedback mechanisms, there is plenty here to work on. Getting the model to produce another patch is only one part of the system.

### Graph engineering

Now suppose the work contains several tasks with different dependencies. Some can run independently; others need earlier results. You have a scheduling and coordination problem.

Suppose the search feature needs a new endpoint and a change to the screen. Once you've agreed on the request and response contract, the handler and its consumer can be developed separately. An integration check needs both implementations. A final inspection needs the integrated result.

![A dependency graph for a search feature: agree on the API contract, develop the request handler and screen behavior independently, join them for an integration check, then inspect the result. Either implementation task can contain an agent loop.](/static/images/posts/bring-back-the-fun-in-software-engineering/task-graph.png)

*The arrows express dependencies. A task can use ordinary code, an agent, or a complete loop.*

The graph gives you somewhere to express those relationships. It also forces decisions about ownership and state. Which worker owns the shared types? What happens if the response format changes while another task is using the earlier version? Can a failed task be retried without overwriting someone else's work?

These aren't new problems invented by AI. They belong to concurrency, build systems, and distributed systems. Agents introduce another source of variability into them.

[LLMCompiler](https://proceedings.mlr.press/v235/kim24y.html) is a concrete research example: it separates planning function calls, dispatching tasks according to dependencies, and executing them. The useful idea here is making dependencies explicit enough for an executor to act on them.

A graph also doesn't require a different agent in every box. [LangGraph's Graph API](https://docs.langchain.com/oss/python/langgraph/graph-api) explicitly permits nodes containing ordinary code as well as model calls, with state and conditional transitions connecting them. Loops and graphs can be combined; they aren't successive levels of intelligence.

You might decide that one agent working through the feature sequentially is simpler. Working out whether coordination buys anything is part of the engineering. A more elaborate diagram doesn't settle that question.

## Stay involved in the problem

None of this guarantees that you'll enjoy the shift. If the particular thing you love is implementing an algorithm line by line, watching an agent implement it is a different experience. I wouldn't pretend otherwise. You can still choose to write that part yourself.

The part I'd try to preserve is the moment when my understanding changes: when I find the reason for a bug, see why an abstraction is awkward, or realize a simpler design will do. An agent can write the patch while I still work through that question. If I hand over both the implementation and the reasoning, I can see why the work would feel less satisfying.

I wouldn't judge that satisfaction by how much code appeared or how many tasks I closed. I'd ask what I understand now that I didn't before. Can I explain why the fix works? Did I make a choice about the behavior, or just accept the first version that ran? Those questions give me a way to notice when I'm becoming a spectator and choose where to get involved again.

For your next feature, choose a question you actually want to work through. It might be how a search interaction should feel, where a transaction should end, or why a retry corrupts state. Let the agent help with implementation, but keep investigating that question: try an approach, inspect what happens, and change your mind when the evidence calls for it.

That's a problem to solve, a design to make, and often code to write. The work has shifted. There is still room to get your hands into it.
