"""CV-based figure digitization with replay overlays."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import cv2
import numpy as np

from extractors.common import artifact_path
from extractors.figure.models import DigitizedCurveArtifact, DigitizedEndpointArtifact, FigureTriageArtifact
from schemas.models import ExtractorRunContext
from utils.io import write_jsonl, write_optional_csv

MIN_EDGE_POINTS = 800
MIN_CLUSTER_POINTS = 250


def _parse_bbox(value: Any) -> list[float] | None:
    if value is None:
        return None
    if isinstance(value, list):
        return value
    if isinstance(value, str) and value.strip():
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            return None
    if not isinstance(value, list) or len(value) != 4:
        return None
    try:
        x0, y0, x1, y1 = [float(item) for item in value]
    except (TypeError, ValueError):
        return None
    x0 = min(max(0.0, x0), 1.0)
    y0 = min(max(0.0, y0), 1.0)
    x1 = min(max(0.0, x1), 1.0)
    y1 = min(max(0.0, y1), 1.0)
    if x1 - x0 < 0.08 or y1 - y0 < 0.08:
        return None
    return [x0, y0, x1, y1]


def _bbox_to_pixels(image: np.ndarray, bbox: list[float]) -> tuple[int, int, int, int]:
    height, width = image.shape[:2]
    x0, y0, x1, y1 = bbox
    left = int(max(0, min(width - 2, round(float(x0) * width))))
    right = int(max(left + 1, min(width - 1, round(float(x1) * width))))
    top = int(max(0, min(height - 2, round(float(y0) * height))))
    bottom = int(max(top + 1, min(height - 1, round(float(y1) * height))))
    return left, top, right, bottom


def _normalize_bbox_from_rect(image: np.ndarray, rect: tuple[int, int, int, int]) -> list[float]:
    height, width = image.shape[:2]
    left, top, right, bottom = rect
    return [
        max(0.0, min(1.0, left / max(1.0, width))),
        max(0.0, min(1.0, top / max(1.0, height))),
        max(0.0, min(1.0, right / max(1.0, width))),
        max(0.0, min(1.0, bottom / max(1.0, height))),
    ]


def _crop_by_bbox(image: np.ndarray, bbox: list[float]) -> np.ndarray:
    left, top, right, bottom = _bbox_to_pixels(image, bbox)
    return image[top:bottom, left:right].copy()


def _write_preprocessed(run_context: ExtractorRunContext, triage: FigureTriageArtifact, image: np.ndarray) -> str:
    path = artifact_path(
        run_context,
        "figure",
        "digitize_preprocessed",
        f"{triage.trace_id or triage.paper_id}.png",
    )
    cv2.imwrite(str(path), image)
    return str(path)


def _write_bbox_overlay(
    run_context: ExtractorRunContext,
    triage: FigureTriageArtifact,
    image: np.ndarray,
    bbox: list[float],
    bbox_source: str,
) -> str:
    overlay = image.copy()
    left, top, right, bottom = _bbox_to_pixels(image, bbox)
    cv2.rectangle(overlay, (left, top), (right, bottom), (0, 255, 0), thickness=5)
    cv2.putText(
        overlay,
        bbox_source,
        (left, max(24, top - 10)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2,
        cv2.LINE_AA,
    )
    path = artifact_path(
        run_context,
        "figure",
        "bbox_overlays",
        f"{triage.trace_id or triage.paper_id}.png",
    )
    cv2.imwrite(str(path), overlay)
    return str(path)


def _auto_detect_plot_bbox(image: np.ndarray) -> tuple[list[float] | None, dict[str, float | int]]:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    adaptive = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 31, 7)
    edges = cv2.Canny(blurred, 40, 120)
    combined = cv2.bitwise_or(adaptive, edges)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9))
    combined = cv2.morphologyEx(combined, cv2.MORPH_CLOSE, kernel, iterations=2)
    contours, _ = cv2.findContours(combined, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    height, width = image.shape[:2]
    page_area = float(height * width) or 1.0
    best_bbox: list[float] | None = None
    best_score = 0.0
    best_area_ratio = 0.0

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        area_ratio = (w * h) / page_area
        if w < width * 0.18 or h < height * 0.14:
            continue
        if not 0.04 <= area_ratio <= 0.75:
            continue
        aspect = w / max(1.0, float(h))
        if not 0.55 <= aspect <= 2.8:
            continue
        contour_area = cv2.contourArea(contour)
        rectangularity = contour_area / max(1.0, float(w * h))
        center_penalty = abs(((x + w / 2.0) / width) - 0.5)
        score = (area_ratio * 3.0) + (rectangularity * 2.0) - center_penalty
        if score > best_score:
            best_score = score
            best_area_ratio = area_ratio
            best_bbox = _normalize_bbox_from_rect(image, (x, y, x + w, y + h))

    diagnostics = {
        "bbox_candidates": int(len(contours)),
        "bbox_best_score": round(best_score, 4),
        "bbox_best_area_ratio": round(best_area_ratio, 4),
    }
    return best_bbox, diagnostics


def _tighten_bbox_with_foreground(image: np.ndarray, bbox: list[float]) -> tuple[list[float], str]:
    crop = _crop_by_bbox(image, bbox)
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
    dark_mask = cv2.threshold(gray, 225, 255, cv2.THRESH_BINARY_INV)[1]
    sat_mask = cv2.inRange(hsv, (0, 35, 20), (179, 255, 255))
    combined = cv2.bitwise_or(dark_mask, sat_mask)
    combined = cv2.morphologyEx(
        combined,
        cv2.MORPH_CLOSE,
        cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7)),
        iterations=1,
    )
    ys, xs = np.where(combined > 0)
    if xs.size < 400:
        return bbox, "triage"

    x_min = float(xs.min()) / max(1.0, crop.shape[1])
    x_max = float(xs.max()) / max(1.0, crop.shape[1])
    y_min = float(ys.min()) / max(1.0, crop.shape[0])
    y_max = float(ys.max()) / max(1.0, crop.shape[0])
    if x_max - x_min < 0.35 or y_max - y_min < 0.30:
        return bbox, "triage"

    base_x0, base_y0, base_x1, base_y1 = bbox
    width = base_x1 - base_x0
    height = base_y1 - base_y0
    refined = [
        base_x0 + width * max(0.0, x_min - 0.02),
        base_y0 + height * max(0.0, y_min - 0.02),
        base_x0 + width * min(1.0, x_max + 0.02),
        base_y0 + height * min(1.0, y_max + 0.02),
    ]
    parsed = _parse_bbox(refined)
    return (parsed or bbox), ("triage_refined" if parsed else "triage")


def _resolve_plot_bbox(image: np.ndarray, triage: FigureTriageArtifact) -> tuple[list[float] | None, str, dict[str, float | int]]:
    triage_bbox = _parse_bbox(triage.plot_bbox)
    if triage_bbox is not None:
        refined_bbox, refined_source = _tighten_bbox_with_foreground(image, triage_bbox)
        return refined_bbox, refined_source, {"bbox_candidates": 0, "bbox_best_score": 0.0, "bbox_best_area_ratio": 0.0}

    detected_bbox, diagnostics = _auto_detect_plot_bbox(image)
    if detected_bbox is not None:
        return detected_bbox, "auto_detect", diagnostics
    return None, "missing", diagnostics


def _expand_bbox(bbox: list[float], pad_x: float = 0.05, pad_y: float = 0.06) -> list[float] | None:
    x0, y0, x1, y1 = bbox
    expanded = [
        max(0.0, x0 - pad_x),
        max(0.0, y0 - pad_y),
        min(1.0, x1 + pad_x),
        min(1.0, y1 + pad_y),
    ]
    return _parse_bbox(expanded)


def _default_plot_bbox() -> list[float]:
    return [0.08, 0.12, 0.94, 0.92]


def _iter_image_candidates(triage: FigureTriageArtifact) -> list[tuple[int | None, str, str]]:
    ordered: list[tuple[int | None, str, str]] = []
    seen: set[str] = set()

    primary_path = str(triage.selected_image_path or "").strip()
    if primary_path:
        ordered.append((triage.page_number, primary_path, "triage_primary"))
        seen.add(primary_path)

    for index, path in enumerate(triage.selected_image_paths):
        normalized_path = str(path or "").strip()
        if not normalized_path or normalized_path in seen:
            continue
        page_number = triage.selected_pages[index] if index < len(triage.selected_pages) else triage.page_number
        origin = "triage_alternative" if page_number != triage.page_number else "triage_selected"
        ordered.append((page_number, normalized_path, origin))
        seen.add(normalized_path)

    return ordered


def _iter_bbox_candidates(
    image: np.ndarray,
    triage: FigureTriageArtifact,
) -> list[tuple[list[float], str, dict[str, float | int]]]:
    candidates: list[tuple[list[float], str, dict[str, float | int]]] = []
    seen: set[tuple[float, float, float, float]] = set()

    def add(bbox: list[float] | None, source: str, diagnostics: dict[str, float | int]) -> None:
        if bbox is None:
            return
        key = tuple(round(value, 4) for value in bbox)
        if key in seen:
            return
        seen.add(key)
        candidates.append((bbox, source, diagnostics))

    resolved_bbox, resolved_source, resolved_diag = _resolve_plot_bbox(image, triage)
    add(resolved_bbox, resolved_source, resolved_diag)
    if resolved_bbox is not None:
        add(_expand_bbox(resolved_bbox, pad_x=0.04, pad_y=0.05), f"{resolved_source}_expanded", resolved_diag)

    auto_bbox, auto_diag = _auto_detect_plot_bbox(image)
    add(auto_bbox, "auto_detect", auto_diag)
    if auto_bbox is not None:
        add(_expand_bbox(auto_bbox, pad_x=0.05, pad_y=0.06), "auto_detect_expanded", auto_diag)

    add(_default_plot_bbox(), "default_plot_bbox", {"bbox_candidates": 0, "bbox_best_score": 0.0, "bbox_best_area_ratio": 0.0})
    return candidates


def _remove_axes_edges(edges: np.ndarray) -> np.ndarray:
    height, width = edges.shape[:2]
    lines = cv2.HoughLinesP(
        edges,
        1,
        np.pi / 180,
        threshold=120,
        minLineLength=int(0.65 * min(height, width)),
        maxLineGap=10,
    )
    output = edges.copy()
    if lines is not None:
        for line in lines[:, 0, :]:
            x1, y1, x2, y2 = line
            cv2.line(output, (x1, y1), (x2, y2), 0, thickness=7)
    return output


def _enhance_crop(crop_bgr: np.ndarray) -> np.ndarray:
    lab = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2LAB)
    l_channel, a_channel, b_channel = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    enhanced_l = clahe.apply(l_channel)
    enhanced = cv2.merge((enhanced_l, a_channel, b_channel))
    enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
    return cv2.detailEnhance(enhanced, sigma_s=8, sigma_r=0.15)


def _filter_small_components(mask: np.ndarray, min_area: int = 18) -> np.ndarray:
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    output = np.zeros_like(mask)
    for label_index in range(1, num_labels):
        if stats[label_index, cv2.CC_STAT_AREA] >= min_area:
            output[labels == label_index] = 255
    return output


def _extract_edge_mask(crop_bgr: np.ndarray) -> tuple[np.ndarray, np.ndarray, dict[str, int]]:
    preprocessed = _enhance_crop(crop_bgr)
    gray = cv2.cvtColor(preprocessed, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges_primary = cv2.Canny(blurred, 40, 120)
    edges_secondary = cv2.Canny(blurred, 20, 80)
    adaptive = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 31, 5)
    hsv = cv2.cvtColor(preprocessed, cv2.COLOR_BGR2HSV)
    color_mask = cv2.inRange(hsv, (0, 30, 20), (179, 255, 255))

    combined = cv2.bitwise_or(edges_primary, edges_secondary)
    combined = cv2.bitwise_or(combined, adaptive)
    combined = cv2.bitwise_or(combined, color_mask)
    combined = _remove_axes_edges(combined)
    combined = cv2.morphologyEx(
        combined,
        cv2.MORPH_CLOSE,
        cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)),
        iterations=2,
    )
    combined = cv2.dilate(combined, np.ones((3, 3), np.uint8), iterations=1)
    combined = _filter_small_components(combined)

    diagnostics = {
        "edge_primary_points": int(np.count_nonzero(edges_primary)),
        "edge_secondary_points": int(np.count_nonzero(edges_secondary)),
        "adaptive_points": int(np.count_nonzero(adaptive)),
        "color_points": int(np.count_nonzero(color_mask)),
        "combined_points": int(np.count_nonzero(combined)),
    }
    return combined, preprocessed, diagnostics


def _kmeans_cluster_colors(hsv_pixels: np.ndarray, clusters: int) -> tuple[np.ndarray, np.ndarray]:
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 50, 0.5)
    compactness, labels, centers = cv2.kmeans(
        hsv_pixels.astype(np.float32),
        clusters,
        None,
        criteria,
        3,
        cv2.KMEANS_PP_CENTERS,
    )
    return labels.flatten(), centers


def _build_curve_from_points(xs: np.ndarray, ys: np.ndarray, min_cols: int = 30) -> tuple[np.ndarray, np.ndarray]:
    if xs.size < 50:
        return np.array([]), np.array([])
    columns: dict[int, list[int]] = {}
    for x_value, y_value in zip(xs, ys):
        columns.setdefault(int(x_value), []).append(int(y_value))
    if len(columns) < min_cols:
        return np.array([]), np.array([])
    x_out = np.array(sorted(columns), dtype=np.float32)
    y_out = np.array([int(np.median(columns[int(x_value)])) for x_value in x_out], dtype=np.float32)
    return x_out, y_out


def _pixel_to_data(
    xpix: np.ndarray,
    ypix: np.ndarray,
    x_min: float,
    x_max: float,
    y_min: float,
    y_max: float,
    width: int,
    height: int,
) -> tuple[np.ndarray, np.ndarray]:
    x_data = x_min + (xpix / max(1.0, width - 1)) * (x_max - x_min)
    y_data = y_max - (ypix / max(1.0, height - 1)) * (y_max - y_min)
    return x_data, y_data


def _interp_at(x_values: np.ndarray, y_values: np.ndarray, query_x: float) -> float:
    if x_values.size < 2:
        return float("nan")
    order = np.argsort(x_values)
    xs = x_values[order]
    ys = y_values[order]
    clipped_x = min(max(query_x, float(xs[0])), float(xs[-1]))
    return float(np.interp(clipped_x, xs, ys))


def _coarse_color_name(hsv_center: np.ndarray) -> str:
    hue, saturation, value = hsv_center
    if value < 40:
        return "black"
    if saturation < 40 and value > 180:
        return "gray"
    if saturation < 40:
        return "gray"
    degrees = float(hue) * 2.0
    if degrees < 15 or degrees >= 345:
        return "red"
    if degrees < 45:
        return "orange"
    if degrees < 75:
        return "yellow"
    if degrees < 150:
        return "green"
    if degrees < 210:
        return "cyan"
    if degrees < 270:
        return "blue"
    if degrees < 330:
        return "purple"
    return "red"


def _write_overlay(
    run_context: ExtractorRunContext,
    triage: FigureTriageArtifact,
    crop: np.ndarray,
    xpix: np.ndarray,
    ypix: np.ndarray,
    curve_id: str,
) -> str:
    overlay = crop.copy()
    for x_value, y_value in zip(xpix.astype(int), ypix.astype(int)):
        cv2.circle(overlay, (int(x_value), int(y_value)), radius=1, color=(0, 0, 255), thickness=-1)
    path = artifact_path(
        run_context,
        "figure",
        "digitize_overlays",
        f"{triage.paper_id}__{curve_id}.png",
    )
    cv2.imwrite(str(path), overlay)
    return str(path)


def _write_crop(run_context: ExtractorRunContext, triage: FigureTriageArtifact, crop: np.ndarray) -> str:
    path = artifact_path(
        run_context,
        "figure",
        "digitize_crops",
        f"{triage.trace_id or triage.paper_id}.png",
    )
    cv2.imwrite(str(path), crop)
    return str(path)


def _write_mask(run_context: ExtractorRunContext, triage: FigureTriageArtifact, mask: np.ndarray) -> str:
    path = artifact_path(
        run_context,
        "figure",
        "digitize_masks",
        f"{triage.trace_id or triage.paper_id}.png",
    )
    cv2.imwrite(str(path), mask)
    return str(path)


def _curve_trace_id(triage: FigureTriageArtifact, curve_id: str) -> str:
    base = triage.trace_id or triage.paper_id
    return f"{base}::{curve_id}"


def digitize_figure_curves(
    triage_artifacts: list[FigureTriageArtifact],
    run_context: ExtractorRunContext,
    output_curves_jsonl: str | Path | None = None,
    output_endpoints_jsonl: str | Path | None = None,
    output_endpoints_csv: str | Path | None = None,
) -> dict[str, list[DigitizedCurveArtifact] | list[DigitizedEndpointArtifact]]:
    """Digitize figure curves and emit traceable curve artifacts."""

    curves: list[DigitizedCurveArtifact] = []
    endpoints: list[DigitizedEndpointArtifact] = []

    for triage in triage_artifacts:
        if triage.digitizable != "yes" or triage.recommended_route != "digitize":
            continue
        if triage.y_kind == "percent":
            continue

        image_candidates = _iter_image_candidates(triage)
        if not image_candidates:
            endpoints.append(
                DigitizedEndpointArtifact(
                    paper_id=triage.paper_id,
                    doi=triage.doi,
                    title=triage.title,
                    trace_id=f"{triage.trace_id}::missing_plot_context",
                    triage_trace_id=triage.trace_id,
                    figure_id=triage.figure_id,
                    page_number=triage.page_number,
                    subplot=triage.subplot,
                    image_path="",
                    status="fail_missing_plot_context",
                    diagnostics={"reason": "missing_selected_image_candidates"},
                )
            )
            continue

        required = [triage.x_min, triage.x_max, triage.y_min, triage.y_max]
        if any(value is None for value in required):
            endpoints.append(
                DigitizedEndpointArtifact(
                    paper_id=triage.paper_id,
                    doi=triage.doi,
                    title=triage.title,
                    trace_id=f"{triage.trace_id}::missing_axis_range",
                    triage_trace_id=triage.trace_id,
                    figure_id=triage.figure_id,
                    page_number=triage.page_number,
                    subplot=triage.subplot,
                    image_path=str(triage.selected_image_path or ""),
                    status="fail_missing_axis_range",
                    diagnostics={"reason": "missing_axis_range"},
                )
            )
            continue

        best_candidate: dict[str, Any] | None = None
        image_read_failures = 0
        bbox_attempts = 0

        for page_number, image_path, image_origin in image_candidates:
            if not image_path or not Path(image_path).exists():
                continue
            image = cv2.imread(image_path)
            if image is None:
                image_read_failures += 1
                continue

            for bbox, bbox_source, bbox_diagnostics in _iter_bbox_candidates(image, triage):
                bbox_attempts += 1
                crop = _crop_by_bbox(image, bbox)
                if crop.size == 0:
                    continue
                mask, preprocessed, edge_diagnostics = _extract_edge_mask(crop)
                ys, xs = np.where(mask > 0)
                candidate = {
                    "page_number": page_number if page_number is not None else triage.page_number,
                    "image_path": image_path,
                    "image_origin": image_origin,
                    "image": image,
                    "bbox": bbox,
                    "bbox_source": bbox_source,
                    "bbox_diagnostics": bbox_diagnostics,
                    "crop": crop,
                    "mask": mask,
                    "preprocessed": preprocessed,
                    "edge_diagnostics": edge_diagnostics,
                    "edge_points": int(xs.size),
                    "xs": xs,
                    "ys": ys,
                }
                if best_candidate is None or candidate["edge_points"] > best_candidate["edge_points"]:
                    best_candidate = candidate

        if best_candidate is None:
            failure_status = "fail_image_read" if image_read_failures else "fail_missing_plot_context"
            endpoints.append(
                DigitizedEndpointArtifact(
                    paper_id=triage.paper_id,
                    doi=triage.doi,
                    title=triage.title,
                    trace_id=f"{triage.trace_id}::{failure_status}",
                    triage_trace_id=triage.trace_id,
                    figure_id=triage.figure_id,
                    page_number=triage.page_number,
                    subplot=triage.subplot,
                    image_path=str(triage.selected_image_path or ""),
                    status=failure_status,
                    diagnostics={
                        "reason": "no_usable_image_candidate",
                        "image_candidates_tried": len(image_candidates),
                        "image_read_failures": image_read_failures,
                        "bbox_candidates_tried": bbox_attempts,
                    },
                )
            )
            continue

        image_path = str(best_candidate["image_path"])
        image = best_candidate["image"]
        bbox = best_candidate["bbox"]
        bbox_source = str(best_candidate["bbox_source"])
        bbox_diagnostics = dict(best_candidate["bbox_diagnostics"])
        crop = best_candidate["crop"]
        mask = best_candidate["mask"]
        preprocessed = best_candidate["preprocessed"]
        xs = best_candidate["xs"]
        ys = best_candidate["ys"]
        page_number = best_candidate["page_number"]
        bbox_overlay_path = _write_bbox_overlay(run_context, triage, image, bbox, bbox_source)
        crop_path = _write_crop(run_context, triage, crop)
        mask_path = _write_mask(run_context, triage, mask)
        preprocessed_path = _write_preprocessed(run_context, triage, preprocessed)
        height, width = crop.shape[:2]
        shared_diagnostics = {
            **bbox_diagnostics,
            **best_candidate["edge_diagnostics"],
            "bbox_source": bbox_source,
            "image_origin": str(best_candidate["image_origin"]),
            "image_candidates_tried": len(image_candidates),
            "bbox_candidates_tried": bbox_attempts,
        }
        if xs.size < MIN_EDGE_POINTS:
            endpoints.append(
                DigitizedEndpointArtifact(
                    paper_id=triage.paper_id,
                    doi=triage.doi,
                    title=triage.title,
                    trace_id=f"{triage.trace_id}::few_edges",
                    triage_trace_id=triage.trace_id,
                    figure_id=triage.figure_id,
                    page_number=page_number,
                    subplot=triage.subplot,
                    image_path=image_path,
                    crop_path=crop_path,
                    mask_path=mask_path,
                    preprocessed_path=preprocessed_path,
                    bbox_overlay_path=bbox_overlay_path,
                    bbox_source=bbox_source,
                    bbox_used=bbox,
                    status="fail_few_edges",
                    diagnostics={
                        **shared_diagnostics,
                        "edge_points": int(xs.size),
                    },
                )
            )
            continue

        hsv = cv2.cvtColor(preprocessed, cv2.COLOR_BGR2HSV)
        hsv_pixels = hsv[ys, xs, :]
        approx_curves = max(1, min(int(triage.approx_curves_count or 1), 6))
        curve_parts: list[tuple[str, np.ndarray | None, np.ndarray, np.ndarray, np.ndarray, np.ndarray]] = []

        if approx_curves == 1:
            xpix, ypix = _build_curve_from_points(xs, ys)
            if xpix.size >= 30:
                curve_parts.append(("cluster_1", None, xs, ys, xpix, ypix))
        else:
            try:
                labels, centers = _kmeans_cluster_colors(hsv_pixels, approx_curves)
                for cluster_index in range(approx_curves):
                    member_idx = np.where(labels == cluster_index)[0]
                    if member_idx.size < MIN_CLUSTER_POINTS:
                        continue
                    xs_cluster = xs[member_idx]
                    ys_cluster = ys[member_idx]
                    xpix, ypix = _build_curve_from_points(xs_cluster, ys_cluster)
                    if xpix.size >= 30:
                        curve_parts.append((f"cluster_{cluster_index + 1}", centers[cluster_index], xs_cluster, ys_cluster, xpix, ypix))
            except Exception:
                xpix, ypix = _build_curve_from_points(xs, ys)
                if xpix.size >= 30:
                    curve_parts.append(("cluster_1", None, xs, ys, xpix, ypix))

        if not curve_parts:
            endpoints.append(
                DigitizedEndpointArtifact(
                    paper_id=triage.paper_id,
                    doi=triage.doi,
                    title=triage.title,
                    trace_id=f"{triage.trace_id}::no_curves",
                    triage_trace_id=triage.trace_id,
                    figure_id=triage.figure_id,
                    page_number=page_number,
                    subplot=triage.subplot,
                    image_path=image_path,
                    crop_path=crop_path,
                    mask_path=mask_path,
                    preprocessed_path=preprocessed_path,
                    bbox_overlay_path=bbox_overlay_path,
                    bbox_source=bbox_source,
                    bbox_used=bbox,
                    status="fail_no_curves",
                    diagnostics={
                        **shared_diagnostics,
                        "edge_points": int(xs.size),
                        "approx_curves": approx_curves,
                    },
                )
            )
            continue

        x_min = float(triage.x_min)
        x_max = float(triage.x_max)
        y_min = float(triage.y_min)
        y_max = float(triage.y_max)
        x_unit = triage.axes_x_unit
        y_unit = triage.axes_y_unit
        y_kind = triage.y_kind

        for curve_id, center, xs_cluster, ys_cluster, xpix, ypix in curve_parts:
            x_data, y_data = _pixel_to_data(xpix, ypix, x_min, x_max, y_min, y_max, width, height)
            q_final = _interp_at(x_data, y_data, x_max)
            color_name = _coarse_color_name(center) if center is not None else ""
            overlay_path = _write_overlay(run_context, triage, crop, xpix, ypix, curve_id)
            trace_id = _curve_trace_id(triage, curve_id)
            diagnostics = {
                **shared_diagnostics,
                "edge_points": int(xs.size),
                "approx_curves": approx_curves,
                "cluster_points": int(xs_cluster.size),
            }
            curve_artifact = DigitizedCurveArtifact(
                paper_id=triage.paper_id,
                doi=triage.doi,
                title=triage.title,
                trace_id=trace_id,
                triage_trace_id=triage.trace_id,
                figure_id=triage.figure_id,
                page_number=page_number,
                subplot=triage.subplot,
                image_path=image_path,
                crop_path=crop_path,
                mask_path=mask_path,
                overlay_path=overlay_path,
                preprocessed_path=preprocessed_path,
                bbox_overlay_path=bbox_overlay_path,
                bbox_source=bbox_source,
                bbox_used=bbox,
                curve_id=curve_id,
                curve_color=color_name,
                x_unit=x_unit,
                y_unit=y_unit,
                y_kind=y_kind,
                x_min=x_min,
                x_max=x_max,
                y_min=y_min,
                y_max=y_max,
                t_last=float(x_max),
                q_final=float(q_final) if np.isfinite(q_final) else None,
                curve_xy=[[float(x_value), float(y_value)] for x_value, y_value in zip(x_data.tolist(), y_data.tolist())],
                status="ok",
                diagnostics=diagnostics,
            )
            curves.append(curve_artifact)
            endpoints.append(
                DigitizedEndpointArtifact(
                    paper_id=triage.paper_id,
                    doi=triage.doi,
                    title=triage.title,
                    trace_id=trace_id,
                    triage_trace_id=triage.trace_id,
                    figure_id=triage.figure_id,
                    page_number=page_number,
                    subplot=triage.subplot,
                    image_path=image_path,
                    crop_path=crop_path,
                    mask_path=mask_path,
                    overlay_path=overlay_path,
                    preprocessed_path=preprocessed_path,
                    bbox_overlay_path=bbox_overlay_path,
                    bbox_source=bbox_source,
                    bbox_used=bbox,
                    status="ok",
                    curve_id=curve_id,
                    curve_color=color_name,
                    endpoint_time=float(x_max),
                    endpoint_time_unit=x_unit,
                    endpoint_value=curve_artifact.q_final,
                    endpoint_unit=y_unit,
                    y_kind=y_kind,
                    diagnostics=diagnostics,
                )
            )

    if output_curves_jsonl:
        write_jsonl(curves, output_curves_jsonl)
    if output_endpoints_jsonl:
        write_jsonl(endpoints, output_endpoints_jsonl)
    if output_endpoints_csv:
        write_optional_csv([endpoint.model_dump(mode="json") for endpoint in endpoints], output_endpoints_csv)
    return {
        "curves": curves,
        "endpoints": endpoints,
    }
