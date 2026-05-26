"""Generate rule-based mini-audits and draft outreach messages.

Reads Scored Leads.md, selects leads at or above a score threshold, and writes:
- Mini Audits.md
- Draft Messages.md

No messages are sent. Workflow cleanup rows receive existing-website audits and
starter-site rows receive starter-site audits.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCORED_LEADS = ROOT / "Scored Leads.md"
MINI_AUDITS = ROOT / "Mini Audits.md"
DRAFT_MESSAGES = ROOT / "Draft Messages.md"
DEFAULT_SENDER_NAME = "Your Name"


def clean_cell(value: str) -> str:
    return value.strip().replace("\\|", "|").replace("<br>", "\n")


def escape_md(value: object) -> str:
    text = "" if value is None else str(value)
    return text.replace("\n", "<br>").replace("|", "\\|").strip()


def slug(value: str) -> str:
    cleaned = "".join(ch.lower() if ch.isalnum() else "-" for ch in value)
    while "--" in cleaned:
        cleaned = cleaned.replace("--", "-")
    return cleaned.strip("-") or "lead"


def parse_markdown_table(path: Path) -> list[dict[str, str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    table_lines = [line for line in lines if line.strip().startswith("|")]
    if len(table_lines) < 3:
        return []

    header = [clean_cell(cell) for cell in table_lines[0].strip("|").split("|")]
    rows = []
    for line in table_lines[2:]:
        cells = [clean_cell(cell) for cell in line.strip("|").split("|")]
        if len(cells) < len(header):
            cells += [""] * (len(header) - len(cells))
        row = dict(zip(header, cells[: len(header)]))
        if any(row.values()):
            rows.append(row)
    return rows


def score_value(row: dict[str, str]) -> int:
    try:
        return int(float(row.get("Score /100", "0").strip()))
    except ValueError:
        return 0


def is_workflow_cleanup_candidate(row: dict[str, str]) -> bool:
    return row.get("Status", "").strip().lower() == "workflow cleanup candidate"


def is_starter_site_candidate(row: dict[str, str]) -> bool:
    return row.get("Status", "").strip().lower() == "starter site candidate"


def is_manual_review(row: dict[str, str]) -> bool:
    return row.get("Status", "").strip().lower() == "manual review needed"


def offer_type(row: dict[str, str]) -> str:
    if is_workflow_cleanup_candidate(row):
        return "Website + Workflow Improvement Audit"
    if is_starter_site_candidate(row):
        return "Starter Site + Lead Tracker"
    return "Manual Review Needed"


def draft_message_type(row: dict[str, str]) -> str:
    if is_workflow_cleanup_candidate(row):
        return "Existing website workflow cleanup"
    if is_starter_site_candidate(row):
        return "No website starter site"
    return "Manual review needed"


def subject_for(row: dict[str, str]) -> str:
    if is_workflow_cleanup_candidate(row):
        return "Quick workflow question"
    if is_starter_site_candidate(row):
        return "Quick website/quote flow question"
    return "Manual review needed"


def sender_name() -> str:
    return os.getenv("LEAD_SCANNER_SENDER_NAME", DEFAULT_SENDER_NAME)


def draft_message(row: dict[str, str]) -> str:
    business = row.get("Business", "[Business]")
    signature = sender_name()
    if is_workflow_cleanup_candidate(row):
        return (
            f"Hi {business} team,\n\n"
            "Quick question: when someone asks for a quote or estimate through your website, is it easy to track "
            "who needs follow-up?\n\n"
            "I'm testing a small lead/quote intake cleanup service for local businesses. I review the quote/contact "
            "flow and send 3-5 practical notes on reducing friction or making follow-up easier. No rebuild or "
            "software pitch.\n\n"
            "Would a short outside review be useful?\n\n"
            "Thanks,\n"
            f"{signature}"
        )
    if is_starter_site_candidate(row):
        return (
            f"Hi {business} team,\n\n"
            "Quick question: do quote or service requests ever get hard to track when they come through phone, "
            "email, or contact forms?\n\n"
            "I'm testing a small starter site and lead-tracker service for local businesses. The goal is to make "
            "new requests easier to capture and follow up with, without adding a complicated system.\n\n"
            "Would a short example be useful?\n\n"
            "Thanks,\n"
            f"{signature}"
        )
    return ""


def mini_audit_section(row: dict[str, str]) -> str:
    business = row.get("Business", "")
    if is_workflow_cleanup_candidate(row):
        offer_line = "Website + Workflow Improvement Audit"
        simple_fix = "Review the quote/contact flow, tighten the form, add a lead tracker, and document a simple follow-up process."
        ai_fix = "Use AI only after the manual workflow is clear: summarize inquiries, draft follow-ups, flag missing details, and produce a weekly lead summary."
        package = "$75 Website + Quote Flow Audit, $150 Quote Form + Lead Tracker Setup, or $300 Website Lead Flow Cleanup + Follow-Up System."
        question = "How do you currently track new quote requests so none slip through?"
        noticed = row.get("Visible signals", "")
        issue = row.get("Likely pain", "")
    else:
        offer_line = "Starter Site + Lead Tracker"
        simple_fix = "Create a starter site mockup with services, service area, quote/contact form fields, FAQ, and a simple lead tracker."
        ai_fix = "Use AI later to summarize quote requests, draft follow-up replies, and produce a weekly lead summary after the manual form/tracker works."
        package = "$75 Website + Lead Flow Mini-Audit, $150 Starter Landing Page, $300 Landing Page + Lead Tracker, or $500+ Website + Workflow Setup."
        question = "Would you be open to me sending over a quick example?"
        noticed = row.get("Visible signals", "No website provided / missing online presence")
        issue = row.get("Likely pain", "Missing or weak web presence may limit quote requests, lead capture, and follow-up.")

    return f"""## {business}

### Business
{business}

### Niche
{row.get("Niche", "")}

### Website
{row.get("Website", "")}

### Offer Type
{offer_line}

### What I Noticed
{noticed}

### Possible Workflow Issue
{issue}

### Simple Fix
{simple_fix}

### AI-Assisted Fix
{ai_fix}

### Offer Package
{package}

### One Question To Ask
{question}

### Confidence
{row.get("Confidence", "")}

### Status
Draft generated. Needs manual review.
"""


def write_mini_audits(rows: list[dict[str, str]]) -> None:
    content = [
        "# Mini Audits",
        "",
        "Source: [[03 Projects/Income Strategy Portfolio/AI Lead Scanner/Automation Workflow]]",
        "",
        "Generated by `scripts/generate_mini_audits.py`. Review manually before use.",
        "",
    ]
    if os.getenv("OPENAI_API_KEY"):
        content.append("Note: `OPENAI_API_KEY` is configured, but this local MVP currently uses rule-based drafts for safety and repeatability.\n")
    else:
        content.append("Note: no AI API key was used. These are rule-based drafts.\n")
    for row in rows:
        content.append(mini_audit_section(row))
    MINI_AUDITS.write_text("\n".join(content).strip() + "\n", encoding="utf-8")


def write_draft_messages(rows: list[dict[str, str]]) -> None:
    header = [
        "Business",
        "Offer Type",
        "Draft Message Type",
        "Contact method",
        "Subject",
        "Draft message",
        "Mini-audit link/path",
        "Review status",
        "Gmail draft created?",
        "Sent?",
        "Notes",
    ]
    lines = [
        "# Draft Messages",
        "",
        "Source: [[03 Projects/Income Strategy Portfolio/AI Lead Scanner/Automation Workflow]]",
        "",
        "Generated outreach drafts only. Review manually before sending.",
        "",
        "| " + " | ".join(header) + " |",
        "|" + "|".join(["---"] * len(header)) + "|",
    ]
    for row in rows:
        business = row.get("Business", "")
        values = {
            "Business": business,
            "Offer Type": offer_type(row),
            "Draft Message Type": draft_message_type(row),
            "Contact method": "Manual public contact path only",
            "Subject": subject_for(row),
            "Draft message": draft_message(row),
            "Mini-audit link/path": f"Mini Audits.md#{slug(business)}",
            "Review status": "Needs review",
            "Gmail draft created?": "No",
            "Sent?": "No",
            "Notes": "Do not send until manually reviewed.",
        }
        lines.append("| " + " | ".join(escape_md(values.get(col, "")) for col in header) + " |")
    DRAFT_MESSAGES.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--threshold", type=int, default=70)
    args = parser.parse_args()

    rows = [row for row in parse_markdown_table(SCORED_LEADS) if score_value(row) >= args.threshold]
    write_mini_audits(rows)
    write_draft_messages(rows)
    print(f"Wrote {len(rows)} mini-audits and draft messages.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
