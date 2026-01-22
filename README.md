Doc Scanner App – Backend

This repository contains the backend of the Doc Scanner App.
The backend is responsible for processing document images, detecting the document boundaries, applying perspective correction, and returning a scanned document image to the frontend.

It is built using FastAPI and OpenCV and is deployed on Render.

🧠 Why This Backend Exists

In a real-world document scanning app:

The frontend should stay lightweight

Heavy image processing should happen on a server

The backend should expose clean APIs

This backend:

Receives an image URL

Downloads the image

Detects the document edges

Applies perspective transform (scanner effect)

Saves and serves the scanned image

🛠️ Tech Stack Used (and Why)
1️⃣ FastAPI (Backend Framework)

Modern and fast Python web framework

Easy to define APIs

Automatic request validation using Pydantic

Very beginner-friendly

2️⃣ OpenCV

Used for image processing

Detects document edges

Applies perspective correction

Industry standard for computer vision

3️⃣ NumPy

Handles image arrays

Required by OpenCV for mathematical operations

4️⃣ Requests

Downloads the image from a public URL (Cloudinary)

Allows backend to work with remote images

5️⃣ Uvicorn

ASGI server used to run FastAPI

Lightweight and fast


🔗 API Overview
Base URL (Deployed)
https://doc-scanner-backend-ku8a.onrender.com

📌 POST /process

This endpoint:

Receives an image URL

Processes the image

Returns a scanned image URL

Request Body (JSON)
{
  "image_url": "https://res.cloudinary.com/..."
}

Response (Success)
{
  "message": "Document scanned successfully",
  "output_url": "https://doc-scanner-backend-ku8a.onrender.com/outputs/scan_xxx.png"
}

🔄 Backend Workflow (Step by Step)
1️⃣ Receive Image URL

Frontend sends a public image URL

Backend does NOT receive raw image files

This keeps the API lightweight

2️⃣ Download the Image

Uses requests to fetch the image

Converts raw bytes into an OpenCV-readable format

3️⃣ Preprocess the Image

Steps applied:

Convert image to grayscale

Apply Gaussian blur

Detect edges using Canny edge detection

Purpose:

Make document edges easier to detect

4️⃣ Detect Document Contours

Finds all contours in the image

Sorts them by area

Selects the largest 4-point contour

This assumes:

The document is the largest rectangular object

5️⃣ Perspective Transformation (Scanner Effect)

Orders the four detected corner points

Calculates width and height

Applies perspective transform

Result:

Cropped, straightened document

Looks like a scanned page

6️⃣ Save the Scanned Image

Image is saved inside the outputs/ folder

Unique filename generated using UUID

Image is served as a static file

7️⃣ Return Output URL

Backend returns the public URL

Frontend displays the scanned document

🗂️ Static File Serving

The backend uses FastAPI’s static file support:

app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")


This allows scanned images to be accessed via:

/outputs/scan_xxx.png

🔐 CORS Configuration

To allow frontend-backend communication:

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


This ensures:

Frontend hosted on Vercel can call backend on Render

No browser CORS errors

▶️ Running Backend Locally
1️⃣ Create virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

2️⃣ Install dependencies
pip install -r requirements.txt

3️⃣ Create outputs folder
mkdir outputs

4️⃣ Run server
uvicorn main:app --reload


Backend runs at:

http://127.0.0.1:8000

🚀 Deployment on Render
Why Render?

Free tier available

Simple Python deployment

Automatic GitHub integration

Deployment Steps:

Push backend code to GitHub

Create a new Web Service on Render

Set:

Build command:

pip install -r requirements.txt


Start command:

bash start.sh


Ensure outputs/ folder exists at runtime

⚠️ Known Limitations (Expected for Assignment)

No OCR (text extraction)

Works best with clear document images

Assumes document is largest object in image

These are acceptable trade-offs for an intern-level assignment.

✅ Key Features Implemented

REST API using FastAPI

Document edge detection

Perspective correction

Static image serving

Cloud-compatible deployment

Clean and readable code

📌 Final Notes

This backend is:

Easy to understand for beginners

Structured for real-world use

Ready for future enhancements like OCR, PDF export, or authentication