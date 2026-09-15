"""
preprocess.py
Cleans up a raw bill/receipt photo before OCR:
grayscale -> denoise -> adaptive threshold -> deskew
"""

import cv2
import numpy as np


def preprocess_image(image_path: str) -> np.ndarray:
    """Takes a path to a raw bill image, returns a cleaned-up image array."""
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Could not read image at {image_path}")

    # 1. Grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 2. Denoise (phone photos are noisy, especially in low light)
    denoised = cv2.fastNlMeansDenoising(gray, h=30)

    # 3. Adaptive threshold — handles uneven lighting across a receipt better
    #    than a single global threshold would.
    thresh = cv2.adaptiveThreshold(
        denoised, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11, 2
    )

    # 4. Deskew — phone photos are rarely perfectly straight
    coords = np.column_stack(np.where(thresh > 0))
    if len(coords) == 0:
        return thresh  # blank image, nothing to deskew

    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    (h, w) = thresh.shape
    center = (w // 2, h // 2)
    rot_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    deskewed = cv2.warpAffine(
        thresh, rot_matrix, (w, h),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REPLICATE
    )

    return deskewed


def save_preprocessed(image_path: str, output_path: str) -> str:
    """Runs preprocessing and writes the result to disk. Returns output path."""
    processed = preprocess_image(image_path)
    cv2.imwrite(output_path, processed)
    return output_path


if __name__ == "__main__":
    # Quick manual test: python preprocess.py sample_bill.jpg
    import sys
    if len(sys.argv) < 2:
        print("Usage: python preprocess.py <image_path>")
        sys.exit(1)
    out = save_preprocessed(sys.argv[1], "processed_output.png")
    print(f"Saved preprocessed image to {out}")
