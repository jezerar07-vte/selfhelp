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

Look at the repo just enough to write a brief: goal, files in scope, definition of done. Keep it short.

## Cycle

Print "Cycle N of 5" at the start of each cycle.

1. Dispatch the builder subagent.
   - Cycle 1: send the brief and tell it to implement the task.
   - Later cycles: send the brief, then the checker's full FAILED section verbatim, and tell it to fix those failures.
2. If the builder says it stopped (task ambiguous, test looks wrong, can't proceed): don't run the checker. Stop and show me its reason.
3. Dispatch the checker subagent. Send the brief and the builder's report.
4. Compare the checker report with the previous one, then apply the stop rules.

## Stop rules

Check these in order after every checker report:

1. ALL GREEN: stop. Done.
2. FAILED with exactly the same failures as the previous report (same file:line, same error): stop. The builder is stuck; another cycle won't help.
3. FAILED on cycle 5: stop. Out of cycles.
4. Otherwise: start the next cycle.

If some failures got fixed and new ones appeared, that counts as progress. Continue, but mention it.

## Final output

On ALL GREEN:
- `git status --short` output
- The builder's last report
- The checker's full final output
- If every check was SKIPPED, say clearly that nothing was actually verified.

On any other stop:
- Which stop rule fired and on which cycle
- The checker's full last report
- What changed between the last two reports
- Your read on why it's stuck and what I should decide
