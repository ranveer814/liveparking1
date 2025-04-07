from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import cv2
import numpy as np
import os
from ultralytics import YOLO
import uuid
import uvicorn

app = FastAPI()

# Load YOLOv8 model (cars detection)
model = YOLO("yolov8n.pt")

# Ensure uploads folder exists
os.makedirs("uploads", exist_ok=True)

@app.post("/upload-image/")
async def detect_parking_slots(file: UploadFile = File(...)):
    # Read image bytes and decode to OpenCV format
    img_bytes = await file.read()
    img_array = np.frombuffer(img_bytes, dtype=np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    # Get image dimensions to split into 3 slots (left to right)
    height, width, _ = img.shape
    slot_width = width // 3

    # Run YOLOv8 on the image
    results = model(img)[0]

    car_boxes = []
    for box in results.boxes.data.tolist():
        x1, y1, x2, y2, conf, cls = box
        if int(cls) == 2:  # Class 2 = Car in COCO dataset
            center_x = (x1 + x2) / 2
            car_boxes.append(center_x)

    # Initialize slots
    slots = {"Slot 1": "Empty", "Slot 2": "Empty", "Slot 3": "Empty"}
    for cx in car_boxes:
        if cx < slot_width:
            slots["Slot 1"] = "Occupied"
        elif cx < 2 * slot_width:
            slots["Slot 2"] = "Occupied"
        else:
            slots["Slot 3"] = "Occupied"

    return JSONResponse(content=slots)


# Run the app when called directly
if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 10000))  # Render provides PORT as env variable
    uvicorn.run("main:app", host="0.0.0.0", port=port)
