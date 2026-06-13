# Routes for /port
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.util.manager.port import Port

router = APIRouter(prefix="/port", tags=["ports"])

@router.post("/release")
def release_port(port: int):
    try:
        Port.release(port)
        return {"success": True, "message": f"Port {port} released successfully."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))