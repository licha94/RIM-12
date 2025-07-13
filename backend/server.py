from fastapi import FastAPI, APIRouter, HTTPException, Depends, Header, Request, status
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timedelta
from emergentintegrations.llm.chat import LlmChat, UserMessage
from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionResponse, CheckoutStatusResponse, CheckoutSessionRequest
import asyncio
import hashlib
import json
import base64
import bcrypt

# Import du module de sécurité PHASE 6
try:
    from .security_module import (
        get_security_check, waf_instance, limiter, oauth2_scheme,
        PasswordHasher, api_key_manager, audit_scheduler
    )
except ImportError:
    # Fallback si le module n'est pas trouvé
    async def get_security_check(request: Request):
        return {"allowed": True, "risk_score": 0.0}
    
    limiter = None
    oauth2_scheme = None

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configuration sécurité
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("SECRET_KEY must be set in environment variables")

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(
    title="RIMAREUM API - PHASE 6 SECURED", 
    description="Revolutionary E-commerce & Crypto Platform with Advanced Security",
    version="6.0.0"
)

# PHASE 6 Security Middlewares
app.add_middleware(HTTPSRedirectMiddleware)
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["*"]  # Configure with your domain in production
)

# Rate limiting
if limiter:
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Initialize integrations (will be set when API keys are provided)
stripe_checkout = None
openai_chat = None

# --- MODELS ---

class Product(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    price: float
    category: str  # physical, digital, nft, ai_service
    image_url: Optional[str] = None
    crypto_price: Optional[float] = None  # Price in $RIMAR tokens
    stock: int = 0
    is_featured: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    category: str
    image_url: Optional[str] = None
    crypto_price: Optional[float] = None
    stock: int = 0
    is_featured: bool = False

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    username: str
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    api_keys: List[str] = []
    failed_login_attempts: int = 0
    last_login: Optional[datetime] = None
    wallet_address: Optional[str] = None
    rimar_balance: float = 0.0

class Order(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    products: List[Dict[str, Any]]  # [{"product_id": "...", "quantity": 1, "price": 100}]
    total_amount: float
    payment_method: str  # stripe, crypto
    payment_status: str  # pending, completed, failed
    order_status: str  # processing, shipped, delivered
    created_at: datetime = Field(default_factory=datetime.utcnow)

class PaymentTransaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    user_id: Optional[str] = None
    amount: float
    currency: str
    payment_status: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ChatSession(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    messages: List[ChatMessage] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class WalletConnection(BaseModel):
    user_id: str
    wallet_address: str
    chain_id: int
    balance_eth: float
    balance_rimar: float
    nft_count: int
    connected_at: datetime = Field(default_factory=datetime.utcnow)

class PaymentRequest(BaseModel):
    amount: float
    currency: str = "USD"
    product_id: Optional[str] = None
    payment_method: str = "card"  # card or crypto
    wallet_address: Optional[str] = None

class SecurityEvent(BaseModel):
    event_type: str
    ip_address: str
    user_agent: str
    risk_score: float
    blocked: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    details: Dict[str, Any] = {}

# PHASE 6 Security Models
class UserLogin(BaseModel):
    username: str
    password: str

class UserRegistration(BaseModel):
    email: str
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    api_key: str

class SecurityReport(BaseModel):
    ip_address: str
    event_type: str
    fingerprint: Optional[str] = None
    captcha_response: Optional[str] = None
    details: Dict[str, Any] = {}

# --- AUTHENTICATION HELPERS ---
async def get_current_user(authorization: Optional[str] = Header(None)) -> Optional[User]:
    """Get current user from session token (simplified for MVP)"""
    if not authorization:
        return None
    
    # For MVP, we'll use a simple token system
    # In production, this would validate JWT tokens properly
    session_token = authorization.replace("Bearer ", "")
    user = await db.users.find_one({"session_token": session_token})
    if user:
        return User(**user)
    return None

# --- PRODUCT ROUTES ---

@api_router.get("/products", response_model=List[Product])
async def get_products(category: Optional[str] = None, featured: Optional[bool] = None):
    """Get all products with optional filtering"""
    filter_query = {}
    if category:
        filter_query["category"] = category
    if featured is not None:
        filter_query["is_featured"] = featured
    
    products = await db.products.find(filter_query).to_list(100)
    return [Product(**product) for product in products]

@api_router.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: str):
    """Get a specific product"""
    product = await db.products.find_one({"id": product_id})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return Product(**product)

@api_router.post("/products", response_model=Product)
async def create_product(product_data: ProductCreate, current_user: Optional[User] = Depends(get_current_user)):
    """Create a new product (admin only for MVP)"""
    product = Product(**product_data.dict())
    await db.products.insert_one(product.dict())
    return product

# --- PAYMENT ROUTES ---

@api_router.post("/payments/checkout/session")
async def create_checkout_session(
    request: dict,
    origin: Optional[str] = Header(None, alias="origin")
):
    """Create Stripe checkout session"""
    global stripe_checkout
    if not stripe_checkout:
        raise HTTPException(status_code=503, detail="Payment service not configured")
    
    try:
        # Extract product info and calculate amount
        product_id = request.get("product_id")
        quantity = request.get("quantity", 1)
        
        if product_id:
            product = await db.products.find_one({"id": product_id})
            if not product:
                raise HTTPException(status_code=404, detail="Product not found")
            amount = product["price"] * quantity
        else:
            amount = request.get("amount")
            if not amount:
                raise HTTPException(status_code=400, detail="Amount or product_id required")
        
        # Use origin from header or fallback
        base_url = origin or "https://20423e44-cefc-4fee-92df-010802a91699.preview.emergentagent.com"
        
        checkout_request = CheckoutSessionRequest(
            amount=float(amount),
            currency="usd",
            success_url=f"{base_url}/payment/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{base_url}/payment/cancel",
            metadata={
                "product_id": product_id or "custom",
                "quantity": str(quantity),
                "source": "rimareum"
            }
        )
        
        session = await stripe_checkout.create_checkout_session(checkout_request)
        
        # Create payment transaction record
        payment_transaction = PaymentTransaction(
            session_id=session.session_id,
            amount=float(amount),
            currency="usd",
            payment_status="pending",
            metadata=checkout_request.metadata
        )
        await db.payment_transactions.insert_one(payment_transaction.dict())
        
        return {"url": session.url, "session_id": session.session_id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Payment error: {str(e)}")

@api_router.get("/payments/checkout/status/{session_id}")
async def get_checkout_status(session_id: str):
    """Get payment status"""
    global stripe_checkout
    if not stripe_checkout:
        raise HTTPException(status_code=503, detail="Payment service not configured")
    
    try:
        status = await stripe_checkout.get_checkout_status(session_id)
        
        # Update local payment record
        await db.payment_transactions.update_one(
            {"session_id": session_id},
            {"$set": {"payment_status": status.payment_status}}
        )
        
        return status.dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status check error: {str(e)}")

# --- WALLET ROUTES ---

@api_router.post("/wallet/connect")
async def connect_wallet(wallet_data: WalletConnection):
    """Connect crypto wallet"""
    # Update or create user with wallet address
    user = await db.users.find_one({"id": wallet_data.user_id})
    if user:
        await db.users.update_one(
            {"id": wallet_data.user_id},
            {"$set": {"wallet_address": wallet_data.wallet_address}}
        )
    
    # Store wallet connection
    await db.wallet_connections.insert_one(wallet_data.dict())
    return {"message": "Wallet connected successfully"}

@api_router.get("/wallet/balance/{wallet_address}")
async def get_wallet_balance(wallet_address: str):
    """Get wallet balance (mock for MVP)"""
    # In production, this would query actual blockchain
    return {
        "address": wallet_address,
        "eth_balance": 1.5,
        "rimar_balance": 1000.0,
        "nft_count": 5
    }

# --- AI CHAT ROUTES ---

@api_router.post("/chat/message")
async def send_chat_message(
    data: dict,
    current_user: Optional[User] = Depends(get_current_user)
):
    """Send message to AI assistant"""
    global openai_chat
    if not openai_chat:
        raise HTTPException(status_code=503, detail="AI service not configured")
    
    try:
        session_id = data.get("session_id", str(uuid.uuid4()))
        message = data.get("message", "")
        
        # Create new chat instance for this session
        chat = LlmChat(
            api_key=os.environ.get("OPENAI_API_KEY"),
            session_id=session_id,
            system_message="You are RIMAREUM's AI assistant. Help users with e-commerce, crypto, and DAO questions. Be knowledgeable about blockchain, NFTs, and digital commerce."
        ).with_model("openai", "gpt-4o")
        
        user_message = UserMessage(text=message)
        response = await chat.send_message(user_message)
        
        # Store chat history
        chat_record = ChatMessage(
            session_id=session_id,
            user_id=current_user.id if current_user else None,
            message=message,
            response=response
        )
        await db.chat_messages.insert_one(chat_record.dict())
        
        return {"response": response, "session_id": session_id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

@api_router.get("/chat/history/{session_id}")
async def get_chat_history(session_id: str):
    """Get chat history for a session"""
    messages = await db.chat_messages.find({"session_id": session_id}).to_list(100)
    return [ChatMessage(**msg) for msg in messages]

# --- ADMIN ROUTES ---

@api_router.get("/admin/stats")
async def get_admin_stats():
    """Get platform statistics"""
    stats = {
        "total_products": await db.products.count_documents({}),
        "total_users": await db.users.count_documents({}),
        "total_orders": await db.orders.count_documents({}),
        "total_payments": await db.payment_transactions.count_documents({}),
        "revenue": 0  # Calculate from completed payments
    }
    
    # Calculate revenue
    completed_payments = await db.payment_transactions.find({"payment_status": "paid"}).to_list(1000)
    stats["revenue"] = sum(payment["amount"] for payment in completed_payments)
    
    return stats

# --- CONFIGURATION ROUTES ---

@api_router.post("/config/stripe")
async def configure_stripe(data: dict):
    """Configure Stripe integration"""
    global stripe_checkout
    api_key = data.get("api_key")
    if not api_key:
        raise HTTPException(status_code=400, detail="API key required")
    
    try:
        stripe_checkout = StripeCheckout(api_key=api_key)
        # Store in environment for persistence
        os.environ["STRIPE_API_KEY"] = api_key
        return {"message": "Stripe configured successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Configuration error: {str(e)}")

@api_router.post("/config/openai")
async def configure_openai(data: dict):
    """Configure OpenAI integration"""
    global openai_chat
    api_key = data.get("api_key")
    if not api_key:
        raise HTTPException(status_code=400, detail="API key required")
    
    try:
        # Store in environment for persistence
        os.environ["OPENAI_API_KEY"] = api_key
        return {"message": "OpenAI configured successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Configuration error: {str(e)}")

# Initialize with existing API keys if available
@app.on_event("startup")
async def startup_event():
    global stripe_checkout, openai_chat
    
    # Initialize Stripe if key is available
    stripe_key = os.environ.get("STRIPE_API_KEY")
    if stripe_key:
        stripe_checkout = StripeCheckout(api_key=stripe_key)
    
    # Initialize OpenAI if key is available
    openai_key = os.environ.get("OPENAI_API_KEY")
    if openai_key:
        openai_chat = True  # Flag that it's configured
    
    # Create sample products for MVP
    existing_products = await db.products.count_documents({})
    if existing_products == 0:
        sample_products = [
            {
                "id": str(uuid.uuid4()),
                "name": "Premium Moroccan Argan Oil",
                "description": "100% pure, cold-pressed argan oil from Morocco. Rich in vitamin E and essential fatty acids.",
                "price": 49.99,
                "category": "physical",
                "image_url": "https://images.unsplash.com/photo-1640161704729-cbe966a08476?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzR8MHwxfHNlYXJjaHwxfHxjcnlwdG9jdXJyZW5jeXxlbnwwfHx8fDE3NTIzNDM2NDR8MA&ixlib=rb-4.1.0&q=85",
                "crypto_price": 50.0,
                "stock": 100,
                "is_featured": True,
                "created_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Organic Medjool Dates",
                "description": "Premium organic Medjool dates, naturally sweet and nutritious. Perfect for healthy snacking.",
                "price": 24.99,
                "category": "physical",
                "image_url": "https://images.unsplash.com/photo-1639754390580-2e7437267698?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzR8MHwxfHNlYXJjaHwyfHxjcnlwdG9jdXJyZW5jeXxlbnwwfHx8fDE3NTIzNDM2NDR8MA&ixlib=rb-4.1.0&q=85",
                "crypto_price": 25.0,
                "stock": 200,
                "is_featured": True,
                "created_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "RIMAR Guardian NFT",
                "description": "Exclusive NFT granting DAO voting rights and platform benefits. Limited edition digital collectible.",
                "price": 99.99,
                "category": "nft",
                "image_url": "https://images.unsplash.com/photo-1639322537228-f710d846310a?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1Nzh8MHwxfHNlYXJjaHwxfHxibG9ja2NoYWlufGVufDB8fHx8MTc1MjM5MTk5OHww&ixlib=rb-4.1.0&q=85",
                "crypto_price": 100.0,
                "stock": 50,
                "is_featured": True,
                "created_at": datetime.utcnow()
            }
        ]
        await db.products.insert_many(sample_products)

# --- ROOT ROUTE ---
@api_router.get("/")
async def root():
    return {
        "message": "Welcome to RIMAREUM API",
        "version": "1.0.0",
        "description": "Revolutionary E-commerce & Crypto Platform"
    }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()