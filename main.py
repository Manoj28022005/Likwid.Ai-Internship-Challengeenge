from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routes.customers import router as customer_router
from routes.auth import router as auth_router
from routes.sheets import router as sheets_router
from database import engine
from models import Base

# Initialize database
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Likwid.Ai ERP - Customer Management Module")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# Mount static files for frontend
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(customer_router)
app.include_router(auth_router)
app.include_router(sheets_router)

@app.get("/")
async def root():
    return {"message": "Welcome to Likwid.Ai ERP Customer Management Module"} 