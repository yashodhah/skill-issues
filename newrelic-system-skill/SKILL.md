---
name: newrelic-system-intelligence
description: >
  Use this skill when an AI agent needs to understand a distributed system at runtime.
  Covers: service dependency mapping, latency analysis per hop, change impact assessment,
  active incident investigation, SLO compliance, and error analysis.

  Invoke this skill for questions like:
  - "what does service X depend on?"
  - "where is the latency in this request chain?"
  - "what did this deploy break?"
  - "what is currently alerting?"
  - "is it safe to deploy right now?"
  - "who calls this service?"

  Do NOT use for: code review, writing code, static analysis, git operations.

language: python3
platform: macOS | Windows | Linux
requires:
  env:
    - NEWRELIC_API_KEY        # from https://one.newrelic.com/api-keys
    - NEWRELIC_ACCOUNT_ID     # numeric, from account settings
  install: pip install -r requirements.txt

outputs: json
trust_level: HIGH
---

# New Relic System Intelligence Skill

A reusable skill that gives an AI agent a holistic, trustworthy picture
of a distributed system at runtime, using New Relic as the source of
truth. All scripts are pure Python 3.8+ and output JSON to stdout.

## 1. Quick Start

### Set environment variables

macOS/Linux (bash/zsh):

```
export NEWRELIC_API_KEY="your_api_key_here"
export NEWRELIC_ACCOUNT_ID="your_account_id_here"
```

Windows (Command Prompt):

```
set NEWRELIC_API_KEY=your_api_key_here
set NEWRELIC_ACCOUNT_ID=your_account_id_here
```

Windows (PowerShell):

```
$env:NEWRELIC_API_KEY="your_api_key_here"
$env:NEWRELIC_ACCOUNT_ID="your_account_id_here"
```

Get your API key at https://one.newrelic.com/api-keys. Find your
numeric account ID under the user menu in the same UI.

### Install dependencies

```
pip install -r requirements.txt
```

The only runtime dependency is `httpx==0.27.0`.

### Run your first query

```
python compose/system_snapshot.py --service-name payment-service
```

## 2. Decision Guide

Pick the right script based on what the agent is trying to learn:

| Question the agent has                               | Script to run                                |
|------------------------------------------------------|----------------------------------------------|
| "Does this service exist? What's its guid?"          | topology/get_entity.py                       |
| "What does service X directly call / get called by?" | topology/get_relationships.py                |
| "Show me the full dependency graph around X"         | topology/get_full_map.py                     |
| "Which workloads contain this service?"              | topology/get_workloads.py                    |
| "What are the current golden metric values?"         | health/get_golden_metrics.py                 |
| "What incidents are open right now?"                 | health/get_open_alerts.py                    |
| "What's the SLO status of this service?"             | health/get_service_levels.py                 |
| "What errors are happening right now?"               | health/get_error_groups.py                   |
| "What are the slowest recent traces?"                | traces/get_recent_traces.py                  |
| "Where is the latency going in this service?"        | traces/get_latency_breakdown.py              |
| "Was there a recent deployment?"                     | changes/get_recent_deployments.py            |
| "Did the last deploy degrade anything?"              | changes/get_change_impact.py                 |
| "Run an arbitrary NRQL query"                        | query/nrql.py                                |
| "Give me a full health snapshot of service X"        | compose/system_snapshot.py                   |
| "Service X is on fire, what do I look at first?"     | compose/incident_context.py                  |

## 3. Primary Entry Points

Most agents should start with one of the two compose scripts. They
take only `--service-name` and return a single JSON document that
answers the common questions for that workflow.

### compose/system_snapshot.py

Returns a unified "state of the service" document. Use this when the
agent needs to understand a service's current health, dependencies,
and recent changes without first knowing what to look at.

```
python compose/system_snapshot.py --service-name payment-service
```

Under the hood this script imports and invokes the core functions
from topology, health, and changes modules. It does NOT shell out.

### compose/incident_context.py

Returns a unified "what is broken and why" document focused on the
blast radius of an incident. Use this when a service is already known
to be alerting or suspected to be unhealthy.

```
python compose/incident_context.py --service-name payment-service
```

This walks a depth-2 dependency graph, checks every node for open
alerts, pulls latency breakdowns, and (if a recent deploy exists)
computes the before/after change impact.

## 4. Output Schemas

### compose/system_snapshot.py

```
{
  "service": {
    "guid": "<string>",
    "name": "<string>",
    "entityType": "<string>",
    "tags": [ { "key": "<string>", "values": ["<string>"] } ]
  },
  "dependencies": {
    "calls":     [ { "guid", "name", "entityType", "alertSeverity" } ],
    "called_by": [ { "guid", "name", "entityType", "alertSeverity" } ]
  },
  "health": {
    "golden_metrics": [
      { "name", "title", "unit", "query", "value" }
    ],
    "open_alerts": [
      { "issueId", "title", "priority", "state", "entityGuids", "openedAt" }
    ],
    "slo": {
      "target":     <number or null>,
      "compliance": <number or null>,
      "burn_rate":  <number or null>,
      "status":     "OK" | "AT_RISK" | "BREACHED" | "UNKNOWN"
    }
  },
  "recent_changes": [
    { "version", "timestamp", "changelog", "user", "entityGuid" }
  ],
  "snapshot_time": "<ISO 8601 timestamp>"
}
```

### compose/incident_context.py

```
{
  "service": {
    "guid": "<string>",
    "name": "<string>"
  },
  "active_incidents": [
    { "issueId", "title", "priority", "state", "entityGuids", "openedAt" }
  ],
  "dependency_graph": {
    "nodes": [ { "guid", "name", "entityType", "alertSeverity" } ],
    "edges": [ { "from", "to", "type" } ]
  },
  "latency_breakdown": [
    { "span_name", "avg_duration_ms", "p95_duration_ms" }
  ],
  "recent_changes": [
    { "version", "timestamp", "changelog", "user", "entityGuid" }
  ],
  "change_impact": [
    {
      "metric_name",
      "before_value",
      "after_value",
      "delta",
      "delta_percent",
      "status":  "IMPROVED" | "DEGRADED" | "STABLE" | "UNKNOWN"
    }
  ]
}
```

## 5. All Scripts

| Script path                              | Description                                                   | Key args                                           |
|------------------------------------------|---------------------------------------------------------------|----------------------------------------------------|
| topology/get_entity.py                   | Resolve a service name to a New Relic entity (guid, tags)     | --service-name                                     |
| topology/get_relationships.py            | Direct upstream (called_by) and downstream (calls) entities   | --entity-guid                                      |
| topology/get_full_map.py                 | BFS dependency graph up to N hops                             | --entity-guid, --depth                             |
| topology/get_workloads.py                | List New Relic Workloads in the account                       | --workload-name (optional)                         |
| health/get_golden_metrics.py             | Current values of an entity's golden metrics                  | --entity-guid                                      |
| health/get_open_alerts.py                | Currently-open AI-correlated issues                           | --entity-guid (optional)                           |
| health/get_service_levels.py             | SLI/SLO definitions and status                                | --entity-guid                                      |
| health/get_error_groups.py               | Top error classes/messages for a service                      | --entity-guid, --since                             |
| traces/get_recent_traces.py              | Recent root spans, slowest first                              | --service-name, --since                            |
| traces/get_latency_breakdown.py          | Per-span avg/p95 latency, sorted by avg                       | --service-name, --since                            |
| changes/get_recent_deployments.py        | Deployment records from change tracking                       | --entity-guid, --since                             |
| changes/get_change_impact.py             | Before/after golden-metric comparison for a deploy            | --entity-guid, --deployment-time                   |
| query/nrql.py                            | Execute an arbitrary NRQL query                               | --query, --account-id (optional)                   |
| compose/system_snapshot.py               | Unified "state of the service" snapshot                       | --service-name                                     |
| compose/incident_context.py              | Unified "what is broken and why" incident document            | --service-name                                     |

## 6. Example Invocations

### 1. "What does payment-service depend on at runtime?"

```
python topology/get_full_map.py --entity-guid <GUID> --depth 2
```

### 2. "Is payment-service healthy right now?"

```
python compose/system_snapshot.py --service-name payment-service
```

### 3. "We just deployed payment-service, did anything break?"

```
python changes/get_change_impact.py --entity-guid <GUID> --deployment-time 2024-01-15T14:30:00Z
```

### 4. "Where is the latency in the checkout flow?"

```
python traces/get_latency_breakdown.py --service-name checkout-service
```

### 5. "Payment-service is alerting, what do I look at first?"

```
python compose/incident_context.py --service-name payment-service
```

## Notes for Agents

- Every script prints exactly one JSON object to stdout and exits 0 on
  success. Errors and progress messages go to stderr.
- All configuration comes from `NEWRELIC_API_KEY` and
  `NEWRELIC_ACCOUNT_ID`. No credentials or account IDs are hardcoded.
- All HTTP traffic flows through `common/nerdgraph.py`. Individual
  scripts never build their own HTTP client.
- Compose scripts never shell out; they import sibling modules
  directly and run everything in-process.
