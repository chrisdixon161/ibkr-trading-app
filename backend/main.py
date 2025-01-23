from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    return {"message": "Welcome to the API- CORS configured correctly"}

@app.post("/api/login", response_model=Token)
async def login(data: LoginRequest):
    try:
        print(f"Received login request with email: {data.email}")

        # Authenticate with Supabase
        auth_response = supabase.auth.sign_in_with_password({
            "email": data.email,
            "password": data.password
        })

        # Log the response structure for debugging
        print(f"Supabase Auth Response: {auth_response}")

        # Check if there is no user in the response
        if not auth_response.user:
            print("Authentication failed: No user returned")
            raise HTTPException(status_code=401, detail="Invalid credentials or user not found")

        # Extract the user and access token from the response
        user = auth_response.user
        access_token = auth_response.session.access_token

        if not user:
            print("No user found in the response")
            raise HTTPException(status_code=401, detail="Invalid user")

        # Generate a JWT token for the user
        generated_token = create_access_token(data={"sub": user.id}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        print(f"Generated JWT: {generated_token}")

        return {"access_token": generated_token, "token_type": "bearer"}

    except Exception as e:
        print(f"An error occurred during login: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")





@app.get("/api/account")
async def get_account(authorization: str = Header(None)):
    token = authorization.split(" ")[1] if authorization else None
    user_id = verify_token(token)

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    # Example: fetch account data (replace with real data fetching logic)
    return {"user_id": user_id, "account_balance": 1000.0}


