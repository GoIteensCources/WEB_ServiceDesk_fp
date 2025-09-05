import uvicorn
from fastapi import FastAPI
from routes import auth, users, frontend, admin_panel

app = FastAPI()

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(admin_panel.router, prefix="/users", tags=["admin"])
app.include_router(frontend.router, prefix="", tags=["frontend"])

if __name__ == "__main__":
    uvicorn.run(f"{__name__}:app", port=8000, reload=True)
