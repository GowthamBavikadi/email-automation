#!/usr/bin/env python3
"""Main CLI entrypoint for unique problem statement email automation."""

import logging
import sys
import time
from emailer.cli import parse_args, setup_logging
from emailer.config import AppConfig
from emailer.loader import load_recipients, load_statements
from emailer.renderer import TemplateRenderer
from emailer.selector import pick_unused
from emailer.sender import send_email
from emailer.tracker import SentTracker

logger = logging.getLogger("emailer.main")


def run() -> int:
    args = parse_args()
    setup_logging(log_path="logs/send.log", verbose=args.verbose)

    logger.info("=" * 60)
    logger.info("Starting Problem Statement Email Automation")
    if args.dry_run:
        logger.info("MODE: *** DRY RUN *** (No emails will be sent, no tracking changes saved)")
    else:
        logger.info("MODE: LIVE SENDING")
    logger.info("=" * 60)

    # 1. Load Configuration
    try:
        config = AppConfig.load(args.config)
        logger.info("Loaded configuration from '%s'", args.config)
    except Exception as e:
        logger.error("Configuration error: %s", e)
        return 1

    # 2. Load Data Files
    try:
        recipients = load_recipients(config.files.emails)
        statements = load_statements(config.files.statements)
    except Exception as e:
        logger.error("Failed to load required data files: %s", e)
        return 1

    if not recipients:
        logger.warning("No valid recipients found to process. Exiting.")
        return 0

    if not statements:
        logger.error("No problem statements found in statement bank. Exiting.")
        return 1

    # 3. Initialize State Tracker and Template Renderer
    tracker = SentTracker(config.files.tracker)
    renderer = TemplateRenderer(config.email.template, config.email.html_template)

    # 4. Handle --resume flag (filter out already contacted recipients)
    if args.resume:
        original_count = len(recipients)
        recipients = [r for r in recipients if len(tracker.get_used(r.email)) == 0]
        resumed_skipped = original_count - len(recipients)
        logger.info(
            "--resume specified: skipped %d recipient(s) who already received at least one statement. %d remaining.",
            resumed_skipped,
            len(recipients),
        )

    # 5. Handle --limit flag
    if args.limit is not None and args.limit > 0:
        recipients = recipients[:args.limit]
        logger.info("Applied limit: processing first %d recipient(s).", len(recipients))

    if not recipients:
        logger.info("All recipients have already been processed. Nothing to send.")
        return 0

    # 6. Execution Loop
    sent_count = 0
    simulated_count = 0
    skipped_count = 0
    failed_count = 0
    total_to_process = len(recipients)
    batch_assigned_ids: set[str] = set()

    for idx, recipient in enumerate(recipients, start=1):
        logger.info("[%d/%d] Processing recipient: %s", idx, total_to_process, recipient.email)

        # Pick random unused statement (preferring unique within batch)
        statement = pick_unused(
            recipient.email,
            statements,
            tracker,
            batch_assigned_ids=batch_assigned_ids,
        )
        if not statement:
            logger.warning(
                "Skipping recipient %s: all %d problem statements have already been used.",
                recipient.email,
                len(statements),
            )
            skipped_count += 1
            continue

        batch_assigned_ids.add(statement.id)

        # Render content
        text_body = renderer.render_text(recipient.name, statement.text)
        html_body = renderer.render_html(recipient.name, statement.text)

        # Dry run simulation
        if args.dry_run:
            simulated_count += 1
            logger.info(
                "[DRY-RUN] [OK] Would send statement '%s' to '%s' (%s)",
                statement.id,
                recipient.email,
                recipient.name or "Anonymous",
            )
            logger.debug("[DRY-RUN] Content preview:\n%s", text_body.strip())
            continue

        # Live email delivery
        success = send_email(
            smtp_cfg=config.smtp,
            to=recipient.email,
            subject=config.email.subject,
            body=text_body,
            html_body=html_body,
            name=recipient.name,
            max_retries=config.runtime.max_retries,
            retry_delay=config.runtime.retry_delay_seconds,
        )

        if success:
            sent_count += 1
            # Update and persist tracker
            tracker.mark_sent(recipient.email, statement.id)
            tracker.save()
            logger.info(
                "Sent statement '%s' to %s and updated state tracker.",
                statement.id,
                recipient.email,
            )
        else:
            failed_count += 1
            logger.error(
                "Delivery failed for %s. Statement '%s' remains unused for future retries.",
                recipient.email,
                statement.id,
            )

        # Inter-email delay
        if idx < total_to_process and config.runtime.delay_seconds > 0:
            time.sleep(config.runtime.delay_seconds)

    # 7. Summary Report
    logger.info("=" * 60)
    logger.info("EXECUTION SUMMARY:")
    logger.info("  Total Considered: %d", total_to_process)
    if args.dry_run:
        logger.info("  Simulated Sends : %d", simulated_count)
    else:
        logger.info("  Successfully Sent: %d", sent_count)
        logger.info("  Delivery Failures: %d", failed_count)
    logger.info("  Skipped (Exhausted): %d", skipped_count)
    stats = tracker.get_stats()
    logger.info("  Tracker Total Recipients: %d", stats["total_recipients_tracked"])
    logger.info("  Tracker Total Deliveries : %d", stats["total_statements_delivered"])
    logger.info("=" * 60)

    return 0 if failed_count == 0 else 2


if __name__ == "__main__":
    sys.exit(run())
