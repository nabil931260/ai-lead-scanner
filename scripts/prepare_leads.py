"""Prepare a Markdown lead input table from simple pasted rows.

This helper does not search the web or enrich leads. It only turns manually
collected rows into the table shape expected by analyze_leads.py.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "Raw Leads.txt"
DEFAULT_OUTPUT = ROOT / "Leads Input.md"

HEADER = [
    "Business",
    "Niche",
    "Location",
    "Website",
    "Source",
    "Notes",
    "Status",
    "Online Presence Status",
    "Website Quality",
    "Offer Path",
]


def escape_md(value: object) -> str:
    text = "" if value is None else str(value)
    return text.replace("\n", " ").replace("|", "\\|").strip()


def split_raw_row(line: str) -> list[str]:
    if "|" in line:
        return [part.strip() for part in line.split("|")]
    return [part.strip() for part in next(csv.reader([line]))]


def normalize_row(parts: list[str]) -> dict[str, str]:
    business = parts[0] if len(parts) > 0 else ""
    niche = parts[1] if len(parts) > 1 else ""
    location = parts[2] if len(parts) > 2 else ""
    website = parts[3] if len(parts) > 3 else ""
    notes = parts[4] if len(parts) > 4 else ""
    online_status = "No Website Found" if website.strip().lower() in {"", "n/a", "na", "none", "no website"} else "Has Website"
    offer_path = "Starter Site Offer" if online_status == "No Website Found" else "Website Analyzer"
    return {
        "Business": business,
        "Niche": niche,
        "Location": location,
        "Website": website or "N/A",
        "Source": "Manual public review",
        "Notes": notes,
        "Status": "New",
        "Online Presence Status": online_status,
        "Website Quality": "Unknown" if online_status == "Has Website" else "Missing",
        "Offer Path": offer_path,
    }


def parse_raw_leads(path: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        row = normalize_row(split_raw_row(stripped))
        if row["Business"]:
            rows.append(row)
    return rows


def write_leads_table(rows: list[dict[str, str]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Leads Input",
        "",
        "Prepared from manually collected public leads. Review before analysis.",
        "",
        "| " + " | ".join(HEADER) + " |",
        "|" + "|".join(["---"] * len(HEADER)) + "|",
    ]
    for row in rows:
        lines.append("| " + " | ".join(escape_md(row.get(column, "")) for column in HEADER) + " |")
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def prepare(input_path: Path = DEFAULT_INPUT, output_path: Path = DEFAULT_OUTPUT) -> int:
    rows = parse_raw_leads(input_path)
    write_leads_table(rows, output_path)
    print(f"Wrote {len(rows)} leads to {output_path}")
    return len(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare Leads Input.md from simple pasted lead rows.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    prepare(args.input, args.output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
