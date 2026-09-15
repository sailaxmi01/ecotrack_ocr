# EcoTrack AI — OCR & Bill Processing Module 

Turns a photo of a bill/receipt into structured item data:
`[{"name": "Milk", "quantity": "2L x2", "price": 120.0, "confidence": 0.92}, ...]`

## Setup

```bash
pip install -r requirements.txt --break-system-packages
```

First run will download PaddleOCR model weights (needs internet, ~a few hundred MB).

## Files

| File | Purpose |
|---|---|
| `preprocess.py` | Cleans raw bill photos (grayscale, denoise, threshold, deskew) |
| `ocr_engine.py` | Wraps PaddleOCR — loads model once, returns text + confidence per line |
| `extractor.py` | Parses raw OCR text into structured name/quantity/price |
| `main.py` | Ties the above into one function: `process_bill(image_path)` |
| `api.py` | FastAPI HTTP wrapper so other modules can call this over the network |

## Usage — as a Python function (for teammates importing directly)

```python
from main import process_bill

result = process_bill("path/to/bill.jpg")
print(result)
# {"items": [...], "item_count": 5, "source_image": "bill.jpg"}
```

## Usage — as an API (for the frontend / other services)

```bash
uvicorn api:app --reload --port 8001
```

Then POST an image file to `http://localhost:8001/process-bill` (multipart/form-data, field name `file`).

Response:
```json
{
  "items": [
    {"raw_text": "Milk 2L x2 120.00", "name": "Milk", "quantity": "x2", "price": 120.0, "confidence": 0.92}
  ],
  "item_count": 1,
  "source_image": "bill.jpg"
}
```

## Output contract (share this with Member 2 — AI Product Understanding)

Each item has:
- `name` (string, raw extracted product name — may need further cleaning downstream)
- `quantity` (string, not yet normalized to a strict unit)
- `price` (float or null)
- `confidence` (float 0-1, from OCR)
- `raw_text` (original OCR line, for debugging)

## Known limitations (be upfront about these with the team)

- `extractor.py`'s regex parsing is a first pass — real receipts vary wildly in layout and **will** break it. Expect to keep tuning this against real test bills.
- Low-confidence OCR lines (below 0.6 threshold) are silently skipped, not shown to the user yet. Decide with Member 5 whether to expose a "some items couldn't be read" message.
- Quantity strings aren't normalized (e.g. "2L", "x2", "1kg" are all different formats) — Member 4 (Carbon Calculation) will need to handle or request normalization.
- No retry/fallback if PaddleOCR fails entirely on a bad image.

## Testing checklist (Weeks 3-4)

- [ ] Test on receipts from at least 3 different stores/formats
- [ ] Test on blurry / low-light photos
- [ ] Test on a folded/creased receipt
- [ ] Confirm output JSON matches what Member 2 expects
- [ ] Time how long `process_bill()` takes per image (flag if too slow for demo)
