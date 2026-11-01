---
name: art
description: Show this conversation as one organized HTML artifact that reads like a story, with tabs. Type /art to run.
argument-hint: "[optional: name of a new tab, or leave empty]"
disable-model-invocation: true
---

Show this conversation as one HTML artifact that reads like a story.

- If no artifact exists in this conversation yet, create one with a single tab named after the topic.
- If one already exists, update that same artifact using its slug and base version. Never create a second one.
- Add a new tab only when $ARGUMENTS names one, or when the conversation clearly moves to a different topic. Otherwise add to the current tab.
- Write each tab as a story: the situation, the problem, the steps with a concrete example for each, then the outcome. Use short paragraphs, headings, and code blocks for examples.
- Keep the output of `/fp` and `/anim` in their own tab.
