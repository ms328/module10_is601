# main.py
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import logging

# Local imports
from app.operations import add, subtract, multiply, divide
from app.database import get_db
from app.models.user import User
from app.schemas.base import UserCreate

app = FastAPI(title="FastAPI Calculator & Secure User API")

# Allow all origins for dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ------------------- Calculator Routes -------------------
@app.get("/")
def root(request: Request):
    """Render the homepage template with the calculator UI."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/add")
def add_route(data: dict):
    try:
        a, b = data["a"], data["b"]
        return {"result": add(a, b)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/subtract")
def subtract_route(data: dict):
    try:
        a, b = data["a"], data["b"]
        return {"result": subtract(a, b)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/multiply")
def multiply_route(data: dict):
    try:
        a, b = data["a"], data["b"]
        return {"result": multiply(a, b)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/divide")
def divide_route(data: dict):
    try:
        a, b = data["a"], data["b"]
        return {"result": divide(a, b)}
    except ValueError as e:
        # Expected by tests — sends {"error": "..."}
        return JSONResponse(status_code=400, content={"error": str(e)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Internal Server Error"})


# ------------------- User Registration -------------------
@app.post("/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user securely.
    """
    try:
        new_user = User.register(db, user.model_dump())
        db.commit()
        return {
            "message": "User registered successfully",
            "username": user.username,
            "email": user.email
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    # Run with: python main.py (used by tests' subprocess)
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
