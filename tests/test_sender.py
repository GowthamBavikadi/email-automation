"""Tests for SMTP email sending with mocked connections and retries."""

import smtplib
from unittest.mock import MagicMock
import pytest
from emailer.config import SMTPConfig
from emailer.sender import send_email, build_message


def test_build_message_headers():
    msg = build_message(
        from_addr="sender@example.com",
        to_addr="receiver@example.com",
        subject="Test Subject",
        text_body="Hello Plain",
        html_body="<p>Hello HTML</p>",
        sender_name="Sender Admin",
        recipient_name="Receiver User",
    )

    assert "Sender Admin" in msg["From"]
    assert "sender@example.com" in msg["From"]
    assert "Receiver User" in msg["To"]
    assert "receiver@example.com" in msg["To"]
    assert msg["Subject"] == "Test Subject"
    assert msg.is_multipart()


def test_send_email_success(mocker):
    mock_smtp_class = mocker.patch("smtplib.SMTP")
    mock_server = MagicMock()
    mock_smtp_class.return_value.__enter__.return_value = mock_server

    cfg = SMTPConfig(
        host="smtp.example.com",
        port=587,
        username="user",
        password="secretpassword",
        use_tls=True,
    )

    success = send_email(
        smtp_cfg=cfg,
        to="target@example.com",
        subject="Test",
        body="Body text",
        name="Target Name",
        max_retries=1,
    )

    assert success is True
    mock_server.starttls.assert_called_once()
    mock_server.login.assert_called_once_with("user", "secretpassword")
    mock_server.sendmail.assert_called_once()


def test_send_email_retries_on_failure_then_succeeds(mocker):
    mock_smtp_class = mocker.patch("smtplib.SMTP")
    mocker.patch("time.sleep")  # avoid slowing down test

    # First attempt raises SMTPConnectError, second attempt succeeds
    mock_server_good = MagicMock()
    mock_smtp_class.side_effect = [
        smtplib.SMTPConnectError(421, "Temporary failure"),
        MagicMock(__enter__=MagicMock(return_value=mock_server_good)),
    ]

    cfg = SMTPConfig(host="smtp.example.com", port=587, username="", password="", use_tls=False)

    success = send_email(
        smtp_cfg=cfg,
        to="target@example.com",
        subject="Test",
        body="Body text",
        max_retries=2,
        retry_delay=0.01,
    )

    assert success is True
    assert mock_smtp_class.call_count == 2


def test_send_email_fails_after_max_retries(mocker):
    mock_smtp_class = mocker.patch("smtplib.SMTP")
    mocker.patch("time.sleep")

    mock_smtp_class.side_effect = smtplib.SMTPServerDisconnected("Disconnected")

    cfg = SMTPConfig(host="smtp.example.com", port=587, username="", password="", use_tls=False)

    success = send_email(
        smtp_cfg=cfg,
        to="target@example.com",
        subject="Test",
        body="Body text",
        max_retries=3,
        retry_delay=0.01,
    )

    assert success is False
    assert mock_smtp_class.call_count == 3
