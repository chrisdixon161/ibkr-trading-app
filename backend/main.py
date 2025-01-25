from fastapi import FastAPI, HTTPException, Depends, Header, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from jose import JWTError, jwt
from datetime import datetime, timedelta
from supabase import create_client
from ib_insync import IB, Option, MarketOrder, LimitOrder
import nest_asyncio
import os
from dotenv import load_dotenv

# Apply nest_asyncio
nest_asyncio.apply()

# Load environment variables
load_dotenv()

# Supabase client setup
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
IBKR_HOST = os.getenv("IBKR_HOST", "127.0.0.1")
IBKR_PORT = int(os.getenv("IBKR_PORT", 7497))  # Default port for TWS/Gateway
IBKR_CLIENT_ID = int(os.getenv("IBKR_CLIENT_ID", 1))

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Interactive Brokers client
ib = IB()

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


class OptionTradeRequest(BaseModel):
    symbol: str
    expiry: str
    strike: float
    right: str  # "C" for call, "P" for put
    quantity: int
    action: str  # "BUY" or "SELL"
    order_type: str  # "MKT" or "LMT"
    limit_price: float | None = None  # Required only for limit orders


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
        return payload
    except JWTError:
        return None


# FastAPI Lifecycle Events
@app.on_event("startup")
async def startup_event():
    try:
        print("Starting up and connecting to IBKR API...")
        ib.connect(IBKR_HOST, IBKR_PORT, clientId=IBKR_CLIENT_ID)
        print("Connected to IBKR API during startup")
    except Exception as e:
        print(f"Error during IBKR connection on startup: {e}")
        raise ConnectionError("Could not connect to Interactive Brokers")


@app.on_event("shutdown")
async def shutdown_event():
    try:
        print("Shutting down IBKR connection...")
        ib.disconnect()
        print("Disconnected from IBKR API")
    except Exception as e:
        print(f"Error during IBKR disconnection: {e}")


# Routes
@app.get("/")
async def root():
    return {"message": "Welcome to the API - CORS configured correctly"}


@app.post("/api/login", response_model=Token)
async def login(data: LoginRequest):
    try:
        print(f"Received login request with email: {data.email}")

        # Authenticate with Supabase
        auth_response = supabase.auth.sign_in_with_password({
            "email": data.email,
            "password": data.password
        })

        print(f"Supabase Auth Response: {auth_response}")

        if not auth_response.user:
            print("Authentication failed: No user returned")
            raise HTTPException(status_code=401, detail="Invalid credentials or user not found")

        # Extract user details
        user = auth_response.user

        # Generate a JWT token with both user ID and email
        generated_token = create_access_token(
            data={"sub": user.id, "email": user.email},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        print(f"Generated JWT: {generated_token}")
        return {"access_token": generated_token, "token_type": "bearer"}

    except Exception as e:
        print(f"An error occurred during login: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/api/verify-access")
async def verify_access(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")

    token = authorization.split(" ")[1]
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = payload.get("sub")
    email = payload.get("email")
    if not user_id or not email:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    # Query the profiles table
    profile_response = supabase.table("profiles").select("id, plan").eq("id", user_id).single().execute()
    plan = profile_response.data.get("plan")

    if not profile_response.data or not plan or plan.upper() == "NULL":
        raise HTTPException(status_code=403, detail="Access denied: No valid plan found")

    return {"message": "Access granted", "user_id": user_id, "email": email}


@app.get("/api/ibkr/account-data")
async def get_ibkr_account_data():
    try:
        print("Fetching account data...")

        # Get account summary
        account_data = ib.accountSummary()

        # Convert the list of AccountSummary objects to a list of dictionaries
        account_data_dict = [summary._asdict() for summary in account_data]

        return {"account_data": account_data_dict}

    except Exception as e:
        print(f"Error retrieving IBKR account data: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve account data")
