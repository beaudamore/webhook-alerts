from typing import Any

from fastapi import FastAPI

from . import gmail_oauth, slack
from .models import OpenWebUIAlert


app = FastAPI(title="Open WebUI Webhook Alerts")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/webhooks/openwebui/prompt-injection-lockout")
async def openwebui_prompt_injection_lockout(alert: OpenWebUIAlert) -> dict[str, Any]:
    forwarded: list[str] = []
    errors: dict[str, str] = {}

    try:
        if await slack.forward(alert):
            forwarded.append("slack")
    except Exception as exc:
        errors["slack"] = str(exc)

    try:
        if await gmail_oauth.forward(alert):
            forwarded.append("gmail_oauth")
    except Exception as exc:
        errors["gmail_oauth"] = str(exc)

    return {"ok": not errors, "forwarded": forwarded, "errors": errors}
