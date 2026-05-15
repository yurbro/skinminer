from __future__ import annotations

import matplotlib as mpl
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt

import demonstration_v5_finalize_figure as base


OUTPUT_STEM = "fig_logo_cv_composite_large_labels"


def configure_style_large() -> None:
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "DejaVu Sans"],
            "font.size": 10,
            "axes.labelsize": 11,
            "axes.titlesize": 11,
            "axes.titleweight": "bold",
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "legend.fontsize": 9,
            "legend.frameon": False,
            "axes.linewidth": 0.75,
            "xtick.major.width": 0.75,
            "ytick.major.width": 0.75,
            "xtick.major.size": 3.6,
            "ytick.major.size": 3.6,
            "figure.dpi": 300,
            "savefig.dpi": 300,
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.06,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def panel_title_parenthesized(ax: plt.Axes, letter: str, text: str) -> None:
    ax.set_title(f"({letter}) {text}", loc="left", pad=6, fontweight="bold")


def build_composite_large_labels() -> None:
    base.FONT_SCALE = 1.25
    base.MICRO_UNIT = "µg/cm²"
    base.panel_title = panel_title_parenthesized

    configure_style_large()
    base.ensure_dirs()
    predictions, per_formulation, _source, metrics = base.load_inputs()

    fig = plt.figure(figsize=(15.8, 9.6), facecolor="white")
    gs = gridspec.GridSpec(
        2,
        3,
        figure=fig,
        hspace=0.42,
        wspace=0.34,
        left=0.065,
        right=0.985,
        top=0.955,
        bottom=0.095,
    )
    axes = [fig.add_subplot(gs[row, col]) for row in range(2) for col in range(3)]

    base.draw_panel_a(axes[0], predictions)
    base.draw_panel_b(axes[1], predictions, metrics)
    base.draw_panel_c(axes[2], predictions, metrics)
    base.draw_panel_d(axes[3], per_formulation, metrics)
    base.draw_panel_e(axes[4], predictions)
    base.draw_panel_f(axes[5], predictions)

    for ax in axes:
        ax.set_facecolor("white")
        ax.grid(False)

    png = base.FIGURE_DIR / f"{OUTPUT_STEM}.png"
    pdf = base.FIGURE_DIR / f"{OUTPUT_STEM}.pdf"
    fig.savefig(png)
    fig.savefig(pdf)
    plt.close(fig)
    print("Large-label composite figure generated")
    print(f"PNG: {png} ({png.stat().st_size} bytes)")
    print(f"PDF: {pdf} ({pdf.stat().st_size} bytes)")


def main() -> None:
    build_composite_large_labels()


if __name__ == "__main__":
    main()
