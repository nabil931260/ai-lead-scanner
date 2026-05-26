# Scanner Prompt Library

Source: [[Scanner Overview]]

Use these prompts with manually gathered or public information only. Do not paste private data, sensitive personal data, or login-gated content.

## Scoring A Lead

```text
Act as a practical lead scoring assistant. Score this lead for my Income Strategy Portfolio.

Context:
- I am validating small business workflow automation, student org/frat workflow pain, and CS student job-search workflows.
- Do not invent facts.
- Use only the information I provide.
- A lead score is not validation.

Lead info:
[paste manual/public notes here]

Score out of 100 using:
- Likely pain level: 20
- Ease of contacting: 10
- Likelihood of reply: 15
- AI/workflow automation fit: 15
- Revenue potential: 10
- Warmth of relationship: 10
- Evidence quality: 10
- Next best action clarity: 10

Return:
- Score /100
- Confidence: High/Medium/Low
- Likely pain point
- Offer angle
- Recommended message
- Next best action
- What not to assume
```

## Writing A Mini-Audit

```text
Create a short mini-audit for this lead.

Rules:
- Use only the info provided.
- Do not pretend public clues prove private workflow pain.
- Keep the audit practical and short.
- End with one low-pressure question to ask.

Lead info:
[paste manual/public notes here]

Output:
- Lead name
- Segment
- Source/public clue
- What I noticed
- Possible workflow problem
- Current workaround guess
- Simple manual/no-code fix
- AI-assisted fix
- Offer angle
- One question to ask
- Suggested outreach message
- Confidence level
- Next step
```

## Identifying Workflow Pain From Public Info

```text
Review these public/manual notes and identify possible workflow pain signals.

Rules:
- Do not infer private facts.
- Separate visible signals from guesses.
- Focus on boring workflows: booking, intake, spreadsheets, follow-up, member lists, dues/payments, event RSVPs, job applications.

Notes:
[paste public/manual notes here]

Return:
- Visible signals
- Possible pain points
- Current workaround guesses
- Best segment fit
- Best question to ask
- Confidence level
```

## Generating A Casual Outreach Message

```text
Write a casual, non-salesy outreach message for this lead.

Rules:
- Do not pitch a finished product.
- Ask about their current workflow.
- Keep it short.
- Sound natural.
- No hype.
- No pressure.

Lead:
[paste lead info]

Message goal:
[small business spreadsheet cleanup / student org workflow / CS career workflow]

Return:
- Message
- Follow-up if they reply with a real problem
- What to log if they answer
```

## Prioritizing Top 10 Leads

```text
Prioritize these leads for manual outreach.

Rules:
- Prefer warm or semi-warm leads.
- Prefer visible workflow pain.
- Prefer clear next question.
- Do not prioritize generic leads just because they look impressive.

Lead list:
[paste scored leads]

Return a table:
- Rank
- Lead
- Segment
- Score
- Why message first
- Message angle
- Risk/uncertainty
- Move to Outreach Tracker? Yes/No
```

## Moving Qualified Leads Into Outreach Tracker.md

```text
Convert these qualified leads into Outreach Tracker rows.

Rules:
- Do not add private data.
- Keep notes short.
- Use only the information provided.
- Recommended message must match one of the project outreach angles.

Qualified leads:
[paste leads]

Return rows with:
- Date
- Name
- Segment or Role/org
- Contact method
- Message version
- Pain point
- Next step
- Notes
```

## Checking Whether I Am Overbuilding Or Avoiding Outreach

```text
Act as a direct project accountability advisor.

Current scanner work:
[describe what I have done]

Check whether I am still using the scanner correctly.

Answer:
- Is this supporting outreach or replacing outreach?
- What is the next smallest useful action?
- What should I stop building?
- What must be true before I add another feature?
- Should I send 1-3 messages now?

Be honest and concise.
```
