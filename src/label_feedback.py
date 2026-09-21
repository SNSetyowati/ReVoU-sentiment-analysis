"""Label customer feedback with sentiment, topic, and severity, then split by urgency."""

import argparse
import csv
import re
from pathlib import Path

POSITIVE_PATTERNS = [
    r"\blove\b", r"\bloved\b", r"\bgreat\b", r"\bfantastic\b", r"\bthank you\b",
    r"\bthanks\b", r"\bawesome\b", r"\bappreciate\b", r"\bnice\b", r"\bkind\b",
    r"\bwonderful\b", r"\bhappy\b", r"\bexcellent\b", r"\bamazing\b",
    r"\bwell done\b", r"\bimpressed\b", r"\bcherry on top\b", r"\bsnappier\b",
    r"\bkeep up the great work\b",
]

NEGATIVE_PATTERNS = [
    r"\bunacceptable\b", r"\bcannot\b", r"\bcan not\b", r"\bdisappeared\b",
    r"\bgone\b", r"\bpanicking\b", r"\bcancel\b", r"\bcancelling\b",
    r"\bserious\b", r"\bcrashes?\b", r"\blosing\b", r"\bblocking\b",
    r"\bdisappointed\b", r"\bfrustrating\b", r"\bconfusing\b", r"\bgave up\b",
    r"\bslow\b", r"\bcuts off\b", r"\bunfinished\b", r"\bfails?\b",
    r"\bfailing\b", r"\bstuck\b", r"\btoo many\b", r"\bthin\b", r"\blost\b",
    r"\bbug\b", r"\bbroken\b", r"\berror\b", r"\bproblem\b", r"\bcharged twice\b",
    r"\brefund\b", r"\binvalid\b", r"\bdo not match\b", r"\bnot reply\b",
    r"\bnobody has replied\b", r"\blost on how\b",
]

TOPIC_RULES = [
    ("data_loss", [r"\bdisappeared\b", r"\bgone\b", r"\brecover\b", r"\blost.*work\b"]),
    ("security_privacy", [
        r"\bprivacy\b", r"\banother customer'?s\b", r"\bpersonal data\b",
        r"\bregulations?\b", r"\bdelete all of my\b",
    ]),
    ("authentication", [r"\blog in\b", r"\blogin\b", r"\bsession\b", r"\blogging me out\b"]),
    ("outage_reliability", [r"\boutage\b", r"\bcancelling our team plan\b"]),
    ("billing_payment", [
        r"\bcharged\b", r"\brefund\b", r"\bsubscription\b", r"\binvoice\b",
        r"\bpayment\b", r"\bbilling\b", r"\bpricing\b", r"\bplan\b", r"\bupgrade\b",
    ]),
    ("data_integrity", [r"\bdo not match\b", r"\bnumbers\b.*\breport\b", r"\bboard\b"]),
    ("support_response", [
        r"\bsupport ticket\b", r"\bresponse time\b", r"\bnobody has replied\b",
        r"\bsupport agent\b",
    ]),
    ("mobile", [r"\bmobile app\b", r"\bandroid\b", r"\bios\b"]),
    ("performance", [r"\bslow\b", r"\bseconds? to load\b", r"\bspeed\b"]),
    ("notifications", [r"\bnotifications?\b"]),
    ("documentation", [r"\bdocs\b", r"\bdocumentation\b", r"\bapi docs\b"]),
    ("onboarding", [r"\bonboarding\b", r"\bwalkthrough\b", r"\binvite my teammates\b", r"\btrial\b"]),
    ("bug", [r"\bcrash(es)?\b", r"\bbug\b", r"\bresets\b", r"\btypo\b", r"\bcuts off\b"]),
    ("usability", [r"\bconfusing\b", r"\bcould not find\b", r"\bgave up\b"]),
    ("feature_request", [
        r"\bwould love\b", r"\bintegration\b", r"\bwish\b", r"\bsuggestion\b",
        r"\bkeyboard shortcuts\b", r"\bwidget\b", r"\bdark mode\b",
    ]),
]

CRITICAL_PATTERNS = [
    r"\bdisappeared\b", r"\bgone\b", r"\bcannot log in at all\b",
    r"\binvalid session\b", r"\banother customer'?s\b", r"\bcancelling our\b",
    r"\bmoving to a competitor\b", r"\bpanicking\b", r"\boutage\b",
    r"\bin two hours\b", r"\bneed this fixed now\b", r"\bimmediately\b",
]

HIGH_PATTERNS = [
    r"\brefund\b", r"\bcharged twice\b", r"\bover its limit\b", r"\bcrashes?\b",
    r"\blosing my changes\b", r"\bblocking my work\b", r"\bpayment keeps failing\b",
    r"\bstuck on monthly\b", r"\bdo not match\b", r"\bdelete all of my\b",
    r"\bboard\b",
]

MEDIUM_PATTERNS = [
    r"\bfour days\b", r"\bdisappointed\b", r"\bslow\b", r"\bseconds? to load\b",
    r"\btoo many\b", r"\bconfusing\b", r"\blost on how\b", r"\bevery few hours\b",
]


def _count_matches(text, patterns):
    return sum(1 for pattern in patterns if re.search(pattern, text))


def classify_sentiment(message):
    text = message.lower()
    positive = _count_matches(text, POSITIVE_PATTERNS)
    negative = _count_matches(text, NEGATIVE_PATTERNS)
    if positive > negative:
        return "positive"
    if negative > positive:
        return "negative"
    return "neutral"


def classify_topic(message):
    text = message.lower()
    best_topic, best_score = "other", 0
    for topic, patterns in TOPIC_RULES:
        score = _count_matches(text, patterns)
        if score > best_score:
            best_topic, best_score = topic, score
    return best_topic


def classify_severity(message):
    text = message.lower()
    score = (
        3 * _count_matches(text, CRITICAL_PATTERNS)
        + 2 * _count_matches(text, HIGH_PATTERNS)
        + 1 * _count_matches(text, MEDIUM_PATTERNS)
    )
    if score >= 5:
        return "critical"
    if score >= 3:
        return "high"
    if score >= 1:
        return "medium"
    return "low"


def label_rows(rows):
    labeled = []
    for row in rows:
        message = row["message"]
        labeled.append({
            **row,
            "sentiment": classify_sentiment(message),
            "topic": classify_topic(message),
            "severity": classify_severity(message),
        })
    return labeled


def write_csv(path, rows, fieldnames):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="data/feedback.csv", type=Path)
    parser.add_argument("--output-dir", default="data", type=Path)
    args = parser.parse_args()

    with open(args.input, newline="", encoding="utf-8") as f:
        rows = [row for row in csv.DictReader(f) if row.get("id")]

    labeled = label_rows(rows)
    fieldnames = list(labeled[0].keys())

    urgent = [row for row in labeled if row["severity"] in ("critical", "high")]
    routine = [row for row in labeled if row["severity"] not in ("critical", "high")]

    write_csv(args.output_dir / "labeled_feedback.csv", labeled, fieldnames)
    write_csv(args.output_dir / "feedback_urgent.csv", urgent, fieldnames)
    write_csv(args.output_dir / "feedback_routine.csv", routine, fieldnames)

    print(f"Labeled {len(labeled)} rows")
    print(f"  urgent (high/critical): {len(urgent)} -> {args.output_dir / 'feedback_urgent.csv'}")
    print(f"  routine (medium/low):   {len(routine)} -> {args.output_dir / 'feedback_routine.csv'}")


if __name__ == "__main__":
    main()
