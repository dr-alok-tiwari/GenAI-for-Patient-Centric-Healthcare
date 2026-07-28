from __future__ import annotations

from io import BytesIO
import unittest

from PIL import Image

from modules import imaging_core
from modules.imaging_core import (
    build_multimodal_prompt,
    compute_technical_metrics,
    load_medical_image,
    review_ai_draft,
    technical_observations,
)


CASE = {
    "title": "Chest X-ray",
    "modality": "X-ray",
    "body_region": "Chest",
    "human_owner": "radiologist",
    "systematic_review": ["Technical adequacy", "Lungs and pleura"],
    "cannot_miss": ["Pneumothorax"],
    "limitations": ["Single-view limitation"],
}


class ImagingCoreTests(unittest.TestCase):
    def _png(self, color: int = 128) -> bytes:
        image = Image.new("L", (640, 512), color=color)
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        return buffer.getvalue()

    def test_raster_load_and_metrics(self) -> None:
        loaded = load_medical_image(self._png(), "synthetic.png")
        metrics = compute_technical_metrics(loaded.image)
        self.assertEqual(metrics["width_px"], 640)
        self.assertEqual(metrics["height_px"], 512)
        self.assertIn("robust_intensity_span", metrics)

    def test_technical_observations_always_include_limitation(self) -> None:
        loaded = load_medical_image(self._png(), "synthetic.png")
        observations = technical_observations(compute_technical_metrics(loaded.image))
        self.assertTrue(any("not validated diagnostic" in item for item in observations))

    def test_prompt_preserves_professional_owner_and_safety_boundary(self) -> None:
        prompt = build_multimodal_prompt(CASE, "Synthetic context", "Review image", None)
        self.assertIn("qualified radiologist", prompt)
        self.assertIn("must not issue a final diagnosis", prompt)
        self.assertIn("Pneumothorax", prompt)

    def test_draft_review_flags_unsafe_certainty(self) -> None:
        result = review_ai_draft(
            "Technique adequate. Findings are definitely diagnostic of pneumonia. "
            "Impression recorded. Limitations: none. Radiologist review required."
        )
        self.assertIn("Unsupported certainty", result["risk_phrases"])
        self.assertLess(result["score"], 100)

    def test_empty_file_rejected(self) -> None:
        with self.assertRaises(ValueError):
            load_medical_image(b"", "empty.png")

    @unittest.skipIf(imaging_core.pydicom is None, "pydicom is not installed")
    def test_dicom_preview_excludes_patient_identifiers(self) -> None:
        from pydicom.dataset import FileDataset, FileMetaDataset
        from pydicom.uid import ExplicitVRLittleEndian, SecondaryCaptureImageStorage, generate_uid
        import numpy as np

        meta = FileMetaDataset()
        meta.MediaStorageSOPClassUID = SecondaryCaptureImageStorage
        meta.MediaStorageSOPInstanceUID = generate_uid()
        meta.TransferSyntaxUID = ExplicitVRLittleEndian
        dataset = FileDataset(None, {}, file_meta=meta, preamble=b"\0" * 128)
        dataset.SOPClassUID = SecondaryCaptureImageStorage
        dataset.SOPInstanceUID = meta.MediaStorageSOPInstanceUID
        dataset.PatientName = "Hidden^Person"
        dataset.PatientID = "SHOULD-NOT-LEAK"
        dataset.Modality = "DX"
        dataset.Rows = 16
        dataset.Columns = 16
        dataset.SamplesPerPixel = 1
        dataset.PhotometricInterpretation = "MONOCHROME2"
        dataset.BitsAllocated = 16
        dataset.BitsStored = 12
        dataset.HighBit = 11
        dataset.PixelRepresentation = 0
        dataset.PixelData = np.arange(256, dtype=np.uint16).reshape(16, 16).tobytes()
        buffer = BytesIO()
        dataset.save_as(buffer, enforce_file_format=True)

        loaded = load_medical_image(buffer.getvalue(), "synthetic.dcm")
        self.assertEqual(loaded.source_format, "DICOM")
        self.assertEqual(loaded.safe_metadata["Modality"], "DX")
        self.assertNotIn("PatientName", loaded.safe_metadata)
        self.assertNotIn("PatientID", loaded.safe_metadata)


if __name__ == "__main__":
    unittest.main()
