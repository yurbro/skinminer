from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
AUDIT_DIR = ROOT / "outputs" / "claude_gold_audit"
POLICIES = ["v2", "v3", "v4"]


def annotation_workbook() -> Path:
    filled = AUDIT_DIR / "claude_annotation_packet_FILLED.xlsx"
    if filled.exists():
        return filled
    return AUDIT_DIR / "claude_annotation_packet.xlsx"


def normalize_label(value: object) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip().lower()


def main() -> None:
    overlap = pd.read_csv(AUDIT_DIR / "overlap_analysis.csv")
    packet_path = annotation_workbook()
    new_annotations = pd.read_excel(packet_path, sheet_name="Records to Annotate")
    new_annotations = new_annotations.rename(columns={"record_id": "claude_record_id"})

    annotation_cols = [
        "claude_record_id",
        "gold_keep_record",
        "gold_endpoint_value_correct",
        "gold_endpoint_value_note",
        "gold_notes",
    ]
    missing_cols = [col for col in annotation_cols if col not in new_annotations.columns]
    if missing_cols:
        raise ValueError(f"Missing annotation columns in {packet_path}: {missing_cols}")

    merged = overlap.merge(new_annotations[annotation_cols], on="claude_record_id", how="left", suffixes=("", "_new"))

    final_rows = []
    for _, row in merged.iterrows():
        inherited = normalize_label(row.get("gold_label_inherited"))
        needs_new = bool(row.get("needs_new_annotation"))
        if needs_new:
            keep = normalize_label(row.get("gold_keep_record"))
            value_correct = normalize_label(row.get("gold_endpoint_value_correct"))
            source = "new_annotation"
        else:
            keep = inherited
            value_correct = normalize_label(row.get("gold_endpoint_value_correct_inherited"))
            source = "inherited_gpt_round2"
        final = row.to_dict()
        final["final_gold_keep_record"] = keep
        final["final_gold_endpoint_value_correct"] = value_correct
        final["gold_label_source"] = source
        final_rows.append(final)

    combined = pd.DataFrame(final_rows)
    missing_required = combined[combined["final_gold_keep_record"] == ""]
    if not missing_required.empty:
        path = AUDIT_DIR / "claude_precision_missing_annotations.csv"
        missing_required.to_csv(path, index=False, encoding="utf-8-sig")
        raise ValueError(f"Missing gold_keep_record labels for {len(missing_required)} rows. See {path}")

    summary_rows = []
    for policy in POLICIES:
        subset = combined[combined[f"policy_{policy}"] == "yes"]
        keep = subset["final_gold_keep_record"].map(normalize_label)
        tp = int((keep == "yes").sum())
        uncertain = int((keep == "uncertain").sum())
        total = len(subset)
        fp = total - tp - uncertain
        precision = (tp / total * 100.0) if total else float("nan")
        summary_rows.append(
            {
                "policy": policy,
                "verified": total,
                "tp": tp,
                "fp": fp,
                "uncertain": uncertain,
                "precision_pct": precision,
                "inherited_labels": int((subset["gold_label_source"] == "inherited_gpt_round2").sum()),
                "new_annotations": int((subset["gold_label_source"] == "new_annotation").sum()),
            }
        )

    summary = pd.DataFrame(summary_rows)
    combined.to_csv(AUDIT_DIR / "claude_precision_combined_labels.csv", index=False, encoding="utf-8-sig")
    summary.to_csv(AUDIT_DIR / "claude_per_policy_precision.csv", index=False, encoding="utf-8-sig")

    report_lines = [
        "# Claude Per-Policy Precision",
        "",
        f"- Annotation workbook: `{packet_path.relative_to(ROOT)}`",
        f"- Combined labels: `outputs/claude_gold_audit/claude_precision_combined_labels.csv`",
        "",
        summary.to_markdown(index=False, floatfmt=".1f"),
        "",
        "Precision is calculated as `TP / verified` for each policy bucket; uncertain labels are counted separately and remain in the denominator.",
    ]
    (AUDIT_DIR / "claude_per_policy_precision.md").write_text("\n".join(report_lines), encoding="utf-8")
    print(summary.to_string(index=False))
    print(f"Outputs: {AUDIT_DIR}")


if __name__ == "__main__":
    main()
