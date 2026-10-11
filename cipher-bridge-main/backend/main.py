from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from backend.models.schemas import HealthResponse, ResetResponse
from backend.services.transfer_service import reset, run_transfer, status

app = FastAPI(title="CipherBridge ESP Secure Transfer API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8080", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="online", mode="python_backend", disclaimer="Educational ESP/IPsec Simulation")

@app.get("/api/status")
def get_status() -> dict:
    return status()

async def read_upload(file: UploadFile) -> tuple[str, bytes]:
    data = await file.read()
    if not file.filename:
        raise HTTPException(status_code=400, detail="A filename is required.")
    if not data:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")
    if len(data) > 25 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Files must be smaller than 25 MB.")
    return file.filename, data

@app.post("/api/encrypt")
async def encrypt(file: UploadFile = File(...)) -> dict:
    filename, data = await read_upload(file)
    result = run_transfer(filename, data, attack=False)
    result["stage"] = "encrypted"
    return result

@app.post("/api/transmit")
async def transmit(file: UploadFile = File(...)) -> dict:
    filename, data = await read_upload(file)
    return run_transfer(filename, data, attack=False)

@app.post("/api/receive")
async def receive(file: UploadFile = File(...)) -> dict:
    filename, data = await read_upload(file)
    return run_transfer(filename, data, attack=False)

@app.post("/api/attack")
async def attack(file: UploadFile = File(...)) -> dict:
    filename, data = await read_upload(file)
    return run_transfer(filename, data, attack=True)

@app.post("/api/demo")
async def demo(file: UploadFile = File(...), attack_mode: bool = False) -> dict:
    filename, data = await read_upload(file)
    return run_transfer(filename, data, attack=attack_mode)

@app.post("/api/reset", response_model=ResetResponse)
def reset_state() -> ResetResponse:
    return ResetResponse(success=True, stats=reset())
