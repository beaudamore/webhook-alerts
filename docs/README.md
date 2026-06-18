# Webhook Alerts Documentation

This folder contains deployment and integration documentation for the Open WebUI webhook alert receiver.

## Files

- [deployment.md](deployment.md) - Docker, GHCR, Portainer, and Open WebUI wiring guide.
- [simple-compose.yml](simple-compose.yml) - Minimal local Compose file that builds from this repo.
- [portainer-stack.yml](portainer-stack.yml) - Portainer-friendly stack that pulls the GHCR image.
- [slack-security-alert-bot-manifest.yaml](slack-security-alert-bot-manifest.yaml) - Slack app manifest for creating the Security Alert Bot.

## Runtime Contract

Open WebUI sends one generic JSON event to this receiver. Integrations such as Slack, Gmail OAuth, Teams, SIEM, and ticketing systems are implemented here rather than inside the Open WebUI filter.
