import cv2
import numpy as np
import requests
import uuid
import os

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# ✅ CORS (required for frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ IMPORTANT FIX: create outputs folder BEFORE mounting
os.makedirs("outputs", exist_ok=True)

# ✅ Now it is safe to mount
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")

class ImageRequest(BaseModel):
    image_url: str


def order_points(pts):
    rect = np.zeros((4, 2), dtype="float32")

    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]

    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]

    return rect


@app.post("/process")
def process_image(data: ImageRequest):
    # 1️⃣ Download image
    response = requests.get(data.image_url)
    image_bytes = np.asarray(bytearray(response.content), dtype=np.uint8)
    image = cv2.imdecode(image_bytes, cv2.IMREAD_COLOR)

    orig = image.copy()

    # 2️⃣ Preprocess
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blur, 75, 200)

    # 3️⃣ Find contours
    contours, _ = cv2.findContours(
        edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE
    )
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    doc_cnt = None
    for c in contours:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        if len(approx) == 4:
            doc_cnt = approx
            break

    if doc_cnt is None:
        return {"error": "Document not detected"}

    # 4️⃣ Perspective transform
    rect = order_points(doc_cnt.reshape(4, 2))
    (tl, tr, br, bl) = rect

    widthA = np.linalg.norm(br - bl)
    widthB = np.linalg.norm(tr - tl)
    maxWidth = int(max(widthA, widthB))

    heightA = np.linalg.norm(tr - br)
    heightB = np.linalg.norm(tl - bl)
    maxHeight = int(max(heightA, heightB))

    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]
    ], dtype="float32")

    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(orig, M, (maxWidth, maxHeight))

    # 5️⃣ Save output
    filename = f"outputs/scan_{uuid.uuid4().hex}.png"
    cv2.imwrite(filename, warped)

    return {
        "message": "Document scanned successfully",
        # ⚠️ Localhost is fine for now; we’ll change after deploy
        "output_url": f"https://doc-scanner-backend-ku8a.onrender.com/{filename}"

    }
