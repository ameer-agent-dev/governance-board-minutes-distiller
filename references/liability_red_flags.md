# Liability Red Flags and Anti-Discovery Scrubbing Guide

## Contents

- [Why Verbose Minutes Create Legal Liability](#why-verbose-minutes-create-legal-liability)
- [Prohibited Debate and Emotional Verbs](#prohibited-debate-and-emotional-verbs)
- [Verbatim Quote Hazards](#verbatim-quote-hazards)
- [HOA and Public Comment Forum Rules](#hoa-and-public-comment-forum-rules)
- [Executive Session Leak Categories](#executive-session-leak-categories)
- [Before-and-After Scrubbing Examples](#before-and-after-scrubbing-examples)
- [Manual Fallback Checklist](#manual-fallback-checklist)
- [Counsel Verification Note](#counsel-verification-note)

## Why Verbose Minutes Create Legal Liability

Board minutes are discoverable business records in civil litigation, employment disputes, regulatory audits, and HOA member challenges. Including raw "he-said/she-said" narratives, speculative opinions, or off-hand remarks can waive attorney-client privilege, expose individual directors to defamation or breach-of-fiduciary-duty claims, and create contradictions against official corporate resolutions.

## Prohibited Debate and Emotional Verbs

Remove all attributive or emotional verbs describing how directors spoke or felt during deliberations. `scripts/lint_board_minutes.py` flags these terms automatically:

- `accused`, `alleged`, `argued`, `attacked`, `blamed`
- `claimed`, `complained`, `criticized`, `demanded`, `disagreed`
- `fumed`, `insisted`, `interrupted`, `protested`, `ranted`
- `snapped`, `vented`, `yelled`

Replace attributed debate blocks with a single neutral sentence: `Discussion was held regarding [Topic].`

## Verbatim Quote Hazards

- Never include double-quoted speech from directors, staff, or guests in narrative sections.
- Quoted language is permitted only inside formal motion text when quoting a specific resolution clause or contract title.
- Summarizing a director's rationale for a "no" vote is unnecessary unless the director formally requests a recorded dissent under bylaws; otherwise record only the numeric tally (for example, `Carried 4-1`).

## HOA and Public Comment Forum Rules

Homeowner and public comment sessions frequently contain personal grievances, unverified accusations, and neighbor disputes.

- **Never** transcribe individual homeowner rants, complaints, or accusations.
- **Never** list individual homeowner names or unit numbers alongside complaints.
- **Always** condense the entire period to one neutral line: `Open Homeowner Forum was held from HH:MM to HH:MM.` (or `Public Comment Period was held from HH:MM to HH:MM.`). If timestamps are missing, insert `[SECRETARY VERIFY: Open Homeowner Forum Start/End Times]`.

## Executive Session Leak Categories

Move these topics strictly to `executive_session_record.md` and keep specific details out of `official_minutes_draft.md`:

- **Personnel and HR**: Terminations, disciplinary actions, performance reviews, severance terms, or named employee complaints.
- **Delinquencies and Collections**: Past-due assessment balances, homeowner names, unit numbers, payment plans, liens, or foreclosure steps.
- **Pending or Threatened Litigation**: Settlement figures, opposing counsel correspondence, legal risk assessments, or privileged attorney advice.
- **Sensitive Contract or Real Estate Negotiations**: Confidential bid strategies or unexecuted negotiation ceilings.

## Before-and-After Scrubbing Examples

### Example 1: Heated Vendor Debate

- **Raw notes (unsafe)**: `Bob argued for 20 minutes that Vendor A was "a total rip-off" and accused Mary of rushing the roof bid. Mary insisted Vendor B had better warranty terms. Eventually Bob voted no and everyone else approved Vendor B for $117,214.`
- **Distilled minutes (safe)**: `Discussion was held regarding roof replacement vendor proposals. Motion: To approve the roof replacement contract with Vendor B in the amount of $117,214. Moved by: [Mover]. Seconded by: [Seconder]. Vote Result: Carried 4-1.`

### Example 2: HOA Homeowner Complaint

- **Raw notes (unsafe)**: `Mrs. Jenkins in Unit 4B ranted for 10 minutes that the pool gate is broken and complained that management ignores emails.`
- **Distilled minutes (safe)**: `Open Homeowner Forum was held from 18:10 to 18:25.`

### Example 3: Executive Session Leak

- **Raw notes (unsafe)**: `Moved into closed session at 19:15 to discuss terminating Jane Doe for attendance issues and sending Unit 302 (John Smith, $4,200 delinquent) to collections. Returned at 19:45.`
- **Distilled open minutes (safe)**: `The Board entered Executive Session at 19:15 to discuss Personnel/HR and Member Delinquency matters and returned to Open Session at 19:45. See executive_session_record.md.`

## Manual Fallback Checklist

Use this checklist if `scripts/lint_board_minutes.py` cannot be executed in the current environment:

1. Confirm total word count is under 800 words for a standard 1-to-2-hour meeting.
2. Confirm zero double-quoted speech appears outside formal motion text.
3. Confirm zero prohibited debate or emotional verbs appear anywhere in the draft.
4. Confirm quorum is explicitly declared and attendance math matches the threshold.
5. Confirm every motion has an explicit mover, vote result, and either a seconder or `Consensus action noted without formal second - [SECRETARY VERIFY]`.
6. Confirm zero employee names, homeowner names, unit numbers, delinquency figures, or litigation details appear in `official_minutes_draft.md`.
7. Confirm every missing date, time, or threshold is flagged with `[SECRETARY VERIFY: ...]`.

## Counsel Verification Note

This skill produces draft administrative records aligned with general Robert's Rules of Order practices and does not constitute legal advice. Secretaries should confirm state-specific statutory disclosure, Sunshine Law, and executive-session notice rules with corporate or association counsel prior to publication.
