"""
health/get_golden_metrics.py

Return the current values of a service's golden metrics.

New Relic defines a small set of "golden metrics" per entity type
(for APM services these are typically throughput, error rate, response
time, and apdex). This script first asks NerdGraph for the metric
definitions for a given entity, then executes each metric's NRQL query
to retrieve its current value.

NerdGraph query used to discover the metrics:

    {
      actor {
        entity(guid: "<GUID>") {
          goldenMetrics {
            metrics { name query unit title }
          }
        }
      }
    }

The NRQL returned by the API is then executed against the entity's
account via the standard nrql endpoint.

Usage:
    python health/get_golden_metrics.py --entity-guid <GUID>
"""

import argparse
import json
import os
import sys

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


def _first_numeric_value(results):
    """
    Extract the first numeric value from an NRQL results array.

    NRQL results look like [{"average.duration": 12.3}]. We don't know
    the key up front because it depends on the query, so we return the
    first numeric value we find.
    """
    if not results:
        return None
    first = results[0]
    if not isinstance(first, dict):
        return None
    for value in first.values():
        if isinstance(value, (int, float)):
            return value
    return None


def get_golden_metrics(entity_guid, account_id):
    """
    Return a list of current golden metric values for an entity.

    Parameters
    ----------
    entity_guid : str
        Entity guid.
    account_id : str
        Numeric account id (as a string) to execute the NRQL queries
        against.

    Returns
    -------
    list of dict
        [{ "name", "title", "unit", "query", "value" }]
        If a metric could not be evaluated, "value" is None.
    """
    safe_guid = entity_guid.replace('"', '\\"')
    data = nerdgraph_query(_GOLDEN_METRICS_QUERY % safe_guid)

    try:
        metrics = data["actor"]["entity"]["goldenMetrics"]["metrics"]
    except (KeyError, TypeError):
        metrics = []

    output = []
    for metric in metrics or []:
        nrql = metric.get("query") or ""
        # The NRQL returned by goldenMetrics already contains the
        # correct entity scope, so we just execute it. Escape quotes
        # for embedding inside a GraphQL string.
        escaped_nrql = nrql.replace("\\", "\\\\").replace('"', '\\"')
        value = None
        try:
            nrql_data = nerdgraph_query(_NRQL_QUERY % (account_id, escaped_nrql))
            results = nrql_data["actor"]["account"]["nrql"]["results"]
            value = _first_numeric_value(results)
        except Exception as exc:
            print(
                "WARN: failed to evaluate golden metric '{0}': {1}".format(
                    metric.get("name"), exc
                ),
                file=sys.stderr,
            )

        output.append(
            {
                "name": metric.get("name"),
                "title": metric.get("title"),
                "unit": metric.get("unit"),
                "query": nrql,
                "value": value,
            }
        )

    return output


def main():
    _api_key, account_id = check_env()
    parser = argparse.ArgumentParser(
        description="Return current golden metric values for an entity."
    )
    parser.add_argument("--entity-guid", required=True)
    args = parser.parse_args()

    metrics = get_golden_metrics(args.entity_guid, account_id)
    print(json.dumps(metrics, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
