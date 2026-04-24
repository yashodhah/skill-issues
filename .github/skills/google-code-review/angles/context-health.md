# Context & Code Health Angle

Source: https://google.github.io/eng-practices/review/reviewer/looking-for.html
        https://google.github.io/eng-practices/review/reviewer/standard.html

Review the change in the context of the whole file and the system, not just the
diff. A change that looks harmless in isolation may degrade code health when
viewed in context.

## Rules

### Whole-File Context
- Read the surrounding code, not just the changed lines. Does the new code
  make sense in the context of the full file?
- Does the change create inconsistency with patterns already established in
  the same file? (e.g., a new function in a different style, a new field
  that doesn't follow the existing field naming convention)
- Does the change belong in the file it was placed in, or does it dilute the
  file's cohesion?

### Code Health Trajectory
- Is this CL improving overall code health, maintaining it, or degrading it?
  Per Google's standard: "Reviewers should never accept CLs that degrade the
  overall code health of the system."
- Even small degradations matter — they accumulate. A minor hack today
  enables a larger hack tomorrow. Flag even subtle regressions in health.
- Conversely, a CL does not have to be perfect to be approved. If it
  demonstrably improves the system even with some imperfections, it should
  be approved with Nit comments.

### Incremental Complexity
- Is this CL part of a pattern of gradually increasing complexity in a file
  or module?
- Are there signs that a refactor or cleanup is becoming necessary that this
  CL is deferring?
- If the CL is addressing a problem caused by earlier technical debt, does it
  reduce that debt or just work around it?

### Health vs. Velocity Balance
- The goal of code health review is not to block progress — it is to prevent
  decline. When in doubt, lean toward approving a CL that makes things better,
  not blocking it because it isn't perfect.
- Use "Nit:" for findings that represent missed improvement opportunities
  rather than active degradations. Reserve Blocking for changes that leave
  the codebase measurably worse than before.

### Positive Health Patterns
- Acknowledge CLs that visibly improve code health: removing dead code,
  consolidating duplicated logic, adding missing abstractions that clarify
  intent, or cleaning up debt while adding a feature.

## Severity Guide

- **Blocking**: A change that actively degrades code health — introduces
  technical debt, makes a component harder to reason about, or creates
  inconsistency that will confuse future contributors.
- **Nit**: A missed opportunity to improve the surrounding code (but where
  the CL itself doesn't make things worse); a minor stylistic inconsistency
  with the rest of the file.
- **Positive**: Acknowledge a CL that leaves the codebase meaningfully
  cleaner or better-structured than it found it.
