"""
ocr_engine.py
Thin wrapper around PaddleOCR. Loads the model once (slow) and reuses it
for every call (fast).
"""

from paddleocr import PaddleOCR

# Loaded once at import time — do NOT re-instantiate this per request,
# model loading is the slow part.
# NOTE: PaddleOCR 3.x replaced use_angle_cls/cls=True with this newer API.
_ocr_model = PaddleOCR(
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=True,
    lang='en',
    enable_mkldnn=False  # works around a CPU compatibility bug on some Windows machines
)


def run_ocr(image_path: str) -> list[dict]:
    """
    Runs OCR on an image and returns a list of detected lines:
    [{"text": ..., "confidence": ..., "bbox": [[x,y], ...]}, ...]
    """
    results = _ocr_model.predict(image_path)

    lines = []
    if not results:
        return lines

    # PaddleOCR 3.x returns a list of result objects (one per image),
    # each exposing rec_texts / rec_scores / rec_polys as parallel lists.
    for res in results:
        texts = res.get("rec_texts", []) if hasattr(res, "get") else res["rec_texts"]
        scores = res.get("rec_scores", []) if hasattr(res, "get") else res["rec_scores"]
        polys = res.get("rec_polys", []) if hasattr(res, "get") else res["rec_polys"]

        for text, score, poly in zip(texts, scores, polys):
            bbox = poly.tolist() if hasattr(poly, "tolist") else poly
            lines.append({
                "text": text,
                "confidence": float(score),
                "bbox": bbox
            })

    return lines


if __name__ == "__main__":
    import sys, json
    if len(sys.argv) < 2:
        print("Usage: python ocr_engine.py <image_path>")
        sys.exit(1)
    lines = run_ocr(sys.argv[1])
    print(json.dumps(lines, indent=2))