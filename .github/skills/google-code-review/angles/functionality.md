# Functionality Angle

Source: https://google.github.io/eng-practices/review/reviewer/looking-for.html

Review whether the change does what the developer intended and whether that
behavior is correct for both end-users and future developers working with this
code.

## Rules

### Intent vs. Implementation
- Does the code actually do what the CL description claims it does?
- Are there gaps between the stated intent and what the implementation delivers?
- If you cannot verify the implementation matches the intent from reading the
  code, flag it — the developer may be confident the code works but have
  introduced a subtle misalignment.

### End-User Impact
- For user-facing changes (UI, API responses, CLI output), does the change
  improve or at minimum not harm the user experience?
- Could the change impact users in ways that aren't described in the CL
  description? Undocumented user-facing changes are a concern.
- For library or framework changes, "users" includes future developers who will
  call this code — consider their experience too.

### Edge Cases
- What happens at boundaries? (empty inputs, zero values, maximum values,
  single-element collections, null/nil/None)
- What happens when external dependencies fail or return unexpected values?
- Are all code paths handled, including error paths?
- If the author has not considered an edge case that could cause a crash or
  silent data corruption, flag it as Blocking.

### Concurrency and Parallelism
- If the code runs in a multi-threaded or async context, are shared mutable
  resources properly protected?
- Could this code introduce a deadlock? (e.g., acquiring locks in inconsistent
  order, holding a lock while waiting on another resource)
- Could this code introduce a race condition? (e.g., check-then-act on shared
  state without synchronization)
- Flag concurrency bugs as Blocking — they are notoriously difficult to
  reproduce and fix after the fact.

### Correctness Confidence
- The reviewer is not required to exhaustively test every path, but should
  think carefully enough to have reasonable confidence the code is correct.
- If you are unsure whether code is correct, say so explicitly rather than
  approving under uncertainty.

## Severity Guide

- **Blocking**: Incorrect behavior for common inputs, unhandled error paths
  that cause crashes or data loss, race conditions or deadlocks, user-visible
  regressions.
- **Nit**: Handling an edge case that is extremely unlikely but harmless to
  address; minor wording improvement in an error message.
- **Positive**: Acknowledge thorough edge-case handling, clear error messages,
  or well-handled concurrency patterns.
