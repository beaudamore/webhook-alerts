# Deployment Guide

This service is intended to be deployable on Windows, macOS, and Linux hosts through Docker. The container itself runs Linux and is built from `python:3.12-slim`.

## Image Options

You can run the service in two ways:

1. Build locally from this repository.
2. Pull a published image from GHCR.

Use local builds while developing. Use the GHCR image for Portainer, servers, or repeatable production deployments.

## Environment Variables

| Variable | Required | Description |
| --- | --- | --- |
| `WEBHOOK_ALERTS_IMAGE` | No | Image used by the Portainer/GHCR stack. Defaults to `ghcr.io/beaudamore/webhook-alerts:latest`. |
| `SLACK_WEBHOOK_URL` | No | Slack incoming webhook URL. Leave empty to disable Slack forwarding. |
| `ALERT_EMAIL_TO` | No | Email recipient. Leave empty to disable email forwarding. |
| `ALERT_EMAIL_FROM` | No | Email sender. Defaults to `openwebui-alerts@example.com`. |
| `SMTP_HOST` | No | SMTP server host. Required only for email forwarding. |
| `SMTP_PORT` | No | SMTP port. Defaults to `25`. |
| `SMTP_USERNAME` | No | SMTP username. Leave empty for unauthenticated SMTP. |
| `SMTP_PASSWORD` | No | SMTP password. |
| `SMTP_STARTTLS` | No | Enable SMTP STARTTLS. Defaults to `true`. |

Only define variables for integrations you want enabled.

## Simple Local Compose

From the repository root:

```bash
docker compose -f docs/simple-compose.yml up --build -d
```

This stack builds the image locally from the parent directory.

Health check:

```bash
curl http://localhost:8080/health
```

## Portainer Stack

Use [portainer-stack.yml](portainer-stack.yml) in Portainer. It pulls an image instead of building locally.

Recommended Portainer stack variables:

```env
WEBHOOK_ALERTS_IMAGE=ghcr.io/beaudamore/webhook-alerts:latest
SLACK_WEBHOOK_URL=
ALERT_EMAIL_TO=
ALERT_EMAIL_FROM=openwebui-alerts@example.com
SMTP_HOST=
SMTP_PORT=25
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_STARTTLS=true
```

If you publish this repository under a different GitHub owner or repo, change `WEBHOOK_ALERTS_IMAGE` accordingly.

## Open WebUI Wiring

Set this environment variable on the Open WebUI container:

```yaml
environment:
  PROMPT_INJECTION_WEBHOOK_URL: ${PROMPT_INJECTION_WEBHOOK_URL}
```

If both containers are in the same Docker network and the webhook service is named `webhook-alerts`, set the value to:

```text
http://webhook-alerts:8080/webhooks/openwebui/prompt-injection-lockout
```

Then configure the prompt injection filter valves:

```yaml
enable_webhook_notifications: true
notification_webhook_url_env: "PROMPT_INJECTION_WEBHOOK_URL"
notification_webhook_subject: "Prompt injection lockout"
```

The valve stores the environment variable name, not the receiver URL.

## Test Payload

```bash
curl -X POST http://localhost:8080/webhooks/openwebui/prompt-injection-lockout \
  -H "Content-Type: application/json" \
  -d '{"event":"prompt_injection_lockout","subject":"Prompt injection lockout","user_id":"u1","user_name":"Test User","user_email":"test@example.com","reason":"Test","timestamp":"2026-06-18T12:34:56Z","content_preview":"test content"}'
```

Expected response shape:

```json
{
  "ok": true,
  "forwarded": ["slack"],
  "errors": {}
}
```

If no integrations are configured, `forwarded` is empty and `ok` remains `true`.

## Slack Setup

Use [slack-security-alert-bot-manifest.yaml](slack-security-alert-bot-manifest.yaml) to create the Slack app. After installing the app to a channel, copy the generated incoming webhook URL into `SLACK_WEBHOOK_URL` for this service.

## Publishing to GHCR

The GitHub Actions workflow at `../.github/workflows/publish-ghcr.yml` publishes multi-architecture images for:

- `linux/amd64`
- `linux/arm64`

Images are published to:

```text
ghcr.io/<owner>/<repo>:latest
ghcr.io/<owner>/<repo>:<branch-or-tag>
ghcr.io/<owner>/<repo>:sha-<commit>
```
