"""Content acquisition strategy for the current OA-only pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class ContentStrategy:
    """Describe how the pipeline should resolve and materialize OA content."""

    prefer_structured_text: bool = True
    eager_download_primary: bool = False
    auto_download_pdf_for_legacy: bool = True
    routing_backend: str = "structured_first"
    text_backend: str = "structured_first"
    table_backend: str = "structured_first"
    figure_backend: str = "pdf_image"
    notes: list[str] = field(default_factory=list)

    @property
    def summary(self) -> str:
        """Compact human-readable summary for logging and status panels."""

        parts = [
            "structured_preferred" if self.prefer_structured_text else "pdf_preferred",
            "primary_download=on" if self.eager_download_primary else "primary_download=off",
            "auto_pdf=on" if self.auto_download_pdf_for_legacy else "auto_pdf=off",
            f"routing={self.routing_backend}",
            f"text={self.text_backend}",
            f"table={self.table_backend}",
            f"figure={self.figure_backend}",
        ]
        return " | ".join(parts)


def build_default_content_strategy(
    *,
    eager_download_primary: bool = False,
    auto_download_pdf_for_legacy: bool = True,
) -> ContentStrategy:
    """Build the default content plan for the current research pipeline.

    The current pipeline now routes and extracts text and table evidence from
    structured OA content when available, while the figure branch remains PDF-first.
    PDFs are still auto-materialized when available so legacy figure extraction and
    PDF fallbacks can proceed.
    """

    notes = [
        "PMC XML / HTML are the preferred textual representations for OA content.",
        "The router now prefers PMC XML / HTML before falling back to PDF.",
        "The text extractor now prefers structured evidence windows with PDF fallback.",
        "The table extractor now prefers structured tables with PDF fallback.",
        "The figure extractor still relies on local PDFs.",
        "PDFs are auto-downloaded when available so figure extraction and PDF fallback can proceed.",
    ]
    return ContentStrategy(
        prefer_structured_text=True,
        eager_download_primary=eager_download_primary,
        auto_download_pdf_for_legacy=auto_download_pdf_for_legacy,
        routing_backend="structured_first",
        text_backend="structured_first",
        table_backend="structured_first",
        figure_backend="pdf_image",
        notes=notes,
    )
