"""MoPhones credit portfolio and customer experience analysis.

This script is intentionally implemented with Python standard library only so it can run
in constrained environments without third-party dependencies.
"""

from __future__ import annotations

import csv
import datetime as dt
import json
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[1]
CREDIT_GLOB = "Credit Data - *.csv"
NPS_FILE = ROOT / "NPS Data (1).xlsx"
OUTPUT_DIR = ROOT / "deliverables" / "outputs"


def to_float(value: str | None) -> float:
    if value is None:
        return 0.0
    text = str(value).strip()
    if text == "":
        return 0.0
    try:
        return float(text)
    except ValueError:
        return 0.0


def age_band_from_age(age: float) -> str:
    if age < 26:
        return "18–25"
    if age < 36:
        return "26–35"
    if age < 46:
        return "36–45"
    if age < 56:
        return "46–55"
    return "55+"


def income_band_from_monthly(monthly_amount: float) -> str:
    bins = [5000, 10000, 20000, 30000, 50000, 100000, 150000]
    labels = [
        "<5,000",
        "5,000–9,999",
        "10,000–19,999",
        "20,000–29,999",
        "30,000–49,999",
        "50,000–99,999",
        "100,000–149,999",
        "150,000+",
    ]
    idx = 0
    while idx < len(bins) and monthly_amount >= bins[idx]:
        idx += 1
    return labels[idx]


def normalize_fieldnames(fieldnames: list[str]) -> list[str]:
    cleaned: list[str] = []
    for name in fieldnames:
        cleaned.append("unnamed_col" if (name or "").strip() == "" else name.strip())
    return cleaned


def parse_snapshots() -> list[tuple[dt.date, Path]]:
    snapshots: list[tuple[dt.date, Path]] = []
    for path in sorted(ROOT.glob(CREDIT_GLOB)):
        date_part = path.name.replace("Credit Data - ", "").replace(".csv", "")
        snapshot_date = dt.datetime.strptime(date_part, "%d-%m-%Y").date()
        snapshots.append((snapshot_date, path))
    return snapshots


def xlsx_sheet_rows(path: Path) -> list[list[str]]:
    ns = {"a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}

    def col_to_idx(cell_ref: str) -> int:
        letters = "".join(ch for ch in cell_ref if ch.isalpha())
        index = 0
        for letter in letters:
            index = index * 26 + (ord(letter.upper()) - 64)
        return max(index - 1, 0)

    with zipfile.ZipFile(path) as workbook:
        shared_strings: list[str] = []
        if "xl/sharedStrings.xml" in workbook.namelist():
            ss_root = ET.fromstring(workbook.read("xl/sharedStrings.xml"))
            for item in ss_root.findall("a:si", ns):
                shared_strings.append("".join(t.text or "" for t in item.findall(".//a:t", ns)))

        sheet_root = ET.fromstring(workbook.read("xl/worksheets/sheet1.xml"))
        rows = sheet_root.findall(".//a:sheetData/a:row", ns)

        parsed_rows: list[list[str]] = []
        for row in rows:
            values = [""] * 40
            for cell in row.findall("a:c", ns):
                idx = col_to_idx(cell.attrib.get("r", "A1"))
                raw_value = cell.find("a:v", ns)
                if raw_value is None:
                    value = ""
                else:
                    text = raw_value.text or ""
                    value = (
                        shared_strings[int(text)]
                        if cell.attrib.get("t") == "s" and text.isdigit() and int(text) < len(shared_strings)
                        else text
                    )
                if idx < len(values):
                    values[idx] = value
            parsed_rows.append(values)

    return parsed_rows


def load_nps_scores() -> dict[str, float]:
    rows = xlsx_sheet_rows(NPS_FILE)
    if not rows:
        return {}

    header = rows[0]
    loan_idx = header.index("Loan Id")
    score_idx = next(i for i, col in enumerate(header) if "scale from 0" in col)

    scores: dict[str, float] = {}
    for row in rows[1:]:
        loan_id = row[loan_idx].strip() if loan_idx < len(row) else ""
        score_text = row[score_idx].strip() if score_idx < len(row) else ""
        if not loan_id or not score_text:
            continue
        try:
            scores[loan_id] = float(score_text)
        except ValueError:
            continue
    return scores


def run_analysis() -> dict:
    snapshots = parse_snapshots()
    nps_scores = load_nps_scores()

    portfolio_metrics: list[dict] = []
    age_segment_metrics: dict[tuple[str, str], dict[str, float]] = defaultdict(
        lambda: {"accounts": 0, "par30": 0, "default": 0, "repayment_sum": 0.0, "dpd_sum": 0.0}
    )
    latest_status_breakdown = Counter()
    latest_missingness = Counter()
    latest_row_count = 0
    nps_join_rows: list[dict] = []

    for snapshot_date, file_path in snapshots:
        with file_path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            reader.fieldnames = normalize_fieldnames(reader.fieldnames or [])

            row_count = 0
            par30_count = 0
            default_count = 0
            repayment_values: list[float] = []
            dpd_values: list[float] = []
            active_count = 0
            closed_count = 0

            for row in reader:
                row_count += 1

                dpd = to_float(row.get("DAYS_PAST_DUE"))
                total_paid = to_float(row.get("TOTAL_PAID"))
                total_due = to_float(row.get("TOTAL_DUE_TODAY"))
                weekly_rate = to_float(row.get("WEEKLY_RATE"))

                status_l2 = (row.get("ACCOUNT_STATUS_L2") or "").strip()
                is_active = status_l2 == "Active"
                is_closed = status_l2 in {"Paid Off", "Return", "Inactive"}

                if is_active:
                    active_count += 1
                if is_closed:
                    closed_count += 1

                is_par30 = dpd >= 30
                is_default = dpd >= 90 or status_l2 in {"FPD", "FMD"}

                par30_count += int(is_par30)
                default_count += int(is_default)

                repayment_rate = total_paid / (total_paid + total_due) if (total_paid + total_due) > 0 else 0.0
                repayment_values.append(repayment_rate)
                dpd_values.append(dpd)

                age_band = age_band_from_age(to_float(row.get("CUSTOMER_AGE")))
                # Assumption: true income is unavailable, so weekly installment burden is used as affordability proxy.
                avg_monthly_income_proxy = weekly_rate * 4.33
                _income_band = income_band_from_monthly(avg_monthly_income_proxy)

                bucket = age_segment_metrics[(snapshot_date.isoformat(), age_band)]
                bucket["accounts"] += 1
                bucket["par30"] += int(is_par30)
                bucket["default"] += int(is_default)
                bucket["repayment_sum"] += repayment_rate
                bucket["dpd_sum"] += dpd

                if snapshot_date == snapshots[-1][0]:
                    latest_row_count += 1
                    latest_status_breakdown[status_l2] += 1
                    for col, value in row.items():
                        if (value or "").strip() == "":
                            latest_missingness[col] += 1

                    loan_id = (row.get("LOAN_ID") or "").strip()
                    if loan_id in nps_scores:
                        nps_join_rows.append(
                            {
                                "loan_id": loan_id,
                                "nps_score": nps_scores[loan_id],
                                "days_past_due": dpd,
                                "is_default": int(is_default),
                            }
                        )

            portfolio_metrics.append(
                {
                    "snapshot_date": snapshot_date.isoformat(),
                    "accounts": row_count,
                    "par30_rate": par30_count / row_count,
                    "default_rate": default_count / row_count,
                    "repayment_rate": mean(repayment_values) if repayment_values else 0.0,
                    "avg_days_past_due": mean(dpd_values) if dpd_values else 0.0,
                    "active_to_closed_ratio": active_count / closed_count if closed_count else None,
                }
            )

    age_segment_output = []
    latest_date = snapshots[-1][0].isoformat()
    for (snapshot, age_band), values in sorted(age_segment_metrics.items()):
        accounts = int(values["accounts"])
        if accounts == 0:
            continue
        age_segment_output.append(
            {
                "snapshot_date": snapshot,
                "age_band": age_band,
                "accounts": accounts,
                "par30_rate": values["par30"] / accounts,
                "default_rate": values["default"] / accounts,
                "repayment_rate": values["repayment_sum"] / accounts,
                "avg_days_past_due": values["dpd_sum"] / accounts,
                "is_latest_snapshot": snapshot == latest_date,
            }
        )

    default_rows = [r for r in nps_join_rows if r["is_default"] == 1]
    non_default_rows = [r for r in nps_join_rows if r["is_default"] == 0]
    arrears_rows = [r for r in nps_join_rows if r["days_past_due"] >= 30]
    current_rows = [r for r in nps_join_rows if r["days_past_due"] < 30]

    nps_summary = {
        "joined_accounts": len(nps_join_rows),
        "avg_nps_default": mean([r["nps_score"] for r in default_rows]) if default_rows else None,
        "avg_nps_non_default": mean([r["nps_score"] for r in non_default_rows]) if non_default_rows else None,
        "avg_nps_arrears_30_plus": mean([r["nps_score"] for r in arrears_rows]) if arrears_rows else None,
        "avg_nps_current": mean([r["nps_score"] for r in current_rows]) if current_rows else None,
    }

    top_missing = sorted(
        [
            {
                "column": column,
                "missing_rows": missing_count,
                "missing_rate": missing_count / latest_row_count if latest_row_count else 0.0,
            }
            for column, missing_count in latest_missingness.items()
        ],
        key=lambda item: item["missing_rate"],
        reverse=True,
    )[:10]

    return {
        "portfolio_metrics": portfolio_metrics,
        "age_segment_metrics": age_segment_output,
        "nps_summary": nps_summary,
        "latest_status_breakdown": latest_status_breakdown,
        "latest_missingness_top10": top_missing,
    }


def save_outputs(results: dict) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with (OUTPUT_DIR / "analysis_summary.json").open("w", encoding="utf-8") as handle:
        json.dump(results, handle, indent=2)

    with (OUTPUT_DIR / "portfolio_metrics.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(results["portfolio_metrics"][0].keys()))
        writer.writeheader()
        writer.writerows(results["portfolio_metrics"])

    with (OUTPUT_DIR / "age_segment_metrics.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(results["age_segment_metrics"][0].keys()))
        writer.writeheader()
        writer.writerows(results["age_segment_metrics"])


if __name__ == "__main__":
    results_dict = run_analysis()
    save_outputs(results_dict)
    print(f"Saved outputs to: {OUTPUT_DIR}")
