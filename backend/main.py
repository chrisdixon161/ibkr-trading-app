from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
from jose import JWTError, jwt
from datetime import datetime, timedelta
from supabase import create_client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase client setup
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI()


# Pydantic models
class LoginRequest(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


# Helper functions
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None


# Routes
@app.get("/")
async def root():
    return {"message": "Welcome to the API"}

@app.post("/api/login", response_model=Token)
async def login(data: LoginRequest):
    # Authenticate with Supabase
    auth_response = supabase.auth.sign_in_with_password({
        "email": data.email,
        "password": data.password
    })

    if "error" in auth_response:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user = auth_response.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user")

    # Generate a JWT
    access_token = create_access_token(data={"sub": user["id"]}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/api/account")
async def get_account(authorization: str = Header(None)):
    token = authorization.split(" ")[1] if authorization else None
    user_id = verify_token(token)

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    # Example: fetch account data (replace with real data fetching logic)
    return {"user_id": user_id, "account_balance": 1000.0}
