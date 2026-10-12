"""Email automation package for distributing unique problem statements."""

from emailer.models import Recipient, Statement
from emailer.tracker import SentTracker
from emailer.selector import pick_unused
from emailer.sender import send_email, SMTPConfig

__all__ = [
    "Recipient",
    "Statement",
    "SentTracker",
    "pick_unused",
    "send_email",
    "SMTPConfig",
]
