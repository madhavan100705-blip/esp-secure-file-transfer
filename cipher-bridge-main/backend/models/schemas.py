from pydantic import BaseModel

class HealthResponse(BaseModel):
    status: str
    mode: str
    disclaimer: str

class ResetResponse(BaseModel):
    success: bool
    stats: dict
