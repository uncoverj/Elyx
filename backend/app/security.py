import hashlib
import hmac
import json
from urllib.parse import parse_qsl

from fastapi import HTTPException, status

from app.config import get_settings


def _build_data_check_string(init_data: str) -> tuple[str, str]:
    items = dict(parse_qsl(init_data, keep_blank_values=True))
    received_hash = items.pop("hash", "")
    data_check = "\n".join(f"{k}={v}" for k, v in sorted(items.items()))
    return data_check, received_hash


def validate_tg_init_data(init_data: str) -> int:
    settings = get_settings()
    data_check, received_hash = _build_data_check_string(init_data)
    secret = hmac.new(b"WebAppData", settings.bot_token.encode(), hashlib.sha256).digest()
    calculated = hmac.new(secret, data_check.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(calculated, received_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid initData")

    payload = dict(parse_qsl(init_data, keep_blank_values=True))
    user = json.loads(payload.get("user", "{}"))
    tg_id = user.get("id")
    if not tg_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing user")
    return int(tg_id)
