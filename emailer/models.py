"""Data models for recipients and problem statements."""

from pydantic import BaseModel, Field, field_validator


class Recipient(BaseModel):
    """Recipient data model representing a target email address and optional name."""
    email: str = Field(..., description="Recipient email address")
    name: str = Field(default="", description="Optional recipient name")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        clean = v.strip().lower()
        if not clean or "@" not in clean or "." not in clean.split("@")[-1]:
            raise ValueError(f"Invalid email address: {v}")
        return clean

    @field_validator("name")
    @classmethod
    def clean_name(cls, v: str) -> str:
        return v.strip() if v else ""


class Statement(BaseModel):
    """Problem statement model with unique identifier and text content."""
    id: str = Field(..., description="Unique statement identifier")
    text: str = Field(..., description="Problem statement text")

    @field_validator("id", "text")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        clean = v.strip()
        if not clean:
            raise ValueError("Field must not be empty")
        return clean
