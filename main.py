from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import cv2
import numpy as np
from ultralytics import YOLO
import os

app = FastAPI()

# Load the YOLOv8 model
model = YOLO("yolov8n.pt")  # You can use yolov8s.pt for better accuracy

# Ensure uploads directory exists (optional)
os.makedirs("uploads", exist_ok=True)

@app.get("/")
def read_root():
    return {"message": "YOLOv8 Parking Slot Detection API is live!"}

@app.post("/upload-image/")
async def detect_parking_slots(file: UploadFile = File(...)):
    # Read the uploaded image
    img_bytes = await file.read()
    img_array = np.frombuffer(img_bytes, dtype=np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    if img is None:
        return JSONResponse(content={"error": "Invalid image"}, status_code=400)

    height, width, _ = img.shape
    slot_width = width // 3  # divide image into 3 vertical parts

    # Run YOLOv8 object detection
    results = model(img)[0]

    car_boxes = []
    for box in results.boxes.data.tolist():
        x1, y1, x2, y2, conf, cls = box
        if int(cls) == 2:  # Class 2 = Car
            center_x = (x1 + x2) / 2
            car_boxes.append(center_x)

    # Determine which slots are occupied
    slots = {"Slot 1": "Empty", "Slot 2": "Empty", "Slot 3": "Empty"}
    for cx in car_boxes:
        if cx < slot_width:
            slots["Slot 1"] = "Occupied"
        elif cx < 2 * slot_width:
            slots["Slot 2"] = "Occupied"
        else:
            slots["Slot 3"] = "Occupied"

    return JSONResponse(content=slots)

# Entry point for Render or local use
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=10000)
