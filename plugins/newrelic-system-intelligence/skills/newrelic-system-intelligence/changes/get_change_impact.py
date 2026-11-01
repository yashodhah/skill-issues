"""
changes/get_change_impact.py

Compare golden metrics for an entity in the 30 minutes BEFORE and the
30 minutes AFTER a specific deployment time, and classify each metric
as IMPROVED, DEGRADED, or STABLE. This is the backbone of "did the
deploy break anything?" analysis.

The script discovers golden metric NRQL via the same NerdGraph
goldenMetrics API used elsewhere, then runs each query twice - once
with a SINCE/UNTIL window before the deployment, once with a window
after. The deltas are returned with a simple status.

Usage:
    python changes/get_change_impact.py \\
        --entity-guid <GUID> \\
        --deployment-time 2024-01-15T14:30:00Z
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from common.config import check_env  # noqa: E402
from common.nerdgraph import nerdgraph_query  # noqa: E402


_GOLDEN_METRICS_QUERY = """
{
  actor {
    entity(guid: "%s") {
      goldenMetrics {
        metrics {
          name
          query
          unit
          title
        }
      }
    }
  }
}
"""


_NRQL_QUERY = """
{
  actor {
    account(id: %s) {
      nrql(query: "%s") {
        results
      }
    }
  }
}
"""


# Metrics where higher is "better"; lower is degraded. Anything not
# listed here is treated as "lower is better" (latency, error rate,
# etc).
_HIGHER_IS_BETTER = {"throughput", "apdex"}

# Metrics where a higher value is unambiguously worse.
_LOWER_IS_BETTER = {"response_time", "errorRate", "latency", "responseTimeMs"}


def _parse_iso(ts):
    """
    Parse an ISO-8601 timestamp string. Accepts a trailing 'Z' for UTC.
    """
    if ts.endswith("Z"):
        ts = ts[:-1] + "+00:00"
    return datetime.fromisoformat(ts)


def _first_numeric(results):
    if not results:
        return None
    first = results[0]
    if not isinstance(first, dict):
        return None
    for value in first.values():
        if isinstance(value, (int, float)):
            return value
    return None


def _strip_since(nrql):
    """
    Remove any existing SINCE/UNTIL clause from an NRQL query so we
    can substitute our own time window.
    """
    upper = nrql.upper()
    for marker in (" SINCE ", " UNTIL "):
        idx = upper.find(marker)
        if idx != -1:
            nrql = nrql[:idx]
            upper = nrql.upper()
    return nrql.strip()


def _run_nrql(nrql, account_id):
    escaped = nrql.replace("\\", "\\\\").replace('"', '\\"')
    data = nerdgraph_query(_NRQL_QUERY % (account_id, escaped))
    try:
        return data["actor"]["account"]["nrql"]["results"] or []
    except (KeyError, TypeError):
        return []


def _classify(name, delta_percent, lower_is_better_default=True):
    """
    Classify a metric change as IMPROVED / DEGRADED / STABLE.

    delta_percent of <= 5% absolute is considered STABLE.
    """
    if delta_percent is None:
        return "UNKNOWN"
    if abs(delta_percent) <= 5.0:
        return "STABLE"

    name_lower = (name or "").lower()
    higher_better = any(key in name_lower for key in _HIGHER_IS_BETTER)
    lower_better = any(key in name_lower for key in _LOWER_IS_BETTER)

    if not higher_better and not lower_better:
        # Fall back to a conservative default: assume lower is better
        # for unknown metrics (since latency/error is the common case).
        lower_better = lower_is_better_default

    improved = False
    if higher_better and delta_percent > 0:
        improved = True
    if lower_better and delta_percent < 0:
        improved = True

    return "IMPROVED" if improved else "DEGRADED"


def get_change_impact(entity_guid, deployment_time, account_id, window_minutes=30):
    """
    Compare golden metrics before and after a deployment.

    Parameters
    ----------
    entity_guid : str
    deployment_time : str
        ISO-8601 timestamp of the deployment. 'Z' suffix accepted.
    account_id : str
    window_minutes : int
        Size of the before/after comparison window on each side.

    Returns
    -------
    list of dict
        [{ "metric_name", "before_value", "after_value", "delta",
           "delta_percent", "status" }]
    """
    deploy_dt = _parse_iso(deployment_time)
    before_start = deploy_dt - timedelta(minutes=window_minutes)
    after_end = deploy_dt + timedelta(minutes=window_minutes)

    # NRQL SINCE/UNTIL accept ISO-8601 with single quotes.
    def _fmt(dt):
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    before_window = "SINCE '{0}' UNTIL '{1}'".format(_fmt(before_start), _fmt(deploy_dt))
    after_window = "SINCE '{0}' UNTIL '{1}'".format(_fmt(deploy_dt), _fmt(after_end))

    safe_guid = entity_guid.replace('"', '\\"')
    data = nerdgraph_query(_GOLDEN_METRICS_QUERY % safe_guid)
    try:
        metrics = data["actor"]["entity"]["goldenMetrics"]["metrics"] or []
    except (KeyError, TypeError):
        metrics = []

    out = []
    for metric in metrics:
        base = _strip_since(metric.get("query") or "")
        if not base:
            continue

        before_nrql = "{0} {1}".format(base, before_window)
        after_nrql = "{0} {1}".format(base, after_window)

        try:
            before_value = _first_numeric(_run_nrql(before_nrql, account_id))
            after_value = _first_numeric(_run_nrql(after_nrql, account_id))
        except Exception as exc:
            print(
                "WARN: failed to evaluate metric {0}: {1}".format(
                    metric.get("name"), exc
                ),
                file=sys.stderr,
            )
            before_value = None
            after_value = None

        delta = None
        delta_percent = None
        if before_value is not None and after_value is not None:
            delta = after_value - before_value
            if before_value != 0:
                delta_percent = (delta / before_value) * 100.0
            elif after_value == 0:
                delta_percent = 0.0
            else:
                delta_percent = None

        out.append(
            {
                "metric_name": metric.get("name"),
                "before_value": before_value,
                "after_value": after_value,
                "delta": delta,
                "delta_percent": delta_percent,
                "status": _classify(metric.get("name"), delta_percent),
            }
        )

    return out


def main():
    _api_key, account_id = check_env()
    parser = argparse.ArgumentParser(
        description="Compare golden metrics before and after a deployment."
    )
    parser.add_argument("--entity-guid", required=True)
    parser.add_argument("--deployment-time", required=True)
    args = parser.parse_args()

    impact = get_change_impact(args.entity_guid, args.deployment_time, account_id)
    print(json.dumps(impact, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
