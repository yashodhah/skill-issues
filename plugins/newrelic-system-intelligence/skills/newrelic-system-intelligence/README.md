# New Relic System Intelligence Skill

A reusable skill that gives AI agents (coding agents, ops bots,
incident responders) a holistic, trustworthy view of a distributed
system at runtime, using New Relic as the source of truth.

The agent-facing contract is defined in `SKILL.md`. This README is a
human-readable setup and development guide.

## What it does

Given a service name, this skill lets an agent answer:

1. What does this service depend on at runtime (upstream + downstream)?
2. What is the health of this service and its dependencies right now?
3. What changed recently, and what was the impact?
4. Where is the latency in the request chain?

## Requirements

- Python 3.8 or newer
- A New Relic user API key (`NEWRELIC_API_KEY`)
- A numeric New Relic account ID (`NEWRELIC_ACCOUNT_ID`)
- `httpx==0.27.0` (the only runtime dependency)

Runs identically on macOS, Windows, and Linux. No shell scripts,
subprocess calls, or OS-specific code.

## Setup

### 1. Install dependencies

```
pip install -r requirements.txt
```

### 2. Set environment variables

macOS/Linux:

```
export NEWRELIC_API_KEY="your_api_key_here"
export NEWRELIC_ACCOUNT_ID="your_account_id_here"
```

Windows Command Prompt:

```
set NEWRELIC_API_KEY=your_api_key_here
set NEWRELIC_ACCOUNT_ID=your_account_id_here
```

Windows PowerShell:

```
$env:NEWRELIC_API_KEY="your_api_key_here"
$env:NEWRELIC_ACCOUNT_ID="your_account_id_here"
```

Get your API key at https://one.newrelic.com/api-keys. Your numeric
account ID lives in the same UI under the user menu.

### 3. Run a smoke test

```
python topology/get_entity.py --service-name <your-service-name>
```

If this returns a JSON object with a `guid`, the skill is wired up
correctly.

## Repository Layout

```
newrelic-system-intelligence/
├── SKILL.md                         master skill definition (agent reads this first)
├── README.md                        this file
├── requirements.txt                 httpx pinned to 0.27.0
│
├── common/
│   ├── config.py                    check_env(), endpoints, headers
│   └── nerdgraph.py                 shared nerdgraph_query() HTTP client
│
├── topology/
│   ├── get_entity.py
│   ├── get_relationships.py
│   ├── get_full_map.py
│   └── get_workloads.py
│
├── health/
│   ├── get_golden_metrics.py
│   ├── get_open_alerts.py
│   ├── get_service_levels.py
│   └── get_error_groups.py
│
├── traces/
│   ├── get_recent_traces.py
│   └── get_latency_breakdown.py
│
├── changes/
│   ├── get_recent_deployments.py
│   └── get_change_impact.py
│
├── query/
│   └── nrql.py
│
└── compose/
    ├── system_snapshot.py
    └── incident_context.py
```

## Invocation

Every script is runnable standalone, like this:

```
python topology/get_entity.py --service-name payment-service
python compose/system_snapshot.py --service-name payment-service
python compose/incident_context.py --service-name payment-service
```

Scripts print exactly one JSON object to stdout and exit 0 on
success. Errors, warnings, and progress are written to stderr. See
`SKILL.md` for the full decision guide and output schemas.

## Design Principles

- **Single source of config**: every script calls `check_env()` from
  `common/config.py` at startup. Credentials and account IDs only come
  from environment variables.
- **Single source of HTTP**: all NerdGraph traffic goes through
  `common/nerdgraph.py`. Individual scripts never build their own HTTP
  client.
- **JSON on stdout, everything else on stderr**: scripts are
  composable and agent-friendly. You can pipe their output into `jq`
  or into another script.
- **Compose = import, not exec**: the `compose/` scripts import core
  functions directly from their siblings. They never shell out. This
  keeps the call graph observable and avoids fork/exec overhead.
- **Standalone scripts for humans**: each script is deliberately
  small, self-contained, and documented so a human can read, review,
  and modify just that one file without understanding the whole
  repository.

## Extending the skill

To add a new data source:

1. Create a new script under the relevant subdirectory.
2. Call `check_env()` at the top.
3. Fetch data via `nerdgraph_query()` - never `httpx.post` directly.
4. Use `argparse` for CLI args.
5. Print one JSON object to stdout; route errors to stderr.
6. Add an entry to the decision guide and the "All Scripts" table in
   `SKILL.md`.

## Troubleshooting

- **"NEWRELIC_API_KEY environment variable is not set"**: your shell
  doesn't have the variable exported. See "Setup" above.
- **HTTP 401 / 403 from NerdGraph**: the API key is valid but doesn't
  have access to the account. Re-create a user key scoped to the
  correct account.
- **Empty `entities` array from `get_entity.py`**: the name didn't
  match. New Relic entity search is case-sensitive and does exact
  matching. Try the name as it appears in the New Relic UI.
