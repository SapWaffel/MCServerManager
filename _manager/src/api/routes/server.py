# Routes for /server
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.backend.scripts.create import main as create_server_script
from src.backend.scripts.start import main as start_server_script

router = APIRouter(prefix="/server", tags=["servers"])

class CreateServerRequest(BaseModel):
    server_name: str
    owner_username: str
    server_version: str | None = None
    ovr_metadata: dict | None = None
    ovr_resources: dict | None = None
    ovr_properties: dict | None = None
    ovr_runtime: dict | None = None

class StartServerRequest(BaseModel):
    uuid: str
    port: int | None = None

@router.post("/create")
def create_server_endpoint(payload: CreateServerRequest):
    result = create_server_script(
        server_name=payload.server_name,
        owner_username=payload.owner_username,
        server_version=payload.server_version,
        ovr_metadata=payload.ovr_metadata,
        ovr_resources=payload.ovr_resources,
        ovr_properties=payload.ovr_properties,
        ovr_runtime=payload.ovr_runtime
    )
    if not result.get("success", False):
        raise HTTPException(status_code=400, detail=result.get("error", "Unknown error"))
    return result

@router.post("/start")
def start_server_endpoint(payload: StartServerRequest):
    result = start_server_script(uuid=payload.uuid, port=payload.port)
    if not result.get("success", False):
        raise HTTPException(status_code=400, detail=result.get("error", "Unknown error"))
    return result