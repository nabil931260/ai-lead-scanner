# AI Lead Scanner Scripts

These scripts support a local Obsidian-controlled MVP. They do not send messages and should only process manually provided public business website URLs.

Main workflow docs:

- `../Method 2 Website Analyzer Playbook.md`
- `../Lead Search Field Guide.md`

## Run The Public Demo

The demo uses fake `.test` domains, stays offline, and writes only to `../examples/output/`.

```powershell
py -B .\run_demo.py
```

Generated files:

```text
../examples/output/Scored Leads.md
../examples/output/Mini Audits.md
../examples/output/Draft Messages.md
../examples/output/Outreach Queue.md
```

## Install Dependencies

From this folder:

```powershell
python -m pip install requests beautifulsoup4
```

`pandas` is optional and not required by the current scripts.

## Add Leads

Add real public business websites to:

```text
../Leads Input.md
```

Use only:

- Public business websites
- Manually supplied URLs
- Pages accessible without login

Do not use:

- LinkedIn
- Instagram
- Facebook
- TikTok
- Login-gated pages
- Private profiles
- Scraped lists
- Sensitive personal data

## Run Lead Analysis

### Path A: Website Analyzer

```powershell
py -B .\analyze_leads.py
py -B .\generate_mini_audits.py --threshold 60
py -B .\build_outreach_queue.py
```

Updates:

```text
../Scored Leads.md
../Mini Audits.md
../Draft Messages.md
../Outreach Queue.md
```

What it does:

- Reads `Leads Input.md`
- Checks URL safety
- Checks robots.txt
- Fetches only the supplied public page
- Extracts visible text
- Looks for workflow pain signals
- Scores leads
- Writes results back to Obsidian

Use Path A for leads with a valid public business website.

To run against explicit paths instead of the private root files:

```powershell
py -B .\analyze_leads.py --input "..\examples\Leads Input.example.md" --output "..\examples\output\Scored Leads.md" --offline
py -B .\generate_mini_audits.py --input "..\examples\output\Scored Leads.md" --audits-output "..\examples\output\Mini Audits.md" --drafts-output "..\examples\output\Draft Messages.md" --threshold 60
py -B .\build_outreach_queue.py --scored "..\examples\output\Scored Leads.md" --drafts "..\examples\output\Draft Messages.md" --output "..\examples\output\Outreach Queue.md"
```

### Path B: Starter Site Offer

```powershell
py -B .\analyze_leads.py
py -B .\generate_starter_sites.py
py -B .\generate_mini_audits.py --threshold 50
py -B .\build_outreach_queue.py
```

Use Path B for leads where:

- `Website` is `N/A`, blank, `no website`, `no site`, `not found`, or `unknown`
- `Online Presence Status` is `No Website Found`, `Social Only`, or `Weak Website`
- `Offer Path` is `Starter Site Offer`

Generated sites stay local in:

```text
../generated_sites/[slug]/index.html
```

Nothing is published and nothing is sent automatically.

## Regenerate Better Starter Sites

```powershell
py -B .\generate_starter_sites.py
py -B .\build_outreach_queue.py
```

This overwrites local mockups and rebuilds the manual review queue, but it does not publish anything.

## Generate Mini-Audits And Draft Messages

```powershell
py -B .\generate_mini_audits.py --threshold 70
py -B .\build_outreach_queue.py
```

Updates:

```text
../Mini Audits.md
../Draft Messages.md
```

What it does:

- Reads `Scored Leads.md`
- Selects leads at or above the threshold
- Generates rule-based mini-audits
- Generates draft outreach messages
- Generates workflow-cleanup drafts for existing websites
- Generates starter-site drafts for no-site and weak-presence leads
- Sends nothing

## Two-Offer Outreach Strategy

- Existing website -> Website + Workflow Improvement Audit
- No website / weak website -> Starter Site + Lead Tracker

Use the first lane when the business already has a website and the opportunity is about improving quote/contact flow, intake, lead tracking, service-area clarity, FAQ structure, or follow-up handling.

Use the second lane when the business has no website, an N/A website, social-only presence, or a very weak web presence.

## Gmail Draft Creation

Steps:
1. Enable Gmail API in Google Cloud.
2. Create OAuth Desktop credentials.
3. Download credentials.json.
4. Put credentials.json in the scripts folder.
5. Install dependencies:
   `python -m pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib`
6. Add Contact Email to Outreach Queue.md.
7. Set Approved For Draft?, Reviewed Mockup?, and Reviewed Message? to Yes.
8. Run:
   `python .\create_gmail_drafts.py`
9. Open Gmail Drafts and manually review/send.

This creates Gmail drafts only. It never sends emails automatically, never calls Gmail send endpoints, and requires manual Gmail review before anything is sent.

## Safety Rules

- Do not automate sending.
- Do not scrape private data.
- Do not scrape LinkedIn, Instagram, Facebook, or login-gated sites.
- Do not bypass robots.txt, platform rules, or access controls.
- Use only manually supplied public business URLs.
- Do not collect personal/private contact data.
- Do not build a SaaS, Chrome extension, or CRM.
- Keep Obsidian as the control center.

## Stop Rule

Do not improve the scripts until:

- 10 real public business URLs have been manually added
- `Scored Leads.md` has usable scores
- 5 mini-audits have been reviewed
- at least 1 manual outreach decision has been made

Do not move to API-based lead discovery until at least 20 targeted manual sends have been attempted and the reply data shows which niche/message is worth scaling.

