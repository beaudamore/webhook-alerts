from .models import OpenWebUIAlert


def alert_text(alert: OpenWebUIAlert) -> str:
    return (
        f"Event: {alert.event}\n"
        f"Subject: {alert.subject}\n"
        f"User Name: {alert.user_name}\n"
        f"User Email: {alert.user_email}\n"
        f"User ID: {alert.user_id}\n"
        f"Reason: {alert.reason}\n"
        f"Timestamp: {alert.timestamp}\n\n"
        f"Content preview:\n{alert.content_preview}"
    )