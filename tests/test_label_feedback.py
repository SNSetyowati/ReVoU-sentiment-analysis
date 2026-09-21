import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from label_feedback import classify_sentiment, classify_severity, classify_topic, label_rows


class ClassifySentimentTests(unittest.TestCase):
    def test_positive_message(self):
        self.assertEqual(classify_sentiment("I love this app, great work!"), "positive")

    def test_negative_message(self):
        self.assertEqual(
            classify_sentiment("This is unacceptable, my data is gone and I am panicking."),
            "negative",
        )

    def test_neutral_message(self):
        self.assertEqual(
            classify_sentiment("Does the Pro plan include the team workspace feature?"),
            "neutral",
        )


class ClassifyTopicTests(unittest.TestCase):
    def test_billing_topic(self):
        self.assertEqual(
            classify_topic("I was charged twice for my June subscription."),
            "billing_payment",
        )

    def test_data_loss_topic(self):
        self.assertEqual(
            classify_topic("All of my saved projects have disappeared and are gone."),
            "data_loss",
        )

    def test_security_topic(self):
        self.assertEqual(
            classify_topic("I could see another customer's invoices, this is a privacy problem."),
            "security_privacy",
        )


class ClassifySeverityTests(unittest.TestCase):
    def test_critical_severity(self):
        message = "All of my saved projects have disappeared. I am panicking, please fix this immediately."
        self.assertEqual(classify_severity(message), "critical")

    def test_low_severity(self):
        self.assertEqual(
            classify_severity("Small thing: there is a typo on the billing page."),
            "low",
        )


class LabelRowsTests(unittest.TestCase):
    def test_adds_labels_without_losing_original_fields(self):
        rows = [{"id": "1", "name": "Andre", "message": "I love this, great work!"}]
        labeled = label_rows(rows)
        self.assertEqual(len(labeled), 1)
        self.assertEqual(labeled[0]["id"], "1")
        self.assertEqual(labeled[0]["name"], "Andre")
        self.assertEqual(labeled[0]["sentiment"], "positive")
        self.assertIn("topic", labeled[0])
        self.assertIn("severity", labeled[0])


if __name__ == "__main__":
    unittest.main()
