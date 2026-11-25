# Robert's Rules Board Minutes Specification

## Contents

- [Core Principle: Record What Was Done](#core-principle-record-what-was-done)
- [Mandatory Sections](#mandatory-sections)
- [Quorum Math and Attendance](#quorum-math-and-attendance)
- [Formal Motions and Informal Consensus](#formal-motions-and-informal-consensus)
- [Conflict-of-Interest Recusals](#conflict-of-interest-recusals)
- [Organization-Type Nuances](#organization-type-nuances)
- [Executive Session Boundaries](#executive-session-boundaries)
- [Pre-Approval Secretary Checklist](#pre-approval-secretary-checklist)

## Core Principle: Record What Was Done

Under Robert's Rules of Order Newly Revised (RONR), official minutes are a legal record of actions taken by the body, not a transcript of what was said. Keep standard 1-to-2-hour meeting minutes concise (target under 800 words) and written in neutral, passive or objective third-person voice.

## Mandatory Sections

Every `official_minutes_draft.md` must include:

- **Header**: Full organization name, organization type, meeting type (Regular, Special, or Annual), date, start time, and physical location or remote video platform.
- **Attendance and Quorum**: Voting members present, voting members absent, non-voting guests or staff present, and an explicit statement of whether a quorum was established.
- **Approval of Prior Minutes**: Date of prior meeting minutes and formal action (approved as presented, approved as amended, or deferred).
- **Agenda Items and Formal Motions**: Neutral one-line topic summary (`Discussion was held regarding [Topic].`) paired with exact formal motion wording, mover, seconder, and vote outcome.
- **Conflict-of-Interest Recusals**: Recorded explicitly whenever a director discloses a conflict and abstains or leaves the room.
- **Executive Session Reference**: Only if a closed session occurred, record entry time, exit time, and permitted statutory category, pointing to `executive_session_record.md`.
- **Adjournment**: Exact adjournment timestamp and method (motion or unanimous consent).
- **Signature Block**: Secretary name, draft date, and approval date line.

## Quorum Math and Attendance

- Default quorum is a simple majority of voting directors (`floor(total / 2) + 1`) unless bylaws specify a different threshold.
- Record voting members separately from non-voting guests, property managers, or executive staff so guests are never counted toward quorum.
- If the source notes omit the quorum threshold or total voting seats, do not guess. Write `[SECRETARY VERIFY: Quorum Threshold]` and list it in the Pre-Approval Checklist.
- If quorum is lost mid-meeting due to departures or recusals (where bylaws require quorum to remain present), note the time quorum was lost and flag any subsequent votes with `[SECRETARY VERIFY: Quorum Validity]`.

## Formal Motions and Informal Consensus

- Record exact final motion text as voted on (incorporating accepted amendments).
- Record `Moved by`, `Seconded by`, and `Vote Result` (such as `Unanimous`, `Carried 4-1`, `Carried 4-0-1 (1 abstention)`, or `Failed 2-3`).
- Do not record withdrawn motions unless required by organizational bylaws.
- **Informal consensus without a formal second**: If the board took action without a recorded seconder, never invent a name. Record `Consensus action noted without formal second - [SECRETARY VERIFY]` in the seconder or vote notes column.

## Conflict-of-Interest Recusals

Conflict-of-interest recusals are legally protective for fiduciary duty and tax-exempt governance (such as IRS Form 990 compliance for 501(c)(3) nonprofits):

- Preserve the recusing director's name, the agenda item or vendor involved, and whether the director exited the room and abstained from voting.
- Remove any emotional debate or side commentary surrounding the conflict.
- Example neutral phrasing: `Director Patel disclosed a potential conflict of interest regarding Agenda Item 4.2, exited the room during deliberation, and recused from the vote.`

## Organization-Type Nuances

- **`nonprofit` (default)**: Emphasize fiduciary diligence, conflict-of-interest recusals, grant or budget approvals, and committee delegations.
- **`corporate`**: Emphasize formal resolutions (`RESOLVED, that...`), officer authorizations, equity or debt approvals, and stockholder or charter references.
- **`hoa`**: Record `Open Homeowner Forum was held from HH:MM to HH:MM.` without naming individual homeowners or transcribing complaints; keep architectural, vendor, and reserve-fund votes crisp; isolate member delinquency and violation hearings in `executive_session_record.md`.
- **`public_agency`**: Include explicit statutory citation placeholders (`[SECRETARY VERIFY: Open-Meetings Statutory Citation]`) for closed sessions and roll-call vote breakdowns when required by local open-meetings rules.

## Executive Session Boundaries

- Never place employee names, termination grounds, HR complaints, homeowner delinquency balances, unit numbers, or privileged attorney-client advice inside `official_minutes_draft.md`.
- In `official_minutes_draft.md`, record only: `The Board entered Executive Session at HH:MM to discuss [Permitted Statutory Category] and returned to Open Session at HH:MM. See executive_session_record.md.`
- Always remind the secretary to confirm statutory open-meetings and disclosure requirements with corporate or association counsel.

## Pre-Approval Secretary Checklist

List every `[SECRETARY VERIFY: ...]` field at the end of `official_minutes_draft.md` so the board secretary can confirm missing timestamps, quorum thresholds, unseconded consensus actions, or statutory citations before circulating the minutes for board approval.
