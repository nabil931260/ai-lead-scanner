"""Run the public fake-data demo without touching private root files."""

from __future__ import annotations

import sys
from pathlib import Path

import analyze_leads
import build_outreach_queue
import generate_mini_audits


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"
OUTPUT = EXAMPLES / "output"


def main() -> int:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    leads = EXAMPLES / "Leads Input.example.md"
    scored = OUTPUT / "Scored Leads.md"
    audits = OUTPUT / "Mini Audits.md"
    drafts = OUTPUT / "Draft Messages.md"
    queue = OUTPUT / "Outreach Queue.md"

    analyze_leads.analyze(input_path=leads, output_path=scored, offline=True)
    generate_mini_audits.generate(input_path=scored, audits_output=audits, drafts_output=drafts, threshold=60)
    rows = build_outreach_queue.build_queue(
        scored_path=scored,
        drafts_path=drafts,
        queue_path=queue,
        generated_sites_path=OUTPUT / "generated_sites",
    )
    build_outreach_queue.write_queue(rows, queue)

    print("Demo complete. Generated:")
    for path in (scored, audits, drafts, queue):
        print(f"- {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
