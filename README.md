# skill-issues

My personal Claude Code skills. Each one is isolated and runs only when I type it.

| Command | Use it to |
|---|---|
| `/fp` | Break a problem into its smallest verified facts and find the actual problem |
| `/anim` | Get an interactive HTML animation of how something works |
| `/ste` | Rewrite text in ASD-STE100 Simplified Technical English |

With no argument, each command works on the topic or message we are discussing.
Combine them by typing them in sequence, for example `/fp` then `/anim`.

## Install

Copy the skills into your personal skills folder once:

```bash
git clone https://github.com/yashodhah/skill-issues.git
mkdir -p ~/.claude/skills
cp -r skill-issues/skills/* ~/.claude/skills/
```

Start a new Claude Code session after copying, so the commands are picked up.

## Layout

```
skills/
  fp/SKILL.md
  anim/SKILL.md
  ste/SKILL.md
```

Each skill is a folder with one `SKILL.md`. To add one, create `skills/<name>/SKILL.md`
with `disable-model-invocation: true` in its frontmatter so it runs only when typed.
