import os


def env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def env_bool(name: str, default: str = "false") -> bool:
    return env(name, default).lower() in {"1", "true", "yes", "on"}