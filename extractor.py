"""
extractor.py (v2)
Real receipts often split item name and price into separate OCR text
blocks that only line up by vertical (row) position -- not by being on
the same literal text line. This version groups OCR results into rows
using bounding-box y-coordinates, then reads left-to-right within each
row to reconstruct quantity, name, and price.
"""

import re

_PRICE_ONLY = re.compile(r'^\d+\.\d{2}$')
_LEADING_QTY = re.compile(r'^(\d+)\s+(.*)')

_SKIP_NAMES = {"total", "cash", "change", "subtotal", "tax"}


def _bbox_center(bbox):
    xs = [p[0] for p in bbox]
    ys = [p[1] for p in bbox]
    return sum(xs) / len(xs), sum(ys) / len(ys)


def _group_into_rows(lines, y_tolerance=10):
    entries = []
    for line in lines:
        x, y = _bbox_center(line["bbox"])
        entries.append({**line, "x": x, "y": y})

    entries.sort(key=lambda e: e["y"])

    rows = []
    current_row = []
    current_y = None

    for e in entries:
        if current_y is None or abs(e["y"] - current_y) <= y_tolerance:
            current_row.append(e)
            current_y = e["y"] if current_y is None else (current_y + e["y"]) / 2
        else:
            rows.append(current_row)
            current_row = [e]
            current_y = e["y"]

    if current_row:
        rows.append(current_row)

    return rows


def extract_items(ocr_lines: list, confidence_threshold: float = 0.6) -> list:
    filtered = [l for l in ocr_lines if l["confidence"] >= confidence_threshold]
    rows = _group_into_rows(filtered)

    items = []
    for row in rows:
        row_sorted = sorted(row, key=lambda e: e["x"])

        price = None
        name_parts = []
        confidences = []

        for entry in row_sorted:
            text = entry["text"].strip()
            confidences.append(entry["confidence"])
            if _PRICE_ONLY.match(text):
                price = float(text)
            else:
                name_parts.append(text)

        name = " ".join(name_parts).strip()

        quantity = "1"
        qty_match = _LEADING_QTY.match(name)
        if qty_match:
            quantity, name = qty_match.group(1), qty_match.group(2)

        if not name or name.lower() in _SKIP_NAMES or price is None:
            continue

        items.append({
            "raw_text": " | ".join(e["text"] for e in row_sorted),
            "name": name,
            "quantity": quantity,
            "price": price,
            "confidence": min(confidences),
        })

    return items


if __name__ == "__main__":
    sample_lines = [
        {"text": "2 APPLE", "confidence": 0.99, "bbox": [[224, 210], [306, 210], [306, 234], [224, 234]]},
        {"text": "1.00", "confidence": 0.99, "bbox": [[473, 210], [517, 210], [517, 233], [473, 233]]},
    ]
    import json
    print(json.dumps(extract_items(sample_lines), indent=2))