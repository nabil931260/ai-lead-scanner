"""Analyze manually supplied public business leads.

Safety boundaries:
- Reads only rows manually entered in Leads Input.md.
- Fetches only manually supplied public business website URLs.
- Classifies missing/weak website leads as starter-site candidates.
- Classifies valid websites as workflow-cleanup candidates when analysis succeeds.
- Sends nothing and never uses private or login-gated data.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
LEADS_INPUT = ROOT / "Leads Input.md"
SCORED_LEADS = ROOT / "Scored Leads.md"

USER_AGENT = "ObsidianAILeadScanner/0.2 (+manual local research; no automated outreach)"
TIMEOUT_SECONDS = 12
MAX_TEXT_CHARS = 12000

MISSING_WEBSITE_VALUES = {"", "n/a", "na", "none", "no website", "no site", "not found", "unknown"}
WEAK_PRESENCE_VALUES = {"weak website", "social only", "no website found"}
SOCIAL_DOMAINS = {
    "linkedin.com",
    "instagram.com",
    "facebook.com",
    "m.facebook.com",
    "x.com",
    "twitter.com",
    "tiktok.com",
}

SIGNAL_PATTERNS = {
    "DM/text booking language": r"\b(dm|direct message|text|call)\b.{0,40}\b(book|schedule|appointment|quote|estimate|price|availability)\b",
    "Quote/estimate language": r"\b(quote|estimate|request a quote|get an estimate|free estimate)\b",
    "Booking/scheduling language": r"\b(book now|schedule|appointment|availability|calendar|booking)\b",
    "Contact-only intake": r"\b(contact us|call us|text us|send us a message|get in touch)\b",
    "Service menu language": r"\b(services|packages|pricing|rates|menu)\b",
    "Follow-up or reminder language": r"\b(follow up|reminder|confirmation|we will get back|we'll get back)\b",
    "Manual form language": r"\b(google form|fill out this form|form below|submit request)\b",
    "FAQ missing clue": r"\b(faq|frequently asked questions)\b",
}

NICHE_HINTS = {
    "Contractors / home services": ("quote", "estimate", "repair", "service area", "licensed", "insured"),
    "Contractos / home services": ("quote", "estimate", "repair", "service area", "licensed", "insured"),
    "Contractors / home service": ("quote", "estimate", "repair", "service area", "licensed", "insured"),
    "Wedding/event vendors": ("wedding", "event", "availability", "package", "deposit", "booking"),
    "Barbers/salons/detailers": ("book", "appointment", "detail", "barber", "salon", "price"),
    "Personal trainers / coaches": ("coach", "training", "consultation", "program", "client"),
    "Small nonprofits": ("donate", "volunteer", "event", "member", "signup"),
    "Bookkeeping / invoice intake": ("invoice", "receipt", "bookkeeping", "documents", "tax"),
}


@dataclass
class Lead:
    business: str
    niche: str
    location: str
    website: str
    source: str
    notes: str
    status: str
    online_presence_status: str = ""
    website_quality: str = ""
    offer_path: str = ""


def clean_cell(value: str) -> str:
    return value.strip().replace("<br>", " ").replace("\\|", "|")


def escape_md(value: object) -> str:
    text = "" if value is None else str(value)
    return text.replace("\n", " ").replace("|", "\\|").strip()


def parse_markdown_table(path: Path) -> list[dict[str, str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    required_header = ["Business", "Niche", "Location", "Website", "Source", "Notes", "Status"]

    header_index = None
    header: list[str] = []
    for index, line in enumerate(lines):
        if not line.strip().startswith("|"):
            continue
        candidate = [clean_cell(cell) for cell in line.strip().strip("|").split("|")]
        if candidate[: len(required_header)] == required_header:
            header_index = index
            header = candidate
            break

    if header_index is None or header_index + 2 >= len(lines):
        return []

    rows: list[dict[str, str]] = []
    for line in lines[header_index + 2 :]:
        if not line.strip():
            continue
        if not line.strip().startswith("|"):
            break
        cells = [clean_cell(cell) for cell in line.strip().strip("|").split("|")]
        if len(cells) < len(header):
            cells += [""] * (len(header) - len(cells))
        row = dict(zip(header, cells[: len(header)]))
        if any(row.values()):
            rows.append(row)
    return rows


def load_leads(path: Path = LEADS_INPUT) -> list[Lead]:
    rows = parse_markdown_table(path)
    return [
        Lead(
            business=row.get("Business", ""),
            niche=row.get("Niche", ""),
            location=row.get("Location", ""),
            website=row.get("Website", ""),
            source=row.get("Source", ""),
            notes=row.get("Notes", ""),
            status=row.get("Status", ""),
            online_presence_status=row.get("Online Presence Status", ""),
            website_quality=row.get("Website Quality", ""),
            offer_path=row.get("Offer Path", ""),
        )
        for row in rows
    ]


def normalized(value: str) -> str:
    return value.strip().lower()


def is_missing_website(value: str) -> bool:
    return normalized(value) in MISSING_WEBSITE_VALUES


def is_weak_presence(lead: Lead) -> bool:
    return normalized(lead.online_presence_status) in WEAK_PRESENCE_VALUES or normalized(lead.website_quality) == "weak"


def domain_from_url(url: str) -> str:
    parsed = urlparse(url)
    return (parsed.netloc or "").lower().removeprefix("www.")


def is_social_url(url: str) -> bool:
    domain = domain_from_url(url)
    return any(domain == blocked or domain.endswith("." + blocked) for blocked in SOCIAL_DOMAINS)


def is_valid_public_website(url: str) -> tuple[bool, str]:
    if is_missing_website(url):
        return False, "Missing website"
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        return False, "Invalid website URL"
    domain = domain_from_url(url)
    if not domain:
        return False, "Missing domain"
    if domain == "example.com" or domain.endswith(".example.com"):
        return False, "Placeholder URL skipped"
    if is_social_url(url):
        return False, "Social/login-gated platform skipped"
    return True, ""


def robots_allows(url: str) -> tuple[bool, str]:
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    rp = RobotFileParser()
    rp.set_url(robots_url)
    try:
        rp.read()
    except Exception as exc:
        return False, f"Could not verify robots.txt: {exc}"
    if not rp.can_fetch(USER_AGENT, url):
        return False, "robots.txt disallows this URL"
    return True, ""


def fetch_visible_text(url: str) -> tuple[str, str]:
    ok, reason = is_valid_public_website(url)
    if not ok:
        return "", reason

    robots_ok, reason = robots_allows(url)
    if not robots_ok:
        return "", reason

    try:
        response = requests.get(
            url,
            headers={"User-Agent": USER_AGENT},
            timeout=TIMEOUT_SECONDS,
            allow_redirects=True,
        )
        response.raise_for_status()
    except Exception as exc:
        return "", f"Fetch failed: {exc}"

    content_type = response.headers.get("content-type", "").lower()
    if "text/html" not in content_type and "application/xhtml" not in content_type:
        return "", f"Skipped non-HTML content type: {content_type or 'unknown'}"

    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "noscript", "svg", "form"]):
        tag.decompose()
    text = " ".join(soup.get_text(" ").split())
    return text[:MAX_TEXT_CHARS], ""


def offline_text_for_lead(lead: Lead) -> str:
    return " ".join(
        value
        for value in (
            lead.notes,
            lead.online_presence_status,
            lead.website_quality,
            lead.offer_path,
            lead.niche,
            lead.source,
        )
        if value
    )


def find_signals(text: str) -> list[str]:
    lowered = text.lower()
    return [label for label, pattern in SIGNAL_PATTERNS.items() if re.search(pattern, lowered, flags=re.IGNORECASE)]


def is_home_service(niche: str) -> bool:
    lowered = niche.lower()
    return "contractor" in lowered or "contractos" in lowered or "home service" in lowered or "handyman" in lowered


def infer_pain(niche: str, signals: Iterable[str]) -> str:
    signal_text = " ".join(signals).lower()
    if "quote" in signal_text or "contact-only" in signal_text:
        return "Lead intake, quote requests, and follow-up may be manually handled."
    if "booking" in signal_text:
        return "Booking, scheduling, and confirmation may require back-and-forth messages."
    if "form" in signal_text:
        return "Form submissions may not clearly connect to a tracker or follow-up process."
    if "follow-up" in signal_text:
        return "Follow-up and confirmation may not be systematized."
    if is_home_service(niche):
        return "Quote intake and job follow-up may be hard to track."
    if "event" in niche.lower() or "wedding" in niche.lower():
        return "Inquiry, availability, and booking follow-up may be scattered."
    return "Workflow pain is possible but not strongly visible from the public page."


def score_website_lead(niche: str, text: str, signals: list[str]) -> tuple[int, str]:
    score = 25
    score += min(len(signals) * 8, 40)
    lowered = text.lower()
    if any(word in lowered for word in ("contact", "quote", "book", "schedule", "estimate")):
        score += 10
    if any(word in lowered for word in ("form", "calendar", "portal", "crm")):
        score += 5
    if any(hint in lowered for hint in NICHE_HINTS.get(niche, ())):
        score += 10
    if len(text) < 500:
        score -= 10
    score = max(0, min(100, score))
    confidence = "High" if score >= 80 else "Medium" if score >= 60 else "Low"
    return score, confidence


def score_offline_lead(niche: str, text: str, signals: list[str]) -> tuple[int, str]:
    score, _ = score_website_lead(niche, text, signals)
    if signals:
        score = max(score, 65)
    if any(word in text.lower() for word in ("quote", "estimate", "form", "follow-up", "booking")):
        score = max(score, 70)
    confidence = "High" if score >= 80 else "Medium" if score >= 60 else "Low"
    return score, confidence


def workflow_row(lead: Lead, signals: list[str], score: int, confidence: str) -> dict[str, object]:
    return {
        "Business": lead.business,
        "Niche": lead.niche,
        "Website": lead.website,
        "Visible signals": "; ".join(signals) if signals else "No strong public signals found",
        "Likely pain": infer_pain(lead.niche, signals),
        "Offer Type": "Website + Workflow Improvement Audit",
        "Offer angle": "Website + quote/contact flow audit",
        "Score /100": score,
        "Confidence": confidence,
        "Recommended next action": "Review website flow and draft mini-audit",
        "Status": "Workflow Cleanup Candidate",
    }


def starter_row(lead: Lead) -> dict[str, object]:
    return {
        "Business": lead.business,
        "Niche": lead.niche,
        "Website": lead.website or "N/A",
        "Visible signals": "No website provided / missing online presence",
        "Likely pain": "Missing or weak web presence may limit quote requests, lead capture, and follow-up.",
        "Offer Type": "Starter Site + Lead Tracker",
        "Offer angle": "Starter landing page + quote/contact form + lead tracker",
        "Score /100": 75,
        "Confidence": "Medium",
        "Recommended next action": "Generate starter site mockup",
        "Status": "Starter Site Candidate",
    }


def manual_review_row(lead: Lead, reason: str) -> dict[str, object]:
    return {
        "Business": lead.business,
        "Niche": lead.niche,
        "Website": lead.website,
        "Visible signals": reason,
        "Likely pain": "Manual review needed before analysis.",
        "Offer Type": "Manual Review Needed",
        "Offer angle": "Manual review needed",
        "Score /100": 0,
        "Confidence": "Low",
        "Recommended next action": "Manual Review Needed",
        "Status": "Manual Review Needed",
    }


def write_scored_rows(rows: list[dict[str, object]], output_path: Path = SCORED_LEADS) -> None:
    header = [
        "Business",
        "Niche",
        "Website",
        "Visible signals",
        "Likely pain",
        "Offer Type",
        "Offer angle",
        "Score /100",
        "Confidence",
        "Recommended next action",
        "Status",
    ]
    lines = [
        "# Scored Leads",
        "",
        "Source: [[03 Projects/Income Strategy Portfolio/AI Lead Scanner/Automation Workflow]]",
        "",
        "Generated by `scripts/analyze_leads.py` from manually supplied public business leads.",
        "",
        "| " + " | ".join(header) + " |",
        "|" + "|".join(["---"] * len(header)) + "|",
    ]
    for row in rows:
        lines.append("| " + " | ".join(escape_md(row.get(col, "")) for col in header) + " |")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def analyze(input_path: Path = LEADS_INPUT, output_path: Path = SCORED_LEADS, offline: bool = False) -> int:
    leads = load_leads(input_path)
    print(f"Loaded {len(leads)} leads from {input_path}")
    output: list[dict[str, object]] = []
    workflow_count = 0
    starter_count = 0
    manual_review_count = 0
    skipped_count = 0

    for lead in leads:
        if not lead.business:
            skipped_count += 1
            continue

        website = lead.website.strip()
        presence = normalized(lead.online_presence_status)

        if is_missing_website(website) or presence in WEAK_PRESENCE_VALUES or (is_weak_presence(lead) and is_missing_website(website)):
            output.append(starter_row(lead))
            starter_count += 1
            continue

        valid_url, reason = is_valid_public_website(website)
        if not valid_url:
            output.append(manual_review_row(lead, reason))
            manual_review_count += 1
            continue

        if offline:
            text = offline_text_for_lead(lead)
        else:
            robots_ok, reason = robots_allows(website)
            if not robots_ok:
                output.append(manual_review_row(lead, reason))
                manual_review_count += 1
                continue

            text, error = fetch_visible_text(website)
            if error:
                output.append(manual_review_row(lead, error))
                manual_review_count += 1
                continue

        if is_weak_presence(lead):
            output.append(starter_row(lead))
            starter_count += 1
            continue

        signals = find_signals(text)
        if offline:
            score, confidence = score_offline_lead(lead.niche, text, signals)
        else:
            score, confidence = score_website_lead(lead.niche, text, signals)
        output.append(workflow_row(lead, signals, score, confidence))
        workflow_count += 1

    write_scored_rows(output, output_path)
    print(f"Workflow cleanup candidates: {workflow_count}")
    print(f"Starter site candidates: {starter_count}")
    print(f"Manual review leads: {manual_review_count}")
    print(f"Skipped blank rows: {skipped_count}")
    print(f"Wrote {len(output)} scored rows to {output_path}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze manually supplied public business leads.")
    parser.add_argument("--input", type=Path, default=LEADS_INPUT)
    parser.add_argument("--output", type=Path, default=SCORED_LEADS)
    parser.add_argument("--offline", action="store_true", help="Use notes/status fields instead of fetching websites.")
    args = parser.parse_args()
    return analyze(input_path=args.input, output_path=args.output, offline=args.offline)


if __name__ == "__main__":
    sys.exit(main())
