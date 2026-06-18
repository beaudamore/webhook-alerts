import base64
from email.message import EmailMessage

import httpx

from .config import env
from .formatting import alert_text
from .models import OpenWebUIAlert


TOKEN_URL = "https://oauth2.googleapis.com/token"
GMAIL_SEND_URL = "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"


async def _access_token() -> str:
    client_id = env("GMAIL_CLIENT_ID")
    client_secret = env("GMAIL_CLIENT_SECRET")
    refresh_token = env("GMAIL_REFRESH_TOKEN")
    if not client_id or not client_secret or not refresh_token:
        return ""

    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(TOKEN_URL, data=data)
        response.raise_for_status()
        payload = response.json()
    return str(payload.get("access_token", ""))


def _raw_message(alert: OpenWebUIAlert) -> str:
    from_address = env("GMAIL_FROM")
    to_address = env("GMAIL_TO")

    message = EmailMessage()
    message["To"] = to_address
    if from_address:
        message["From"] = from_address
    message["Subject"] = alert.subject
    message.set_content(alert_text(alert))

    encoded = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
    return encoded.rstrip("=")


async def forward(alert: OpenWebUIAlert) -> bool:
    if not env("GMAIL_TO"):
        return False

    token = await _access_token()
    if not token:
        return False

    payload = {"raw": _raw_message(alert)}
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(GMAIL_SEND_URL, headers=headers, json=payload)
        response.raise_for_status()
    return True