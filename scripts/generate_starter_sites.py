"""Generate local starter-site mockups for missing/weak website leads.

Reads Leads Input.md and creates local HTML files only. Nothing is published.
No outreach is sent.
"""

from __future__ import annotations

import html
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEADS_INPUT = ROOT / "Leads Input.md"
GENERATED_SITES = ROOT / "generated_sites"

MISSING_WEBSITE_VALUES = {"", "n/a", "na", "none", "no website", "no site", "not found", "unknown"}


def clean_cell(value: str) -> str:
    return value.strip().replace("<br>", " ").replace("\\|", "|")


def parse_markdown_table(path: Path) -> list[dict[str, str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    required_header = [
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
    rows = []
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


def is_missing_website(value: str) -> bool:
    return value.strip().lower() in MISSING_WEBSITE_VALUES


def should_generate(row: dict[str, str]) -> bool:
    presence = row.get("Online Presence Status", "").strip().lower()
    offer = row.get("Offer Path", "").strip().lower()
    quality = row.get("Website Quality", "").strip().lower()
    return (
        is_missing_website(row.get("Website", ""))
        or presence in {"no website found", "social only", "weak website"}
        or offer == "starter site offer"
        or quality == "missing"
    )


def slugify(value: str) -> str:
    slug = "".join(ch.lower() if ch.isalnum() else "-" for ch in value)
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug.strip("-") or "business"


def headline_for_business(row: dict[str, str]) -> str:
    business = row.get("Business", "Local service")
    niche = row.get("Niche", "").lower()
    if "paint" in niche:
        return f"Cleaner painting quotes and faster follow-up for {business}."
    if "roof" in niche:
        return f"Simple roof repair and renovation quote requests for {business}."
    if "drywall" in niche:
        return f"Fast drywall estimate requests and organized follow-up for {business}."
    if "tv mounting" in niche or "mounting" in niche:
        return f"Let customers request mounting services with the right details upfront."
    if "handyman" in niche or "contractor" in niche or "home" in niche:
        return f"Make it easier for customers to request repairs and small projects from {business}."
    return f"A clear way for customers to request service from {business}."


def subheadline_for_business(row: dict[str, str]) -> str:
    business = row.get("Business", "this business")
    location = row.get("Location", "the local area")
    return f"A local-service starter page for {business} serving {location}. Customers can request quotes, ask questions, and get a simple follow-up path."


def cta_label_for_niche(niche: str) -> str:
    lowered = niche.lower()
    if "roof" in lowered:
        return "Request a Roof Quote"
    if "paint" in lowered:
        return "Request a Painting Quote"
    if "drywall" in lowered:
        return "Request a Drywall Estimate"
    if "mounting" in lowered or "tv" in lowered:
        return "Request Mounting Help"
    if "handyman" in lowered or "contractor" in lowered or "home" in lowered:
        return "Get a Free Quote"
    return "Request a Free Quote"


def form_title_for_niche(niche: str) -> str:
    lowered = niche.lower()
    if "roof" in lowered:
        return "Request a Roof Estimate"
    if "paint" in lowered:
        return "Request a Painting Estimate"
    if "drywall" in lowered:
        return "Request a Drywall Estimate"
    if "mounting" in lowered or "tv" in lowered:
        return "Request Mounting Service"
    return "Request a Quote"


def services_for_niche(niche: str, business: str) -> list[dict[str, str]]:
    lowered = f"{niche} {business}".lower()
    if "paint" in lowered:
        return [
            {"title": "Interior Painting", "desc": "Room updates, trim, ceilings, and clean finish work."},
            {"title": "Exterior Painting", "desc": "Curb appeal and weather-ready exterior projects."},
            {"title": "Drywall Repair", "desc": "Patch holes, damage, and prep before painting."},
            {"title": "Estimates & Follow-Up", "desc": "Simple quote request handling and next-step tracking."},
        ]
    if "drywall" in lowered:
        return [
            {"title": "Drywall Repair", "desc": "Patches, cracks, and damaged wall sections."},
            {"title": "Texture Matching", "desc": "Blend repairs into existing finishes."},
            {"title": "Paint Prep", "desc": "Small project prep before paint or remodel work."},
            {"title": "Estimates & Follow-Up", "desc": "Quote requests and next-step reminders."},
        ]
    if "roof" in lowered:
        return [
            {"title": "Roof Repairs", "desc": "Leak checks, patch work, and small roof fixes."},
            {"title": "Roof Inspections", "desc": "Review damage and surface condition."},
            {"title": "Renovation Support", "desc": "Related exterior and repair work."},
            {"title": "Estimates & Follow-Up", "desc": "Quote request handling and follow-up tracking."},
        ]
    if "mounting" in lowered or "tv" in lowered:
        return [
            {"title": "TV Mounting", "desc": "Mounting service with the right wall and screen details."},
            {"title": "Shelf / Hardware Install", "desc": "Small home mounting and installation jobs."},
            {"title": "Cable Clean-Up", "desc": "Simple finish work around a mounted setup."},
            {"title": "Estimates & Follow-Up", "desc": "Request handling and next-step reminders."},
        ]
    if "handyman" in lowered or "contractor" in lowered or "home" in lowered:
        return [
            {"title": "Repairs & Maintenance", "desc": "General repair tasks and home maintenance jobs."},
            {"title": "Installations", "desc": "Fixtures, hardware, and small project installs."},
            {"title": "Drywall / Painting / Home Projects", "desc": "Common small-project work in one place."},
            {"title": "Estimates & Follow-Up", "desc": "Simple quote requests and follow-up handling."},
        ]
    return [
        {"title": "Services", "desc": "Primary work offered by this business."},
        {"title": "Estimates", "desc": "Quote requests handled in one place."},
        {"title": "Scheduling", "desc": "Simple next-step communication."},
        {"title": "Follow-Up", "desc": "Lead status and reminders."},
    ]


def render_services(cards: list[dict[str, str]]) -> str:
    return "\n".join(
        f"<article class='service-card'><h3>{html.escape(card['title'])}</h3><p>{html.escape(card['desc'])}</p></article>"
        for card in cards
    )


def html_page(row: dict[str, str]) -> str:
    business = html.escape(row.get("Business", "Business"))
    niche = html.escape(row.get("Niche", "Local service"))
    location = html.escape(row.get("Location", "Local area"))
    cta = html.escape(cta_label_for_niche(row.get("Niche", "")))
    form_title = html.escape(form_title_for_niche(row.get("Niche", "")))
    headline = html.escape(headline_for_business(row))
    subheadline = html.escape(subheadline_for_business(row))
    services = render_services(services_for_niche(row.get("Niche", ""), row.get("Business", "")))

    return f"""<!doctype html>
<!-- Generated locally by AI Lead Scanner. Review manually before sharing. -->
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{business} - Demo Starter Site</title>
  <style>
    :root {{
      --bg: #f3f4f6;
      --surface: #ffffff;
      --surface-soft: #f8fafc;
      --text: #111827;
      --muted: #4b5563;
      --line: #d1d5db;
      --brand: #0f4c5c;
      --brand-dark: #0b3945;
      --accent: #d97706;
      --accent-dark: #b45309;
      --shadow: 0 12px 32px rgba(15, 23, 42, 0.08);
      --radius: 18px;
      --radius-sm: 14px;
      --max: 1120px;
    }}
    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      margin: 0;
      background: linear-gradient(180deg, #f8fafc 0%, #eef2f7 100%);
      color: var(--text);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.55;
    }}
    a {{ color: inherit; }}
    .demo-bar {{
      position: sticky;
      top: 0;
      z-index: 20;
      background: #111827;
      color: white;
      text-align: center;
      font-size: 0.95rem;
      padding: 10px 16px;
      letter-spacing: 0.01em;
    }}
    .shell {{ max-width: var(--max); margin: 0 auto; padding: 0 20px 56px; }}
    .topbar {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      padding: 20px 0;
      position: sticky;
      top: 42px;
      background: rgba(243, 244, 246, 0.96);
      backdrop-filter: blur(8px);
      z-index: 15;
      border-bottom: 1px solid rgba(209, 213, 219, 0.7);
    }}
    .brand {{
      display: flex;
      flex-direction: column;
      gap: 2px;
    }}
    .brand strong {{ font-size: 1.05rem; }}
    .brand span {{ color: var(--muted); font-size: 0.94rem; }}
    nav {{
      display: flex;
      align-items: center;
      gap: 16px;
      flex-wrap: wrap;
      justify-content: flex-end;
      font-size: 0.95rem;
    }}
    nav a {{
      text-decoration: none;
      color: var(--muted);
    }}
    nav a.cta {{
      background: var(--accent);
      color: white;
      padding: 11px 16px;
      border-radius: 999px;
      font-weight: 700;
    }}
    .hero {{
      display: grid;
      grid-template-columns: 1.15fr 0.85fr;
      gap: 24px;
      align-items: stretch;
      padding: 18px 0 28px;
    }}
    .panel {{
      background: var(--surface);
      border: 1px solid rgba(209, 213, 219, 0.8);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
    }}
    .hero-copy {{ padding: 36px; }}
    .eyebrow {{
      display: inline-flex;
      padding: 7px 12px;
      background: rgba(15, 76, 92, 0.1);
      color: var(--brand-dark);
      border-radius: 999px;
      font-size: 0.86rem;
      font-weight: 700;
      margin-bottom: 18px;
    }}
    h1 {{
      margin: 0 0 12px;
      font-size: clamp(2rem, 4vw, 3.6rem);
      line-height: 1.04;
      letter-spacing: -0.03em;
    }}
    .hero-copy p.sub {{
      margin: 0 0 20px;
      color: var(--muted);
      font-size: 1.06rem;
      max-width: 58ch;
    }}
    .cta-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      margin: 24px 0 14px;
    }}
    .btn {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      padding: 13px 18px;
      border-radius: 999px;
      text-decoration: none;
      font-weight: 800;
      border: 1px solid transparent;
    }}
    .btn.primary {{ background: var(--brand); color: white; }}
    .btn.primary:hover {{ background: var(--brand-dark); }}
    .btn.secondary {{ background: white; border-color: var(--line); color: var(--text); }}
    .trust-row {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 10px;
      margin-top: 20px;
    }}
    .trust-pill {{
      background: var(--surface-soft);
      border: 1px solid rgba(209, 213, 219, 0.75);
      border-radius: 999px;
      padding: 10px 14px;
      text-align: center;
      font-size: 0.92rem;
      color: var(--muted);
    }}
    .hero-side {{
      padding: 28px;
      display: grid;
      gap: 14px;
    }}
    .mini-stat {{
      background: linear-gradient(180deg, rgba(15, 76, 92, 0.07), rgba(15, 76, 92, 0.03));
      border: 1px solid rgba(15, 76, 92, 0.12);
      border-radius: var(--radius-sm);
      padding: 16px;
    }}
    .mini-stat strong {{ display: block; margin-bottom: 4px; }}
    .section {{
      padding: 10px 0 4px;
      margin-top: 16px;
    }}
    .section h2 {{
      margin: 0 0 14px;
      font-size: 1.55rem;
      letter-spacing: -0.02em;
    }}
    .section p.lead {{
      margin: -4px 0 18px;
      color: var(--muted);
      max-width: 68ch;
    }}
    .grid {{
      display: grid;
      gap: 16px;
    }}
    .services-grid {{
      grid-template-columns: repeat(4, minmax(0, 1fr));
    }}
    .service-card, .info-card, .audit-card {{
      background: var(--surface);
      border: 1px solid rgba(209, 213, 219, 0.8);
      border-radius: var(--radius-sm);
      box-shadow: var(--shadow);
      padding: 20px;
    }}
    .service-card h3, .info-card h3 {{
      margin: 0 0 8px;
      font-size: 1.03rem;
    }}
    .service-card p, .info-card p, .audit-card p {{
      margin: 0;
      color: var(--muted);
    }}
    .quote-grid {{
      display: grid;
      grid-template-columns: 1.1fr 0.9fr;
      gap: 20px;
      align-items: start;
    }}
    .form-card {{
      padding: 22px;
      background: white;
      border: 1px solid rgba(209, 213, 219, 0.8);
      border-radius: var(--radius-sm);
      box-shadow: var(--shadow);
    }}
    label {{
      display: block;
      font-weight: 700;
      margin: 12px 0 6px;
    }}
    input, textarea {{
      width: 100%;
      padding: 12px 14px;
      border-radius: 12px;
      border: 1px solid var(--line);
      font: inherit;
      background: white;
      color: var(--text);
    }}
    textarea {{ min-height: 116px; resize: vertical; }}
    .form-note {{ margin-top: 12px; color: var(--muted); font-size: 0.93rem; }}
    .tracker {{
      overflow: hidden;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.95rem;
    }}
    th, td {{
      text-align: left;
      padding: 12px 14px;
      border-bottom: 1px solid var(--line);
      vertical-align: top;
    }}
    th {{ background: #f8fafc; font-size: 0.88rem; text-transform: uppercase; letter-spacing: 0.04em; color: var(--muted); }}
    .process {{
      grid-template-columns: repeat(3, minmax(0, 1fr));
    }}
    .step {{
      display: flex;
      gap: 14px;
      align-items: flex-start;
    }}
    .step-num {{
      width: 36px;
      height: 36px;
      border-radius: 50%;
      background: var(--brand);
      color: white;
      display: grid;
      place-items: center;
      font-weight: 800;
      flex: 0 0 auto;
    }}
    .faq-item + .faq-item {{ margin-top: 12px; padding-top: 12px; border-top: 1px solid var(--line); }}
    .footer {{
      margin-top: 28px;
      padding: 24px 0 8px;
      color: var(--muted);
      border-top: 1px solid rgba(209, 213, 219, 0.8);
    }}
    .footer-top {{
      display: flex;
      justify-content: space-between;
      gap: 16px;
      flex-wrap: wrap;
      align-items: center;
    }}
    .footer .btn {{ margin-top: 8px; }}
    @media (max-width: 920px) {{
      .hero, .quote-grid {{ grid-template-columns: 1fr; }}
      .services-grid, .process, .trust-row {{ grid-template-columns: 1fr 1fr; }}
      .topbar {{ align-items: flex-start; flex-direction: column; }}
      nav {{ justify-content: flex-start; }}
    }}
    @media (max-width: 620px) {{
      .shell {{ padding: 0 14px 44px; }}
      .hero-copy, .hero-side, .form-card {{ padding: 22px; }}
      .services-grid, .process, .trust-row {{ grid-template-columns: 1fr; }}
      .cta-row, nav {{ gap: 10px; }}
      .btn {{ width: 100%; }}
      nav a.cta {{ width: 100%; text-align: center; }}
      table {{ display: block; overflow-x: auto; white-space: nowrap; }}
    }}
  </style>
</head>
<body>
  <div class="demo-bar">Demo mockup for validation only. Not published. Not the official website.</div>
  <div class="shell">
    <div class="topbar">
      <div class="brand">
        <strong>{business}</strong>
        <span>{niche} serving {location}</span>
      </div>
      <nav>
        <a href="#services">Services</a>
        <a href="#service-area">Service Area</a>
        <a href="#quote">Request Quote</a>
        <a class="cta" href="#quote">{html.escape(cta_label_for_niche(row.get("Niche", "")))}</a>
      </nav>
    </div>

    <section class="hero">
      <div class="panel hero-copy">
        <span class="eyebrow">Local service provider</span>
        <h1>{headline}</h1>
        <p class="sub">{subheadline}</p>
        <div class="cta-row">
          <a class="btn primary" href="#quote">Request a Free Quote</a>
          <a class="btn secondary" href="#services">See Services</a>
        </div>
        <div class="trust-row">
          <div class="trust-pill">Local service provider</div>
          <div class="trust-pill">Fast quote follow-up</div>
          <div class="trust-pill">Simple request process</div>
        </div>
      </div>

      <aside class="panel hero-side">
        <div class="mini-stat">
          <strong>Contact path</strong>
          <span>Quote request flow designed for quick response and follow-up.</span>
        </div>
        <div class="mini-stat">
          <strong>Review focus</strong>
          <span>Starter-site concept only. Not the official website.</span>
        </div>
        <div class="mini-stat">
          <strong>Next step</strong>
          <span>Request the quote, confirm details, then complete the job.</span>
        </div>
      </aside>
    </section>

    <section id="services" class="section">
      <h2>Services</h2>
      <p class="lead">Simple service cards that make it easier for customers to know what to ask for and easier for the business to follow up.</p>
      <div class="grid services-grid">
        {services}
      </div>
    </section>

    <section class="section quote-grid" id="quote">
      <div class="form-card">
        <h2>{form_title}</h2>
        <label>Name</label>
        <input placeholder="Customer name">
        <label>Phone or email</label>
        <input placeholder="Best contact info">
        <label>Service needed</label>
        <input placeholder="Repair, estimate, installation, or other request">
        <label>Project location</label>
        <input placeholder="Address or neighborhood">
        <label>Timeline</label>
        <input placeholder="ASAP, this week, next week, or flexible">
        <label>Project details</label>
        <textarea placeholder="Describe the issue, timeline, and any helpful context"></textarea>
        <label>Optional photos note</label>
        <input placeholder="Attach photos if helpful">
        <p class="form-note">Example form only. In a real setup, submissions would feed a private lead tracker.</p>
      </div>

      <div class="grid" style="gap: 16px;">
        <div class="audit-card tracker">
          <h2>Lead Tracker</h2>
          <table>
            <thead>
              <tr>
                <th>Lead</th>
                <th>Service</th>
                <th>Status</th>
                <th>Next Follow-Up</th>
              </tr>
            </thead>
            <tbody>
              <tr><td>Example lead 1</td><td>Estimate request</td><td>New</td><td>Today</td></tr>
              <tr><td>Example lead 2</td><td>Repair request</td><td>Contacted</td><td>Tomorrow</td></tr>
              <tr><td>Example lead 3</td><td>Project quote</td><td>Estimate Sent</td><td>Follow Up Later</td></tr>
            </tbody>
          </table>
        </div>

        <div class="audit-card">
          <h2>Process</h2>
          <div class="step"><div class="step-num">1</div><div><strong>Request</strong><p>Customer submits a quote request with the right details.</p></div></div>
          <div class="step" style="margin-top: 14px;"><div class="step-num">2</div><div><strong>Confirm</strong><p>Business confirms the request, answers questions, and sets next steps.</p></div></div>
          <div class="step" style="margin-top: 14px;"><div class="step-num">3</div><div><strong>Complete</strong><p>Lead moves to the tracker until the job is finished or followed up later.</p></div></div>
        </div>
      </div>
    </section>

    <section class="section" id="service-area">
      <h2>Service Area</h2>
      <p class="lead">Serving {location} and nearby areas.</p>
    </section>

    <section class="section">
      <h2>Trust Signals</h2>
      <div class="grid services-grid">
        <article class="info-card"><h3>Clear service request process</h3><p>Customers know how to request help without guessing.</p></article>
        <article class="info-card"><h3>Organized follow-up</h3><p>Leads can be tracked from new request to completed job.</p></article>
        <article class="info-card"><h3>Mobile-friendly quote form</h3><p>The form is easy to review on a phone before a call or visit.</p></article>
        <article class="info-card"><h3>Simple lead tracking</h3><p>A spreadsheet-style workflow keeps the next action visible.</p></article>
      </div>
    </section>

    <section class="section">
      <h2>FAQ</h2>
      <div class="panel" style="padding: 20px;">
        <div class="faq-item"><strong>How do I request a quote?</strong><p>Use the form above and include the basic project details.</p></div>
        <div class="faq-item"><strong>What details should I include?</strong><p>Service needed, project location, timeline, and any photos that help explain the request.</p></div>
        <div class="faq-item"><strong>How are follow-ups tracked?</strong><p>Each request can move through a simple lead tracker with status fields like New, Contacted, Estimate Sent, and Follow Up Later.</p></div>
        <div class="faq-item"><strong>Can this connect to a spreadsheet?</strong><p>Yes. The starter concept pairs naturally with a private spreadsheet lead tracker.</p></div>
      </div>
    </section>

    <section class="section">
      <h2>Lead Tracker Explanation</h2>
      <p class="lead">This starter concept pairs the page with a basic spreadsheet or sheet-backed workflow so requests do not get lost in texts or scattered notes.</p>
    </section>

    <footer class="footer">
      <div class="footer-top">
        <div>
          <strong>{business}</strong><br>
          <span>{niche} serving {location}</span>
        </div>
        <a class="btn primary" href="#quote">{html.escape(cta_label_for_niche(row.get("Niche", "")))}</a>
      </div>
      <p style="margin-top: 16px;">Demo mockup for validation only. Not published. Not the official website.</p>
    </footer>
  </div>
</body>
</html>
"""


def main() -> int:
    rows = [row for row in parse_markdown_table(LEADS_INPUT) if should_generate(row)]
    GENERATED_SITES.mkdir(exist_ok=True)
    created = []
    seen: dict[str, int] = {}
    for row in rows:
        base_slug = slugify(row.get("Business", "business"))
        seen[base_slug] = seen.get(base_slug, 0) + 1
        final_slug = base_slug if seen[base_slug] == 1 else f"{base_slug}-{seen[base_slug]}"
        target_dir = GENERATED_SITES / final_slug
        target_dir.mkdir(exist_ok=True)
        target = target_dir / "index.html"
        target.write_text(html_page(row), encoding="utf-8")
        created.append(target)

    print(f"Generated {len(created)} local starter-site mockups.")
    for path in created:
        print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
