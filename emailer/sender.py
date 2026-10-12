"""SMTP email dispatch module with TLS support, multipart MIME, and retries."""

import email.utils
import logging
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional
from emailer.config import SMTPConfig

logger = logging.getLogger(__name__)


def build_message(
    from_addr: str,
    to_addr: str,
    subject: str,
    text_body: str,
    html_body: Optional[str] = None,
    sender_name: str = "",
    recipient_name: str = "",
) -> MIMEMultipart:
    """Build a standard MIME email message with plaintext and optional HTML fallback."""
    msg = MIMEMultipart("alternative")

    from_header = (
        email.utils.formataddr((sender_name, from_addr))
        if sender_name
        else from_addr
    )
    to_header = (
        email.utils.formataddr((recipient_name, to_addr))
        if recipient_name
        else to_addr
    )

    msg["From"] = from_header
    msg["To"] = to_header
    msg["Subject"] = subject
    msg["Date"] = email.utils.formatdate(localtime=True)
    domain = from_addr.split("@")[-1] if "@" in from_addr else "automation.local"
    msg["Message-ID"] = email.utils.make_msgid(domain=domain)

    # Plaintext version (always present)
    msg.attach(MIMEText(text_body, "plain", "utf-8"))

    # HTML version (if provided)
    if html_body:
        msg.attach(MIMEText(html_body, "html", "utf-8"))

    return msg


def send_email(
    smtp_cfg: SMTPConfig,
    to: str,
    subject: str,
    body: str,
    html_body: Optional[str] = None,
    name: str = "",
    max_retries: int = 3,
    retry_delay: float = 2.0,
) -> bool:
    """Send an email using configured SMTP settings with automatic retries on failure.

    Args:
        smtp_cfg: SMTP configuration (host, port, credentials, TLS).
        to: Target recipient email.
        subject: Email subject line.
        body: Plaintext body content.
        html_body: Optional HTML body content.
        name: Optional recipient display name.
        max_retries: Number of attempts before marking as failure.
        retry_delay: Initial delay in seconds between retries.

    Returns:
        bool: True if email was sent successfully, False otherwise.
    """
    from_addr = smtp_cfg.from_email or smtp_cfg.username or "noreply@example.com"
    msg = build_message(
        from_addr=from_addr,
        to_addr=to,
        subject=subject,
        text_body=body,
        html_body=html_body,
        sender_name=smtp_cfg.sender_name,
        recipient_name=name,
    )

    last_error: Optional[Exception] = None

    for attempt in range(1, max_retries + 1):
        try:
            logger.debug(
                "Attempt %d/%d sending email to %s via %s:%d",
                attempt,
                max_retries,
                to,
                smtp_cfg.host,
                smtp_cfg.port,
            )

            if smtp_cfg.use_ssl:
                server = smtplib.SMTP_SSL(smtp_cfg.host, smtp_cfg.port, timeout=30)
            else:
                server = smtplib.SMTP(smtp_cfg.host, smtp_cfg.port, timeout=30)

            with server as s:
                s.ehlo()
                if smtp_cfg.use_tls and not smtp_cfg.use_ssl:
                    s.starttls()
                    s.ehlo()

                if smtp_cfg.username and smtp_cfg.password:
                    s.login(smtp_cfg.username, smtp_cfg.password)

                s.sendmail(from_addr, [to], msg.as_string())

            logger.info("Successfully delivered email to %s (Subject: '%s')", to, subject)
            return True

        except (smtplib.SMTPException, OSError, TimeoutError) as e:
            last_error = e
            logger.warning(
                "Attempt %d/%d failed for %s: %s",
                attempt,
                max_retries,
                to,
                e,
            )
            if attempt < max_retries:
                sleep_time = retry_delay * (1.5 ** (attempt - 1))
                time.sleep(sleep_time)

    logger.error("Failed to deliver email to %s after %d attempts. Error: %s", to, max_retries, last_error)
    return False
