---
name: animated-explainer
description: Explain how something works as one interactive HTML animation with big diagrams, animated arrows, and Play/Pause/Step/Reset controls. Use only when the user types /animated-explainer.
argument-hint: "[topic to explain]"
disable-model-invocation: true
---

Explain $ARGUMENTS as one self-contained HTML file with no external dependencies: a large SVG diagram of its parts, arrows that animate along the flow in order, and Play, Pause, Step, and Reset buttons. Clicking a part highlights it and its connections. Save the file in the current working directory as `<topic>-explainer.html`, then send it to the user.
