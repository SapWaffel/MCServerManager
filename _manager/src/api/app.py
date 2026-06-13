from fastapi import FastAPI
from src.api.routes.server import router as server_router
from src.api.routes.health import router as health_router
from src.api.routes.port import router as port_router

def create_app():
    app = FastAPI(title="CL4P-TP VM-100: Minecraft Server Manager API")
    app.include_router(server_router)
    app.include_router(health_router)
    app.include_router(port_router)
    return app