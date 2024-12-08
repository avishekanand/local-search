import sys
print("PYTHONPATH:", sys.path)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.routes import search

app = FastAPI()

# Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(search.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Local Search API"}
