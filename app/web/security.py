"""Validation of Telegram WebApp initData.

Spec: https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app

The data-check string is "auth_date=...\\nquery_id=...\\nuser=..." (sorted by key,
newline-joined), then HMAC-SHA256 signed with a secret_key derived as
HMAC-SHA256("WebAppData", bot_token). We recompute and compare with the received hash.
"""
import hashlib
import hmac
import json
from urllib.parse import unquote, parse_qsl


def _secret_key(bot_token: str) -> bytes:
    return hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()


def validate_init_data(init_data: str, bot_token: str) -> dict | None:
    """Validate Telegram initData and return parsed fields (incl. user), or None if invalid."""
    if not init_data or not bot_token:
        return None

    try:
        pairs = dict(parse_qsl(init_data, keep_blank_values=True))
    except Exception:
        return None

    received_hash = pairs.pop("hash", None)
    if not received_hash:
        return None

    # Build the data-check string: sorted by key, joined with newlines
    data_check = "\n".join(f"{k}={v}" for k, v in sorted(pairs.items()))

    secret = _secret_key(bot_token)
    computed = hmac.new(secret, data_check.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(computed, received_hash):
        return None

    # Parse the user object
    user_raw = pairs.get("user")
    user = None
    if user_raw:
        try:
            user = json.loads(unquote(user_raw))
        except Exception:
            user = None

    return {
        "query_id": pairs.get("query_id"),
        "user": user,
        "auth_date": pairs.get("auth_date"),
        "start_param": pairs.get("start_param"),
    }
