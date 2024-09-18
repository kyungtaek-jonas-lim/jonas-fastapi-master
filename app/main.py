from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.base_routes import router
from app.config import current_config

app = FastAPI()

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=current_config.ORIGIN.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print(current_config)

# Include routers
app.include_router(router)
import os
database_url = os.getenv('ORIGIN')
print(database_url)

@app.get("/health_check")
def read_root():
    response = {
        "status": 200,
        "message": "healthy"
    }
    return response
