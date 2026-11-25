---
title: "Scaling Code Generation Without Scaling Risk"
date: 2026-11-25
slug: scaling-code-generation-without-scaling-risk
lang: en
tags: [Software engineering, AI, Agents]
excerpt: "How engineering teams can scale coding agent autonomy through verification, harness engineering, and human judgment."
---

Coding agents help engineering teams get more done without needing to hire more people. But if teams don’t also improve how they verify, integrate, and operate code, that extra capacity can become a risk.

A recent [EXT4 pull request](https://lore.landau.one/lkml/179557603037.190026.16193029745159421407.pr-tracker-bot%40kernel.org/T/) for the Linux kernel included AI-generated fixes and additional test coverage. Linus Torvalds criticized the size of the contribution and its timing: the kernel was already in its release stabilization phase.

Just because we can find and make improvements faster now doesn’t mean we should always do it. The real question is how much independence an engineering system can handle safely.

## Verification as the bottleneck

Simon Willison describes [three key moments in LLM development](https://simonwillison.net/2026/Nov/24/llm-inflection-points/), moving from agents that needed lots of corrections to models that can handle complex goals with the right tools. He correctly shows why it’s becoming less necessary to supervise every step for some tasks.

Imagine a team that can do twice as much work but keeps the same review process. Pull requests start to pile up, reviewers have less time for each change, and the team has to choose between longer review times or less careful checks. I experienced this firsthand as my team currently moves to an AI-native engineering workflow.

The Claude Code team reports that between June and September 2026 its [merged PRs more than doubled while the proportion of reverted changes fell by over 40%](https://claude.dev/blog/solving-code-review-at-anthropic/). The team moved much of its review work to agents and invested in verification and recovery. This shows that increasing throughput doesn't have to mean accepting a proportionally higher revert rate.

## How much autonomy is safe?

It’s easy enough to let an agent use a test suite. The harder question is whether that test suite really proves the code is correct.

Picture an agent setting up access control in a multi-tenant app. It might handle authentication correctly and pass all its tests, but still miss that an authenticated user could reach another tenant’s private data.

A pattern that became normal in agentic engineering is [red/green TDD](https://simonwillison.net/guides/agentic-engineering-patterns/red-green-tdd/): write a test, confirm that it fails, then implement the change. Without the first step, a passing test might not exercise the intended change at all.

But even a test that fails as expected can be based on the wrong requirement. In the multi-tenant app example, you could use property-based testing with different users, resources, and permissions to check an isolation rule defined separately. Having another agent review the code can help, but if both agents share the same wrong assumptions, that won’t fix the problem.

Drawing on the Claude Code team's approach to risk-based review, I currently test these three dimensions for evaluating changes in my engineering teams:

| Dimension | Question |
| --- | --- |
| Verifiability | How reliably can we establish that the change satisfies its requirements? |
| Impact | What happens if verification misses something? |
| Reversibility | How easily can we recover from an incorrect change? |

A change that’s well tested, isolated, and easy to undo is a good fit for automated review and merging. But changes to authorization boundaries, stored data, or critical infrastructure need more independent checks and clear human approval. The same change might also need more or less scrutiny depending on where you are in the release cycle.

## Engineering the agent harness

Verification doesn’t have to wait until an agent opens a pull request. Giving agents [back pressure](https://banay.me/dont-waste-your-backpressure/), feedback that helps agents spot and fix mistakes while they’re working, instead of leaving it for an engineer to find later is another key to quality agent output.

How well this works depends in part on the harness and how it interacts with the codebase. Instructions in files like `AGENTS.md` or `CLAUDE.md` set expectations.

Hooks can give back linting or type-checking errors after edits, or even block completion until all checks pass. Permission rules and sandboxing can limit sensitive actions. These controls are especially important when several agents are working at the same time.

OpenAI’s [harness engineering experiment](https://openai.com/index/harness-engineering/) shows how these ideas can apply to the codebase itself. Instead of just using repository instructions, the team built custom linters and structural tests to enforce architecture rules. Engineers also worked to make the environment easier for agents to understand and use.

Not all rules should be inside the harness. Protected CI checks, merge rules, and deployment safeguards should stay outside the agent’s control. Agents shouldn’t be able to weaken the checks that approve their own changes.

This shifts how teams think about engineering infrastructure. Strong typing, reliable tests, and clear architecture rules all help decide how much work can be safely handed off without constant supervision.

## Where engineering judgment matters

Code written by humans isn’t automatically more trustworthy than code from agents. What matters more is the evidence behind a change and the risks if something goes wrong, not who wrote it.

OpenAI’s [Performance Factory](https://openai.com/index/how-openai-performance-factory-keeps-chatgpt-fast/) is a real-world example of splitting up responsibilities. When there’s a performance alert, an agent investigates and suggests a fix, which an engineer then reviews. After deployment, another agent checks if performance is back to normal. OpenAI says they ran over 1,700 investigations in just over three months and found root causes in more than 600 cases.

I also wrote about that in [Bring back the fun in software engineering](https://goeksu.me/articles/bring-back-the-fun-in-software-engineering/), where I argued that delegating implementation does not require delegating the reasoning behind it. Engineers need sufficient understanding of their systems to recognize when existing verification mechanisms are inadequate.

The key point is that verification isn’t just about passing CI. Engineers still have to step in when the fix needs real-world judgment.

There’s another reason to keep humans in the loop. [Microsoft’s research on code review](https://www.microsoft.com/en-us/research/publication/expectations-outcomes-and-challenges-of-modern-code-review/) found that it helps with knowledge sharing as well as catching bugs. As more work becomes automated, teams need new ways to keep the understanding needed to run their systems and spot when current checks aren’t enough.

Counting merged pull requests shows throughput, but not always productivity. Deployment failures, recovery times, and the work needed to fix changes give more clues. Still, even these don’t always show if the architecture is getting worse or if people understand the codebase less.

Currently, my team looks at which verification tasks take up the most human time and which ones could become reliable, automated checks, as we try to get more agents involved in our tasks. Where verification can be made stronger, agents can have more freedom. But if it’s hard to be sure about correctness or mistakes are costly to fix, keeping humans involved makes sense.
