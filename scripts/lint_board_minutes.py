#!/usr/bin/env python3
"""Automated anti-liability linter for Robert's Rules board minutes.

Zero external dependencies (Python 3 standard library only).

Exit codes:
  0 - Passed (0 liability errors/flags)
  1 - Liability flags found
  2 - Invalid path, missing file, or argument error
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from typing import Any


PROHIBITED_DEBATE_VERBS = [
    "accused",
    "alleged",
    "argued",
    "attacked",
    "blamed",
    "claimed",
    "complained",
    "criticized",
    "demanded",
    "disagreed",
    "fumed",
    "insisted",
    "interrupted",
    "protested",
    "ranted",
    "snapped",
    "vented",
    "yelled",
]

CONFIDENTIAL_LEAK_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("hr_termination", re.compile(r"\b(terminat(?:ed|ion|ing)|fired|severance|disciplinary\s+action|performance\s+improvement\s+plan|hr\s+complaint)\b", re.IGNORECASE)),
    ("delinquency_collections", re.compile(r"\b(delinquen(?:t|cy)|past[- ]due|in\s+arrears|foreclosure|lien\s+filed|unpaid\s+assessments?)\b", re.IGNORECASE)),
    ("litigation_detail", re.compile(r"\b(settlement\s+offer|deposition|privileged\s+advice|opposing\s+counsel|lawsuit\s+against)\b", re.IGNORECASE)),
]

EXPECTED_RESOLUTION_HEADERS = [
    "resolution_id",
    "meeting_date",
    "agenda_item",
    "motion_text",
    "moved_by",
    "seconded_by",
    "vote_result",
    "status",
    "owner",
]

OUTCOME_PATTERN = re.compile(
    r"\b(carried|passed|approved|adopted|failed|defeated|tabled|withdrawn|postponed|unanimous|consensus)\b|\b\d+\s*-\s*\d+\b",
    re.IGNORECASE,
)

QUORUM_RATIO_PATTERN = re.compile(
    r"\b(\d+)\s+of\s+(\d+)\s+(?:voting\s+)?(?:directors?|members?|trustees?|commissioners?)\b",
    re.IGNORECASE,
)

SECRETARY_VERIFY_PATTERN = re.compile(r"\[SECRETARY VERIFY:\s*([^\]]+)\]")

EXEC_NEUTRAL_LINE_PATTERN = re.compile(
    r"(executive\s+session|closed\s+session|statutory\s+category|see\s+executive_session_record)",
    re.IGNORECASE,
)


def strip_markdown_for_word_count(text: str) -> list[str]:
    cleaned = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    cleaned = re.sub(r"[|#*_`>-]", " ", cleaned)
    return re.findall(r"[A-Za-z0-9]+(?:['-][A-Za-z0-9]+)*", cleaned)


def is_formal_motion_line(line: str) -> bool:
    stripped = line.strip()
    return bool(re.match(r"^(?:[-*]\s*)?(?:\*\*)?(?:Motion|Formal Motion|RESOLVED|Resolution)\b", stripped, re.IGNORECASE))


def check_quoted_speech(lines: list[str]) -> list[dict[str, Any]]:
    flags: list[dict[str, Any]] = []
    quote_re = re.compile(r'"[^"\n]{2,}"|\u201c[^\u201d\n]{2,}\u201d')
    in_motion_table = False
    motion_col_idx: int | None = None

    for idx, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            lower_cells = [c.lower() for c in cells]
            if any("motion" in c for c in lower_cells) and any(("moved" in c or "mover" in c) for c in lower_cells):
                in_motion_table = True
                motion_col_idx = next((i for i, c in enumerate(lower_cells) if "motion" in c), None)
                continue
            if in_motion_table:
                if all(re.fullmatch(r":?-{2,}:?", c.replace(" ", "")) for c in cells if c):
                    continue
                # Check all non-motion cells inside the formal motions table
                for col_i, cell in enumerate(cells):
                    if col_i == motion_col_idx:
                        continue
                    if quote_re.search(cell):
                        flags.append(
                            {
                                "rule": "quoted_speech_outside_motion",
                                "severity": "error",
                                "line": idx,
                                "message": "Quoted speech detected outside formal motion text column.",
                                "excerpt": stripped[:140],
                            }
                        )
                        break
                continue
            # Non-motion table row: flag any quoted speech
            if quote_re.search(stripped):
                flags.append(
                    {
                        "rule": "quoted_speech_outside_motion",
                        "severity": "error",
                        "line": idx,
                        "message": "Quoted speech detected inside non-motion table.",
                        "excerpt": stripped[:140],
                    }
                )
            continue

        if in_motion_table:
            in_motion_table = False
            motion_col_idx = None

        if is_formal_motion_line(line):
            continue
        if quote_re.search(line):
            flags.append(
                {
                    "rule": "quoted_speech_outside_motion",
                    "severity": "error",
                    "line": idx,
                    "message": "Quoted speech detected outside formal motion text.",
                    "excerpt": stripped[:140],
                }
            )
    return flags


def check_prohibited_verbs(lines: list[str]) -> list[dict[str, Any]]:
    flags: list[dict[str, Any]] = []
    verb_re = re.compile(r"\b(" + "|".join(PROHIBITED_DEBATE_VERBS) + r")\b", re.IGNORECASE)
    for idx, line in enumerate(lines, start=1):
        matches = verb_re.findall(line)
        if matches:
            unique_verbs = sorted({m.lower() for m in matches})
            flags.append(
                {
                    "rule": "prohibited_debate_verb",
                    "severity": "error",
                    "line": idx,
                    "message": f"Emotional or attributive debate verb(s) found: {', '.join(unique_verbs)}.",
                    "excerpt": line.strip()[:140],
                }
            )
    return flags


def check_quorum(
    text: str,
    voting_present: int | None,
    voting_total: int | None,
    quorum_required: int | None,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    flags: list[dict[str, Any]] = []
    quorum_declared = bool(re.search(r"\bquorum\b", text, re.IGNORECASE))
    ratio_match = QUORUM_RATIO_PATTERN.search(text)

    parsed_present = voting_present
    parsed_total = voting_total
    if parsed_present is None and ratio_match:
        parsed_present = int(ratio_match.group(1))
        parsed_total = int(ratio_match.group(2))

    required = quorum_required
    if required is None and parsed_total is not None and parsed_total > 0:
        required = (parsed_total // 2) + 1

    math_status = "not_evaluated"
    quorum_met: bool | None = None
    if parsed_present is not None and required is not None:
        quorum_met = parsed_present >= required
        math_status = "met" if quorum_met else "not_met"
        if not quorum_met and re.search(r"\bquorum\s+(?:was\s+)?(?:present|established|confirmed|met)\b", text, re.IGNORECASE):
            flags.append(
                {
                    "rule": "quorum_math_mismatch",
                    "severity": "error",
                    "line": None,
                    "message": f"Draft declares quorum met, but {parsed_present} present is below required threshold {required}.",
                }
            )

    if not quorum_declared:
        flags.append(
            {
                "rule": "quorum_not_declared",
                "severity": "error",
                "line": None,
                "message": "Minutes do not explicitly declare quorum status.",
            }
        )

    info = {
        "quorum_declared": quorum_declared,
        "voting_present": parsed_present,
        "voting_total": parsed_total,
        "quorum_required": required,
        "quorum_met": quorum_met,
        "math_status": math_status,
    }
    return info, flags


def check_motions(lines: list[str]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    flags: list[dict[str, Any]] = []
    motions_checked = 0

    in_motion_table = False
    header_cols: list[str] = []
    for idx, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            lower_cells = [c.lower() for c in cells]
            if any("motion" in c for c in lower_cells) and any(("moved" in c or "mover" in c) for c in lower_cells):
                in_motion_table = True
                header_cols = lower_cells
                continue
            if in_motion_table:
                if all(re.fullmatch(r":?-{2,}:?", c.replace(" ", "")) for c in cells if c):
                    continue
                if len(cells) < 3 or all(not c for c in cells):
                    continue
                motions_checked += 1
                row_map = {header_cols[i]: cells[i] for i in range(min(len(header_cols), len(cells)))}
                mover = next((v for k, v in row_map.items() if "moved" in k or "mover" in k), "")
                seconder = next((v for k, v in row_map.items() if "second" in k), "")
                outcome = next((v for k, v in row_map.items() if "vote" in k or "result" in k or "outcome" in k), "")
                row_text = " ".join(cells)

                if not mover or mover.lower() in {"none", "n/a", "-"}:
                    if "consensus action noted without formal second" not in row_text.lower():
                        flags.append(
                            {
                                "rule": "motion_missing_mover",
                                "severity": "error",
                                "line": idx,
                                "message": "Formal motion row is missing a mover.",
                                "excerpt": stripped[:140],
                            }
                        )
                if not outcome or not OUTCOME_PATTERN.search(outcome):
                    flags.append(
                        {
                            "rule": "motion_missing_outcome",
                            "severity": "error",
                            "line": idx,
                            "message": "Formal motion row is missing a clear vote outcome or tally.",
                            "excerpt": stripped[:140],
                        }
                    )
                if (not seconder or seconder.lower() in {"none", "n/a", "-"}) and "secretary verify" not in row_text.lower():
                    flags.append(
                        {
                            "rule": "motion_missing_seconder_note",
                            "severity": "warning",
                            "line": idx,
                            "message": "Formal motion lacks a seconder; mark 'Consensus action noted without formal second - [SECRETARY VERIFY]' if unseconded.",
                            "excerpt": stripped[:140],
                        }
                    )
        else:
            if in_motion_table:
                in_motion_table = False

    if motions_checked == 0:
        for idx, line in enumerate(lines, start=1):
            if re.match(r"^(?:[-*]\s*)?(?:\*\*)?(?:Motion|Formal Motion)\b", line.strip(), re.IGNORECASE):
                motions_checked += 1
                window = " ".join(lines[idx - 1 : min(len(lines), idx + 3)])
                if not re.search(r"\b(moved\s+by|mover)\b", window, re.IGNORECASE):
                    flags.append(
                        {
                            "rule": "motion_missing_mover",
                            "severity": "error",
                            "line": idx,
                            "message": "Standalone motion block is missing a mover.",
                            "excerpt": line.strip()[:140],
                        }
                    )
                if not OUTCOME_PATTERN.search(window):
                    flags.append(
                        {
                            "rule": "motion_missing_outcome",
                            "severity": "error",
                            "line": idx,
                            "message": "Standalone motion block is missing a vote outcome.",
                            "excerpt": line.strip()[:140],
                        }
                    )

    return {"motions_checked": motions_checked}, flags


def check_executive_session_leaks(
    lines: list[str],
    forbidden_terms: list[str],
) -> list[dict[str, Any]]:
    flags: list[dict[str, Any]] = []
    for idx, line in enumerate(lines, start=1):
        is_neutral_exec = bool(EXEC_NEUTRAL_LINE_PATTERN.search(line))
        for category, pattern in CONFIDENTIAL_LEAK_PATTERNS:
            if pattern.search(line) and not is_neutral_exec:
                flags.append(
                    {
                        "rule": "executive_session_leak",
                        "severity": "error",
                        "line": idx,
                        "message": f"Potential confidential {category} detail in open minutes.",
                        "excerpt": line.strip()[:140],
                    }
                )
        for term in forbidden_terms:
            clean_term = term.strip()
            if clean_term and re.search(re.escape(clean_term), line, re.IGNORECASE):
                flags.append(
                    {
                        "rule": "executive_session_term_leak",
                        "severity": "error",
                        "line": idx,
                        "message": f"Confidential executive-session term leaked into open minutes: '{clean_term}'.",
                        "excerpt": line.strip()[:140],
                    }
                )
    return flags


def validate_resolution_log(csv_path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    flags: list[dict[str, Any]] = []
    if not csv_path.is_file():
        return {"checked": False, "error": f"File not found: {csv_path}"}, [
            {
                "rule": "resolution_log_missing",
                "severity": "error",
                "line": None,
                "message": f"Resolution log file not found: {csv_path}",
            }
        ]

    with csv_path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.reader(fh)
        rows = list(reader)

    if not rows:
        flags.append(
            {
                "rule": "resolution_log_empty",
                "severity": "error",
                "line": 1,
                "message": "Resolution log CSV is empty.",
            }
        )
        return {"checked": True, "row_count": 0, "headers_valid": False}, flags

    headers = [h.strip() for h in rows[0]]
    headers_valid = headers == EXPECTED_RESOLUTION_HEADERS
    if not headers_valid:
        flags.append(
            {
                "rule": "resolution_log_header_mismatch",
                "severity": "error",
                "line": 1,
                "message": f"Resolution log headers mismatch. Expected {EXPECTED_RESOLUTION_HEADERS}, got {headers}.",
            }
        )

    data_rows = [r for r in rows[1:] if any(cell.strip() for cell in r)]
    return {
        "checked": True,
        "headers_valid": headers_valid,
        "row_count": len(data_rows),
    }, flags


def lint_minutes(
    draft_path: Path,
    source_path: Path | None,
    resolution_log_path: Path | None,
    max_words: int,
    voting_present: int | None,
    voting_total: int | None,
    quorum_required: int | None,
    forbidden_terms: list[str],
) -> dict[str, Any]:
    draft_text = draft_path.read_text(encoding="utf-8")
    lines = draft_text.splitlines()
    draft_words = strip_markdown_for_word_count(draft_text)
    draft_word_count = len(draft_words)

    findings: list[dict[str, Any]] = []

    if draft_word_count > max_words:
        findings.append(
            {
                "rule": "word_count_budget_exceeded",
                "severity": "error",
                "line": None,
                "message": f"Draft word count is {draft_word_count}, exceeding the {max_words}-word budget for standard 1-to-2-hour meetings.",
            }
        )

    findings.extend(check_quoted_speech(lines))
    findings.extend(check_prohibited_verbs(lines))

    quorum_info, quorum_flags = check_quorum(draft_text, voting_present, voting_total, quorum_required)
    findings.extend(quorum_flags)

    motion_info, motion_flags = check_motions(lines)
    findings.extend(motion_flags)

    findings.extend(check_executive_session_leaks(lines, forbidden_terms))

    verify_items = SECRETARY_VERIFY_PATTERN.findall(draft_text)

    removed_audit: dict[str, Any] = {
        "source_provided": False,
        "source_word_count": None,
        "draft_word_count": draft_word_count,
        "words_removed": None,
        "reduction_percent": None,
    }
    if source_path is not None:
        source_text = source_path.read_text(encoding="utf-8")
        source_word_count = len(strip_markdown_for_word_count(source_text))
        words_removed = max(0, source_word_count - draft_word_count)
        reduction_pct = round((words_removed / source_word_count) * 100.0, 2) if source_word_count > 0 else 0.0
        removed_audit = {
            "source_provided": True,
            "source_word_count": source_word_count,
            "draft_word_count": draft_word_count,
            "words_removed": words_removed,
            "reduction_percent": reduction_pct,
        }

    resolution_log_info: dict[str, Any] = {"checked": False}
    if resolution_log_path is not None:
        resolution_log_info, csv_flags = validate_resolution_log(resolution_log_path)
        findings.extend(csv_flags)

    errors = [f for f in findings if f["severity"] == "error"]
    warnings = [f for f in findings if f["severity"] == "warning"]
    status = "pass" if len(errors) == 0 else "fail"

    return {
        "status": status,
        "draft_file": str(draft_path),
        "flag_count": len(errors),
        "warning_count": len(warnings),
        "word_count": draft_word_count,
        "max_words": max_words,
        "quorum_check": quorum_info,
        "motion_check": motion_info,
        "resolution_log_check": resolution_log_info,
        "removed_content_audit": removed_audit,
        "secretary_verify_items": verify_items,
        "findings": findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="lint_board_minutes.py",
        description="Run automated Robert's Rules anti-liability checks on draft board minutes.",
        epilog="Exit codes: 0 = pass (0 errors), 1 = liability flags found, 2 = invalid path or argument error.",
    )
    parser.add_argument("--draft", required=True, help="Path to official_minutes_draft.md")
    parser.add_argument("--source", help="Optional path to raw meeting notes or transcript for removed-content word audit")
    parser.add_argument("--resolution-log", help="Optional path to resolution_log.csv to validate headers and row count")
    parser.add_argument("--max-words", type=int, default=800, help="Word-count budget ceiling (default: 800)")
    parser.add_argument("--voting-present", type=int, help="Optional count of voting directors present for quorum math")
    parser.add_argument("--voting-total", type=int, help="Optional total count of voting directors for quorum math")
    parser.add_argument("--quorum-required", type=int, help="Optional explicit minimum voting directors required for quorum")
    parser.add_argument(
        "--exec-session-terms",
        help="Optional comma-separated confidential names, units, or terms that must not appear in open minutes",
    )
    parser.add_argument("--output", help="Optional path to write liability_lint_report.json")
    args = parser.parse_args()

    draft_path = Path(args.draft).resolve()
    if not draft_path.is_file():
        print(f"Error: Draft file not found: {draft_path}", file=sys.stderr)
        return 2

    source_path: Path | None = None
    if args.source:
        source_path = Path(args.source).resolve()
        if not source_path.is_file():
            print(f"Error: Source file not found: {source_path}", file=sys.stderr)
            return 2

    res_log_path: Path | None = Path(args.resolution_log).resolve() if args.resolution_log else None
    forbidden_terms = [t.strip() for t in args.exec_session_terms.split(",") if t.strip()] if args.exec_session_terms else []

    report = lint_minutes(
        draft_path=draft_path,
        source_path=source_path,
        resolution_log_path=res_log_path,
        max_words=args.max_words,
        voting_present=args.voting_present,
        voting_total=args.voting_total,
        quorum_required=args.quorum_required,
        forbidden_terms=forbidden_terms,
    )

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
