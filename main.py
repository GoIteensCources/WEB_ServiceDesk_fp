import uvicorn
from fastapi import  FastAPI
from routes import auth, users

app = FastAPI()

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])


if __name__ == "__main__":
    uvicorn.run(f"{__name__}:app", port=8000, reload=True)
