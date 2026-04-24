## Code Review Philosophy

When reviewing code, follow the Google Engineering Code Review standard.

Core principle: The goal of code review is to improve overall code health over
time — not to produce perfect code. Approve a CL once it clearly improves the
system, even if it isn't perfect.

Rules:
- Use "Nit:" prefix for non-blocking style suggestions
- Use mentoring tone — explain *why*, not just *what* to fix
- Technical facts overrule personal preferences
- Never block a CL that clearly improves the system
- Acknowledge good things the developer did
- "No such thing as perfect code — only better code"
