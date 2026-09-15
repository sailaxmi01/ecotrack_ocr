# EcoTrack AI

EcoTrack AI is a project that helps estimate the carbon footprint of everyday purchases. The idea is to take a bill or receipt, identify the products in it, and use that information for further carbon-footprint calculation.

## OCR & Bill Processing

This repository contains the OCR part of the project.

The module takes a photo of a bill/receipt and extracts the product details from it. The extracted information is then structured so that it can be used by the other parts of EcoTrack AI.

For example, a bill like:

    Milk 2L x2    120.00

can be converted into:

    {
        "name": "Milk",
        "quantity": "x2",
        "price": 120.0,
        "confidence": 0.92
    }

## How it works

The basic flow is:

    Bill Image
        ↓
    Image Preprocessing
        ↓
    OCR
        ↓
    Text Extraction
        ↓
    Product Details

The product details can then be passed to the next stage of the project for carbon-footprint calculation.

## Files

- `preprocess.py` - prepares the bill image before OCR
- `ocr_engine.py` - runs PaddleOCR and gets the text from the image
- `extractor.py` - extracts product name, quantity and price from the OCR text
- `main.py` - combines the different steps and processes a bill
- `api.py` - provides an API for sending bill images to the module
- `requirements.txt` - contains the required Python packages
- `sample_bill.jpeg` - sample image used for testing

## Setup

Clone the repository and open the project folder.

Install the required packages:

    pip install -r requirements.txt

PaddleOCR may download its model files the first time it is run, so an internet connection is required during the initial setup.

## Running the OCR

The module can be used directly from Python:

    from main import process_bill

    result = process_bill("sample_bill.jpeg")
    print(result)

The output contains the extracted items along with their quantity, price and OCR confidence.

## Running the API

To run the API locally:

    uvicorn api:app --reload --port 8001

Once the server starts, bill images can be sent to:

    POST /process-bill

The image should be sent using the form field `file`.

## Output

Each detected item can contain:

- `name` - product name found on the bill
- `quantity` - quantity as read from the bill
- `price` - price of the item
- `confidence` - OCR confidence score
- `raw_text` - original line detected by OCR

Example:

    {
        "items": [
            {
                "name": "Milk",
                "quantity": "x2",
                "price": 120.0,
                "confidence": 0.92
            }
        ],
        "item_count": 1,
        "source_image": "sample_bill.jpeg"
    }

## Testing

The OCR module is being tested with different types of bills and images, including:

- bills from different stores
- blurry images
- low-light images
- different product and quantity formats
- folded or slightly damaged receipts

Testing with more real bills will help improve the extraction accuracy.

## Part of EcoTrack AI

This OCR module is the first step in the overall EcoTrack AI pipeline. Its job is to convert the information on a physical bill into structured data that can be used by the other modules of the project.

More features and improvements will be added as the project develops.