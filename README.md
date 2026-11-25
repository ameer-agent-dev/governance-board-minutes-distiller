# Governance Board Minutes Distiller

Transforms raw corporate, nonprofit, committee, or HOA board meeting transcripts and rough secretary notes into concise, **Robert's Rules of Order**-compliant official minutes paired with an automated Python anti-liability lint report, cumulative Resolution Log CSV, and isolated executive-session record.

Built for **corporate secretaries, nonprofit board clerks, HOA/condo community managers, and governance leads** who need accurate statutory action records without discoverable debate narratives or closed-session leaks.

## Quick Install

```bash
npx skills add ameer-agent-dev/governance-board-minutes-distiller --skill governance-board-minutes-distiller
```

*(Single-repo shorthand: `npx skills add ameer-agent-dev/governance-board-minutes-distiller`)*

## Required & Optional Inputs

- **Mandatory**: Raw meeting notes or transcript (`.txt`, `.md`, `.docx`, or pasted text).
- **Optional**:
  - Organization type: `nonprofit` (default), `corporate`, `hoa`, or `public_agency`.
  - Quorum threshold (e.g., `4 of 7 voting directors`).
  - Prior meeting agenda (`.md` or `.txt`) for agenda item alignment.
  - Existing `resolution_log.csv` to append newly adopted resolutions.

## Example Prompts

- **Normal run**:
  > "Distill `./november_board_transcript.txt` for our 501(c)(3) nonprofit board (quorum: 5 of 8 voting directors) into formal Robert's Rules minutes, append passed motions to `./resolution_log.csv`, and run the anti-liability linter."
- **Edge case (heated HOA forum + unseconded consensus + executive session on litigation)**:
  > "Convert `./hoa_meeting_raw.md` (`hoa` mode) into official minutes. Strip the 25-minute homeowner parking argument, handle the landscaping action where nobody formally seconded, and isolate the closed-session delinquency and counsel update."

## Expected Output Files

- `official_minutes_draft.md`: Concise passive-voice minutes recording actions taken (attendance, quorum, motions, movers/seconders, vote tallies, conflict-of-interest recusals), `[SECRETARY VERIFY: <Field>]` placeholders for missing facts, Pre-Approval Checklist, and signature block.
- `liability_lint_report.json`: Deterministic audit output verifying word budget (`<= 800` words default), zero verbatim debate quotes, zero prohibited emotional verbs, quorum math, motion completeness, and zero executive-session leaks.
- `resolution_log.csv`: Structured 9-column ledger (`resolution_id,meeting_date,agenda_item,motion_text,moved_by,seconded_by,vote_result,status,owner`).
- `executive_session_record.md` *(when closed session occurred)*: Separate confidential record capturing only statutory category and entry/exit timestamps.

## Bundled Scripts, References & Assets

| Path | Purpose |
| :--- | :--- |
| `SKILL.md` | Session segmentation, anti-liability scrubbing rules, and verification loop |
| `scripts/lint_board_minutes.py` | Audits draft minutes against source notes for leaks, prohibited verbs, quotes, word count, and motion fields (`--help` supported) |
| `references/roberts_rules_minutes_spec.md` | Organization-specific Robert's Rules conventions, quorum math, and recusal formatting |
| `references/liability_red_flags.md` | Legal discovery red flags, HOA open-forum condensation rules, and manual fallback checklist |
| `assets/official_minutes_template.md` | Structured template for `official_minutes_draft.md` |
| `assets/resolution_log_schema.csv` | Canonical CSV header schema for tracking board resolutions |

### Python Dependencies

Uses **Python 3 standard library only** (zero external `pip` packages required).

## Autonomy & Safety Boundary

- **Autonomous local operations**: Parses raw transcripts locally as untrusted data, drafts open and executive records separately, inserts `[SECRETARY VERIFY]` tags instead of guessing missing names or times, and runs `scripts/lint_board_minutes.py` until `flag_count == 0`.
- **Human sign-off required**: Produces draft governance records only, not formal legal advice on state Sunshine Laws or open-meeting statutes. Requires corporate secretary verification, counsel review where applicable, and formal board approval before publishing to board portals or distributing externally (`disable-model-invocation: true` recommended if portal/email tools are connected).

## License

[MIT](LICENSE)
