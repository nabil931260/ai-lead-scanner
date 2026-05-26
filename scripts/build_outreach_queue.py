"""Build a manual-review outreach queue.

Reads:
- Scored Leads.md
- Draft Messages.md
- generated_sites/[slug]/index.html

Writes:
- Outreach Queue.md

This script sends nothing, publishes nothing, and does not use Gmail.
"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCORED_LEADS = ROOT / "Scored Leads.md"
DRAFT_MESSAGES = ROOT / "Draft Messages.md"
GENERATED_SITES = ROOT / "generated_sites"
OUTREACH_QUEUE = ROOT / "Outreach Queue.md"

MANUAL_COLUMNS = [
    "Contact Email",
    "Approved For Draft?",
    "Reviewed Mockup?",
    "Reviewed Message?",
    "Gmail Draft Created?",
    "Gmail Draft ID",
    "Gmail Draft Link",
]


def clean_cell(value: str) -> str:
    return value.strip().replace("\\|", "|").replace("<br>", "\n")


def escape_md(value: object) -> str:
    text = "" if value is None else str(value)
    return text.replace("\n", "<br>").replace("|", "\\|").strip()


def slugify(value: str) -> str:
    slug = "".join(ch.lower() if ch.isalnum() else "-" for ch in value)
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug.strip("-") or "business"


def parse_markdown_table(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    table_lines = [line for line in lines if line.strip().startswith("|")]
    if len(table_lines) < 3:
        return []

    header = [clean_cell(cell) for cell in table_lines[0].strip("|").split("|")]
    rows: list[dict[str, str]] = []
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


def generated_site_for_business(business: str, occurrence: int) -> str:
    base = slugify(business)
    candidates = [base] if occurrence == 1 else [f"{base}-{occurrence}", base]
    for candidate in candidates:
        path = GENERATED_SITES / candidate / "index.html"
        if path.exists():
            return str(path.relative_to(ROOT)).replace("\\", "/")
    return ""


def offer_type(row: dict[str, str]) -> str:
    return row.get("Offer Type", "").strip() or "Manual Review Needed"


def offer_package(row: dict[str, str], site_path: str) -> str:
    status = row.get("Status", "").strip().lower()
    score = score_value(row)
    if status == "manual review needed":
        return "Manual review needed"
    if status == "workflow cleanup candidate":
        if score >= 80:
            return "$300 cleanup package"
        if score >= 70:
            return "$150 setup"
        return "$75 audit"
    if status == "starter site candidate":
        if site_path and score >= 70:
            return "$150 setup"
        return "$75 audit"
    return "Manual review needed"


def draft_message_type(row: dict[str, str]) -> str:
    status = row.get("Status", "").strip().lower()
    if status == "workflow cleanup candidate":
        return "Existing website workflow cleanup"
    if status == "starter site candidate":
        return "No website starter site"
    return "Manual review needed"


def draft_ready(row: dict[str, str]) -> bool:
    return bool(row.get("Draft message", "").strip())


def has_contact_path(value: str) -> bool:
    cleaned = value.strip()
    if not cleaned:
        return False
    return cleaned.lower() not in {"n/a", "na", "none", "missing"}


def priority(row: dict[str, str], site_path: str, draft_ok: bool, review_first: bool) -> str:
    score = score_value(row)
    status = row.get("Status", "").strip().lower()
    if review_first:
        return "Review First"
    if draft_ok and status in {"workflow cleanup candidate", "starter site candidate"} and score >= 70:
        if status == "starter site candidate" and not site_path:
            return "Review First"
        return "High"
    if draft_ok and 50 <= score <= 69:
        return "Medium"
    return "Low"


def recommended_action(row: dict[str, str], site_path: str, review_first: bool, draft_ok: bool) -> str:
    status = row.get("Status", "").strip().lower()
    notes = row.get("Notes", "").lower()
    if "duplicate" in notes:
        return "Resolve duplicate before outreach."
    if review_first:
        if "robots.txt" in notes:
            return "Review skipped URL reason before outreach."
        if "contractos" in row.get("Niche", "").lower():
            return "Fix niche typo and review before outreach."
        if not has_contact_path(row.get("Contact Email", "")):
            return "Add contact email before drafting."
        if not draft_ok:
            return "Generate or review the draft before outreach."
        return "Manual review needed before outreach."
    if status == "workflow cleanup candidate" and draft_ok:
        return "Review site, mini-audit, and workflow cleanup draft."
    if status == "starter site candidate" and site_path and draft_ok:
        return "Review generated mockup, mini-audit, and starter-site draft."
    if status == "starter site candidate":
        return "Generate or locate starter-site mockup."
    return "Review mini-audit and draft."


def build_queue() -> list[dict[str, object]]:
    scored = parse_markdown_table(SCORED_LEADS)
    drafts = {row.get("Business", ""): row for row in parse_markdown_table(DRAFT_MESSAGES)}
    counts = Counter(row.get("Business", "") for row in scored)

    existing_rows = parse_markdown_table(OUTREACH_QUEUE)
    existing_lookup: dict[tuple[str, int], dict[str, str]] = {}
    if existing_rows:
        seen: Counter[str] = Counter()
        for row in existing_rows:
            business = row.get("Business", "")
            seen[business] += 1
            existing_lookup[(business, seen[business])] = row

    seen_scored: Counter[str] = Counter()
    rows: list[dict[str, object]] = []

    for row in scored:
        business = row.get("Business", "")
        seen_scored[business] += 1
        occurrence = seen_scored[business]
        draft = drafts.get(business, {})
        site_path = generated_site_for_business(business, occurrence)
        draft_ok = draft_ready(draft)
        duplicate = counts[business] > 1
        review_first = False
        merged_manual = existing_lookup.get((business, occurrence), {})
        contact_path = merged_manual.get("Contact Email", row.get("Contact Email", ""))

        notes = []
        if duplicate:
            notes.append("Duplicate business name in scored leads.")
            review_first = True
        if "robots.txt disallows this url" in row.get("Visible signals", "").lower():
            notes.append("robots.txt disallows this URL.")
            review_first = True
        if "contractos" in row.get("Niche", "").lower():
            notes.append("Niche typo: Contractos.")
            review_first = True
        if not has_contact_path(contact_path):
            notes.append("Missing contact email.")
            review_first = True
        if not draft_ok:
            notes.append("Draft message missing or weak.")
            review_first = True
        if row.get("Status", "").strip().lower() == "manual review needed":
            notes.append("Manual review needed.")
            review_first = True
        if row.get("Status", "").strip().lower() == "starter site candidate" and not site_path:
            notes.append("Starter-site mockup not found.")
            review_first = True
        manual_defaults = {
            column: merged_manual.get(column, "No" if column in {"Approved For Draft?", "Reviewed Mockup?", "Reviewed Message?", "Gmail Draft Created?"} else "")
            for column in MANUAL_COLUMNS
        }
        manual_defaults["Contact Email"] = contact_path
        for column in MANUAL_COLUMNS:
            if merged_manual.get(column, ""):
                manual_defaults[column] = merged_manual.get(column, "")

        rows.append(
            {
                "Priority": priority(row, site_path, draft_ok, review_first),
                "Business": business,
                "Niche": row.get("Niche", ""),
                "Score": score_value(row),
                "Offer Type": offer_type(row),
                "Offer Package": offer_package(row, site_path),
                "Draft Message Type": draft_message_type(row),
                "Generated site path": site_path,
                "Mini-audit link/path": draft.get("Mini-audit link/path", f"Mini Audits.md#{slugify(business)}"),
                "Draft message ready?": "Yes" if draft_ok else "No",
                "Review status": "Needs review",
                "Recommended action": recommended_action({**row, "Contact Email": contact_path}, site_path, review_first, draft_ok),
                "Notes": " ".join(notes),
                **manual_defaults,
            }
        )

    priority_order = {"Review First": 0, "High": 1, "Medium": 2, "Low": 3}
    rows.sort(key=lambda item: (priority_order.get(str(item["Priority"]), 9), -int(item["Score"]), str(item["Business"])))
    return rows


def write_queue(rows: list[dict[str, object]]) -> None:
    header = [
        "Priority",
        "Business",
        "Niche",
        "Score",
        "Offer Type",
        "Offer Package",
        "Draft Message Type",
        "Generated site path",
        "Mini-audit link/path",
        "Draft message ready?",
        "Review status",
        "Recommended action",
        "Notes",
        "Contact Email",
        "Approved For Draft?",
        "Reviewed Mockup?",
        "Reviewed Message?",
        "Gmail Draft Created?",
        "Gmail Draft ID",
        "Gmail Draft Link",
    ]
    lines = [
        "# Outreach Queue",
        "",
        "Source: [[03 Projects/Income Strategy Portfolio/AI Lead Scanner/Automation Workflow]]",
        "",
        "Manual review queue only. Do not send automatically. Review generated site, mini-audit, and draft message before contacting any business.",
        "",
        "| " + " | ".join(header) + " |",
        "|" + "|".join(["---"] * len(header)) + "|",
    ]
    for row in rows:
        lines.append("| " + " | ".join(escape_md(row.get(col, "")) for col in header) + " |")
    OUTREACH_QUEUE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    rows = build_queue()
    write_queue(rows)
    high_count = sum(1 for row in rows if row["Priority"] == "High")
    print(f"Wrote {len(rows)} businesses to {OUTREACH_QUEUE}")
    print(f"High priority: {high_count}")
    print("Top 5:")
    for row in rows[:5]:
        print(f"- {row['Business']} ({row['Priority']}, score {row['Score']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
