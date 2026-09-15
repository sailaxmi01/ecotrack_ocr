"""
main.py
Ties preprocess -> OCR -> extraction into one callable function.
This is what the rest of the team (or your API layer) should import and call.
"""

import json
import os
import tempfile

from preprocess import save_preprocessed
from ocr_engine import run_ocr
from extractor import extract_items


def process_bill(image_path: str, confidence_threshold: float = 0.6, use_preprocessing: bool = False) -> dict:
    """
    Full pipeline: raw bill image -> structured items.

    use_preprocessing: PaddleOCR already does strong internal cleanup
    (orientation/unwarp/textline detection), so for clean, sharp images
    (screenshots, printed receipts, clear photos) leave this False.
    Turn it on only for rough, blurry, tilted real-world phone photos
    where the extra denoise/threshold/deskew steps actually help.

    Returns:
        {
            "items": [ {name, quantity, price, confidence, raw_text}, ... ],
            "item_count": int,
            "source_image": str
        }
    """
    if use_preprocessing:
        with tempfile.TemporaryDirectory() as tmp_dir:
            processed_path = os.path.join(tmp_dir, "processed.png")
            save_preprocessed(image_path, processed_path)
            ocr_lines = run_ocr(processed_path)
    else:
        ocr_lines = run_ocr(image_path)

    items = extract_items(ocr_lines, confidence_threshold=confidence_threshold)

    return {
        "items": items,
        "item_count": len(items),
        "source_image": os.path.basename(image_path),
    }


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python main.py <bill_image_path> [--preprocess]")
        sys.exit(1)

    use_prep = "--preprocess" in sys.argv
    image_arg = sys.argv[1]

    result = process_bill(image_arg, use_preprocessing=use_prep)
    print(json.dumps(result, indent=2))