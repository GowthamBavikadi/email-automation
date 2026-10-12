"""Configuration parsing and validation with environment variable expansion."""

import os
import re
from pathlib import Path
from typing import Optional
import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator


# Load .env if present
load_dotenv(override=True)


def expand_env_vars(data):
    """Recursively expand environment variables formatted as ${VAR_NAME} or $VAR_NAME."""
    pattern = re.compile(r"\$\{([^}]+)\}")

    if isinstance(data, str):
        def replace(match):
            var_name = match.group(1)
            # Support ${VAR_NAME:-default}
            if ":-" in var_name:
                key, default = var_name.split(":-", 1)
                return os.environ.get(key, default)
            return os.environ.get(var_name, "")
        return pattern.sub(replace, data)
    elif isinstance(data, dict):
        return {k: expand_env_vars(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [expand_env_vars(item) for item in data]
    return data


class SMTPConfig(BaseModel):
    host: str = Field(default="smtp.gmail.com", description="SMTP server host")
    port: int = Field(default=587, description="SMTP server port")
    username: str = Field(default="", description="SMTP auth username/email")
    password: str = Field(default="", description="SMTP auth password/app password")
    use_tls: bool = Field(default=True, description="Whether to use STARTTLS")
    use_ssl: bool = Field(default=False, description="Whether to use direct SSL/TLS (port 465)")
    sender_name: str = Field(default="", description="Friendly display name for sender")
    from_email: Optional[str] = Field(default=None, description="Explicit sender email address (defaults to username)")

    @field_validator("password")
    @classmethod
    def clean_password(cls, v: str) -> str:
        clean = v.strip()
        # If it looks like a Google 16-character app password with spaces ('xxxx xxxx xxxx xxxx')
        if " " in clean and len(clean.replace(" ", "")) == 16:
            return clean.replace(" ", "")
        return clean


class FilesConfig(BaseModel):
    emails: Path = Field(default=Path("emails.csv"), description="Path to emails CSV")
    statements: Path = Field(default=Path("statements.json"), description="Path to statements JSON/TXT")
    tracker: Path = Field(default=Path("sent_tracker.json"), description="Path to sent tracker JSON")


class EmailContentConfig(BaseModel):
    subject: str = Field(default="Your Problem Statement", description="Subject line")
    template: Path = Field(default=Path("templates/statement.txt"), description="Plaintext Jinja2 template")
    html_template: Optional[Path] = Field(default=Path("templates/statement.html"), description="Optional HTML template")


class RuntimeConfig(BaseModel):
    batch_size: int = Field(default=50, ge=1, description="Number of emails per batch")
    delay_seconds: float = Field(default=2.0, ge=0.0, description="Delay between emails in seconds")
    max_retries: int = Field(default=3, ge=1, description="Max retry attempts for sending each email")
    retry_delay_seconds: float = Field(default=2.0, ge=0.0, description="Initial retry backoff delay")


class AppConfig(BaseModel):
    smtp: SMTPConfig = Field(default_factory=SMTPConfig)
    files: FilesConfig = Field(default_factory=FilesConfig)
    email: EmailContentConfig = Field(default_factory=EmailContentConfig)
    runtime: RuntimeConfig = Field(default_factory=RuntimeConfig)

    @classmethod
    def load(cls, config_path: Optional[Path | str] = None) -> "AppConfig":
        """Load configuration from YAML file or environment defaults."""
        load_dotenv(override=True)
        path = Path(config_path) if config_path else Path("config.yaml")

        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                raw_data = yaml.safe_load(f) or {}
            expanded_data = expand_env_vars(raw_data)
            return cls(**expanded_data)

        # Fallback to defaults + env vars
        return cls(
            smtp=SMTPConfig(
                host=os.environ.get("SMTP_HOST", "smtp.gmail.com"),
                port=int(os.environ.get("SMTP_PORT", "587")),
                username=os.environ.get("SMTP_USER", ""),
                password=os.environ.get("SMTP_PASS", ""),
                use_tls=os.environ.get("SMTP_USE_TLS", "true").lower() in ("true", "1", "yes"),
            )
        )
