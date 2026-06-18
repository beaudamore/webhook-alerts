from pydantic import BaseModel, Field


class OpenWebUIAlert(BaseModel):
    event: str = Field(default="prompt_injection_lockout")
    subject: str = Field(default="Prompt injection lockout")
    user_id: str = Field(default="unknown")
    user_name: str = Field(default="unknown")
    user_email: str = Field(default="unknown")
    reason: str = Field(default="unknown")
    timestamp: str = Field(default="unknown")
    content_preview: str = Field(default="")