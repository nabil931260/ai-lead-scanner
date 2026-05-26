# AI Lead Scanner

A small local tool for finding and reviewing public small-business leads before doing manual outreach.

I built this because I wanted a better way to decide which local businesses were actually worth contacting. A big list of names is not useful by itself. I needed a workflow that could take a small batch of public business websites, look for visible quote/contact/follow-up signals, score the leads, and prepare a review queue without sending anything automatically.

This project is intentionally conservative. It does not scrape private platforms, it does not automate cold outreach, and it does not send email. The goal is to support careful manual research, not blast messages.

## What It Does

- Reads a manually created Markdown table of leads.
- Converts simple pasted lead rows into the required Markdown lead table.
- Checks whether each website is a valid public business site.
- Skips social platforms and login-gated URLs.
- Checks `robots.txt` before fetching a page.
- Pulls visible page text from supplied URLs and a small set of likely same-domain pages.
- Looks for workflow signals like quote requests, contact-only intake, booking language, service menus, and follow-up wording.
- Records evidence, pages checked, contact signals, and missing signals so scores can be reviewed.
- Scores each lead and classifies it as:
  - website/workflow cleanup candidate
  - starter-site candidate
  - manual review needed
- Generates short rule-based mini-audits.
- Builds a manual outreach queue.
- Adds next-action categories like `Needs contact email`, `Needs mockup`, and `Ready to review`.
- Optionally creates Gmail drafts after explicit approval flags are set.

## What It Does Not Do

- It does not send emails.
- It does not scrape LinkedIn, Instagram, Facebook, TikTok, or private profiles.
- It does not bypass login walls or access controls.
- It does not collect hidden contact data.
- It does not replace manual review.

## Why This Exists

The first version was built around a local service idea: helping small businesses clean up lead/quote intake and follow-up workflows.

For example, a painting or remodeling business might have a quote form, a phone number, and an email address, but no obvious way to keep track of who needs follow-up after the request comes in. This tool helps spot those situations from public website signals and prepares a small audit-style workflow for review.

It is not meant to prove demand by itself. A scored lead is just a lead. Real validation starts when a business replies and describes an actual workflow problem.

## Project Structure

```text
.
|-- scripts/
|   |-- prepare_leads.py
|   |-- analyze_leads.py
|   |-- generate_mini_audits.py
|   |-- build_outreach_queue.py
|   |-- create_gmail_drafts.py
|   |-- generate_starter_sites.py
|   `-- run_demo.py
|-- examples/
|   |-- Raw Leads.example.txt
|   |-- Leads Input.example.md
|   |-- output/
|   |   |-- Scored Leads.md
|   |   |-- Mini Audits.md
|   |   |-- Draft Messages.md
|   |   `-- Outreach Queue.md
|   `-- Outreach Queue.example.md
|-- Automation Workflow.md
|-- Lead Search Field Guide.md
|-- Lead Scorecard.md
|-- Method 2 Website Analyzer Playbook.md
|-- Opportunity Signals.md
|-- requirements.txt
`-- README.md
```

## Try The Demo

The fastest way to see the project work is to run the fake-data demo. It uses only example `.test` domains and does not fetch websites, create Gmail drafts, or touch private working files.

```powershell
py -B .\scripts\run_demo.py
```

Generated demo files appear in:

```text
examples/output/
```

This is the best path for reviewing the project on GitHub because it shows the full workflow without requiring Gmail setup or real leads.

## Setup

Use Python 3.12 or a recent Python 3 version.

```powershell
py -m pip install -r requirements.txt
```

If you only want to run lead analysis and mini-audit generation, the main required packages are:

```powershell
py -m pip install requests beautifulsoup4
```

The Gmail packages are only needed if you want to create Gmail drafts.

## Basic Workflow

Use this workflow for private/local batches after you have reviewed the demo.

Start by copying the example lead file:

```powershell
Copy-Item ".\examples\Leads Input.example.md" ".\Leads Input.md"
```

Edit `Leads Input.md` manually. Add only public business websites that you intentionally reviewed.

If you have a rough pasted list first, you can format it into the expected table:

```powershell
Copy-Item ".\examples\Raw Leads.example.txt" ".\Raw Leads.txt"
py -B .\scripts\prepare_leads.py --input ".\Raw Leads.txt" --output ".\Leads Input.md"
```

Then run:

```powershell
py -B .\scripts\analyze_leads.py --max-pages 5
py -B .\scripts\generate_mini_audits.py --threshold 60
py -B .\scripts\build_outreach_queue.py
```

Outputs:

```text
Scored Leads.md
Mini Audits.md
Draft Messages.md
Outreach Queue.md
```

Review the outputs manually before using anything.

`Scored Leads.md` includes evidence columns so you can see why a lead scored the way it did. `Outreach Queue.md` includes an action category so the next manual step is easier to choose.

You can also run the scripts against explicit input/output paths:

```powershell
py -B .\scripts\analyze_leads.py --input ".\examples\Leads Input.example.md" --output ".\examples\output\Scored Leads.md" --offline
py -B .\scripts\generate_mini_audits.py --input ".\examples\output\Scored Leads.md" --audits-output ".\examples\output\Mini Audits.md" --drafts-output ".\examples\output\Draft Messages.md" --threshold 60
py -B .\scripts\build_outreach_queue.py --scored ".\examples\output\Scored Leads.md" --drafts ".\examples\output\Draft Messages.md" --output ".\examples\output\Outreach Queue.md"
```

## Lead Input Format

`Leads Input.md` expects a Markdown table with these columns:

```text
Business
Niche
Location
Website
Source
Notes
Status
Online Presence Status
Website Quality
Offer Path
```

Example row:

```markdown
| Example Painting Co | Painting services | Plano, TX | https://example-painting.test/contact | Manual public review | Quote form asks for project details, so follow-up may be tracked manually. | New | Has Website | Unknown | Website Analyzer |
```

## Optional Gmail Drafts

The Gmail draft step is optional and should be treated carefully.

To use it:

1. Enable the Gmail API in Google Cloud.
2. Create OAuth Desktop credentials.
3. Save the file as `scripts/credentials.json`.
4. Make sure `credentials.json` and `token.json` are ignored by git.
5. Add a contact email to `Outreach Queue.md`.
6. Set `Approved For Draft?` and `Reviewed Message?` to `Yes`.
7. Run:

```powershell
py -B .\scripts\create_gmail_drafts.py
```

The script creates drafts only. It includes a safety check to prevent Gmail send calls from being added accidentally.

## Safety Notes

This project is designed around a few rules:

- Use public business websites only.
- Respect `robots.txt`.
- Do not scrape social media or private profiles.
- Do not automate sending.
- Keep outreach review manual.
- Do not treat generated drafts as final copy.

These constraints make the tool slower than a scraper, but they keep the workflow closer to actual customer discovery.

## Current Limitations

- The site analysis is rule-based, not an LLM.
- It only fetches the supplied page, not an entire website crawl.
- Multi-page analysis is intentionally shallow and capped by `--max-pages`.
- Some useful sites are skipped because of `robots.txt` or `403` responses.
- Scoring is a heuristic and needs human judgment.
- Gmail draft creation requires local OAuth setup.

## Next Improvements

- Safer CSV import/export.
- A simple HTML report for a scored batch.

## Status

Working local prototype. Useful for small manual batches and portfolio demonstration, but not a production lead-generation system.
