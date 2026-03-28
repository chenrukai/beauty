from base64 import b64decode
import math
import re
import zlib

import cv2
import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel
from rapidocr_onnxruntime import RapidOCR


app = FastAPI(title="Beauty OCR Service")
ocr_engine = RapidOCR()


class OcrRequest(BaseModel):
    imageBase64: str


class EmbedRequest(BaseModel):
    texts: list[str]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ocr")
def ocr(req: OcrRequest):
    try:
        image_bytes = b64decode(req.imageBase64)
    except Exception:
        return {"text": ""}

    try:
        return {"text": _ocr_best_text(image_bytes)}
    except Exception:
        return {"text": ""}


def _extract_text(result) -> str:
    if not result:
        return ""
    return "\n".join([line[1] for line in result if len(line) >= 2 and line[1]]).strip()


def _ocr_once(image_input) -> str:
    result, _ = ocr_engine(image_input)
    return _extract_text(result)


def _ocr_best_text(image_bytes: bytes) -> str:
    candidates: list[str] = []

    try:
        raw_text = _ocr_once(image_bytes)
        if raw_text:
            candidates.append(raw_text)
    except Exception:
        pass

    arr = np.frombuffer(image_bytes, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        return max(candidates, key=len) if candidates else ""

    h, w = img.shape[:2]
    variants = [
        img,
        cv2.resize(img, (max(1, w * 2), max(1, h * 2)), interpolation=cv2.INTER_CUBIC)
    ]

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(gray)
    variants.append(clahe)

    th = cv2.adaptiveThreshold(
        clahe, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 35, 11
    )
    variants.append(th)

    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]], dtype=np.float32)
    sharp = cv2.filter2D(img, -1, kernel)
    variants.append(sharp)

    for v in variants:
        try:
            t = _ocr_once(v)
            if t:
                candidates.append(t)
        except Exception:
            continue

    return max(candidates, key=len) if candidates else ""


def _mock_vector(text: str, dim: int = 384) -> list[float]:
    safe = (text or "").lower()
    tokens = re.split(r"\s+|[，。！？；,.!?;:\-_/()\[\]{}\"'‘’“”]+", safe)
    vec = [0.0] * dim
    for token in tokens:
        if not token:
            continue
        v = zlib.crc32(token.encode("utf-8")) & 0xFFFFFFFF
        i1 = v % dim
        i2 = (v // 97) % dim
        vec[i1] += 1.0
        vec[i2] += 0.5

    norm = math.sqrt(sum(x * x for x in vec))
    if norm > 0:
        vec = [x / norm for x in vec]
    return vec


@app.post("/embed")
def embed(req: EmbedRequest):
    texts = req.texts or []
    return {"vectors": [_mock_vector(t) for t in texts]}
