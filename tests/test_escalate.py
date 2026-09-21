import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from escalate import build_escalation_email, process


def make_row(id_, severity, topic="billing_payment", name="Andre Wijaya"):
    return {
        "id": id_,
        "date": "6/22/2026",
        "name": name,
        "email": "andre.wijaya@example.com",
        "channel": "email",
        "message": "Something went wrong.",
        "sentiment": "negative",
        "topic": topic,
        "severity": severity,
    }


class BuildEscalationEmailTests(unittest.TestCase):
    def test_email_addressed_to_support_lead(self):
        row = make_row("1", "critical")
        email = build_escalation_email(row, "lead@example.com")
        self.assertEqual(email["to"], "lead@example.com")
        self.assertIn("CRITICAL", email["subject"])
        self.assertIn("Feedback #1", email["subject"])
        self.assertIn("Suggested reply to customer", email["body"])


class ProcessTests(unittest.TestCase):
    def test_splits_escalated_from_routine_and_writes_files(self):
        rows = [
            make_row("1", "critical"),
            make_row("2", "high"),
            make_row("3", "medium"),
            make_row("4", "low"),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            escalation_dir = tmp_path / "escalations"
            routine_log = tmp_path / "routine.log"

            result = process(rows, escalation_dir, routine_log, support_lead_email="lead@example.com")

            self.assertEqual({row["id"] for row in result["escalated"]}, {"1", "2"})
            self.assertEqual({row["id"] for row in result["routine"]}, {"3", "4"})
            self.assertEqual(len(result["draft_paths"]), 2)

            for path in result["draft_paths"]:
                self.assertTrue(path.exists())
                self.assertIn("To: lead@example.com", path.read_text(encoding="utf-8"))

            self.assertTrue(routine_log.exists())
            log_content = routine_log.read_text(encoding="utf-8")
            self.assertIn("id=3", log_content)
            self.assertIn("id=4", log_content)
            self.assertNotIn("id=1", log_content)


if __name__ == "__main__":
    unittest.main()
