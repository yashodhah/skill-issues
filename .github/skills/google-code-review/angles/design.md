# Design Angle

Source: https://google.github.io/eng-practices/review/reviewer/looking-for.html

Review the overall architecture and integration of the change. Ask whether the
code is well-designed before examining lower-level details — a fundamental design
flaw invalidates all other review work.

## Rules

### Overall Design Soundness
- Does the change make architectural sense as a whole?
- Is the interaction between different parts of the code logical and clean?
- If multiple components or services are touched, does the CL create appropriate
  boundaries between them?

### Correct Placement of Code
- Does this code belong in the codebase, or should it live in a shared library,
  a separate service, or a third-party dependency?
- Is the abstraction level of the new code consistent with the surrounding code?
- Is the change adding to a layer that already has too many responsibilities?

### System Integration
- Does the change integrate well with the rest of the system?
- Are dependencies between modules introduced in a direction that makes sense
  (e.g., avoiding circular dependencies, keeping dependencies pointing toward
  stable modules)?
- Does the change respect existing contracts, interfaces, and invariants?

### Timing and Readiness
- Is this the right time to introduce this functionality?
- If the feature is speculative or anticipates requirements that don't yet exist,
  flag it — solving future problems prematurely adds complexity with no present
  benefit.
- Does the codebase have the prerequisite infrastructure to support this change
  cleanly, or is the change working around a gap that should be addressed first?

### Design Feedback Timing
- Raise major design concerns early, even if the rest of the review is incomplete.
  Significant design problems will likely invalidate other review feedback, so
  it is better to surface them first rather than completing a full review on
  fundamentally flawed code.

## Severity Guide

- **Blocking**: Fundamental architectural mismatch, circular dependencies
  introduced, code placed in the wrong layer or wrong repository.
- **Nit**: Minor structural preference, debatable abstraction boundaries where
  both approaches are defensible.
- **Positive**: Acknowledge clean separation of concerns, well-chosen abstraction
  boundaries, or code that clearly belongs where it was placed.
