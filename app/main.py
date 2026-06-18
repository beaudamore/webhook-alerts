from typing import Any

from fastapi import FastAPI

from . import email, google_oauth, slack
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
        if email.forward(alert):
            forwarded.append("email")
    except Exception as exc:
        errors["email"] = str(exc)

    try:
        if await google_oauth.forward(alert):
            forwarded.append("google_oauth")
    except Exception as exc:
        errors["google_oauth"] = str(exc)

    return {"ok": not errors, "forwarded": forwarded, "errors": errors}
