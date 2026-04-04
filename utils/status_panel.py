"""Lightweight terminal status panel for long-running pipeline stages."""

from __future__ import annotations

import os
import shutil
import sys
import time
from dataclasses import dataclass
from typing import Callable, TextIO

ProgressCallback = Callable[[int, str, str], None]


@dataclass(slots=True)
class StageStatus:
    """Mutable snapshot of one pipeline stage in the live terminal panel."""

    label: str
    state: str = "pending"
    completed: int = 0
    total: int | None = None
    current_item: str = ""
    detail: str = ""
    started_at: float | None = None
    finished_at: float | None = None


def _enable_windows_vt_mode(stream: TextIO) -> None:
    """Enable ANSI escape handling in Windows terminals when possible."""

    if os.name != "nt" or not hasattr(stream, "fileno"):
        return
    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)
        if handle in (0, -1):
            return
        mode = ctypes.c_uint()
        if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            kernel32.SetConsoleMode(handle, mode.value | 0x0004)
    except Exception:
        return


def _format_seconds(seconds: float) -> str:
    whole = max(0, int(seconds))
    hours, rem = divmod(whole, 3600)
    minutes, secs = divmod(rem, 60)
    if hours:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def _truncate(value: str, width: int) -> str:
    if width <= 0:
        return ""
    clean = " ".join((value or "").split())
    if len(clean) <= width:
        return clean.ljust(width)
    if width <= 3:
        return clean[:width]
    return (clean[: width - 3] + "...").ljust(width)


class PipelineStatusPanel:
    """Render a compact live table of stage progress in the terminal."""

    def __init__(
        self,
        *,
        enabled: bool = True,
        stream: TextIO | None = None,
        title: str = "SkinMiner Live Status",
        refresh_interval: float = 0.2,
        header_lines: list[str] | None = None,
    ) -> None:
        self.stream = stream or sys.stdout
        self.enabled = bool(enabled and hasattr(self.stream, "isatty") and self.stream.isatty())
        self.title = title
        self.refresh_interval = refresh_interval
        self.header_lines = header_lines or []
        self._stages: dict[str, StageStatus] = {}
        self._order: list[str] = []
        self._last_render_at = 0.0
        self._is_open = False

    def __enter__(self) -> "PipelineStatusPanel":
        if self.enabled:
            _enable_windows_vt_mode(self.stream)
            self._is_open = True
            self._render(force=True)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if not self.enabled:
            return
        self._render(force=True)
        self.stream.write("\x1b[?25h\n")
        self.stream.flush()
        self._is_open = False

    def register_stage(self, key: str, label: str) -> None:
        """Register a stage so it appears in a stable order in the panel."""

        if key not in self._stages:
            self._stages[key] = StageStatus(label=label)
            self._order.append(key)
            self._render()

    def start_stage(self, key: str, *, total: int | None = None, detail: str = "") -> None:
        """Mark a stage as running and optionally set its total count."""

        stage = self._require_stage(key)
        stage.state = "running"
        stage.started_at = time.perf_counter()
        stage.finished_at = None
        stage.completed = 0
        stage.total = total
        stage.current_item = ""
        stage.detail = detail
        self._render(force=True)

    def update_stage(
        self,
        key: str,
        *,
        completed: int | None = None,
        total: int | None = None,
        current_item: str | None = None,
        detail: str | None = None,
        state: str | None = None,
        force: bool = False,
    ) -> None:
        """Update one or more stage fields and refresh the live panel."""

        stage = self._require_stage(key)
        if stage.started_at is None and state == "running":
            stage.started_at = time.perf_counter()
        if completed is not None:
            stage.completed = completed
        if total is not None:
            stage.total = total
        if current_item is not None:
            stage.current_item = current_item
        if detail is not None:
            stage.detail = detail
        if state is not None:
            stage.state = state
            if state in {"done", "skipped", "error"} and stage.finished_at is None:
                stage.finished_at = time.perf_counter()
        self._render(force=force)

    def finish_stage(
        self,
        key: str,
        *,
        completed: int | None = None,
        total: int | None = None,
        detail: str = "",
    ) -> None:
        """Mark a stage as completed."""

        stage = self._require_stage(key)
        if completed is None and stage.total is not None:
            completed = stage.total
        self.update_stage(
            key,
            completed=completed,
            total=total,
            detail=detail,
            current_item="",
            state="done",
            force=True,
        )

    def skip_stage(self, key: str, detail: str = "") -> None:
        """Mark a stage as intentionally skipped."""

        self.update_stage(key, detail=detail, current_item="", state="skipped", force=True)

    def fail_stage(self, key: str, detail: str = "") -> None:
        """Mark a stage as failed."""

        self.update_stage(key, detail=detail, current_item="", state="error", force=True)

    def make_callback(self, key: str) -> ProgressCallback:
        """Build a simple callback suitable for per-item progress updates."""

        def callback(completed: int, current_item: str = "", detail: str = "") -> None:
            self.update_stage(
                key,
                completed=completed,
                current_item=current_item,
                detail=detail,
                state="running",
            )

        return callback

    def _require_stage(self, key: str) -> StageStatus:
        if key not in self._stages:
            self.register_stage(key, key)
        return self._stages[key]

    def _render(self, *, force: bool = False) -> None:
        if not self.enabled or not self._is_open:
            return
        now = time.perf_counter()
        if not force and now - self._last_render_at < self.refresh_interval:
            return
        self._last_render_at = now

        width = shutil.get_terminal_size((140, 40)).columns
        stage_width = 18
        state_width = 10
        progress_width = 12
        elapsed_width = 10
        current_width = min(32, max(18, width // 5))
        detail_width = max(20, width - (stage_width + state_width + progress_width + elapsed_width + current_width + 19))

        lines: list[str] = [self.title]
        lines.extend(self.header_lines)
        lines.append("-" * width)
        header = (
            f"| {_truncate('Stage', stage_width)} "
            f"| {_truncate('State', state_width)} "
            f"| {_truncate('Progress', progress_width)} "
            f"| {_truncate('Elapsed', elapsed_width)} "
            f"| {_truncate('Current', current_width)} "
            f"| {_truncate('Detail', detail_width)} |"
        )
        lines.append(header)
        lines.append("-" * width)

        for key in self._order:
            stage = self._stages[key]
            elapsed = 0.0
            if stage.started_at is not None:
                elapsed = (stage.finished_at or now) - stage.started_at
            progress = "-"
            if stage.total is not None:
                progress = f"{stage.completed}/{stage.total}"
            elif stage.completed:
                progress = str(stage.completed)
            lines.append(
                f"| {_truncate(stage.label, stage_width)} "
                f"| {_truncate(stage.state.upper(), state_width)} "
                f"| {_truncate(progress, progress_width)} "
                f"| {_truncate(_format_seconds(elapsed), elapsed_width)} "
                f"| {_truncate(stage.current_item, current_width)} "
                f"| {_truncate(stage.detail, detail_width)} |"
            )

        rendered = "\n".join(lines)
        self.stream.write("\x1b[?25l\x1b[2J\x1b[H")
        self.stream.write(rendered)
        self.stream.write("\x1b[J")
        self.stream.flush()
