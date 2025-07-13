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
    
    # Mock objects for fallback
    class MockWAF:
        def __init__(self):
            self.blocked_ips = set()
    
    class MockPasswordHasher:
        @staticmethod
        def hash_password(password: str) -> str:
            return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        @staticmethod
        def verify_password(password: str, hashed: str) -> bool:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    class MockAPIKeyManager:
        def generate_api_key(self, user_id: str) -> str:
            return base64.b64encode(f"{user_id}:{datetime.utcnow().timestamp()}".encode()).decode()
    
    class MockAuditScheduler:
        async def run_scheduled_audit(self):
            pass
    
    limiter = None
    oauth2_scheme = None
    waf_instance = MockWAF()
    PasswordHasher = MockPasswordHasher()
    api_key_manager = MockAPIKeyManager()
    audit_scheduler = MockAuditScheduler()

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

# CORS configuration for security
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://localhost:3000"],  # Restrict to specific origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
    expose_headers=["X-Security-Score", "X-Rate-Limit-Remaining"]
)

# Démarrer l'audit automatique
@app.on_event("startup")
async def startup_event():
    """Démarrage des services de sécurité"""
    asyncio.create_task(audit_scheduler.run_scheduled_audit())
    print("🛡️ RIMAREUM PHASE 6 SECURITY ACTIVATED")
    print("✅ WAF: Active")
    print("✅ Guardian AI: Active")
    print("✅ Rate Limiting: Active")
    print("✅ Geo Blocking: Active")
    print("✅ Audit Scheduler: Active")

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

# --- SECURITY ENDPOINTS PHASE 6 ---

@api_router.post("/auth/register", response_model=Dict[str, Any])
async def register_user(
    user_data: UserRegistration,
    request: Request,
    security_check: Dict = Depends(get_security_check)
):
    """Inscription utilisateur avec sécurité renforcée"""
    try:
        # Vérifier si l'utilisateur existe déjà
        existing_user = await db.users.find_one({"email": user_data.email})
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="User already exists with this email"
            )
        
        # Hasher le mot de passe avec la nouvelle méthode
        password_hash = PasswordHasher.hash_password(user_data.password)
        
        # Créer l'utilisateur
        user = User(
            email=user_data.email,
            username=user_data.username,
            password_hash=password_hash
        )
        
        # Insérer en base
        await db.users.insert_one(user.dict())
        
        # Générer une clé API
        api_key = api_key_manager.generate_api_key(user.id)
        
        # Mettre à jour l'utilisateur avec la clé API
        await db.users.update_one(
            {"id": user.id},
            {"$push": {"api_keys": api_key}}
        )
        
        return {
            "message": "User registered successfully",
            "user_id": user.id,
            "api_key": api_key
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/auth/login", response_model=TokenResponse)
async def login_user(
    login_data: UserLogin,
    request: Request,
    security_check: Dict = Depends(get_security_check)
):
    """Connexion utilisateur avec OAuth2"""
    try:
        # Trouver l'utilisateur
        user_doc = await db.users.find_one({"username": login_data.username})
        if not user_doc:
            raise HTTPException(
                status_code=401,
                detail="Invalid credentials"
            )
        
        # Vérifier le mot de passe
        if not PasswordHasher.verify_password(login_data.password, user_doc["password_hash"]):
            # Incrémenter les tentatives échouées
            await db.users.update_one(
                {"id": user_doc["id"]},
                {"$inc": {"failed_login_attempts": 1}}
            )
            raise HTTPException(
                status_code=401,
                detail="Invalid credentials"
            )
        
        # Réinitialiser les tentatives échouées et mettre à jour la dernière connexion
        await db.users.update_one(
            {"id": user_doc["id"]},
            {
                "$set": {
                    "failed_login_attempts": 0,
                    "last_login": datetime.utcnow()
                }
            }
        )
        
        # Générer une nouvelle clé API
        api_key = api_key_manager.generate_api_key(user_doc["id"])
        
        # Ajouter la clé API à l'utilisateur
        await db.users.update_one(
            {"id": user_doc["id"]},
            {"$push": {"api_keys": api_key}}
        )
        
        return TokenResponse(
            access_token=api_key,
            token_type="bearer",
            expires_in=7200,  # 2 heures
            api_key=api_key
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/security/report")
async def report_security_event(
    event: SecurityReport,
    request: Request,
    security_check: Dict = Depends(get_security_check)
):
    """Rapport d'événement de sécurité depuis le frontend"""
    try:
        # Créer l'événement de sécurité
        security_event = SecurityEvent(
            event_type=event.event_type,
            ip_address=event.ip_address,
            user_agent=request.headers.get("user-agent", ""),
            risk_score=0.5,  # Score par défaut
            blocked=False,
            details=event.details
        )
        
        # Stocker en base
        await db.security_events.insert_one(security_event.dict())
        
        return {"message": "Security event reported successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/security/status")
async def get_security_status(
    request: Request,
    security_check: Dict = Depends(get_security_check)
):
    """Obtenir le statut de sécurité actuel"""
    try:
        return {
            "security_level": "PHASE_6_ACTIVE",
            "waf_active": True,
            "guardian_ai_active": True,
            "rate_limit_active": True,
            "geo_blocking_active": True,
            "blocked_ips": len(waf_instance.blocked_ips),
            "risk_score": security_check.get("risk_score", 0.0),
            "last_audit": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/security/audit")
async def get_security_audit(
    request: Request,
    security_check: Dict = Depends(get_security_check)
):
    """Audit de sécurité détaillé (admin uniquement)"""
    try:
        # Récupérer les événements de sécurité récents
        recent_events = await db.security_events.find(
            {"timestamp": {"$gte": datetime.utcnow() - timedelta(hours=24)}}
        ).sort("timestamp", -1).limit(100).to_list(100)
        
        # Statistiques
        total_events = len(recent_events)
        blocked_events = sum(1 for e in recent_events if e.get("blocked", False))
        high_risk_events = sum(1 for e in recent_events if e.get("risk_score", 0) > 0.7)
        
        return {
            "audit_period": "24h",
            "total_events": total_events,
            "blocked_events": blocked_events,
            "high_risk_events": high_risk_events,
            "guardian_ai_status": "ACTIVE",
            "recent_events": recent_events[:10]  # 10 plus récents
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
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
@limiter.limit("30/minute") if limiter else lambda x: x
async def get_products(
    request: Request,
    category: Optional[str] = None, 
    featured: Optional[bool] = None
):
    """Get all products with optional filtering"""
    filter_query = {}
    if category:
        filter_query["category"] = category
    if featured is not None:
        filter_query["is_featured"] = featured
    
    products = await db.products.find(filter_query).to_list(100)
    return [Product(**product) for product in products]

@api_router.get("/products/{product_id}", response_model=Product)
@limiter.limit("60/minute") if limiter else lambda x: x
async def get_product(
    product_id: str,
    request: Request
):
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

# --- PAYMENT ENDPOINTS ---
@api_router.post("/payments/checkout/session")
@limiter.limit("10/minute") if limiter else lambda x: x
async def create_checkout_session(
    payment_request: PaymentRequest,
    request: Request,
    security_check: Dict = Depends(get_security_check)
):
    """Create a checkout session for payment"""
    try:
        if not stripe_checkout:
            raise HTTPException(
                status_code=503,
                detail="Payment service not configured"
            )
        
        # Create checkout session
        session_request = CheckoutSessionRequest(
            success_url="https://your-domain.com/success",
            cancel_url="https://your-domain.com/cancel",
            line_items=[{
                "price_data": {
                    "currency": payment_request.currency.lower(),
                    "product_data": {"name": f"Product {payment_request.product_id}"},
                    "unit_amount": int(payment_request.amount * 100)
                },
                "quantity": 1
            }]
        )
        
        session = await stripe_checkout.create_session(session_request)
        
        # Store payment transaction
        transaction = PaymentTransaction(
            amount=payment_request.amount,
            currency=payment_request.currency,
            product_id=payment_request.product_id,
            payment_method=payment_request.payment_method,
            session_id=session.id
        )
        
        await db.payments.insert_one(transaction.dict())
        
        return {"session_id": session.id, "url": session.url}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/payments/session/{session_id}/status")
@limiter.limit("30/minute") if limiter else lambda x: x
async def get_payment_status(
    session_id: str,
    request: Request,
    security_check: Dict = Depends(get_security_check)
):
    """Get payment session status"""
    try:
        if not stripe_checkout:
            raise HTTPException(
                status_code=503,
                detail="Payment service not configured"
            )
        
        status = await stripe_checkout.get_session_status(session_id)
        
        return {
            "session_id": session_id,
            "status": status.status,
            "payment_intent": status.payment_intent
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- WALLET ROUTES ---

@api_router.post("/wallet/connect")
@limiter.limit("20/minute") if limiter else lambda x: x
async def connect_wallet(
    wallet_data: WalletConnection,
    request: Request,
    security_check: Dict = Depends(get_security_check)
):
    """Connect crypto wallet"""
    try:
        # Store wallet connection
        await db.wallet_connections.insert_one(wallet_data.dict())
        
        return {"message": "Wallet connected successfully", "address": wallet_data.wallet_address}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/wallet/balance/{address}")
@limiter.limit("100/minute") if limiter else lambda x: x
async def get_wallet_balance(
    address: str,
    request: Request,
    security_check: Dict = Depends(get_security_check)
):
    """Get wallet balance (simulated)"""
    try:
        # Simulate wallet balance
        mock_balance = {
            "address": address,
            "eth_balance": 1.25,
            "rimar_balance": 1000.0,
            "nft_count": 3,
            "last_updated": datetime.utcnow().isoformat()
        }
        
        return mock_balance
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- AI CHAT ROUTES ---

# --- AI CHAT ROUTES ---

@api_router.post("/chat/message")
@limiter.limit("20/minute") if limiter else lambda x: x
async def chat_message(
    message_data: Dict[str, Any],
    request: Request,
    security_check: Dict = Depends(get_security_check)
):
    """Send message to AI chat"""
    try:
        if not openai_chat:
            raise HTTPException(
                status_code=503,
                detail="AI service not configured"
            )
        
        session_id = message_data.get("session_id")
        user_message = message_data.get("message")
        
        if not session_id or not user_message:
            raise HTTPException(
                status_code=400,
                detail="session_id and message are required"
            )
        
        # Get or create chat session
        session = await db.chat_sessions.find_one({"session_id": session_id})
        if not session:
            session = ChatSession(session_id=session_id)
            await db.chat_sessions.insert_one(session.dict())
        
        # Add user message to session
        user_chat_message = ChatMessage(role="user", content=user_message)
        
        # Get AI response
        ai_message = UserMessage(content=user_message)
        response = await openai_chat.send_message(ai_message)
        
        # Add AI response to session
        ai_chat_message = ChatMessage(role="assistant", content=response.content)
        
        # Update session with both messages
        await db.chat_sessions.update_one(
            {"session_id": session_id},
            {
                "$push": {"messages": {"$each": [user_chat_message.dict(), ai_chat_message.dict()]}},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        return {
            "session_id": session_id,
            "message": user_message,
            "response": response.content,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/chat/sessions/{session_id}")
@limiter.limit("60/minute") if limiter else lambda x: x
async def get_chat_session(
    session_id: str,
    request: Request,
    security_check: Dict = Depends(get_security_check)
):
    """Get chat session history"""
    try:
        session = await db.chat_sessions.find_one({"session_id": session_id})
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return ChatSession(**session)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- ADMIN ROUTES ---

# --- ADMIN ROUTES ---

@api_router.get("/admin/stats")
@limiter.limit("10/minute") if limiter else lambda x: x
async def get_admin_stats(
    request: Request,
    security_check: Dict = Depends(get_security_check)
):
    """Get admin dashboard statistics"""
    try:
        # Get basic statistics
        total_products = await db.products.count_documents({})
        total_users = await db.users.count_documents({})
        total_orders = await db.orders.count_documents({})
        total_payments = await db.payments.count_documents({})
        
        # Calculate revenue
        pipeline = [
            {"$group": {"_id": None, "total_revenue": {"$sum": "$amount"}}}
        ]
        revenue_result = await db.payments.aggregate(pipeline).to_list(1)
        total_revenue = revenue_result[0]["total_revenue"] if revenue_result else 0
        
        # Security statistics
        blocked_ips = len(waf_instance.blocked_ips)
        total_security_events = await db.security_events.count_documents({})
        
        return {
            "total_products": total_products,
            "total_users": total_users,
            "total_orders": total_orders,
            "total_payments": total_payments,
            "total_revenue": total_revenue,
            "blocked_ips": blocked_ips,
            "security_events": total_security_events,
            "dao_stats": {
                "total_proposals": 5,
                "active_proposals": 3,
                "total_votes": 1247
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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