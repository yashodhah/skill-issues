"""
common/config.py

Centralised configuration and environment validation for the
newrelic-system-intelligence skill.

Every script in this skill imports check_env() from here and calls it
at startup BEFORE doing any work. All configuration (API key and
account ID) comes exclusively from environment variables. No script
in this skill is allowed to hardcode credentials, account IDs, or
service names.
"""

import os
import sys


# Public constants used by every other module.
NERDGRAPH_ENDPOINT = "https://api.newrelic.com/graphql"
REST_ENDPOINT = "https://api.newrelic.com/v2"


_API_KEY_ERROR = (
    "ERROR: NEWRELIC_API_KEY environment variable is not set.\n"
    "Please set it before running this skill:\n"
    "\n"
    "  macOS/Linux:  export NEWRELIC_API_KEY=\"your_api_key_here\"\n"
    "  Windows CMD:  set NEWRELIC_API_KEY=your_api_key_here\n"
    "  Windows PS:   $env:NEWRELIC_API_KEY=\"your_api_key_here\"\n"
    "\n"
    "Get your API key at: https://one.newrelic.com/api-keys"
)

_ACCOUNT_ID_ERROR = (
    "ERROR: NEWRELIC_ACCOUNT_ID environment variable is not set.\n"
    "Please set it before running this skill:\n"
    "\n"
    "  macOS/Linux:  export NEWRELIC_ACCOUNT_ID=\"your_account_id_here\"\n"
    "  Windows CMD:  set NEWRELIC_ACCOUNT_ID=your_account_id_here\n"
    "  Windows PS:   $env:NEWRELIC_ACCOUNT_ID=\"your_account_id_here\"\n"
    "\n"
    "Find your Account ID at: https://one.newrelic.com > (user menu) > API Keys"
)


def check_env():
    """
    Validate that the required environment variables are set.

    Returns
    -------
    tuple(str, str)
        (api_key, account_id)

    Exits
    -----
    On missing variables, prints a platform-aware setup message to
    stderr and exits with code 1.
    """
    api_key = os.environ.get("NEWRELIC_API_KEY")
    if not api_key:
        print(_API_KEY_ERROR, file=sys.stderr)
        sys.exit(1)

    account_id = os.environ.get("NEWRELIC_ACCOUNT_ID")
    if not account_id:
        print(_ACCOUNT_ID_ERROR, file=sys.stderr)
        sys.exit(1)

    return api_key, account_id


def get_headers(api_key):
    """
    Build the HTTP headers used for every New Relic API call.

    Parameters
    ----------
    api_key : str
        The user API key returned by check_env().

    Returns
    -------
    dict
        A headers dict suitable for httpx or requests.
    """
    return {
        "API-Key": api_key,
        "Content-Type": "application/json",
    }
