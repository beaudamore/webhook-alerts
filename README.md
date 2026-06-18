# Webhook Alerts

Docker-deployable alert receiver for Open WebUI safety-filter webhooks.

This service receives the generic alert payload emitted by the prompt injection filter and forwards it to configured destinations. Provider-specific behavior belongs here, not in the Open WebUI filter.

Full deployment docs and ready-to-copy stack examples live in [docs](docs/):

- [docs/deployment.md](docs/deployment.md)
- [docs/simple-compose.yml](docs/simple-compose.yml)
- [docs/portainer-stack.yml](docs/portainer-stack.yml)

## Open WebUI Contract

The filter sends `POST /webhooks/openwebui/prompt-injection-lockout` with JSON:

```json
{
  "event": "prompt_injection_lockout",
  "subject": "Prompt injection lockout",
  "user_id": "user-id",
  "user_name": "User Name",
  "user_email": "user@example.com",
  "reason": "Attempted instruction override",
  "timestamp": "2026-06-18T12:34:56.000000+00:00",
  "content_preview": "Ignore previous instructions..."
}
```

## Integrations

Currently included:

- Slack incoming webhook forwarding
- SMTP email forwarding

Planned integrations can be added here without changing the Open WebUI filter:

- Google Workspace / Chat
- Microsoft Teams
- SIEM collectors
- Ticketing systems
- Additional generic outbound webhooks

## Code Layout

Provider-specific code is split by resource so integrations can be maintained independently:

```text
app/main.py          # FastAPI routes and integration orchestration
app/models.py        # Generic Open WebUI alert schema
app/config.py        # Environment variable helpers
app/formatting.py    # Shared human-readable alert formatting
app/slack.py         # Slack incoming webhook integration
app/email.py         # SMTP email integration
app/google_oauth.py  # Google OAuth / Workspace integration placeholder
```

Add new destinations as new files under `app/`, then call them from `app/main.py`.

## Configuration

Copy `.env.example` to `.env` for local Docker runs, or define these as Portainer stack variables.

```env
SLACK_WEBHOOK_URL=
ALERT_EMAIL_TO=
ALERT_EMAIL_FROM=openwebui-alerts@example.com
SMTP_HOST=
SMTP_PORT=25
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_STARTTLS=true
```

Only set the variables for integrations you want enabled. If `SLACK_WEBHOOK_URL` is empty, Slack forwarding is skipped. If `ALERT_EMAIL_TO` or `SMTP_HOST` is empty, email forwarding is skipped.

## Platform Support

The supported deployment path is Docker, which runs the same Linux container on Windows, macOS, and Linux hosts through Docker Desktop or Docker Engine. The GHCR workflow publishes multi-architecture Linux images for `linux/amd64` and `linux/arm64`.

Local Python testing also works on Windows, macOS, and Linux with Python 3.12 or newer.

## Docker Compose

For local development, build from the working tree:

```bash
docker compose up --build -d
```

There is also a copyable minimal example at [docs/simple-compose.yml](docs/simple-compose.yml).

For a server or Portainer stack that should pull a published GHCR image instead of building locally, use:

```bash
docker compose -f compose.ghcr.yml up -d
```

There is also a Portainer-focused stack example at [docs/portainer-stack.yml](docs/portainer-stack.yml).

The default image is `ghcr.io/beaudamore/webhook-alerts:latest`. Override it with `WEBHOOK_ALERTS_IMAGE` if you publish under a different owner or repository.

```env
WEBHOOK_ALERTS_IMAGE=ghcr.io/<owner>/<repo>:latest
```

The receiver listens on port `8080` by default.

## Publishing to GHCR

This repo includes [publish-ghcr.yml](.github/workflows/publish-ghcr.yml). After this folder is pushed as a GitHub repository, pushes to `main`, version tags, or manual workflow runs publish images to:

```text
ghcr.io/<owner>/<repo>:latest
ghcr.io/<owner>/<repo>:<branch-or-tag>
ghcr.io/<owner>/<repo>:sha-<commit>
```

For a repository named `beaudamore/webhook-alerts`, the default Compose image is already set to `ghcr.io/beaudamore/webhook-alerts:latest`.

## Local Python Testing

Create and use the local virtual environment.

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m compileall app
```

macOS / Linux:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m compileall app
```

The `.venv/` directory is ignored by git.

Point Open WebUI at it with an environment variable on the Open WebUI container:

```yaml
environment:
  PROMPT_INJECTION_WEBHOOK_URL: ${PROMPT_INJECTION_WEBHOOK_URL}
```

In Portainer, set `PROMPT_INJECTION_WEBHOOK_URL` to:

```text
http://webhook-alerts:8080/webhooks/openwebui/prompt-injection-lockout
```

Use the reachable service name/URL for your Docker network.

Then set the filter valves:

```yaml
enable_webhook_notifications: true
notification_webhook_url_env: "PROMPT_INJECTION_WEBHOOK_URL"
notification_webhook_subject: "Prompt injection lockout"
```

## Slack App Manifest

The Slack app manifest for the Security Alert Bot lives at [docs/slack-security-alert-bot-manifest.yaml](docs/slack-security-alert-bot-manifest.yaml).

Create the Slack app from the manifest, install it to the target channel, copy the generated incoming webhook URL, and set it as `SLACK_WEBHOOK_URL` in this service.

## Health Check

```bash
curl http://localhost:8080/health
```

## Test Event

```bash
curl -X POST http://localhost:8080/webhooks/openwebui/prompt-injection-lockout \
  -H "Content-Type: application/json" \
  -d '{"event":"prompt_injection_lockout","subject":"Prompt injection lockout","user_id":"u1","user_name":"Test User","user_email":"test@example.com","reason":"Test","timestamp":"2026-06-18T12:34:56Z","content_preview":"test content"}'
```
