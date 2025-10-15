from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from users import router as users_router
from authentication import router as auth_router
from roles.hr import router as hr_router
from roles.headteacher import router as headteacher_router

app = FastAPI(
    title="School Management System",
    description="Comprehensive school management API",
    version="1.0.0"
)

# CORS middleware (adjust origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(hr_router)
app.include_router(headteacher_router)

@app.get("/")
def read_root():
    return {
        "message": "School Management System API",
        "version": "1.0.0",
        "docs": "/docs"
    }