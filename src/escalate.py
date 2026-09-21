"""Draft escalation emails for urgent feedback and log the rest to a file.

No email connector is configured for this project, so escalations are not
sent over SMTP: each one is written as a draft .txt file (To/Subject/Body)
under an output directory, ready for a human to review and send.
"""

import argparse
import csv
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_SUPPORT_LEAD_EMAIL = "support-lead@example.com"

ESCALATED_SEVERITIES = ("critical", "high")

TOPIC_ACTIONS = {
    "billing_payment": "We've flagged the billing issue on your account and are working to correct the charge as quickly as possible.",
    "authentication": "We're investigating the login issue affecting your account and working to restore access immediately.",
    "data_loss": "We're checking our backups now to see whether your recent work can be recovered, and will update you as soon as we know more.",
    "outage_reliability": "We understand repeated outages are unacceptable, and our engineering team is prioritizing a permanent fix.",
    "security_privacy": "We take this very seriously and have escalated it to our security team for immediate investigation.",
    "data_integrity": "We're reviewing the discrepancy in your report numbers so you can trust the figures before sharing them.",
}
DEFAULT_TOPIC_ACTION = "We're looking into this right away and will keep you updated."


def draft_customer_reply(row):
    action = TOPIC_ACTIONS.get(row["topic"], DEFAULT_TOPIC_ACTION)
    name = row["name"].split()[0]
    return (
        f"Hi {name},\n\n"
        f"Thank you for reaching out, and I'm sorry for the trouble this has caused. {action}\n\n"
        f"We're treating this as {row['severity']} priority and our team is on it now. "
        "I'll follow up with an update shortly.\n\n"
        "— Support Team"
    )


def build_escalation_email(row, support_lead_email):
    subject = f"[Escalation - {row['severity'].upper()}] {row['topic']} — Feedback #{row['id']}"
    body = (
        f"Customer: {row['name']} ({row['email']})\n"
        f"Channel: {row['channel']}\n"
        f"Date: {row['date']}\n"
        f"Topic: {row['topic']}\n"
        f"Sentiment: {row['sentiment']}\n"
        f"Severity: {row['severity']}\n\n"
        f"Original message:\n\"{row['message']}\"\n\n"
        "Suggested reply to customer (please review before sending):\n"
        "-----\n"
        f"{draft_customer_reply(row)}\n"
        "-----\n"
    )
    return {"to": support_lead_email, "subject": subject, "body": body}


def write_escalation_draft(row, output_dir, support_lead_email):
    email = build_escalation_email(row, support_lead_email)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"feedback_{row['id']}.txt"
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"To: {email['to']}\n")
        f.write(f"Subject: {email['subject']}\n\n")
        f.write(email["body"])
    return path


def log_routine_rows(rows, log_path):
    log_path.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with open(log_path, "a", encoding="utf-8") as f:
        for row in rows:
            f.write(
                f"{timestamp} id={row['id']} severity={row['severity']} "
                f"topic={row['topic']} sentiment={row['sentiment']} "
                f"name={row['name']!r} message={row['message']!r}\n"
            )


def process(labeled_rows, escalation_dir, routine_log_path, support_lead_email=DEFAULT_SUPPORT_LEAD_EMAIL):
    escalated = [row for row in labeled_rows if row["severity"] in ESCALATED_SEVERITIES]
    routine = [row for row in labeled_rows if row["severity"] not in ESCALATED_SEVERITIES]

    draft_paths = [
        write_escalation_draft(row, escalation_dir, support_lead_email) for row in escalated
    ]
    log_routine_rows(routine, routine_log_path)

    return {"escalated": escalated, "routine": routine, "draft_paths": draft_paths}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="data/labeled_feedback.csv", type=Path)
    parser.add_argument("--escalation-dir", default="data/escalations", type=Path)
    parser.add_argument("--routine-log", default="data/routine_log.txt", type=Path)
    parser.add_argument("--support-lead-email", default=DEFAULT_SUPPORT_LEAD_EMAIL)
    args = parser.parse_args()

    with open(args.input, newline="", encoding="utf-8") as f:
        rows = [row for row in csv.DictReader(f) if row.get("id")]

    result = process(rows, args.escalation_dir, args.routine_log, args.support_lead_email)

    print(f"Escalations drafted: {len(result['escalated'])} -> {args.escalation_dir}/")
    print(f"Routine rows logged: {len(result['routine'])} -> {args.routine_log}")


if __name__ == "__main__":
    main()
