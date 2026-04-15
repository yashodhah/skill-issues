"""
common/nerdgraph.py

The single place in the skill where raw HTTP calls to New Relic happen.

Every other script in this skill must go through nerdgraph_query() for
its data access. This gives us one place to handle auth, retries,
error handling, and logging. Individual scripts must never build their
own HTTP client.
"""

import json
import sys

import httpx

from common.config import (
    NERDGRAPH_ENDPOINT,
    check_env,
    get_headers,
)


# Network timeout for a single NerdGraph request, in seconds.
# NerdGraph queries can occasionally be slow when fanning out across
# many entities, so we give them a generous budget.
_DEFAULT_TIMEOUT_SECONDS = 30.0


class NerdGraphError(Exception):
    """Raised when NerdGraph returns an HTTP or GraphQL error."""


def nerdgraph_query(query, variables=None):
    """
    Execute a NerdGraph query and return the parsed response body.

    Parameters
    ----------
    query : str
        The GraphQL query string.
    variables : dict, optional
        A dictionary of GraphQL variables. May be None.

    Returns
    -------
    dict
        The parsed JSON response body (specifically the "data" field
        of the NerdGraph response).

    Raises
    ------
    NerdGraphError
        If the HTTP request fails, or if the response body contains
        GraphQL errors. Details are printed to stderr before raising.
    """
    api_key, _account_id = check_env()
    headers = get_headers(api_key)

    payload = {"query": query}
    if variables is not None:
        payload["variables"] = variables

    try:
        with httpx.Client(timeout=_DEFAULT_TIMEOUT_SECONDS) as client:
            response = client.post(
                NERDGRAPH_ENDPOINT,
                headers=headers,
                content=json.dumps(payload),
            )
    except httpx.HTTPError as exc:
        print(
            "ERROR: HTTP request to NerdGraph failed: {0}".format(exc),
            file=sys.stderr,
        )
        raise NerdGraphError(str(exc))

    if response.status_code != 200:
        print(
            "ERROR: NerdGraph returned HTTP {0}: {1}".format(
                response.status_code, response.text
            ),
            file=sys.stderr,
        )
        raise NerdGraphError(
            "NerdGraph HTTP {0}".format(response.status_code)
        )

    try:
        body = response.json()
    except ValueError as exc:
        print(
            "ERROR: NerdGraph response was not valid JSON: {0}".format(exc),
            file=sys.stderr,
        )
        raise NerdGraphError("invalid JSON response")

    if "errors" in body and body["errors"]:
        print("ERROR: NerdGraph returned GraphQL errors:", file=sys.stderr)
        for err in body["errors"]:
            print("  - {0}".format(err), file=sys.stderr)
        raise NerdGraphError("GraphQL errors in response")

    return body.get("data", {})
