---
description: Run the builder and checker in a loop until all checks pass
argument-hint: <task>
allowed-tools: Read, Grep, Glob, Bash, Agent
model: opus
disable-model-invocation: true
---

Run this task as a loop: $ARGUMENTS

You coordinate only. Never write or edit code yourself. Use Bash only for read-only commands like `git status` and `git diff`. Never commit or push; leave the changes in the working tree for me to review.

Subagents start with no memory. Every dispatch must include the full brief.

## Setup

1. Look at the repo just enough to write a brief: goal, files in scope, definition of done. Keep it short.
2. Baseline: dispatch the checker on the untouched repo. Tell it this is a baseline run, there is no change to review yet.
3. If the baseline is not ALL GREEN: stop before cycle 1. Show me the failures and ask whether fixing them is part of the task.

## Cycle

Print "Cycle N of 5" at the start of each cycle.

1. Dispatch the builder subagent.
   - Cycle 1: send the brief and tell it to implement the task.
   - Later cycles: send the brief, then the checker's full FAILED section verbatim, and tell it to fix those failures.
2. If the builder says it stopped (task ambiguous, test looks wrong, can't proceed): don't run the checker. Stop and show me its reason.
3. Dispatch the checker subagent. Send the brief and the builder's report.
4. Keep a log of every builder report and checker report. Compare the new checker report with the previous one (the baseline on cycle 1), then apply the stop rules.

## Stop rules

Check these in order after every checker report:

1. All green: every check passes. Stop and report success.
2. Regression: tests or types passed in the previous report and fail now. Stop and escalate to me. A lint check going red is not a regression; treat it as a normal failure.
3. Same failure twice in a row: any failure in this report also appeared in the previous one. Match on file and error text, not line number; lines shift when code is edited. Stop and escalate to me. The builder is guessing.
4. 5 cycles used: stop.
5. Otherwise: start the next cycle.

Never report success without checker output from the final cycle.
Never weaken, skip, or delete a check to reach all green, and never accept a change that does.

## Final output

On all green:
- `git status --short` output
- The builder's last report
- The checker's full final output, as proof
- If every check was SKIPPED, say clearly that nothing was actually verified.

On any other stop:
- Which stop rule fired and on which cycle
- The checker's full last report
- What still fails
- What was tried: one line per cycle from the builder reports
- Your read on why it's stuck and what I should decide
