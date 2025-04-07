from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from ultralytics import YOLO
import numpy as np
import cv2

app = FastAPI()

# Allow CORS for frontend to communicate
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

model = YOLO("yolov8n.pt")

@app.post("/detect")
async def detect_car(file: UploadFile = File(...)):
    contents = await file.read()
    npimg = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    height, width, _ = img.shape
    slot_width = width // 3

    results = model(img)[0]
    car_boxes = []
    for box in results.boxes.data.tolist():
        x1, y1, x2, y2, conf, cls = box
        if int(cls) == 2:  # Class ID for 'car' in COCO
            center_x = (x1 + x2) / 2
            car_boxes.append(center_x)

    # Slot detection
    slots = {"Slot 1": "Empty", "Slot 2": "Empty", "Slot 3": "Empty"}
    for cx in car_boxes:
        if cx < slot_width:
            slots["Slot 1"] = "Occupied"
        elif cx < 2 * slot_width:
            slots["Slot 2"] = "Occupied"
        else:
            slots["Slot 3"] = "Occupied"

    return JSONResponse(content=slots)

# For local dev
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
