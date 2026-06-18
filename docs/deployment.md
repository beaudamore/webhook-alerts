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
| `SLACK_WEBHOOK_URL` | No | Slack incoming webhook URL. Leave empty to disable Slack forwarding. |
| `GMAIL_CLIENT_ID` | No | Google OAuth client ID for Gmail API forwarding. |
| `GMAIL_CLIENT_SECRET` | No | Google OAuth client secret for Gmail API forwarding. |
| `GMAIL_REFRESH_TOKEN` | No | Google OAuth refresh token with Gmail send scope. |
| `GMAIL_FROM` | No | Sender address for Gmail messages. Gmail may ignore aliases not allowed by the account. |
| `GMAIL_TO` | No | Recipient address for Gmail forwarding. Leave empty to disable Gmail forwarding. |

Only define variables for integrations you want enabled.

## Simple Local Compose

From the repository root, the default Compose file pulls the published GHCR image:

```bash
docker compose up -d
```

For local development builds, use the simple build example instead:

From the repository root:

```bash
docker compose -f docs/simple-compose.yml up --build -d
```

The docs example builds the image locally from the parent directory.

Health check:

```bash
curl http://localhost:8080/health
```

## Portainer Stack

Use [portainer-stack.yml](portainer-stack.yml) in Portainer. It pulls an image instead of building locally.

Recommended Portainer stack variables:

```env
SLACK_WEBHOOK_URL=
GMAIL_CLIENT_ID=
GMAIL_CLIENT_SECRET=
GMAIL_REFRESH_TOKEN=
GMAIL_FROM=
GMAIL_TO=
```

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

## Gmail OAuth Setup

Gmail forwarding uses the Gmail API, not SMTP. Configure a Google OAuth client with a refresh token that can send mail for the Gmail account, then set `GMAIL_CLIENT_ID`, `GMAIL_CLIENT_SECRET`, `GMAIL_REFRESH_TOKEN`, `GMAIL_FROM`, and `GMAIL_TO`. Leave any of those empty to disable Gmail forwarding.

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
