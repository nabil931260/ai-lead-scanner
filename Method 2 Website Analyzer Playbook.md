# Method 2 Website Analyzer Playbook

Source: [[Automation Workflow]]

Purpose: find public small-business leads manually, use the local scanner to score them, generate mini-audits and outreach drafts, then manually review and send only the best messages.

This is the current recommended workflow because it is fast enough to produce outreach volume, but still controlled enough to avoid spam, private scraping, or low-quality lead lists.

## When To Use This

Use Method 2 when the business has a public website that can be opened without logging in.

Best fit:

- local service businesses
- quote, booking, estimate, or inquiry-based businesses
- businesses where the website shows visible intake or follow-up signals
- businesses small enough that one owner/operator may care about a simple workflow fix

Avoid:

- LinkedIn, Instagram, Facebook, TikTok, Yelp profile scraping, or login-gated pages
- large franchises where the local operator likely cannot change the website or workflow
- medical, legal, financial, or sensitive workflows unless the scope is purely public website/contact-flow review
- businesses where the only contact path is a private profile or hidden email

## Method 2 In One Line

Manually find public business websites -> add them to [[Leads Input]] -> run analysis scripts -> review [[Scored Leads]], [[Mini Audits]], [[Draft Messages]], and [[Outreach Queue]] -> manually send only the best messages.

## Batch Size

Use small batches so this does not become research procrastination.

| Batch type | Size | Goal |
|---|---:|---|
| Quick test | 5 leads | Check whether one niche has obvious signals |
| Normal batch | 10 leads | Produce 3-5 outreach candidates |
| Max research batch | 30 leads | Compare niches before outreach |

Stop researching once you have 5 good candidates. Outreach and replies matter more than more leads.

## Best First Niches

Start with one niche and one city at a time.

| Priority | Niche | Why it fits |
|---:|---|---|
| 1 | cleaning services | quote requests, recurring schedules, customer follow-up |
| 2 | painters / remodelers | estimate requests, project details, follow-up windows |
| 3 | plumbers / HVAC | urgent quote requests, missed calls, service-area clarity |
| 4 | mobile detailers | text/DM booking, package confusion, repeat customers |
| 5 | tutors / coaches | inquiry intake, scheduling, parent/client follow-up |
| 6 | event vendors / caterers | availability, packages, deposits, event details |

Recommended first batch: DFW cleaning companies or painters with public contact/quote pages.

## Lead Qualification Checklist

Only add a lead if at least 3 of these are true:

- Public website is available.
- Business depends on quote, booking, estimate, or inquiry requests.
- Website has a contact form, quote form, service request page, or "call/text for estimate" language.
- Contact path is easy to find.
- Business appears local/small enough to care.
- There is a visible reason to ask about lead tracking or follow-up.
- Offer angle is obvious in one sentence.

Skip the lead if:

- It looks too corporate.
- It has no obvious intake or follow-up workflow.
- The website is only a social profile.
- You cannot explain why they might care in one sentence.
- The contact path feels spammy or private.

## How To Add Leads

Add rows to [[Leads Input]] using this format:

| Business | Niche | Location | Website | Source | Notes | Status | Online Presence Status | Website Quality | Offer Path |
|---|---|---|---|---|---|---|---|---|---|
| Example Cleaning Co | Cleaning services | Plano, TX | https://example.com/contact | Manual public review | Quote form and recurring cleaning language. | New | Has Website | Unknown | Website Analyzer |

Required fields:

- `Business`: business name
- `Niche`: plain niche label
- `Location`: city/area
- `Website`: public website URL
- `Source`: usually `Manual public review`
- `Notes`: one sentence naming the visible signal
- `Status`: `New`
- `Online Presence Status`: `Has Website`
- `Website Quality`: `Unknown`, `Weak`, or `Good`
- `Offer Path`: `Website Analyzer`

Good note examples:

- `Quote form asks for service details but no visible follow-up process.`
- `Contact page pushes phone/email for estimates; likely manual lead tracking.`
- `Services and pricing are scattered, and the next step is unclear.`
- `Recurring service language suggests customer/job tracking and follow-up needs.`

Bad note examples:

- `Looks like a good business.`
- `Maybe needs help.`
- `Could use AI.`
- `No idea.`

## Run The Workflow

From:

```powershell
D:\Obsidian\Central\03 Projects\Income Portfolio\AI Lead Scanner\scripts
```

Run:

```powershell
py -B .\analyze_leads.py
py -B .\generate_mini_audits.py --threshold 60
py -B .\build_outreach_queue.py
```

If `py` is unavailable, use:

```powershell
python .\analyze_leads.py
python .\generate_mini_audits.py --threshold 60
python .\build_outreach_queue.py
```

What each step does:

| Script | Output | Purpose |
|---|---|---|
| `analyze_leads.py` | [[Scored Leads]] | fetches supplied public websites, checks signals, scores leads |
| `generate_mini_audits.py` | [[Mini Audits]], [[Draft Messages]] | creates rule-based audit notes and draft outreach |
| `build_outreach_queue.py` | [[Outreach Queue]] | builds a manual review queue with draft/review gates |

## Review Gates Before Outreach

Do not contact a business until all are true:

- Score is 60+ or there is a clear manual reason to override.
- Mini-audit is specific, not generic.
- Draft message references a real visible signal.
- Contact email or contact form was found manually.
- You can explain the offer in one sentence.
- You are comfortable sending the message under your own name.

Use this approval sequence in [[Outreach Queue]]:

| Field | Required value |
|---|---|
| `Contact Email` | manually added email or contact-form note |
| `Reviewed Mockup?` | `Yes` or `N/A` |
| `Reviewed Message?` | `Yes` |
| `Approved For Draft?` | `Yes` only after review |
| `Gmail Draft Created?` | script updates this if draft creation is used |

## Suggested Outreach Limit

Daily cap:

- 5 reviewed sends max
- 3 is better if the messages are cold
- 1-2 follow-ups max

Do not send every generated draft. The queue exists to reject weak leads.

## What Counts As Progress

Counts:

- 10 leads manually added
- 5 mini-audits reviewed
- 3-5 messages sent manually
- replies logged
- objections and pain signals captured

Does not count:

- more scripts
- more generated mockups
- more unsent drafts
- bigger lead lists
- scored leads with no outreach

## Weekly Review

At the end of each week, record:

- leads added
- leads scored 60+
- mini-audits reviewed
- messages sent
- replies
- positive replies
- paid/testimonial pilots
- best niche
- worst niche
- wording that got replies
- next niche or next batch

If no replies after 20 targeted sends, revise niche, offer, or message before adding more automation.

## Future Automation Ladder

Move up this ladder only after reply data justifies it.

| Stage | Automation level | What changes | Requirement before moving up |
|---:|---|---|---|
| 1 | Manual search + scanner | You manually find websites and scripts score/draft. | Current stage. |
| 2 | Saved search queries | Reuse niche/city query lists and search logs. | 10 leads added and 3 reviewed sends. |
| 3 | CSV import | Paste allowed public-directory rows into a CSV and convert into [[Leads Input]]. | 20 targeted sends and one niche showing replies. |
| 4 | Google Places / SerpAPI discovery | API pulls business names/websites by niche and city. | Clear winning niche, clear offer, and budget/API key approved. |
| 5 | CRM-style pipeline | Cleaner status tracking, follow-up reminders, reply logging. | At least 3 real replies or 1 paid/testimonial pilot. |

Do not automate sending. Draft creation is acceptable; sending stays manual.
