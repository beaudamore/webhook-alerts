import smtplib
from email.message import EmailMessage

from .config import env, env_bool
from .formatting import alert_text
from .models import OpenWebUIAlert


def forward(alert: OpenWebUIAlert) -> bool:
    to_address = env("ALERT_EMAIL_TO")
    smtp_host = env("SMTP_HOST")
    if not to_address or not smtp_host:
        return False

    from_address = env("ALERT_EMAIL_FROM", "openwebui-alerts@example.com")
    smtp_port = int(env("SMTP_PORT", "25"))
    smtp_username = env("SMTP_USERNAME")
    smtp_password = env("SMTP_PASSWORD")

    message = EmailMessage()
    message["Subject"] = alert.subject
    message["From"] = from_address
    message["To"] = to_address
    message.set_content(alert_text(alert))

    with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as smtp:
        if env_bool("SMTP_STARTTLS", "true"):
            smtp.starttls()
        if smtp_username:
            smtp.login(smtp_username, smtp_password)
        smtp.send_message(message)
    return True