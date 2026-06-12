import uvicorn
from src.api.app import create_app as run_api

if __name__ == "__main__":
    app = run_api()
    uvicorn.run(app, host="0.0.0.0", port=8183)