# Naming, Comments & Style Angle

Source: https://google.github.io/eng-practices/review/reviewer/looking-for.html

Review naming clarity, comment quality, and style guide adherence. All style
findings must be prefixed Nit — never block a CL on style alone. Personal
preferences that aren't in the style guide should not be raised at all.

## Rules

### Naming

- Are names long enough to clearly communicate what the item is or does?
  A name like `d` or `tmp` is almost never acceptable outside a trivial loop
  variable.
- Are names short enough to remain readable? A name like
  `listOfAllActiveUserAccountsWithAdminPrivileges` may be precise but is
  cumbersome; a well-named type or variable narrows the scope without repeating it.
- Do function names describe what the function does, using active verbs where
  appropriate? (`fetch_user` not `user_data`)
- Do boolean names read as predicates? (`is_valid`, `has_permission`, not
  `valid`, `permission`)
- Are names consistent with the naming conventions already in use in the
  surrounding codebase? Inconsistency creates cognitive friction.

### Comments

- Do comments explain *why* the code exists, not *what* it does?
  Code that requires a comment to explain what it does should usually be
  refactored to be self-explanatory instead.
- Are there comments that restate the code in prose? These add noise and
  drift out of sync with the code. Flag them for removal.
- Do comments document non-obvious constraints, external dependencies, or
  historical reasons for unusual decisions?
- Are existing TODOs still relevant? If a TODO references a bug or feature
  that has since been resolved, it should be removed.
- Are public API comments (docstrings, JSDoc, godoc) present and accurate
  for anything that exposes a public interface?

### Style

- Does the CL follow the team's or language's established style guide?
  Style guide rules are authoritative — deviations are always at least Nit.
- If a style point is not covered by the style guide, it is the author's
  personal preference. Do not raise it. Accept the author's choice.
- Flag style issues as Nit only. Never block a CL on style.
- If the style guide is silent on an issue and the reviewer has a strong
  preference, it is acceptable to note it with "Nit (personal preference):"
  so the author can clearly distinguish it from a guide violation.

## Severity Guide

- **Blocking**: A name so misleading that it would cause future developers to
  misuse the API (e.g., a function named `save` that deletes); a missing
  public API docstring on a widely-used interface.
- **Nit**: Minor naming improvements; comments that restate the code; style
  guide deviations; stale TODOs.
- **Positive**: Acknowledge exceptionally clear naming that makes surrounding
  code self-documenting, or comments that illuminate genuinely non-obvious
  constraints.
