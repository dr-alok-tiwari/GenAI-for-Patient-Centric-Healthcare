from __future__ import annotations

from dataclasses import asdict, dataclass
from io import BytesIO
import math
import re
from typing import Any

import numpy as np
from PIL import Image, ImageFilter, ImageOps, UnidentifiedImageError

try:
    import pydicom
except ImportError:  # pragma: no cover - handled with a user-facing message
    pydicom = None


RASTER_SUFFIXES = {".png", ".jpg", ".jpeg", ".tif", ".tiff"}
DICOM_SUFFIXES = {".dcm", ".dicom"}


@dataclass
class MedicalImage:
    image: Image.Image
    source_format: str
    safe_metadata: dict[str, str]
    warnings: list[str]


def _first_value(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (list, tuple)):
        value = value[0] if value else None
    try:
        return float(value)
    except (TypeError, ValueError):
        try:
            return float(value[0])
        except (TypeError, ValueError, IndexError):
            return None


def _normalise_array(array: np.ndarray) -> np.ndarray:
    values = np.asarray(array, dtype=np.float32)
    finite = values[np.isfinite(values)]
    if finite.size == 0:
        raise ValueError("The image contains no finite pixel values.")
    low, high = np.percentile(finite, [1, 99])
    if math.isclose(float(low), float(high)):
        low, high = float(finite.min()), float(finite.max())
    if math.isclose(float(low), float(high)):
        return np.zeros(values.shape, dtype=np.uint8)
    scaled = np.clip((values - low) / (high - low), 0, 1) * 255
    return scaled.astype(np.uint8)


def _safe_dicom_metadata(dataset: Any) -> dict[str, str]:
    """Return technical tags only; deliberately exclude patient/study identifiers."""
    tag_names = (
        "Modality",
        "Rows",
        "Columns",
        "BitsStored",
        "PhotometricInterpretation",
        "PixelSpacing",
        "WindowCenter",
        "WindowWidth",
        "NumberOfFrames",
    )
    metadata: dict[str, str] = {}
    for name in tag_names:
        value = getattr(dataset, name, None)
        if value not in (None, ""):
            metadata[name] = str(value)
    return metadata


def _load_dicom(payload: bytes) -> MedicalImage:
    if pydicom is None:
        raise ValueError(
            "DICOM support is unavailable because pydicom is not installed. "
            "Install the project requirements or upload a de-identified PNG/JPEG export."
        )
    try:
        dataset = pydicom.dcmread(BytesIO(payload), force=True)
    except Exception as exc:
        raise ValueError(f"The DICOM file could not be read: {exc}") from exc
    if "PixelData" not in dataset:
        raise ValueError("The DICOM object has no pixel data.")
    try:
        pixels = np.asarray(dataset.pixel_array)
    except Exception as exc:
        raise ValueError(
            "The DICOM pixel data could not be decoded. Compressed studies may require "
            "an additional DICOM decoder; use a de-identified PNG/JPEG export for this demo."
        ) from exc

    warnings: list[str] = []
    if pixels.ndim == 4:
        pixels = pixels[0]
        warnings.append("Only the first frame of this multi-frame object is previewed.")
    if pixels.ndim == 3 and pixels.shape[-1] not in (3, 4):
        pixels = pixels[0]
        warnings.append("Only the first frame/slice is previewed; this is not volume analysis.")
    if pixels.ndim == 3 and pixels.shape[-1] in (3, 4):
        image = Image.fromarray(_normalise_array(pixels)).convert("L")
    else:
        pixels = np.squeeze(pixels).astype(np.float32)
        if pixels.ndim != 2:
            raise ValueError("This DICOM pixel layout is not supported by the workshop preview.")
        slope = _first_value(getattr(dataset, "RescaleSlope", 1)) or 1.0
        intercept = _first_value(getattr(dataset, "RescaleIntercept", 0)) or 0.0
        pixels = pixels * slope + intercept
        center = _first_value(getattr(dataset, "WindowCenter", None))
        width = _first_value(getattr(dataset, "WindowWidth", None))
        if center is not None and width and width > 1:
            low = center - width / 2
            high = center + width / 2
            pixels = np.clip(pixels, low, high)
        rendered = _normalise_array(pixels)
        if str(getattr(dataset, "PhotometricInterpretation", "")).upper() == "MONOCHROME1":
            rendered = 255 - rendered
        image = Image.fromarray(rendered)

    frames = int(getattr(dataset, "NumberOfFrames", 1) or 1)
    if frames > 1 and not any("first frame" in item.lower() for item in warnings):
        warnings.append("Only the first frame is previewed; this is not cine/volume analysis.")
    return MedicalImage(
        image=image,
        source_format="DICOM",
        safe_metadata=_safe_dicom_metadata(dataset),
        warnings=warnings,
    )


def load_medical_image(payload: bytes, filename: str) -> MedicalImage:
    if not payload:
        raise ValueError("The uploaded file is empty.")
    suffix = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if suffix in DICOM_SUFFIXES:
        return _load_dicom(payload)
    if suffix and suffix not in RASTER_SUFFIXES:
        raise ValueError("Supported formats are PNG, JPEG, TIFF and uncompressed DICOM.")
    try:
        with Image.open(BytesIO(payload)) as source:
            source.seek(0)
            image = ImageOps.exif_transpose(source).convert("L").copy()
            source_format = str(source.format or suffix.lstrip(".") or "raster").upper()
    except (UnidentifiedImageError, OSError) as exc:
        raise ValueError("The uploaded file is not a readable PNG, JPEG, TIFF or DICOM image.") from exc
    return MedicalImage(
        image=image,
        source_format=source_format,
        safe_metadata={"Width": str(image.width), "Height": str(image.height)},
        warnings=[],
    )


def compute_technical_metrics(image: Image.Image) -> dict[str, float | int]:
    grayscale = image.convert("L")
    pixels = np.asarray(grayscale, dtype=np.float32)
    if pixels.size == 0:
        raise ValueError("The image has no pixels.")
    p01, p50, p99 = np.percentile(pixels, [1, 50, 99])
    histogram = np.bincount(pixels.astype(np.uint8).ravel(), minlength=256).astype(np.float64)
    probability = histogram / histogram.sum()
    nonzero = probability[probability > 0]
    entropy = float(-(nonzero * np.log2(nonzero)).sum())
    blurred = np.asarray(grayscale.filter(ImageFilter.BoxBlur(2)), dtype=np.float32)
    detail_variance = float(np.var(pixels - blurred))
    return {
        "width_px": int(grayscale.width),
        "height_px": int(grayscale.height),
        "aspect_ratio": round(grayscale.width / max(grayscale.height, 1), 3),
        "mean_intensity": round(float(pixels.mean()), 2),
        "median_intensity": round(float(p50), 2),
        "intensity_std": round(float(pixels.std()), 2),
        "robust_intensity_span": round(float(p99 - p01), 2),
        "dark_clipping_pct": round(float((pixels <= 2).mean() * 100), 2),
        "light_clipping_pct": round(float((pixels >= 253).mean() * 100), 2),
        "entropy_bits": round(entropy, 3),
        "detail_variance_proxy": round(detail_variance, 2),
    }


def technical_observations(metrics: dict[str, float | int]) -> list[str]:
    observations: list[str] = []
    if min(int(metrics["width_px"]), int(metrics["height_px"])) < 512:
        observations.append(
            "Limited pixel dimensions may reduce the visibility of fine detail in a projected workshop demo."
        )
    if float(metrics["robust_intensity_span"]) < 60:
        observations.append(
            "The robust intensity span is narrow; review windowing, export settings and display conditions."
        )
    if float(metrics["dark_clipping_pct"]) > 5:
        observations.append(
            "A notable fraction of pixels is near black; check for clipping, borders or inappropriate windowing."
        )
    if float(metrics["light_clipping_pct"]) > 5:
        observations.append(
            "A notable fraction of pixels is near white; check for clipping, annotations or inappropriate windowing."
        )
    if float(metrics["detail_variance_proxy"]) < 12:
        observations.append(
            "The local-detail proxy is low; possible smoothing, compression or blur should be reviewed visually."
        )
    if not observations:
        observations.append(
            "No major warning was triggered by these simple pixel checks; modality-specific adequacy still requires expert review."
        )
    observations.append(
        "These indicators are not validated diagnostic image-quality measures and cannot establish positioning, exposure or diagnostic adequacy."
    )
    return observations


def build_multimodal_prompt(
    case: dict[str, Any],
    clinical_context: str,
    clinical_question: str,
    metrics: dict[str, float | int] | None,
) -> str:
    checklist = "\n".join(f"- {item}" for item in case["systematic_review"])
    cannot_miss = "\n".join(f"- {item}" for item in case["cannot_miss"])
    limitations = "\n".join(f"- {item}" for item in case["limitations"])
    metric_text = (
        "\n".join(f"- {key.replace('_', ' ').title()}: {value}" for key, value in metrics.items())
        if metrics
        else "- No local image metrics available; assess technical adequacy directly from the uploaded image."
    )
    return f"""ROLE
You are a radiology teaching assistant supporting a qualified {case['human_owner']}. You are not the reporting radiologist and must not issue a final diagnosis, treatment recommendation or clearance.

EXAM
Modality/workflow: {case['modality']} — {case['title']}
Body region: {case['body_region']}
Educational context: {clinical_context or '[Not supplied]'}
Clinical question: {clinical_question or '[Not supplied]'}

IMAGE
The image is uploaded separately. First confirm whether the available file, view, sequence and image quality are sufficient for the requested task. If this is a single frame from a CT/MRI/ultrasound study, state that the full series cannot be assessed.

LOCAL TECHNICAL INDICATORS
{metric_text}
Treat these as non-validated technical hints, not clinical findings.

SYSTEMATIC REVIEW
Use this checklist, but report only what is genuinely visible:
{checklist}

CANNOT-MISS ESCALATION CHECK
Explicitly state whether each item can be assessed from the available image; do not claim absence when the image/view is insufficient:
{cannot_miss}

CASE-SPECIFIC LIMITS
{limitations}

REQUIRED OUTPUT
1. Image/view and technical adequacy
2. Visible observations, organised anatomically
3. Findings that cannot be assessed from the supplied image
4. Pattern-based possibilities for qualified review, with supporting and opposing observations
5. Prior studies, sequences, views or clinical information needed
6. Any potentially urgent feature requiring immediate human escalation
7. Draft report scaffold with Technique, Findings, Impression possibilities and Limitations
8. Verification checklist for the {case['human_owner']}

SAFETY RULES
- Separate observations from hypotheses.
- Do not invent measurements, views, sequences, contrast phase, laterality or prior-study comparison.
- Do not infer protected or identifying attributes.
- Do not assign a definitive diagnosis, final staging, RECIST response, BI-RADS category, treatment plan or patient disposition.
- If image quality or coverage is insufficient, stop and say exactly what is missing.
- End with: “Educational AI-assisted draft only—final interpretation and action require a qualified professional reviewing the complete study and clinical context.”
"""


def review_ai_draft(text: str) -> dict[str, list[str] | int]:
    cleaned = text.strip()
    if not cleaned:
        return {
            "score": 0,
            "present_sections": [],
            "missing_sections": ["No draft supplied"],
            "risk_phrases": [],
            "recommendations": ["Paste an AI-generated draft to run the structural review."],
        }
    section_terms = {
        "Technique/adequacy": ("technique", "adequacy", "quality"),
        "Findings/observations": ("finding", "observation"),
        "Impression/possibilities": ("impression", "possibilit", "differential"),
        "Limitations": ("limitation", "cannot assess", "insufficient"),
        "Human verification": ("radiologist", "qualified", "human review", "clinician review"),
    }
    lower = cleaned.lower()
    present = [name for name, terms in section_terms.items() if any(term in lower for term in terms)]
    missing = [name for name in section_terms if name not in present]
    risky_patterns = {
        "Unsupported certainty": r"\b(definitely|certainly|confirmed diagnosis|diagnostic of)\b",
        "Autonomous clearance": r"\b(cleared for|safe to discharge|no further review|required no follow[- ]?up)\b",
        "Treatment instruction": r"\b(start|prescribe|administer|stop)\s+(antibiotic|steroid|anticoagulant|medication|treatment)\b",
        "False normality risk": r"\b(completely normal|rules out all|no abnormality whatsoever)\b",
    }
    risks = [label for label, pattern in risky_patterns.items() if re.search(pattern, lower)]
    score = max(0, min(100, 20 * len(present) - 15 * len(risks)))
    recommendations = [f"Add or clarify: {item}." for item in missing]
    recommendations.extend(f"Review language flagged for: {item}." for item in risks)
    if not recommendations:
        recommendations.append(
            "The basic structure is present; a qualified professional must still verify every observation against the complete study."
        )
    return {
        "score": score,
        "present_sections": present,
        "missing_sections": missing,
        "risk_phrases": risks,
        "recommendations": recommendations,
    }


def export_session_payload(
    case: dict[str, Any],
    clinical_context: str,
    clinical_question: str,
    metrics: dict[str, float | int] | None,
    observations: list[str],
    draft_review: dict[str, list[str] | int] | None,
) -> dict[str, Any]:
    return {
        "case": {
            "case_id": case["case_id"],
            "title": case["title"],
            "modality": case["modality"],
            "body_region": case["body_region"],
            "human_owner": case["human_owner"],
        },
        "clinical_context": clinical_context,
        "clinical_question": clinical_question,
        "technical_metrics": metrics,
        "technical_observations": observations,
        "draft_review": draft_review,
        "image_included": False,
        "disclaimer": (
            "Educational workflow only. The export excludes image pixels and identifiers. "
            "Final interpretation requires a qualified professional reviewing the complete study."
        ),
    }


def serialise_medical_image(image: MedicalImage) -> dict[str, Any]:
    data = asdict(image)
    data.pop("image", None)
    return data
