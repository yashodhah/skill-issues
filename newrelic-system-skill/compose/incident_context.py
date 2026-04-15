"""
compose/incident_context.py

Build a single unified JSON document that answers "what is broken
and why?" for a given service. This is the primary entry point for
incident response and firefight workflows.

Combines:

    1. topology/get_entity          -> resolve service name
    2. topology/get_full_map        -> depth-2 dependency graph
    3. health/get_open_alerts       -> active incidents on the graph
    4. traces/get_latency_breakdown -> where the time is going right now
    5. changes/get_recent_deploys   -> recent change history
    6. changes/get_change_impact    -> before/after metric comparison
                                        (only when a recent deploy was found)

Imports core functions directly. Never shells out.

Usage:
    python compose/incident_context.py --service-name payment-service
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from common.config import check_env  # noqa: E402
from topology.get_entity import get_entity  # noqa: E402
from topology.get_full_map import get_full_map  # noqa: E402
from health.get_open_alerts import get_open_alerts  # noqa: E402
from traces.get_latency_breakdown import get_latency_breakdown  # noqa: E402
from changes.get_recent_deployments import get_recent_deployments  # noqa: E402
from changes.get_change_impact import get_change_impact  # noqa: E402


def _ts_ms_to_iso(ts_ms):
    """
    Convert an epoch-ms integer (as returned by NerdGraph deployment
    records) to an ISO-8601 UTC timestamp. Returns None if the input
    is falsy or not parseable.
    """
    if not ts_ms:
        return None
    try:
        dt = datetime.fromtimestamp(float(ts_ms) / 1000.0, tz=timezone.utc)
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    except (ValueError, OSError, OverflowError):
        return None


def _safe_call(label, fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except Exception as exc:
        print(
            "WARN: {0} failed: {1}".format(label, exc),
            file=sys.stderr,
        )
        return None


def build_incident_context(service_name, account_id):
    """
    Build the incident context dict for a service.
    """
    entity = get_entity(service_name)
    if entity is None:
        print(
            "ERROR: Could not resolve service-name='{0}' to a New Relic entity.".format(
                service_name
            ),
            file=sys.stderr,
        )
        sys.exit(1)

    guid = entity["guid"]

    graph = _safe_call(
        "get_full_map", get_full_map, guid, 2
    ) or {"root": guid, "depth": 2, "nodes": [], "edges": []}

    # Gather alerts across every node in the graph so agents can see
    # if a dependency is the actual source of the incident.
    all_alerts = []
    seen_alert_ids = set()
    node_guids = [n.get("guid") for n in graph.get("nodes", []) if n.get("guid")]
    if guid not in node_guids:
        node_guids.append(guid)
    for node_guid in node_guids:
        node_alerts = _safe_call(
            "get_open_alerts", get_open_alerts, account_id, node_guid
        ) or []
        for issue in node_alerts:
            issue_id = issue.get("issueId")
            if issue_id in seen_alert_ids:
                continue
            seen_alert_ids.add(issue_id)
            all_alerts.append(issue)

    latency = _safe_call(
        "get_latency_breakdown",
        get_latency_breakdown,
        service_name,
        account_id,
    ) or []

    recent_changes = _safe_call(
        "get_recent_deployments", get_recent_deployments, guid
    ) or []

    change_impact = []
    if recent_changes:
        most_recent = recent_changes[0]
        deploy_iso = _ts_ms_to_iso(most_recent.get("timestamp"))
        if deploy_iso:
            change_impact = _safe_call(
                "get_change_impact",
                get_change_impact,
                guid,
                deploy_iso,
                account_id,
            ) or []

    return {
        "service": {
            "guid": entity.get("guid"),
            "name": entity.get("name"),
        },
        "active_incidents": all_alerts,
        "dependency_graph": {
            "nodes": graph.get("nodes", []),
            "edges": graph.get("edges", []),
        },
        "latency_breakdown": latency,
        "recent_changes": recent_changes,
        "change_impact": change_impact,
    }


def main():
    _api_key, account_id = check_env()
    parser = argparse.ArgumentParser(
        description="Produce an incident-context JSON for a service."
    )
    parser.add_argument("--service-name", required=True)
    args = parser.parse_args()

    context = build_incident_context(args.service_name, account_id)
    print(json.dumps(context, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
