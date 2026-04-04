"""Long-run monitoring and logging helpers for large pipeline executions."""

from __future__ import annotations

import json
import math
import sys
import time
import traceback
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from utils.io import ensure_parent, normalize_json_value

ProgressCallback = Callable[[int, str, str], None]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _payload_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float, bool)):
        return str(value)
    if isinstance(value, dict):
        if value.get("type") == "input_image":
            return ""
        return " ".join(_payload_text(item) for item in value.values())
    if isinstance(value, (list, tuple, set)):
        return " ".join(_payload_text(item) for item in value)
    if hasattr(value, "model_dump"):
        return _payload_text(value.model_dump(mode="json"))
    return str(value)


def _estimate_tokens(value: Any) -> int:
    text = _payload_text(value)
    if not text:
        return 0
    return max(1, math.ceil(len(text) / 4))


def _usage_value(usage: Any, *names: str) -> int | None:
    for name in names:
        if isinstance(usage, dict) and usage.get(name) is not None:
            return int(usage[name])
        if hasattr(usage, name) and getattr(usage, name) is not None:
            return int(getattr(usage, name))
    return None


def _extract_usage(response: Any) -> dict[str, int] | None:
    usage = getattr(response, "usage", None)
    if usage is None and hasattr(response, "model_dump"):
        try:
            payload = response.model_dump(mode="json")
            usage = payload.get("usage")
        except Exception:
            usage = None
    if usage is None:
        return None
    input_tokens = _usage_value(usage, "input_tokens", "prompt_tokens")
    output_tokens = _usage_value(usage, "output_tokens", "completion_tokens")
    total_tokens = _usage_value(usage, "total_tokens")
    if total_tokens is None and input_tokens is not None and output_tokens is not None:
        total_tokens = input_tokens + output_tokens
    if input_tokens is None and output_tokens is None and total_tokens is None:
        return None
    return {
        "input_tokens": input_tokens or 0,
        "output_tokens": output_tokens or 0,
        "total_tokens": total_tokens or ((input_tokens or 0) + (output_tokens or 0)),
    }


def _llm_error_category(exc: BaseException) -> str:
    error_type = type(exc).__name__.lower()
    message = str(exc).lower()
    if "validation" in error_type:
        return "schema_validation_failures"
    if any(token in error_type for token in ("json", "parse")) or any(
        token in message for token in ("invalid json", "malformed", "schema mismatch", "parse failed", "unable to parse", "structured output")
    ):
        return "malformed_output_failures"
    if "ratelimit" in error_type or "rate limit" in message:
        return "rate_limit_failures"
    if "timeout" in error_type or "timed out" in message:
        return "timeout_failures"
    if any(token in error_type for token in ("authentication", "permission")):
        return "auth_failures"
    if any(token in error_type for token in ("connection", "transport")) or any(
        token in message for token in ("connection", "network", "transport")
    ):
        return "transport_failures"
    if "api" in error_type or "server" in message or "status code" in message:
        return "api_failures"
    return "other_failures"


class LongRunMonitor:
    """Write lightweight machine-readable logs for long pipeline runs."""

    def __init__(
        self,
        *,
        enabled: bool,
        run_id: str,
        output_dir: str | Path,
        progress_log_every: int = 25,
    ) -> None:
        self.enabled = enabled
        self.run_id = run_id
        self.output_dir = Path(output_dir)
        self.progress_log_every = max(1, progress_log_every)
        self.long_run_dir = self.output_dir / "long_run"
        self.events_path = self.long_run_dir / "events.jsonl"
        self.state_path = self.long_run_dir / "state.json"
        self.summary_path = self.long_run_dir / "summary.json"
        self._stages: dict[str, dict[str, Any]] = {}
        self._last_logged_progress: dict[str, int] = {}
        self._llm_usage: dict[str, dict[str, Any]] = {}
        self._llm_reliability: dict[str, dict[str, Any]] = {}
        self._active_stage: str = ""
        self._last_error: dict[str, Any] | None = None
        self._started_at = time.perf_counter()
        self._started_at_utc = _utc_now()

    def __enter__(self) -> "LongRunMonitor":
        if self.enabled:
            self.long_run_dir.mkdir(parents=True, exist_ok=True)
            self.record_run_started()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if not self.enabled:
            return
        if exc is not None:
            self.record_unhandled_exception(exc, traceback.format_exception(exc_type, exc, tb))
            self.record_run_finished(status="failed")
        else:
            self.record_run_finished(status="completed")

    @property
    def summary_label(self) -> str:
        """Human-readable summary for status headers."""

        return f"on -> {self.long_run_dir}"

    def record_run_started(self, metadata: dict[str, Any] | None = None) -> None:
        """Record the start of a long pipeline run."""

        self._append_event("run_started", metadata=metadata or {})
        self._write_state_snapshot(force=True)

    def record_run_finished(self, *, status: str) -> None:
        """Record the end of a long pipeline run and write a summary snapshot."""

        payload = self._summary_payload(status=status)
        ensure_parent(self.summary_path).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        self._append_event("run_finished", status=status, summary_path=str(self.summary_path))
        self._write_state_snapshot(force=True, status=status)

    def register_stage(self, key: str, label: str) -> None:
        """Register a stage so its latest state is visible in snapshots."""

        if not self.enabled or key in self._stages:
            return
        self._stages[key] = {
            "label": label,
            "state": "pending",
            "started_at_utc": None,
            "finished_at_utc": None,
            "elapsed_seconds": 0.0,
            "completed": 0,
            "total": None,
            "current_item": "",
            "detail": "",
        }
        self._write_state_snapshot()

    def stage_started(self, key: str, label: str, *, total: int | None = None, detail: str = "") -> None:
        """Record the start of a pipeline stage."""

        if not self.enabled:
            return
        self.register_stage(key, label)
        stage = self._stages[key]
        stage.update(
            {
                "label": label,
                "state": "running",
                "started_at_utc": _utc_now(),
                "_started_perf": time.perf_counter(),
                "finished_at_utc": None,
                "elapsed_seconds": 0.0,
                "completed": 0,
                "total": total,
                "current_item": "",
                "detail": detail,
            }
        )
        self._active_stage = key
        self._last_logged_progress[key] = 0
        self._append_event("stage_started", stage=key, label=label, total=total, detail=detail)
        self._write_state_snapshot(force=True)

    def stage_progress(self, key: str, *, completed: int, current_item: str = "", detail: str = "") -> None:
        """Record throttled stage progress for long runs."""

        if not self.enabled or key not in self._stages:
            return
        stage = self._stages[key]
        stage["state"] = "running"
        stage["completed"] = completed
        stage["current_item"] = current_item
        stage["detail"] = detail
        stage["elapsed_seconds"] = self._elapsed_seconds(stage)
        last_logged = self._last_logged_progress.get(key, 0)
        should_log = completed == 0 or completed == stage.get("total") or completed - last_logged >= self.progress_log_every
        if should_log:
            self._last_logged_progress[key] = completed
            self._append_event(
                "stage_progress",
                stage=key,
                completed=completed,
                total=stage.get("total"),
                current_item=current_item,
                detail=detail,
            )
            self._write_state_snapshot()

    def stage_finished(self, key: str, *, completed: int | None = None, total: int | None = None, detail: str = "") -> None:
        """Record successful stage completion."""

        if not self.enabled or key not in self._stages:
            return
        stage = self._stages[key]
        if completed is not None:
            stage["completed"] = completed
        if total is not None:
            stage["total"] = total
        stage["state"] = "done"
        stage["_finished_perf"] = time.perf_counter()
        stage["current_item"] = ""
        stage["detail"] = detail
        stage["finished_at_utc"] = _utc_now()
        stage["elapsed_seconds"] = self._elapsed_seconds(stage)
        if self._active_stage == key:
            self._active_stage = ""
        self._append_event(
            "stage_finished",
            stage=key,
            completed=stage.get("completed"),
            total=stage.get("total"),
            detail=detail,
            elapsed_seconds=stage.get("elapsed_seconds"),
        )
        self._write_state_snapshot(force=True)

    def stage_skipped(self, key: str, *, detail: str = "") -> None:
        """Record an intentionally skipped stage."""

        if not self.enabled:
            return
        stage = self._stages.get(key)
        if stage is None:
            self.register_stage(key, key)
            stage = self._stages[key]
        stage["state"] = "skipped"
        stage["_finished_perf"] = time.perf_counter()
        stage["detail"] = detail
        stage["finished_at_utc"] = _utc_now()
        stage["elapsed_seconds"] = self._elapsed_seconds(stage)
        self._append_event("stage_skipped", stage=key, detail=detail)
        self._write_state_snapshot(force=True)

    def stage_failed(self, key: str, *, detail: str = "", error_type: str = "", current_item: str = "") -> None:
        """Record a failed stage."""

        if not self.enabled:
            return
        stage = self._stages.get(key)
        if stage is None:
            self.register_stage(key, key)
            stage = self._stages[key]
        stage["state"] = "error"
        stage["detail"] = detail
        if current_item:
            stage["current_item"] = current_item
        stage["_finished_perf"] = time.perf_counter()
        stage["finished_at_utc"] = _utc_now()
        stage["elapsed_seconds"] = self._elapsed_seconds(stage)
        self._last_error = {
            "stage": key,
            "error_type": error_type,
            "detail": detail,
            "current_item": current_item or stage.get("current_item", ""),
            "timestamp_utc": _utc_now(),
        }
        self._append_event(
            "stage_failed",
            stage=key,
            error_type=error_type,
            detail=detail,
            current_item=current_item or stage.get("current_item", ""),
        )
        self._write_state_snapshot(force=True)

    def make_progress_callback(self, key: str) -> ProgressCallback:
        """Build a callback that logs throttled stage progress."""

        def callback(completed: int, current_item: str = "", detail: str = "") -> None:
            self.stage_progress(key, completed=completed, current_item=current_item, detail=detail)

        return callback

    def record_llm_usage(
        self,
        *,
        module_name: str,
        model_name: str,
        response: Any | None = None,
        prompt_payload: Any | None = None,
        output_payload: Any | None = None,
        metadata: dict[str, Any] | None = None,
        retries_used: int = 0,
    ) -> None:
        """Record exact or estimated LLM usage for one completed call."""

        if not self.enabled:
            return
        usage = _extract_usage(response)
        estimated = usage is None
        if usage is None:
            input_tokens = _estimate_tokens(prompt_payload)
            output_tokens = _estimate_tokens(output_payload)
            usage = {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens,
            }

        bucket = self._llm_usage.setdefault(
            module_name,
            {
                "model_name": model_name,
                "requests": 0,
                "estimated_requests": 0,
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
            },
        )
        bucket["requests"] += 1
        if estimated:
            bucket["estimated_requests"] += 1
        bucket["input_tokens"] += usage["input_tokens"]
        bucket["output_tokens"] += usage["output_tokens"]
        bucket["total_tokens"] += usage["total_tokens"]

        reliability = self._llm_reliability.setdefault(
            module_name,
            {
                "model_name": model_name,
                "requests": 0,
                "retries_attempted": 0,
                "retried_requests": 0,
                "retry_successes": 0,
                "final_failures": 0,
                "attempt_failures": 0,
                "schema_validation_failures": 0,
                "malformed_output_failures": 0,
                "rate_limit_failures": 0,
                "timeout_failures": 0,
                "auth_failures": 0,
                "transport_failures": 0,
                "api_failures": 0,
                "other_failures": 0,
            },
        )
        reliability["requests"] += 1
        if retries_used > 0:
            reliability["retried_requests"] += 1
            reliability["retry_successes"] += 1

        self._append_event(
            "llm_usage",
            module_name=module_name,
            model_name=model_name,
            estimated=estimated,
            usage=usage,
            retries_used=retries_used,
            metadata=metadata or {},
        )
        self._write_state_snapshot()

    def record_llm_attempt_failure(
        self,
        *,
        module_name: str,
        model_name: str,
        exc: BaseException,
        attempt: int,
        max_retries: int,
        metadata: dict[str, Any] | None = None,
        terminal: bool,
    ) -> None:
        """Record one failed LLM attempt, including malformed-output and retry buckets."""

        if not self.enabled:
            return
        category = _llm_error_category(exc)
        reliability = self._llm_reliability.setdefault(
            module_name,
            {
                "model_name": model_name,
                "requests": 0,
                "retries_attempted": 0,
                "retried_requests": 0,
                "retry_successes": 0,
                "final_failures": 0,
                "attempt_failures": 0,
                "schema_validation_failures": 0,
                "malformed_output_failures": 0,
                "rate_limit_failures": 0,
                "timeout_failures": 0,
                "auth_failures": 0,
                "transport_failures": 0,
                "api_failures": 0,
                "other_failures": 0,
            },
        )
        reliability["attempt_failures"] += 1
        reliability[category] += 1
        if not terminal:
            reliability["retries_attempted"] += 1
        else:
            reliability["final_failures"] += 1

        self._append_event(
            "llm_attempt_failure",
            module_name=module_name,
            model_name=model_name,
            error_type=type(exc).__name__,
            error_category=category,
            detail=str(exc),
            attempt=attempt,
            max_retries=max_retries,
            terminal=terminal,
            metadata=metadata or {},
        )
        self._write_state_snapshot()

    def record_unhandled_exception(self, exc: BaseException, formatted_traceback: list[str]) -> None:
        """Record an unhandled exception at the run level."""

        if not self.enabled:
            return
        self._last_error = {
            "stage": self._active_stage,
            "error_type": type(exc).__name__,
            "detail": str(exc),
            "traceback": "".join(formatted_traceback),
            "timestamp_utc": _utc_now(),
        }
        self._append_event(
            "unhandled_exception",
            stage=self._active_stage,
            error_type=type(exc).__name__,
            detail=str(exc),
            traceback="".join(formatted_traceback),
        )
        self._write_state_snapshot(force=True, status="failed")

    def _elapsed_seconds(self, stage: dict[str, Any]) -> float:
        started_perf = stage.get("_started_perf")
        if started_perf is None:
            return float(stage.get("elapsed_seconds") or 0.0)
        finished_perf = stage.get("_finished_perf")
        end = finished_perf if finished_perf is not None else time.perf_counter()
        return round(float(end - started_perf), 3)

    def _summary_payload(self, *, status: str) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "status": status,
            "started_at_utc": self._started_at_utc,
            "finished_at_utc": _utc_now(),
            "elapsed_seconds": round(time.perf_counter() - self._started_at, 3),
            "active_stage": self._active_stage,
            "last_error": self._last_error,
            "llm_usage": self._llm_usage,
            "llm_reliability": self._llm_reliability,
            "stages": {
                key: {field: value for field, value in stage.items() if not field.startswith("_")}
                for key, stage in self._stages.items()
            },
            "command": " ".join(sys.argv),
        }

    def _write_state_snapshot(self, *, force: bool = False, status: str = "running") -> None:
        if not self.enabled:
            return
        payload = self._summary_payload(status=status)
        ensure_parent(self.state_path).write_text(json.dumps(normalize_json_value(payload), ensure_ascii=False, indent=2), encoding="utf-8")

    def _append_event(self, event_type: str, **payload: Any) -> None:
        if not self.enabled:
            return
        row = {
            "timestamp_utc": _utc_now(),
            "run_id": self.run_id,
            "event_type": event_type,
            **payload,
        }
        out_path = ensure_parent(self.events_path)
        with out_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(normalize_json_value(row), ensure_ascii=False) + "\n")


def merge_progress_callbacks(*callbacks: ProgressCallback | None) -> ProgressCallback | None:
    """Merge multiple optional progress callbacks into a single callback."""

    active_callbacks = [callback for callback in callbacks if callback is not None]
    if not active_callbacks:
        return None

    def callback(completed: int, current_item: str = "", detail: str = "") -> None:
        for item in active_callbacks:
            item(completed, current_item, detail)

    return callback


def record_openai_usage(
    monitor: LongRunMonitor | None,
    *,
    module_name: str,
    model_name: str,
    response: Any | None = None,
    prompt_payload: Any | None = None,
    output_payload: Any | None = None,
    metadata: dict[str, Any] | None = None,
    retries_used: int = 0,
) -> None:
    """Record LLM usage on the active long-run monitor when available."""

    if monitor is None:
        return
    monitor.record_llm_usage(
        module_name=module_name,
        model_name=model_name,
        response=response,
        prompt_payload=prompt_payload,
        output_payload=output_payload,
        metadata=metadata,
        retries_used=retries_used,
    )


def record_openai_attempt_failure(
    monitor: LongRunMonitor | None,
    *,
    module_name: str,
    model_name: str,
    exc: BaseException,
    attempt: int,
    max_retries: int,
    metadata: dict[str, Any] | None = None,
    terminal: bool,
) -> None:
    """Record one failed LLM attempt on the active long-run monitor when available."""

    if monitor is None:
        return
    monitor.record_llm_attempt_failure(
        module_name=module_name,
        model_name=model_name,
        exc=exc,
        attempt=attempt,
        max_retries=max_retries,
        metadata=metadata,
        terminal=terminal,
    )
