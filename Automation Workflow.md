# Automation Workflow

Source: [[Scanner Overview]]

Purpose: keep Obsidian as the control center for a safe local lead workflow. Scripts can analyze manually supplied public business websites, but nothing sends automatically.

## Safety Rules

- Do not automate sending messages.
- Do not scrape private data.
- Do not scrape LinkedIn, Instagram, Facebook, or login-gated sites.
- Do not bypass robots.txt, platform rules, or access controls.
- Use only manually provided URLs and public business websites.
- Do not build a SaaS, Chrome extension, or CRM.
- Keep outputs in Markdown files for manual review.

## Recommended Current Workflow

Use [[Method 2 Website Analyzer Playbook]] as the main operating guide.

Use [[Lead Search Field Guide]] while finding businesses to add to [[Leads Input]].

Current recommended path:

1. Pick one niche and one city.
2. Manually find 5-10 public business websites.
3. Add only leads with a visible quote, booking, intake, or follow-up signal.
4. Use `scripts/prepare_leads.py` if the leads are still in rough pasted-row format.
5. Run the scanner scripts.
6. Review evidence columns, top mini-audits, and draft messages.
7. Use the outreach queue action category to decide the next manual step.
8. Manually send 3-5 reviewed messages.
9. Log replies and update the offer before expanding automation.

## Full Workflow

1. Manually collect public lead rows in `Raw Leads.txt` or directly in [[Leads Input]].
2. Optional: run `scripts/prepare_leads.py` to convert rough rows into the required table.
3. Run `scripts/analyze_leads.py --max-pages 5`.
4. Review evidence, pages checked, contact signals, and missing signals in [[Scored Leads]].
5. Generate mini-audits for top leads with `scripts/generate_mini_audits.py`.
6. Write outreach drafts to [[Draft Messages]].
7. Build [[Outreach Queue]] with action categories using `scripts/build_outreach_queue.py`.
8. Optional: create Gmail drafts only with `scripts/create_gmail_drafts.py`.
9. Manually review and send.
10. Log replies in [[Reply Log]] and [[03 Projects/Income Portfolio/Validation Tracker]].

## Automation Helpers

- `prepare_leads.py`: formats manually collected rows into `Leads Input.md`.
- `analyze_leads.py --max-pages 5`: checks the supplied URL plus likely same-domain contact/services/quote/FAQ pages.
- `Scored Leads.md`: includes evidence, pages checked, contact signals, and missing signals.
- `build_outreach_queue.py`: assigns action categories such as `Needs contact email`, `Needs stronger evidence`, `Needs mockup`, `Ready to review`, and `Reject / bad fit`.

## Two-Path Workflow

### Path A: Lead Has Website

Lead has website -> analyze site -> workflow mini-audit -> draft message.

Use this path when `Website` is a valid public business website and `Offer Path` is `Website Analyzer`.

### Path B: Lead Has No Website / N/A / Weak Presence

Lead has no website / N/A / weak presence -> starter site mockup -> starter site + lead tracker offer -> draft message.

Use this path when:

- `Website` is `N/A`, blank, `no website`, `no site`, `not found`, or `unknown`
- `Online Presence Status` is `No Website Found`, `Social Only`, or `Weak Website`
- `Offer Path` is `Starter Site Offer`

## Status Flow

New -> Analyzed -> Mini-Audit Created -> Draft Ready -> Draft Created in Gmail -> Reviewed -> Sent -> Replied -> Validated / Rejected

Additional status values:

- No Website Found
- Starter Site Candidate
- Site Mockup Generated
- Draft Ready
- Manual Review Needed

## Manual Review Gates

- A lead must be manually entered before analysis.
- A mini-audit must be reviewed before any message is used.
- A Gmail draft, if created, must be manually reviewed before sending.
- Replies are the only validation signal that counts.

## Manual Review Before Outreach

Before contacting any business:

- Review generated site.
- Review mini-audit.
- Edit message.
- Do not send if the mockup looks generic or inaccurate.
- Do not claim this is their official site.
- Ask permission before sending the mockup.
- Log replies in [[Reply Log]].

## Two-Offer Outreach Strategy

Path A:
Existing website -> Website + Workflow Improvement Audit -> draft mini-audit message -> Gmail draft -> manual review/send.

Path B:
No website / weak website -> Starter Site + Lead Tracker -> local mockup -> draft message -> Gmail draft -> manual review/send.

## Gmail Draft Creation Flow

Leads and drafts are generated locally, then approved rows can be turned into Gmail drafts.

Manual gates:

- Contact Email must be added manually.
- Mockup must be reviewed.
- Message must be reviewed.
- Approved For Draft? must be Yes.
- Gmail draft must be manually reviewed and sent.

## Stop Rule

Stop after 30 public leads, 10 scored leads, and 5 mini-audits. Do not keep improving automation instead of testing real demand.

If no replies come from 20 targeted sends, revise the niche, offer, or message before adding more automation.
