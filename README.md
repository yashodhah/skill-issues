# yashodha-skills

Personal Claude Code skills, packaged as a plugin marketplace. Every skill is
manual-only: it runs when you type `/<skill-name>`, never automatically.

## Skills

| Command | What it does |
|---|---|
| `/aste-100 <text>` | Rewrites or writes text in ASD-STE100 Simplified Technical English. |
| `/animated-explainer <topic>` | Makes one interactive HTML animation of how something works. |
| `/first-principles <problem>` | Reasons from verified basic facts to an answer. |

## Layout

```
.claude-plugin/marketplace.json            marketplace listing
plugins/personal-skills/
  .claude-plugin/plugin.json               plugin manifest
  skills/<skill-name>/SKILL.md             one folder per skill
```

To add a skill, create `plugins/personal-skills/skills/<name>/SKILL.md` with
`name` matching the folder and `disable-model-invocation: true` in the
frontmatter. Bump `version` in `plugin.json` and `marketplace.json`.

## Install

```
/plugin marketplace add yashodhah/skill-issues
/plugin install personal-skills@yashodha-skills
```

For a local checkout, use the repo path in place of `yashodhah/skill-issues`.
