# Documentation Angle

Source: https://google.github.io/eng-practices/review/reviewer/looking-for.html

Review whether external-facing documentation is updated to match the change.
Code that works correctly but is documented incorrectly (or not at all) causes
downstream confusion and support burden.

## Rules

### Build, Test, and Release Documentation
- If the CL changes how users build the project, run tests, or release the
  software, are the relevant instructions (README, CONTRIBUTING, Makefile
  comments, CI configuration comments) updated?
- Are setup instructions still accurate after the change?

### User-Facing and API Documentation
- If the CL adds, modifies, or removes a public API, command-line interface,
  or user-visible behavior, is documentation updated to reflect this?
- Are changelog entries or release notes updated if the project maintains them?
- For REST APIs: are OpenAPI/Swagger specs, API reference docs, or inline
  route documentation updated?

### READMEs and Guides
- If the CL adds a new component, service, or major feature, is there a README
  or guide section for it?
- Are existing READMEs still accurate, or does the change invalidate any of
  their content?

### Removal and Deprecation
- If code is deleted or deprecated, is the corresponding documentation also
  removed or updated?
- Outdated documentation that describes removed functionality is often worse
  than no documentation — it actively misleads future developers.
- If a public API is deprecated rather than deleted, does the documentation
  clearly indicate the deprecation and the migration path?

### Internal Developer Documentation
- If the CL changes internal architecture in ways that affect how engineers
  understand and work with the system, are architecture docs, design docs, or
  runbooks updated?

## Severity Guide

- **Blocking**: A public API change with no documentation update; build or
  test instructions that are now incorrect; deprecated functionality left
  documented as current.
- **Nit**: Minor wording improvements to existing documentation; a small
  omission in documentation that won't cause real confusion.
- **Positive**: Acknowledge documentation that proactively explains a
  non-obvious design decision, or removal of stale documentation that would
  have misled future readers.
