---
name: google-code-review
description: Load this skill when the user asks to review code, a PR, a diff, a changelist (CL), or requests a code review. Trigger words include: review, PR review, pull request review, diff review, code review, CL review, LGTM, look at this code.
---

# Google Engineering Code Review Skill

This skill implements the Google Engineering Code Review standard as documented
at https://google.github.io/eng-practices/review/reviewer/. It provides a
structured framework for evaluating code changes across seven distinct angles.

## Angle Files

Each angle file contains concrete, actionable rules derived from the Google
Engineering practices. The seven angles are:

| Angle | File | Covers |
|---|---|---|
| Design | `angles/design.md` | Architecture, system integration, placement of code |
| Functionality | `angles/functionality.md` | Correctness, edge cases, concurrency, user impact |
| Complexity | `angles/complexity.md` | Readability, over-engineering, function/class size |
| Tests | `angles/tests.md` | Test presence, correctness, quality, and simplicity |
| Naming, Comments & Style | `angles/naming-comments-style.md` | Identifiers, inline comments, style guide adherence |
| Documentation | `angles/documentation.md` | READMEs, guides, deprecation notices |
| Context & Health | `angles/context-health.md` | Whole-file context, code health trajectory |

## How to Use This Skill

When this skill is invoked by a subagent, the subagent's prompt will specify
WHICH angle file to focus on. Load and apply ONLY that angle's rules — do not
apply rules from other angle files. This keeps each reviewer's output focused
and non-overlapping.

## Output Format

Every finding must include all three of these fields:

- **Severity**: One of `Blocking`, `Nit`, or `Positive`
  - `Blocking` — must be resolved before approval
  - `Nit` — optional polish, author may ignore
  - `Positive` — acknowledge something done well
- **Location**: File name and line number(s) if known; otherwise describe the
  area of the change
- **Explanation**: The *why* behind the finding — not just what is wrong, but
  why it matters for code health, maintainability, or correctness

End every angle review with a brief `## Angle Assessment` paragraph (2–4
sentences) summarizing what you found and whether this angle raises any
blockers.
