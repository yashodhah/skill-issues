# Complexity Angle

Source: https://google.github.io/eng-practices/review/reviewer/looking-for.html

Review whether the code is more complex than it needs to be. Complexity is the
primary source of bugs — developers are likely to introduce bugs when calling
or modifying code they cannot understand quickly.

## Rules

### Line-Level Complexity
- Can each non-trivial line be understood in a few seconds by a competent
  engineer who is not the original author?
- Are there deeply nested expressions, chained method calls, or boolean logic
  that requires significant effort to parse?
- If a line requires a comment to explain *what* it does (not *why*), it is
  probably too complex and should be simplified or decomposed.

### Function-Level Complexity
- Does each function do exactly one thing?
- Is the function short enough to understand in one reading?
- Are there functions that mix multiple levels of abstraction (e.g., low-level
  I/O operations alongside high-level business logic)?
- Functions that are too long to display on a single screen without scrolling
  are a signal worth flagging.

### Class-Level Complexity
- Does each class have a single, clear responsibility?
- Are there classes that have grown to manage too many unrelated concerns?
- Is inheritance used where composition would be simpler and more flexible?

### Over-Engineering
- Is the code more generic than the current requirements demand?
- Are there abstractions (interfaces, factories, registries, plugin systems)
  that serve no concrete use case today?
- Is the developer solving a future problem that doesn't exist yet?
- Per Google's standard: "If a reviewer sees code that they think is more
  complex than necessary, they should say so." The author must demonstrate a
  present need, not a hypothetical one.

### Premature Generalization
- Flags to look for: unused type parameters, callback hooks with no callers,
  configurable behavior with only one configuration, abstract base classes with
  a single concrete subclass.
- These patterns are not wrong in principle, but require justification when
  they add complexity without a present payoff.

## Severity Guide

- **Blocking**: A function or class so complex that a reviewer cannot
  confidently understand what it does; complexity that makes the code
  unmaintainable or nearly impossible to test correctly.
- **Nit**: A mildly long function that could be extracted; a slightly
  over-engineered abstraction that isn't yet a serious maintainability burden.
- **Positive**: Acknowledge simple, direct implementations that could have been
  over-engineered but weren't; clean single-responsibility decomposition.
