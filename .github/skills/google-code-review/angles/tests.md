# Tests Angle

Source: https://google.github.io/eng-practices/review/reviewer/looking-for.html

Review the quality, correctness, and completeness of tests. Tests are code and
must be held to the same quality standards as production code.

## Rules

### Presence and Appropriateness
- Are tests present for new functionality? Absence of tests for non-trivial
  logic is a Blocking finding.
- Is the test type appropriate? (unit tests for isolated logic, integration
  tests for component interactions, end-to-end tests for critical user paths)
- Are tests covering the behavior described in the CL, or are they testing
  implementation details that could change without breaking behavior?

### Test Correctness
- Will the tests actually fail when the code they cover is broken?
- Are assertions specific enough to catch real regressions, or are they so
  loose that they pass even when the output is wrong?
- Could tests produce false positives — pass correctly today but fail on an
  unrelated change to internal structure without any real bug being introduced?
- Are mocks and stubs used correctly? Over-mocked tests often verify that the
  code calls a mock, not that the behavior is correct.

### Test Usefulness and Focus
- Is each test focused on one scenario or behavior?
- Are tests simple enough that a reader can understand what they verify in
  under a minute?
- Do test names clearly describe the scenario being tested and the expected
  outcome? A test named `test_foo` is not useful; `test_returns_empty_list_when_input_is_empty` is.
- Are there tests that duplicate each other without adding coverage of distinct
  scenarios?

### Test Fragility
- Are tests tightly coupled to implementation details that are likely to change?
  (e.g., testing private method names, specific log message strings, internal
  object structure)
- Fragile tests create maintenance burden and erode trust in the test suite
  when they fail for reasons unrelated to real bugs.

### Complexity in Tests
- Test code must not be so complex that it itself requires testing or could
  contain its own bugs.
- Avoid test helpers that obscure what's being tested.
- Conditionals and loops in test code are a warning sign — each test case
  should be straightforward.

## Severity Guide

- **Blocking**: No tests for non-trivial new logic; tests that will not fail
  when the code breaks; tests with incorrect assertions that give false
  confidence.
- **Nit**: Minor test naming improvement; slight duplication between test cases;
  a fragile assertion that could be made more robust without much effort.
- **Positive**: Acknowledge thorough edge-case test coverage, well-named tests,
  or tests that clearly document expected behavior as living documentation.
