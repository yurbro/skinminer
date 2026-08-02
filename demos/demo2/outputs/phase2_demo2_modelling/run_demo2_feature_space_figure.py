from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import Patch, Polygon
import numpy as np
import pandas as pd
from scipy.spatial import ConvexHull


OUT = Path(__file__).resolve().parent
PCA_CSV = OUT / "feature_space_pca.csv"
METRICS_JSON = OUT / "feature_space_overlap_metrics.json"
FIG_PDF = OUT / "figure_demo2_feature_space.pdf"
FIG_PNG = OUT / "figure_demo2_feature_space.png"
REPORT = OUT / "demo2_figure_report.md"

PALETTE = {
    "in_house": "#0072B2",
    "literature": "#D55E00",
    "line": "#222222",
    "grid": "#D9D9D9",
}

FEATURE_ORDER = [
    "log10_vehicle_solubility",
    "ethanol_fraction",
    "pg_fraction",
    "water_fraction",
]

FEATURE_LABELS = {
    "log10_vehicle_solubility": "log10 solubility",
    "ethanol_fraction": "ethanol fraction",
    "pg_fraction": "PG fraction",
    "water_fraction": "water fraction",
}

LITERATURE_LABEL_OFFSETS = {
    "F1A": (12, -17),
    "F1B": (-34, 10),
    "F2A": (18, 19),
    "F2B": (18, -24),
    "F3": (10, -17),
    "F4": (-30, 15),
    "F5": (11, -16),
    "F6": (-31, 15),
}

IN_HOUSE_LABEL_OFFSETS = {
    "RUN1": (-31, 18),
    "RUN2": (11, 12),
    "RUN3": (10, -18),
    "RUN4": (12, -18),
}

REPORT_START = "<!-- FIG362_REDRAW_START -->"
REPORT_END = "<!-- FIG362_REDRAW_END -->"


def configure_matplotlib() -> None:
    plt.rcParams.update(
        {
            "font.family": "Arial",
            "font.size": 8.5,
            "axes.titlesize": 9.0,
            "axes.labelsize": 8.5,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "legend.fontsize": 7.6,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "axes.linewidth": 0.8,
        }
    )


def read_and_validate_inputs() -> tuple[pd.DataFrame, dict]:
    rows = pd.read_csv(PCA_CSV)
    metrics = json.loads(METRICS_JSON.read_text(encoding="utf-8"))

    required_columns = {"dataset", "record_id", "PC1", "PC2"}
    missing_columns = required_columns - set(rows.columns)
    if missing_columns:
        raise ValueError(f"Missing PCA columns: {sorted(missing_columns)}")
    if len(rows) != 37 or rows["record_id"].nunique() != 37:
        raise ValueError("Expected 37 unique PCA records.")

    counts = rows.groupby("dataset").size().to_dict()
    if counts != {"Bolla": 8, "Xiao": 29}:
        raise ValueError(f"Unexpected dataset counts: {counts}")

    expected_literature = {"F1A", "F1B", "F2A", "F2B", "F3", "F4", "F5", "F6"}
    observed_literature = set(rows.loc[rows["dataset"] == "Bolla", "record_id"])
    if observed_literature != expected_literature:
        raise ValueError(f"Unexpected literature IDs: {sorted(observed_literature)}")

    selected_in_house = set(IN_HOUSE_LABEL_OFFSETS)
    observed_in_house = set(rows.loc[rows["dataset"] == "Xiao", "record_id"])
    if not selected_in_house.issubset(observed_in_house):
        raise ValueError("RUN1-RUN4 are not all present in the in-house PCA rows.")

    explained = metrics["pca"]["explained_variance_ratio"]
    total_pc12 = explained["PC1"] + explained["PC2"]
    coverage = metrics["standardised_4d_hyperrectangle_coverage"]
    centroid_distance = metrics["pc1_pc2_centroids"]["euclidean_distance_in_pooled_sd_units"]
    ranges = metrics["standardised_feature_range_overlap"]

    if coverage["bolla_records_inside_xiao_hyperrectangle"] != 0:
        raise ValueError("Source metrics no longer support the 0/8 annotation.")
    if coverage["n_bolla_records"] != 8:
        raise ValueError("Source metrics do not contain eight literature records.")
    if not np.isclose(centroid_distance, 1.8954012398379099, atol=1e-12):
        raise ValueError(f"Unexpected centroid distance: {centroid_distance}")
    if not np.isclose(explained["PC1"], 0.7011400846671922, atol=1e-12):
        raise ValueError(f"Unexpected PC1 variance ratio: {explained['PC1']}")
    if not np.isclose(explained["PC2"], 0.18702455099293172, atol=1e-12):
        raise ValueError(f"Unexpected PC2 variance ratio: {explained['PC2']}")
    if not np.isclose(total_pc12, 0.8881646356601239, atol=1e-12):
        raise ValueError(f"Unexpected PC1+PC2 variance ratio: {total_pc12}")
    if [row["feature"] for row in ranges] != FEATURE_ORDER:
        raise ValueError("Per-feature range order differs from the required publication order.")
    if not all(row["ranges_overlap"] for row in ranges):
        raise ValueError("At least one source marginal range no longer overlaps.")

    return rows, metrics


def add_convex_hull(ax: plt.Axes, points: np.ndarray, color: str) -> None:
    hull = ConvexHull(points)
    vertices = points[hull.vertices]
    ax.add_patch(
        Polygon(
            vertices,
            closed=True,
            facecolor=color,
            edgecolor=color,
            linewidth=0.9,
            linestyle=(0, (4, 3)),
            alpha=0.10,
            zorder=1,
        )
    )
    closed = np.vstack([vertices, vertices[0]])
    ax.plot(
        closed[:, 0],
        closed[:, 1],
        color=color,
        linewidth=0.9,
        linestyle=(0, (4, 3)),
        alpha=0.72,
        zorder=2,
    )


def annotate_points(
    ax: plt.Axes,
    rows: pd.DataFrame,
    offsets: dict[str, tuple[int, int]],
) -> None:
    for _, row in rows.iterrows():
        record_id = str(row["record_id"])
        dx, dy = offsets[record_id]
        ax.annotate(
            record_id,
            (float(row["PC1"]), float(row["PC2"])),
            xytext=(dx, dy),
            textcoords="offset points",
            ha="center",
            va="center",
            fontsize=6.8,
            color=PALETTE["line"],
            arrowprops={
                "arrowstyle": "-",
                "linewidth": 0.38,
                "color": "#666666",
                "shrinkA": 1.5,
                "shrinkB": 2.5,
            },
            zorder=6,
        )


def draw_panel_a(ax: plt.Axes, rows: pd.DataFrame, metrics: dict) -> None:
    in_house = rows.loc[rows["dataset"] == "Xiao"].copy()
    literature = rows.loc[rows["dataset"] == "Bolla"].copy()

    in_house_points = in_house[["PC1", "PC2"]].to_numpy(dtype=float)
    literature_points = literature[["PC1", "PC2"]].to_numpy(dtype=float)
    add_convex_hull(ax, in_house_points, PALETTE["in_house"])
    add_convex_hull(ax, literature_points, PALETTE["literature"])

    ax.scatter(
        in_house["PC1"],
        in_house["PC2"],
        s=29,
        marker="o",
        facecolor=PALETTE["in_house"],
        edgecolor=PALETTE["line"],
        linewidth=0.45,
        alpha=0.92,
        label="in-house (P407 cosolvent gels, n=29)",
        zorder=4,
    )
    ax.scatter(
        literature["PC1"],
        literature["PC2"],
        s=38,
        marker="^",
        facecolor=PALETTE["literature"],
        edgecolor=PALETTE["line"],
        linewidth=0.55,
        alpha=0.94,
        label="literature (semisolid formulations, n=8)",
        zorder=5,
    )

    annotate_points(ax, literature, LITERATURE_LABEL_OFFSETS)
    selected_in_house = in_house.loc[in_house["record_id"].isin(IN_HOUSE_LABEL_OFFSETS)]
    annotate_points(ax, selected_in_house, IN_HOUSE_LABEL_OFFSETS)

    explained = metrics["pca"]["explained_variance_ratio"]
    total_pc12 = explained["PC1"] + explained["PC2"]
    coverage = metrics["standardised_4d_hyperrectangle_coverage"]
    centroid_distance = metrics["pc1_pc2_centroids"]["euclidean_distance_in_pooled_sd_units"]
    annotation = (
        f"{coverage['bolla_records_inside_xiao_hyperrectangle']}/"
        f"{coverage['n_bolla_records']} literature points inside in-house 4D feature hyperrectangle\n"
        f"Centroid distance = {centroid_distance:.1f}$\\sigma$ (pooled)\n"
        f"PCA captures {100 * total_pc12:.1f}% of total variance"
    )
    ax.text(
        0.975,
        0.79,
        annotation,
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=6.2,
        linespacing=1.18,
        bbox={
            "boxstyle": "round,pad=0.28",
            "facecolor": "white",
            "edgecolor": "#777777",
            "linewidth": 0.55,
            "alpha": 0.94,
        },
        zorder=7,
    )

    ax.axhline(0, color=PALETTE["grid"], linewidth=0.5, zorder=0)
    ax.axvline(0, color=PALETTE["grid"], linewidth=0.5, zorder=0)
    ax.set_xlim(-5.15, 4.25)
    ax.set_ylim(-2.05, 4.00)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel(f"PC1 ({100 * explained['PC1']:.1f}% variance)")
    ax.set_ylabel(f"PC2 ({100 * explained['PC2']:.1f}% variance)")
    ax.set_title("A  Feature-space distribution (PCA)", loc="left", fontweight="bold", pad=7)
    ax.legend(
        loc="upper right",
        frameon=False,
        handletextpad=0.45,
        borderpad=0.1,
        labelspacing=0.35,
    )
    ax.tick_params(direction="out", length=3, width=0.8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def draw_panel_b(ax: plt.Axes, metrics: dict) -> None:
    range_by_feature = {
        row["feature"]: row for row in metrics["standardised_feature_range_overlap"]
    }
    y_positions = np.arange(len(FEATURE_ORDER), dtype=float)
    bar_height = 0.17
    offset = 0.13

    for index, feature in enumerate(FEATURE_ORDER):
        row = range_by_feature[feature]
        in_house_min = row["xiao_min_standardised"]
        in_house_max = row["xiao_max_standardised"]
        literature_min = row["bolla_min_standardised"]
        literature_max = row["bolla_max_standardised"]

        ax.broken_barh(
            [(in_house_min, in_house_max - in_house_min)],
            (index - offset - bar_height / 2, bar_height),
            facecolors=PALETTE["in_house"],
            edgecolors=PALETTE["line"],
            linewidth=0.5,
            zorder=3,
        )
        ax.broken_barh(
            [(literature_min, literature_max - literature_min)],
            (index + offset - bar_height / 2, bar_height),
            facecolors=PALETTE["literature"],
            edgecolors=PALETTE["line"],
            linewidth=0.5,
            zorder=3,
        )

        for value, y_value in [
            (in_house_min, index - offset),
            (in_house_max, index - offset),
            (literature_min, index + offset),
            (literature_max, index + offset),
        ]:
            ax.plot(
                [value, value],
                [y_value - bar_height / 2, y_value + bar_height / 2],
                color=PALETTE["line"],
                linewidth=0.55,
                zorder=4,
            )

    ax.set_yticks(y_positions)
    ax.set_yticklabels([FEATURE_LABELS[feature] for feature in FEATURE_ORDER])
    ax.set_ylim(3.55, -1.00)
    ax.set_xlim(-3.45, 3.75)
    ax.set_xticks(np.arange(-3, 4, 1))
    ax.axvline(0, color="#777777", linewidth=0.65, linestyle=(0, (3, 3)), zorder=2)
    ax.grid(axis="x", color=PALETTE["grid"], linewidth=0.45, zorder=0)
    ax.set_xlabel("Standardised feature value")
    ax.set_title("B  Per-feature dataset ranges", loc="left", fontweight="bold", pad=7)
    ax.legend(
        handles=[
            Patch(
                facecolor=PALETTE["in_house"],
                edgecolor=PALETTE["line"],
                label="in-house",
            ),
            Patch(
                facecolor=PALETTE["literature"],
                edgecolor=PALETTE["line"],
                label="literature",
            ),
        ],
        loc="upper right",
        bbox_to_anchor=(1.0, 0.995),
        ncol=2,
        frameon=False,
        handlelength=1.35,
        columnspacing=0.9,
        borderaxespad=0,
    )
    ax.text(
        0.0,
        -0.19,
        "All marginal ranges overlap; multivariate separation\n"
        "is the operative gap.",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=7.0,
        color="#333333",
    )
    ax.tick_params(direction="out", length=3, width=0.8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def make_figure(rows: pd.DataFrame, metrics: dict) -> None:
    configure_matplotlib()
    fig, axes = plt.subplots(
        1,
        2,
        figsize=(7.65, 3.65),
        gridspec_kw={"width_ratios": [1.18, 0.82], "wspace": 0.42},
        constrained_layout=False,
    )
    draw_panel_a(axes[0], rows, metrics)
    draw_panel_b(axes[1], metrics)
    fig.subplots_adjust(left=0.075, right=0.985, bottom=0.22, top=0.88)
    fig.savefig(
        FIG_PDF,
        metadata={
            "Creator": "SkinMiner",
            "CreationDate": None,
            "ModDate": None,
        },
    )
    fig.savefig(FIG_PNG, dpi=450, metadata={"Software": "SkinMiner"})
    plt.close(fig)


def update_report(metrics: dict) -> None:
    explained = metrics["pca"]["explained_variance_ratio"]
    total_pc12 = explained["PC1"] + explained["PC2"]
    coverage = metrics["standardised_4d_hyperrectangle_coverage"]
    centroid_distance = metrics["pc1_pc2_centroids"]["euclidean_distance_in_pooled_sd_units"]

    block = "\n".join(
        [
            REPORT_START,
            "",
            "## Figure 3.6.2: Feature-Space Redraw",
            "",
            "The Step 2i feature-space visualisation was redrawn as a main-paper figure without rerunning PCA or changing any record coordinates or analysis values.",
            "",
            "Published figure rendering:",
            "",
            "- filled markers and filled range bars throughout;",
            "- formulation-class dataset legend using `in-house` and `literature` labels;",
            "- dashed convex hulls for visual orientation;",
            f"- source-verified annotations: {coverage['bolla_records_inside_xiao_hyperrectangle']}/8 literature points inside the in-house 4D feature hyperrectangle, centroid distance {centroid_distance:.1f} pooled SD, and PC1+PC2 variance {100 * total_pc12:.1f}%;",
            "- font, panel labels, and blue/orange palette matched to Fig. 3.6.1;",
            "- publication outputs renamed to `figure_demo2_feature_space.pdf` and `figure_demo2_feature_space.png`;",
            "- legacy supplementary figure variants are not required or distributed.",
            "",
            "All 29 in-house records and all 8 literature records are plotted. Literature formulations F1A-F6 and representative in-house records RUN1-RUN4 are labelled with leader lines.",
            "",
            REPORT_END,
        ]
    )

    report_text = REPORT.read_text(encoding="utf-8") if REPORT.exists() else ""
    if REPORT_START in report_text and REPORT_END in report_text:
        prefix, remainder = report_text.split(REPORT_START, 1)
        _, suffix = remainder.split(REPORT_END, 1)
        report_text = prefix.rstrip() + "\n\n" + block + suffix
    else:
        report_text = report_text.rstrip() + "\n\n" + block + "\n"
    REPORT.write_text(report_text, encoding="utf-8")


def main() -> None:
    rows, metrics = read_and_validate_inputs()
    make_figure(rows, metrics)
    update_report(metrics)

    explained = metrics["pca"]["explained_variance_ratio"]
    coverage = metrics["standardised_4d_hyperrectangle_coverage"]
    centroid_distance = metrics["pc1_pc2_centroids"]["euclidean_distance_in_pooled_sd_units"]
    print("[DEMO2 FIGURE 3.6.2 REDRAW] Done")
    print("Records plotted: in-house=29 literature=8")
    print(
        "Source annotations: "
        f"inside={coverage['bolla_records_inside_xiao_hyperrectangle']}/8 "
        f"centroid={centroid_distance:.3f} pooled SD "
        f"PC1+PC2={100 * (explained['PC1'] + explained['PC2']):.3f}%"
    )
    print(f"PDF: {FIG_PDF}")
    print(f"PNG: {FIG_PNG}")
    print(f"Report: {REPORT}")


if __name__ == "__main__":
    main()
