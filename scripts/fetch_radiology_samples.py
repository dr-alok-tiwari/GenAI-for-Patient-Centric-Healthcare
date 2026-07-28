#!/usr/bin/env python3
"""Fetch and attribute the bundled Wikimedia Commons radiology teaching samples."""

from __future__ import annotations

from html import unescape
from io import BytesIO
import json
from pathlib import Path
import re
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parents[1]
SAMPLE_ROOT = ROOT / "assets" / "radiology_samples"
MANIFEST_PATH = ROOT / "data" / "radiology_sample_manifest.json"
ATTRIBUTION_PATH = SAMPLE_ROOT / "ATTRIBUTION.md"
COMMONS_API = "https://commons.wikimedia.org/w/api.php"
USER_AGENT = (
    "GenAI-Healthcare-Educational-Samples/1.0 "
    "(https://github.com/dr-alok-tiwari/GenAI-for-Patient-Centric-Healthcare)"
)
ALLOWED_LICENSE_PREFIXES = ("CC0", "CC BY", "Public domain")


SOURCES: dict[str, list[str]] = {
    "RAD-001": [
        "File:Chest radiograph in influensa and H influenzae, lateral.jpg",
        "File:Chest radiograph in influensa and H influenzae, posteroanterior.jpg",
        "File:Human bocavirus 1 pneumonia.jpg",
        "File:X-ray of lobar pneumonia.jpg",
        "File:Chest Xray PA 3-8-2010.png",
    ],
    "RAD-002": [
        "File:Tubusspitze im rechten Hauptbronchus 64W - CR ap - 001.jpg",
        "File:Tubusspitze im rechten Hauptbronchus 64W - CR ap - 001 - Annotation.jpg",
        "File:ETtubeGoodPosition.png",
        "File:ETTubeandNGtubeMarked.png",
        "File:ETtubeToHigh.png",
    ],
    "RAD-003": [
        "File:Intracerebral hemorrage (CT scan).jpg",
        "File:CT Head Injury Scan.jpg",
        "File:NCCT Brain Imaging.jpg",
        "File:Traumatic acute epidual hematoma.jpg",
        "File:Brain trauma CT.jpg",
    ],
    "RAD-004": [
        "File:Pulmonary embolism CTPA.JPEG",
        "File:CTA Chest With Massive Pulmonary Embolism and Complete Occlusion.jpg",
        "File:Acute RV dilatation post PE.png",
        "File:SADDLE PE.JPG",
        "File:Ct lungenembolie.0001.jpg",
    ],
    "RAD-005": [
        "File:MRI glioma 28 yr old male.JPG",
        "File:Glioblastoma - MR coronal with contrast.jpg",
        "File:AFIP-00405558-Glioblastoma-Radiology.jpg",
        "File:Glioblastoma - MR sagittal with contrast.jpg",
        "File:AFIP-00405589-Glioblastoma-Radiology.jpg",
    ],
    "RAD-006": [
        "File:L4-l5-disc-herniation.png",
        "File:Spinal-disc-protrusion-l5.jpg",
        "File:Cervical Spine MRI showing degenerative changes closeup.jpg",
        "File:Hernie discale L4 L5.png",
        "File:C6-C7-disc-herniation-cevical-mri-scan.jpg",
    ],
    "RAD-007": [
        "File:Scaphoid fracture - barely visible on initial X-ray.jpg",
        "File:Calcaneus Fracture.jpg",
        "File:Whole body radiograph in trauma.jpg",
        "File:Radiograph of Barton's fracture.jpg",
        "File:Simple mandible fracture.jpg",
    ],
    "RAD-008": [
        "File:Axial plane ultrasound at the navel.jpg",
        "File:Ultrasonography of cholecystitis.jpg",
        "File:Ultrasonography of abdominal aortic aneurysm in axial plane, annotated.jpg",
        "File:Ultrasonography of common bile duct stone, with arrow.jpg",
        "File:Ultrasonography of pancreatic cancer.jpg",
    ],
    "RAD-009": [
        "File:Ultrasound of embryo at 5 weeks.png",
        "File:Embryo at 14 weeks profile.JPG",
        "File:Embryo at 12 weeks 2 arms.JPG",
        "File:Fetal face profile.jpg",
        "File:Scan20semanas1.png",
    ],
    "RAD-010": [
        "File:Mammogram showing dense and fatty breasts.jpg",
        "File:Mammogram showing normal dense breasts.jpg",
        "File:Mammogram showing normal fatty breast.jpg",
        "File:Mammogram with obvious cancer.jpg",
        "File:Mammogram with subtle cancer.jpg",
    ],
}


def _plain_text(value: str | None, limit: int = 800) -> str:
    text = re.sub(r"<[^>]+>", " ", value or "")
    text = re.sub(r"\s+", " ", unescape(text)).strip()
    return text[:limit]


def _request(url: str, attempts: int = 6) -> bytes:
    delay = 2
    for attempt in range(attempts):
        try:
            request = Request(url, headers={"User-Agent": USER_AGENT})
            with urlopen(request, timeout=60) as response:
                return response.read()
        except HTTPError as exc:
            if exc.code not in {429, 500, 502, 503, 504} or attempt == attempts - 1:
                raise
        except URLError:
            if attempt == attempts - 1:
                raise
        time.sleep(delay)
        delay *= 2
    raise RuntimeError(f"Unable to download {url}")


def _metadata_for_titles(titles: list[str]) -> dict[str, dict[str, Any]]:
    metadata: dict[str, dict[str, Any]] = {}
    for start in range(0, len(titles), 10):
        batch = titles[start : start + 10]
        query = urlencode(
            {
                "action": "query",
                "format": "json",
                "formatversion": "2",
                "prop": "imageinfo",
                "iiprop": "url|mime|size|extmetadata",
                "iiurlwidth": "960",
                "redirects": "1",
                "titles": "|".join(batch),
            }
        )
        payload = json.loads(_request(f"{COMMONS_API}?{query}"))
        for page in payload.get("query", {}).get("pages", []):
            if page.get("missing"):
                raise RuntimeError(f"Commons source does not exist: {page['title']}")
            image_info = page.get("imageinfo", [])
            if not image_info:
                raise RuntimeError(f"Commons source has no downloadable image: {page['title']}")
            metadata[page["title"]] = image_info[0]
        time.sleep(1)
    return metadata


def _normalise_license_url(value: str) -> str:
    if value.startswith("//"):
        return f"https:{value}"
    return value


def _save_teaching_copy(payload: bytes, destination: Path) -> tuple[int, int]:
    with Image.open(BytesIO(payload)) as source:
        image = ImageOps.exif_transpose(source)
        image.thumbnail((960, 960), Image.Resampling.LANCZOS)
        if image.mode not in {"L", "RGB"}:
            image = image.convert("RGB")
        destination.parent.mkdir(parents=True, exist_ok=True)
        image.save(destination, format="JPEG", quality=88, optimize=True)
        return image.size


def _attribution_markdown(samples: list[dict[str, Any]]) -> str:
    lines = [
        "# Radiology sample image attribution",
        "",
        "These 50 raster teaching copies were sourced from Wikimedia Commons. Each "
        "copy was resized to fit within 960 × 960 pixels and re-encoded as JPEG; "
        "no clinical annotation was added. They are educational examples, not a "
        "validated diagnostic dataset or model benchmark.",
        "",
    ]
    for case_id in SOURCES:
        lines.extend([f"## {case_id}", ""])
        for sample in [item for item in samples if item["case_id"] == case_id]:
            author = sample["author"] or "Author not supplied on source page"
            lines.extend(
                [
                    f"- **{sample['title']}** — {author}. "
                    f"[Source]({sample['source_page']}) · "
                    f"[{sample['license']}]({sample['license_url'] or sample['source_page']})",
                    "",
                ]
            )
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    if any(len(titles) < 5 for titles in SOURCES.values()):
        raise RuntimeError("Every radiology category must define at least five sources.")
    all_titles = [title for titles in SOURCES.values() for title in titles]
    if len(all_titles) != len(set(all_titles)):
        raise RuntimeError("Each bundled radiology sample must use a unique source.")

    metadata = _metadata_for_titles(all_titles)
    samples: list[dict[str, Any]] = []
    for case_id, titles in SOURCES.items():
        for index, requested_title in enumerate(titles, start=1):
            info = metadata.get(requested_title)
            if info is None:
                raise RuntimeError(
                    f"Commons returned a redirect title that is not mapped: {requested_title}"
                )
            ext = info.get("extmetadata", {})
            license_name = _plain_text(
                ext.get("LicenseShortName", {}).get("value"), limit=100
            )
            if not license_name.startswith(ALLOWED_LICENSE_PREFIXES):
                raise RuntimeError(
                    f"Unsupported license for {requested_title}: {license_name or 'missing'}"
                )
            source_url = info.get("thumburl") or info["url"]
            local_path = f"assets/radiology_samples/{case_id}/sample_{index:02d}.jpg"
            destination = ROOT / local_path
            width, height = _save_teaching_copy(_request(source_url), destination)
            title = requested_title.removeprefix("File:")
            samples.append(
                {
                    "sample_id": f"{case_id}-S{index:02d}",
                    "case_id": case_id,
                    "title": title,
                    "local_path": local_path,
                    "width_px": width,
                    "height_px": height,
                    "description": _plain_text(
                        ext.get("ImageDescription", {}).get("value")
                        or ext.get("ObjectName", {}).get("value")
                    ),
                    "author": _plain_text(ext.get("Artist", {}).get("value"), limit=400),
                    "license": license_name,
                    "license_url": _normalise_license_url(
                        ext.get("LicenseUrl", {}).get("value", "")
                    ),
                    "source_page": info["descriptionurl"],
                    "original_url": info["url"],
                    "modification": (
                        "Resized to fit within 960 × 960 pixels and re-encoded as JPEG; "
                        "no clinical annotation added."
                    ),
                }
            )
            print(f"Saved {case_id} sample {index}: {title}")
            time.sleep(0.15)

    manifest = {
        "schema_version": 1,
        "source_repository": "Wikimedia Commons",
        "usage_note": (
            "Public teaching images for guided workflow practice. Not a validated "
            "diagnostic dataset, not ground truth and not suitable for model evaluation."
        ),
        "samples": samples,
    }
    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    ATTRIBUTION_PATH.write_text(_attribution_markdown(samples), encoding="utf-8")
    print(f"Wrote {len(samples)} samples across {len(SOURCES)} categories.")


if __name__ == "__main__":
    main()
