from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory slot data store
slot_status = {
    "Slot 1": "Empty",
    "Slot 2": "Empty",
    "Slot 3": "Empty"
}

@app.post("/receive")
async def receive_data(data: dict):
    global slot_status
    # Validate and update slots
    for key in slot_status:
        if key in data:
            slot_status[key] = data[key]
    return {"message": "Data received"}

@app.get("/slots")
async def get_slots():
    return JSONResponse(content=slot_status)

@app.get("/", response_class=HTMLResponse)
async def index():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Parking Slot Status</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                display: flex;
                flex-direction: column;
                align-items: center;
                padding: 20px;
                background: #f0f0f0;
            }
            h1 {
                margin-bottom: 20px;
            }
            .slots {
                display: flex;
                gap: 20px;
            }
            .slot {
                width: 120px;
                height: 120px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: bold;
                color: white;
                font-size: 18px;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            .occupied {
                background-color: red;
            }
            .empty {
                background-color: green;
            }
        </style>
    </head>
    <body>
        <h1>Live Parking Slots</h1>
        <div class="slots">
            <div id="slot1" class="slot">Slot 1</div>
            <div id="slot2" class="slot">Slot 2</div>
            <div id="slot3" class="slot">Slot 3</div>
        </div>

        <script>
            function updateSlots() {
                fetch("/slots")
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById("slot1").className = "slot " + (data["Slot 1"] === "Occupied" ? "occupied" : "empty");
                        document.getElementById("slot2").className = "slot " + (data["Slot 2"] === "Occupied" ? "occupied" : "empty");
                        document.getElementById("slot3").className = "slot " + (data["Slot 3"] === "Occupied" ? "occupied" : "empty");
                    });
            }

            updateSlots();
            setInterval(updateSlots, 3000);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=10000)
