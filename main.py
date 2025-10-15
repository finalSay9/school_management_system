from fastapi import FastAPI
from users import router as users_router
from authentication import router as auth_router
from roles.hr import router as hr_router

app = FastAPI(title="School Management System")

# Include routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(hr_router)

@app.get("/")
def read_root():
    return {"message": "School Management System API"}