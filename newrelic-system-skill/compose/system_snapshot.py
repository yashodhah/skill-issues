"""
compose/system_snapshot.py

Build a single unified JSON snapshot of a service's current state.
This is the primary entry point for questions like "how is service X
doing?". It combines:

    1. topology/get_entity         -> resolve service name to guid
    2. topology/get_relationships  -> direct upstream / downstream deps
    3. health/get_golden_metrics   -> current metric values
    4. health/get_open_alerts      -> currently-open incidents
    5. changes/get_recent_deploys  -> recent deployment history

The script imports the core functions from each module directly. It
does NOT shell out - everything runs in-process.

Usage:
    python compose/system_snapshot.py --service-name payment-service
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
from topology.get_relationships import get_relationships  # noqa: E402
from health.get_golden_metrics import get_golden_metrics  # noqa: E402
from health.get_open_alerts import get_open_alerts  # noqa: E402
from health.get_service_levels import get_service_levels  # noqa: E402
from changes.get_recent_deployments import get_recent_deployments  # noqa: E402


def _now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _safe_call(label, fn, *args, **kwargs):
    """
    Run a data-fetching function and return its result, or a
    sentinel on failure so that one broken upstream doesn't sink
    the entire snapshot.
    """
    try:
        return fn(*args, **kwargs)
    except Exception as exc:
        print(
            "WARN: {0} failed: {1}".format(label, exc),
            file=sys.stderr,
        )
        return None


def build_snapshot(service_name, account_id):
    """
    Build a snapshot dict for the given service.

    Parameters
    ----------
    service_name : str
    account_id : str

    Returns
    -------
    dict
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

    relationships = _safe_call(
        "get_relationships", get_relationships, guid
    ) or {"calls": [], "called_by": []}
    golden_metrics = _safe_call(
        "get_golden_metrics", get_golden_metrics, guid, account_id
    ) or []
    open_alerts = _safe_call(
        "get_open_alerts", get_open_alerts, account_id, guid
    ) or []
    service_levels = _safe_call(
        "get_service_levels", get_service_levels, guid
    ) or []
    recent_changes = _safe_call(
        "get_recent_deployments", get_recent_deployments, guid
    ) or []

    # Reduce SLO list down to a single summary object to match the
    # output schema. If there are multiple SLIs we report the worst.
    slo_summary = {
        "target": None,
        "compliance": None,
        "burn_rate": None,
        "status": "UNKNOWN",
    }
    if service_levels:
        worst = service_levels[0]
        order = {"BREACHED": 3, "AT_RISK": 2, "UNKNOWN": 1, "OK": 0}
        for sli in service_levels:
            if order.get(sli.get("status"), 0) > order.get(worst.get("status"), 0):
                worst = sli
        slo_summary = {
            "target": worst.get("sloTarget"),
            "compliance": worst.get("compliance"),
            "burn_rate": worst.get("burnRate"),
            "status": worst.get("status"),
        }

    return {
        "service": {
            "guid": entity.get("guid"),
            "name": entity.get("name"),
            "entityType": entity.get("entityType"),
            "tags": entity.get("tags", []),
        },
        "dependencies": {
            "calls": relationships.get("calls", []),
            "called_by": relationships.get("called_by", []),
        },
        "health": {
            "golden_metrics": golden_metrics,
            "open_alerts": open_alerts,
            "slo": slo_summary,
        },
        "recent_changes": recent_changes,
        "snapshot_time": _now_iso(),
    }


def main():
    _api_key, account_id = check_env()
    parser = argparse.ArgumentParser(
        description="Produce a unified JSON snapshot of a service."
    )
    parser.add_argument("--service-name", required=True)
    args = parser.parse_args()

    snapshot = build_snapshot(args.service_name, account_id)
    print(json.dumps(snapshot, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
