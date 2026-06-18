from typing import Any

import httpx

from .config import env
from .models import OpenWebUIAlert


def slack_payload(alert: OpenWebUIAlert) -> dict[str, Any]:
    user_summary = alert.user_email if alert.user_email != "unknown" else alert.user_name
    if user_summary == "unknown":
        user_summary = alert.user_id

    return {
        "text": f"{alert.subject}: {user_summary} locked out ({alert.reason})",
        "blocks": [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": alert.subject},
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Event:*\n{alert.event}"},
                    {"type": "mrkdwn", "text": f"*User:*\n{alert.user_name}"},
                    {"type": "mrkdwn", "text": f"*Email:*\n{alert.user_email}"},
                    {"type": "mrkdwn", "text": f"*User ID:*\n{alert.user_id}"},
                    {"type": "mrkdwn", "text": f"*Reason:*\n{alert.reason}"},
                    {"type": "mrkdwn", "text": f"*Timestamp:*\n{alert.timestamp}"},
                ],
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Content preview:*\n```{alert.content_preview}```"},
            },
        ],
    }


async def forward(alert: OpenWebUIAlert) -> bool:
    webhook_url = env("SLACK_WEBHOOK_URL")
    if not webhook_url:
        return False

    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(webhook_url, json=slack_payload(alert))
        response.raise_for_status()
    return True