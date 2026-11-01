# yashodha-skills

Personal Claude skills, packaged as a Claude Code plugin marketplace so each
skill can be installed on its own.

## Layout

```
.claude-plugin/
  marketplace.json                  lists every plugin in this repo
plugins/
  <plugin-name>/
    .claude-plugin/plugin.json      plugin manifest (name, version, description)
    skills/
      <skill-name>/
        SKILL.md                    the skill itself (frontmatter + instructions)
        ...                         scripts, references, angle files, etc.
```

Rules for adding a skill:

1. Create `plugins/<plugin-name>/skills/<skill-name>/SKILL.md`. The `name` in the
   frontmatter must match the folder name.
2. If it is a new plugin, add `plugins/<plugin-name>/.claude-plugin/plugin.json`
   and add an entry to `.claude-plugin/marketplace.json`.
3. Bump `version` in both `plugin.json` and `marketplace.json` when a skill changes
   so installed copies update.
4. Keep scripts relative to the skill folder so `SKILL.md` paths keep working.

## Current skills

| Plugin | Skill | What it does |
|---|---|---|
| `newrelic-system-intelligence` | `newrelic-system-intelligence` | Runtime view of a distributed system from New Relic: dependencies, health, change impact, latency, incidents. Needs `NEWRELIC_API_KEY` and `NEWRELIC_ACCOUNT_ID`. |

Not in the plugin layout yet (project-scoped, used by the cookbook and GitHub Copilot):

| Location | Contents |
|---|---|
| `.github/skills/java-patterns` | Java / Spring Boot rules (JAVA-001 to JAVA-003) |
| `.github/skills/api-conventions` | REST conventions (API-001 to API-003) |
| `.github/skills/google-code-review` | Google Engineering code review, seven angle files |
| `.github/agents/google-code-reviewer.md` | Copilot agent that orchestrates the review angles |
| `.github/copilot-instructions.md` | Copilot review instructions for this repo |
| `cookbook/spring-boot-app` | Sample Spring Boot 4 app that references the Java and API skills |

## Install

Add this marketplace to Claude Code, then install the plugin:

```
/plugin marketplace add yashodhah/skill-issues
/plugin install newrelic-system-intelligence@yashodha-skills
```

To try a local checkout instead, use the path to the repo:

```
/plugin marketplace add /path/to/skill-issues
```

## Skill ideas

Brainstorm of skills worth building next, grouped by how often they would come up:

**Engineering workflow**
- `pr-writer`: turn a diff into a PR title and description that follow the repo's PR template.
- `commit-message`: write Conventional Commit messages from staged changes.
- `changelog-from-git`: draft release notes from commits between two tags.
- `adr-writer`: draft an Architecture Decision Record from a short problem statement.

**Review and quality**
- `spring-security-review`: checklist for authn/authz, input validation, secrets, and CSRF in Spring apps.
- `migration-review`: review Flyway or Liquibase migrations for locking, backfills, and rollback safety.
- `test-writer-junit`: write JUnit 5 and Testcontainers tests that match the existing test style.
- `dependency-upgrade`: plan a Spring Boot or library upgrade, including breaking-change checks.

**Operations and incidents**
- `postmortem-writer`: turn an incident timeline and New Relic data into a blameless postmortem.
- `runbook-writer`: write a runbook for a service from its topology and alerts.
- `oncall-handoff`: summarize open alerts, recent deploys, and risks for the next on-call.
- `slo-review`: check SLO burn rate and suggest alert thresholds.

**Personal productivity**
- `meeting-notes`: turn raw notes into decisions, action items, and owners.
- `doc-review`: check a design doc for missing sections, unstated assumptions, and open questions.

Pick the ones you want and I can build them as plugins under `plugins/`.
