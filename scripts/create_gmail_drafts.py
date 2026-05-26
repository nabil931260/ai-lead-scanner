"""Create Gmail drafts for manually approved AI Lead Scanner outreach rows.

This script creates Gmail drafts only. It never sends email and keeps the
manual review gate in Gmail.
"""

from __future__ import annotations

import base64
import html
import inspect
import argparse
import re
import sys
from dataclasses import dataclass
from email.message import EmailMessage
from pathlib import Path
from typing import Iterable


SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
PORTFOLIO_ROOT = ROOT.parent
QUEUE_PATH = ROOT / "Outreach Queue.md"
DRAFT_MESSAGES_PATH = ROOT / "Draft Messages.md"
TRACKER_PATH = PORTFOLIO_ROOT / "Outreach Tracker.md"
CREDENTIALS_PATH = SCRIPT_DIR / "credentials.json"
TOKEN_PATH = SCRIPT_DIR / "token.json"

SCOPES = ["https://www.googleapis.com/auth/gmail.compose"]
YES = "yes"

REQUIRED_QUEUE_COLUMNS = [
    "Contact Email",
    "Approved For Draft?",
    "Reviewed Mockup?",
    "Reviewed Message?",
    "Gmail Draft Created?",
    "Gmail Draft ID",
    "Gmail Draft Link",
]


@dataclass
class MarkdownTable:
    lines: list[str]
    header_index: int
    headers: list[str]
    rows: list[tuple[int, dict[str, str]]]


def print_setup_instructions() -> None:
    print("Gmail OAuth is not configured yet. No drafts were created and no emails were sent.")
    print("")
    print("Setup steps:")
    print("1. Enable the Gmail API in Google Cloud.")
    print("2. Create OAuth Desktop credentials.")
    print("3. Download the file as credentials.json.")
    print(f"4. Put credentials.json here: {CREDENTIALS_PATH}")
    print("5. Install dependencies:")
    print("   python -m pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
    print("6. Add Contact Email to Outreach Queue.md.")
    print("7. Set Approved For Draft?, Reviewed Mockup?, and Reviewed Message? to Yes for one test row.")
    print("8. Run:")
    print("   python .\\create_gmail_drafts.py")
    print("")
    print("The script is ready once credentials.json is added. It creates Gmail drafts only.")


def split_markdown_row(line: str) -> list[str]:
    stripped = line.strip()
    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|"):
        stripped = stripped[:-1]
    return [cell.strip() for cell in stripped.split("|")]


def join_markdown_row(cells: Iterable[str]) -> str:
    return "| " + " | ".join(cells) + " |"


def find_table(lines: list[str], first_header: str) -> MarkdownTable:
    header_index = -1
    for index, line in enumerate(lines):
        if line.startswith("|") and split_markdown_row(line)[0] == first_header:
            header_index = index
            break
    if header_index < 0:
        raise ValueError(f"Could not find Markdown table starting with {first_header!r}.")

    headers = split_markdown_row(lines[header_index])
    rows: list[tuple[int, dict[str, str]]] = []
    for line_index in range(header_index + 2, len(lines)):
        line = lines[line_index]
        if not line.startswith("|"):
            continue
        cells = split_markdown_row(line)
        row = {header: cells[i] if i < len(cells) else "" for i, header in enumerate(headers)}
        rows.append((line_index, row))
    return MarkdownTable(lines=lines, header_index=header_index, headers=headers, rows=rows)


def ensure_queue_columns(table: MarkdownTable) -> None:
    changed = False
    for column in REQUIRED_QUEUE_COLUMNS:
        if column not in table.headers:
            table.headers.append(column)
            changed = True
    if changed:
        table.lines[table.header_index] = join_markdown_row(table.headers)
        table.lines[table.header_index + 1] = join_markdown_row(["---"] * len(table.headers))
    for line_index, row in table.rows:
        row_changed = changed
        for column in REQUIRED_QUEUE_COLUMNS:
            if column not in row:
                row[column] = "No" if column in {"Approved For Draft?", "Reviewed Mockup?", "Reviewed Message?", "Gmail Draft Created?"} else ""
                row_changed = True
            elif not row[column].strip() and column in {"Approved For Draft?", "Reviewed Mockup?", "Reviewed Message?", "Gmail Draft Created?"}:
                row[column] = "No"
                row_changed = True
        if row_changed:
            table.lines[line_index] = join_markdown_row(row.get(header, "") for header in table.headers)


def normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip()).casefold()


def is_yes(value: str) -> bool:
    return normalize(value) == YES


def html_to_plain_text(value: str) -> str:
    value = value.replace("<br><br>", "\n\n").replace("<br>", "\n")
    value = re.sub(r"<[^>]+>", "", value)
    return html.unescape(value).strip()


def load_draft_messages() -> dict[str, dict[str, str]]:
    lines = DRAFT_MESSAGES_PATH.read_text(encoding="utf-8").splitlines()
    table = find_table(lines, "Business")
    messages: dict[str, dict[str, str]] = {}
    for _, row in table.rows:
        business = row.get("Business", "").strip()
        if business and business not in messages:
            messages[business] = row
    return messages


def get_subject_and_type(row: dict[str, str], draft_row: dict[str, str]) -> tuple[str, str]:
    subject = draft_row.get("Subject", "").strip()
    if subject:
        return subject, normalize(draft_row.get("Draft Message Type", row.get("Draft Message Type", "")))
    draft_type = normalize(draft_row.get("Draft Message Type", row.get("Draft Message Type", "")))
    offer_type = normalize(row.get("Offer Type", draft_row.get("Offer Type", "")))
    if draft_type == "existing website workflow cleanup" or offer_type == "website + workflow improvement audit":
        return "Quick workflow question", "existing website workflow cleanup"
    if draft_type == "no website starter site" or offer_type == "starter site + lead tracker":
        return "Quick website/quote flow question", "no website starter site"
    return "Manual review needed", "manual review needed"


def get_credentials():
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "Missing Gmail API dependencies. Install them with: "
            "python -m pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib"
        ) from exc

    credentials = None
    if TOKEN_PATH.exists():
        credentials = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_PATH), SCOPES)
            credentials = flow.run_local_server(port=0)
        TOKEN_PATH.write_text(credentials.to_json(), encoding="utf-8")
    return credentials


def build_raw_message(to_email: str, subject: str, body: str) -> str:
    message = EmailMessage()
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)
    return base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")


def create_gmail_draft(service, to_email: str, subject: str, body: str) -> str:
    raw_message = build_raw_message(to_email, subject, body)
    draft = service.users().drafts().create(
        userId="me",
        body={"message": {"raw": raw_message}},
    ).execute()
    return draft.get("id", "")


def extract_tracker_drafts(lines: list[str]) -> dict[str, dict[str, str]]:
    drafts: dict[str, dict[str, str]] = {}
    current_business = ""
    current_subject = ""
    body_lines: list[str] = []

    def flush() -> None:
        if current_business and current_subject and body_lines:
            body = "\n".join(body_lines).strip()
            if body:
                drafts[current_business] = {"subject": current_subject, "body": body}

    in_drafts = False
    in_body = False
    for line in lines:
        if line.startswith("## Draft Messages"):
            in_drafts = True
            continue
        if in_drafts and line.startswith("## ") and not line.startswith("## Draft Messages"):
            flush()
            break
        if not in_drafts:
            continue
        heading = re.match(r"^###\s+(?:\d+\.\s+)?(.+?)\s*$", line)
        if heading:
            flush()
            current_business = heading.group(1).strip()
            current_subject = ""
            body_lines = []
            in_body = False
            continue
        if line.startswith("Subject:"):
            current_subject = line.removeprefix("Subject:").strip()
            in_body = False
            continue
        if current_business and current_subject:
            if line.strip().startswith("Hi"):
                in_body = True
            if in_body:
                body_lines.append(line)
    else:
        flush()

    return drafts


def create_drafts_from_tracker(targets: list[str]) -> int:
    assert_no_gmail_send_calls()

    tracker_lines = TRACKER_PATH.read_text(encoding="utf-8").splitlines()
    tracker_table = find_table(tracker_lines, "Business")
    tracker_drafts = extract_tracker_drafts(tracker_lines)

    targets_normalized = {normalize(target) for target in targets}
    rows_to_create: list[tuple[int, dict[str, str], dict[str, str]]] = []
    skipped: list[str] = []
    errors: list[str] = []
    created: list[str] = []

    for line_index, row in tracker_table.rows:
        business = row.get("Business", "").strip()
        if normalize(business) not in targets_normalized:
            continue
        status = normalize(row.get("Status", ""))
        email = row.get("Email", "").strip()
        draft = tracker_drafts.get(business)
        if status in {"messaged", "sent", "follow-up due", "replied", "qualified"}:
            skipped.append(f"{business}: already contacted or beyond draft stage ({row.get('Status', '')})")
            continue
        if not email:
            skipped.append(f"{business}: Email is blank")
            continue
        if not draft:
            skipped.append(f"{business}: no matching draft message in Outreach Tracker.md")
            continue
        rows_to_create.append((line_index, row, draft))

    if not rows_to_create:
        print("No tracker rows were eligible. No drafts were created and no emails were sent.")
        for item in skipped:
            print(f"- {item}")
        return 1

    from googleapiclient.discovery import build

    credentials = get_credentials()
    service = build("gmail", "v1", credentials=credentials)

    for line_index, row, draft in rows_to_create:
        business = row.get("Business", "").strip()
        try:
            draft_id = create_gmail_draft(service, row["Email"].strip(), draft["subject"], draft["body"])
            row["Status"] = "Drafted"
            row["Last Contacted"] = ""
            row["Follow-Up Date"] = ""
            row["Next Action"] = "Review Gmail draft and send manually"
            notes = row.get("Notes", "").strip()
            draft_note = f"Gmail draft created 2026-05-10. Draft ID: {draft_id}."
            row["Notes"] = f"{notes} {draft_note}".strip()
            tracker_table.lines[line_index] = join_markdown_row(row.get(header, "") for header in tracker_table.headers)
            created.append(f"{business}: {draft_id}")
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{business}: {exc}")

    if created:
        TRACKER_PATH.write_text("\n".join(tracker_table.lines) + "\n", encoding="utf-8")

    print("Gmail tracker draft creation summary")
    print(f"Drafts created: {len(created)}")
    for item in created:
        print(f"- {item}")
    print(f"Rows skipped: {len(skipped)}")
    for item in skipped:
        print(f"- {item}")
    print(f"Errors: {len(errors)}")
    for item in errors:
        print(f"- {item}")
    print("No emails were sent. Review created drafts manually in Gmail Drafts.")
    return 0 if not errors else 1


def assert_no_gmail_send_calls() -> None:
    source = Path(__file__).read_text(encoding="utf-8")
    forbidden_patterns = [
        r"\.drafts\(\)\.send\(",
        r"\.messages\(\)\.send\(",
        r"users\(\)\.drafts\(\)\.send\(",
        r"users\(\)\.messages\(\)\.send\(",
    ]
    for pattern in forbidden_patterns:
        if re.search(pattern, source):
            raise RuntimeError("Safety check failed: Gmail send call found in source code.")
    create_source = inspect.getsource(create_gmail_draft)
    if re.search(r"\.send\(", create_source):
        raise RuntimeError("Safety check failed: create_gmail_draft contains a send call.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create Gmail drafts only. Never sends email.")
    parser.add_argument("--from-tracker", action="store_true", help="Create drafts from Outreach Tracker.md draft section.")
    parser.add_argument("--business", action="append", default=[], help="Business name to draft from Outreach Tracker.md.")
    args = parser.parse_args()

    if args.from_tracker:
        return create_drafts_from_tracker(args.business)

    assert_no_gmail_send_calls()

    if not CREDENTIALS_PATH.exists():
        print_setup_instructions()
        return 0

    queue_lines = QUEUE_PATH.read_text(encoding="utf-8").splitlines()
    queue_table = find_table(queue_lines, "Priority")
    ensure_queue_columns(queue_table)
    QUEUE_PATH.write_text("\n".join(queue_table.lines) + "\n", encoding="utf-8")
    queue_lines = QUEUE_PATH.read_text(encoding="utf-8").splitlines()
    queue_table = find_table(queue_lines, "Priority")

    draft_messages = load_draft_messages()
    approved_rows_found = 0
    drafts_created = 0
    skipped: list[str] = []
    errors: list[str] = []
    rows_to_create: list[tuple[int, dict[str, str], dict[str, str]]] = []

    for line_index, row in queue_table.rows:
        business = row.get("Business", "").strip() or f"row {line_index + 1}"
        draft_row = draft_messages.get(row.get("Business", "").strip())
        draft_type = normalize(row.get("Draft Message Type", "")) or normalize(draft_row.get("Draft Message Type", "") if draft_row else "")
        offer_type = normalize(row.get("Offer Type", "")) or normalize(draft_row.get("Offer Type", "") if draft_row else "")

        reasons = []
        if not row.get("Contact Email", "").strip():
            reasons.append("Contact Email is blank")
        if not is_yes(row.get("Approved For Draft?", "")):
            reasons.append("Approved For Draft? is not Yes")
        if not is_yes(row.get("Reviewed Message?", "")):
            reasons.append("Reviewed Message? is not Yes")
        if is_yes(row.get("Gmail Draft Created?", "")):
            reasons.append("Gmail Draft Created? is already Yes")
        if offer_type != "website + workflow improvement audit" and not is_yes(row.get("Reviewed Mockup?", "")):
            reasons.append("Reviewed Mockup? is not Yes")
        if not draft_row:
            reasons.append("No matching Draft Messages.md row")
        if draft_type == "manual review needed" or offer_type == "manual review needed":
            reasons.append("Manual review needed")

        if reasons:
            skipped.append(f"{business}: " + "; ".join(reasons))
            continue

        approved_rows_found += 1
        body = html_to_plain_text(draft_row.get("Draft message", "")) if draft_row else ""
        if not body:
            skipped.append(f"{business}: draft message is empty")
            continue
        rows_to_create.append((line_index, row, draft_row))

    if approved_rows_found == 0:
        print("No approved rows found. No drafts were created and no emails were sent.")
        print("")
        print("To approve one test draft in Outreach Queue.md:")
        print("1. Add a Contact Email.")
        print("2. Set Approved For Draft? to Yes.")
        print("3. Set Reviewed Mockup? to Yes for starter-site rows.")
        print("4. Set Reviewed Message? to Yes.")
        print("5. Leave Gmail Draft Created? as No.")

    service = None
    if rows_to_create:
        try:
            from googleapiclient.discovery import build
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "Missing Gmail API dependencies. Install them with: "
                "python -m pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib"
            ) from exc
        credentials = get_credentials()
        service = build("gmail", "v1", credentials=credentials)

    for line_index, row, draft_row in rows_to_create:
        business = row.get("Business", "").strip()
        to_email = row.get("Contact Email", "").strip()
        body = html_to_plain_text(draft_row.get("Draft message", ""))
        subject, _ = get_subject_and_type(row, draft_row)
        try:
            draft_id = create_gmail_draft(service, to_email, subject, body)
            row["Gmail Draft Created?"] = "Yes"
            row["Gmail Draft ID"] = draft_id
            row["Gmail Draft Link"] = ""
            queue_table.lines[line_index] = join_markdown_row(row.get(header, "") for header in queue_table.headers)
            drafts_created += 1
        except Exception as exc:  # noqa: BLE001 - summary should report all row errors.
            errors.append(f"{business}: {exc}")

    if drafts_created:
        QUEUE_PATH.write_text("\n".join(queue_table.lines) + "\n", encoding="utf-8")

    print("Gmail draft creation summary")
    print(f"Approved rows found: {approved_rows_found}")
    print(f"Drafts created: {drafts_created}")
    print(f"Rows skipped: {len(skipped)}")
    for item in skipped:
        print(f"- {item}")
    print(f"Errors: {len(errors)}")
    for item in errors:
        print(f"- {item}")
    print("")
    print("Gmail Draft Link is left blank because Gmail does not expose a stable direct draft URL through the API.")
    print("No emails were sent. Review any created drafts manually in Gmail Drafts.")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
