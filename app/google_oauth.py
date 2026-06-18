from .models import OpenWebUIAlert


async def forward(alert: OpenWebUIAlert) -> bool:
    _ = alert
    # Placeholder for Google Workspace / Chat integration.
    # Keep Google OAuth credentials, scopes, refresh, and API-specific payloads here.
    return False