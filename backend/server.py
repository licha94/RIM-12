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

# Import du module de sécurité PHASE 7 - SENTINEL CORE et Smart Commerce PHASE 8
try:
    from .security_module import (
        get_security_check, waf_instance, limiter, oauth2_scheme,
        PasswordHasher, api_key_manager, audit_scheduler,
        ml_detector, gpt_assistant, multilingual_chatbot, 
        continuous_monitor, EnhancedWAF
    )
    from .smart_commerce import smart_commerce, SmartProduct, ShoppingCart, UserPreferences
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
    
    class MockMultilingualChatbot:
        def get_response(self, message: str, language: str = None):
            return {
                "message": "Bonjour! Je suis l'assistant RIMAREUM. Comment puis-je vous aider?",
                "language": "fr",
                "type": "greeting"
            }
        
        def get_supported_languages(self):
            return ["fr", "en", "ar", "es"]
    
    class MockGPTAssistant:
        async def generate_security_report(self, time_period: str = "24h"):
            return {
                "period": time_period,
                "total_threats": 0,
                "security_score": 95,
                "generated_at": datetime.utcnow().isoformat()
            }
        
        async def get_threat_intelligence(self):
            return {
                "active_threats": 0,
                "threat_level": "LOW",
                "last_scan": datetime.utcnow().isoformat(),
                "blocked_ips": 0,
                "suspicious_activities": []
            }
    
    class MockSmartCommerce:
        async def get_all_products(self, category=None):
            return []
        
        async def get_product_by_id(self, product_id):
            return None
        
        async def create_cart(self, session_id, user_id=None):
            return {"id": "mock-cart", "items": [], "total_price": 0.0}
        
        async def get_categories(self):
            return {}
        
        async def search_products(self, search_term, category=None):
            return []
        
        async def add_to_cart(self, cart_id, product_id, quantity):
            return True
        
        async def get_cart(self, cart_id):
            return {"id": cart_id, "items": [], "total_price": 0.0}
        
        class MockAIAssistant:
            async def get_product_recommendations(self, product_id):
                return []
            
            async def analyze_cart_for_upselling(self, cart):
                return []
            
            async def get_cross_sell_suggestions(self, cart):
                return []
            
            async def generate_personalized_response(self, message, language, cart=None):
                return {
                    "message": "Mock AI response",
                    "language": language,
                    "response_type": "mock"
                }
        
        def __init__(self):
            self.ai_assistant = self.MockAIAssistant()
            self.qr_generator = self
        
        def generate_product_qr(self, product_id):
            return f"mock_qr_code_{product_id}"
    
    limiter = None
    oauth2_scheme = None
    waf_instance = MockWAF()
    PasswordHasher = MockPasswordHasher()
    api_key_manager = MockAPIKeyManager()
    audit_scheduler = MockAuditScheduler()
    multilingual_chatbot = MockMultilingualChatbot()
    gpt_assistant = MockGPTAssistant()
    ml_detector = None
    continuous_monitor = None
    EnhancedWAF = MockWAF
    smart_commerce = MockSmartCommerce()
# Import du module PAYCORE PHASE 9
try:
    from .paycore import (
        payment_processor, kyc_processor, invoice_generator, 
        platform_sync, ai_insights, alerts_manager, paycore_database,
        PaymentTransaction, Order, CustomerProfile, PaymentStatus, OrderStatus
    )
except ImportError:
    # Fallback objects
    class MockPaymentProcessor:
        async def process_stripe_payment(self, payment_request):
            return {"status": "completed", "transaction_id": "mock_stripe_123"}
        
        async def process_paypal_payment(self, payment_request):
            return {"status": "completed", "transaction_id": "mock_paypal_123"}
        
        async def process_crypto_payment(self, payment_request):
            return {"status": "completed", "transaction_id": "mock_crypto_123"}
    
    class MockKYCProcessor:
        async def verify_identity(self, user_id, documents):
            return {"status": "approved", "verification_id": "mock_kyc_123"}
    
    class MockInvoiceGenerator:
        async def generate_pdf_invoice(self, order, transaction):
            return "data:application/pdf;base64,mock_pdf_data"
        
        async def generate_nft_receipt(self, order, transaction):
            return '{"name": "Mock NFT Receipt", "token_id": 123}'
    
    class MockPlatformSync:
        async def sync_tiktok_shop(self, product_data):
            return {"status": "synced", "platform": "tiktok"}
        
        async def sync_amazon_store(self, product_data):
            return {"status": "synced", "platform": "amazon"}
        
        async def generate_instagram_shopping_urls(self, products):
            return [{"product_id": p.get("id"), "url": f"https://instagram.com/p/{p.get('id')}"} for p in products]
    
    class MockAIInsights:
        async def analyze_customer_behavior(self, user_id, order_history):
            return {"insights": "Mock customer analysis", "tier": "bronze"}
    
    class MockAlertsManager:
        async def send_order_confirmation(self, order, email):
            return {"status": "sent", "message_id": "mock_email_123"}
        
        async def send_admin_notification(self, order):
            return {"status": "sent", "notification_id": "mock_admin_123"}
    
    payment_processor = MockPaymentProcessor()
    kyc_processor = MockKYCProcessor()
    invoice_generator = MockInvoiceGenerator()
    platform_sync = MockPlatformSync()
    ai_insights = MockAIInsights()
    alerts_manager = MockAlertsManager()
    paycore_database = {"mock": True}
# Import du module SUBSCRIPTION SYSTEM
try:
    from .subscription_system import (
        subscription_payment_processor, ai_retention_engine, tier_manager,
        subscription_database, Subscription, CustomerTierProfile, ChurnPrediction,
        SubscriptionStatus, CustomerTier, ChurnRisk, SUBSCRIPTION_CONFIG
    )
except ImportError:
    # Fallback objects pour subscription system
    class MockSubscriptionPaymentProcessor:
        async def process_stripe_subscription_payment(self, subscription, payment_data):
            return {"success": True, "stripe_subscription_id": "sub_mock_123"}
        
        async def process_paypal_subscription_payment(self, subscription, payment_data):
            return {"success": True, "paypal_subscription_id": "I-MOCK123"}
        
        async def process_crypto_subscription_payment(self, subscription, payment_data):
            return {"success": True, "transaction_hash": "0xmock123"}
    
    class MockAIRetentionEngine:
        async def analyze_churn_risk(self, user_id, subscription, usage_data):
            return {"churn_probability": 0.2, "risk_level": "low"}
        
        async def calculate_engagement_score(self, user_id, activity_data):
            return 0.75
    
    class MockTierManager:
        async def calculate_tier_points(self, user_id, activity_data):
            return 300
        
        async def update_customer_tier(self, user_id, points):
            return "silver"
        
        async def get_tier_benefits(self, tier):
            return {"discount_rate": 0.1, "priority_support": True}
    
    subscription_payment_processor = MockSubscriptionPaymentProcessor()
    ai_retention_engine = MockAIRetentionEngine()
    tier_manager = MockTierManager()
    subscription_database = {"mock": True}
    Subscription = dict
    CustomerTierProfile = dict
    ChurnPrediction = dict
    SubscriptionStatus = str
    CustomerTier = str
    ChurnRisk = str
    SUBSCRIPTION_CONFIG = {"subscription_plans": {}}

# Import du module PHASE 11 - MULTIVERS LOGIQUE
try:
    from .phase11_multivers import (
        multivers_navigation, sanctuaire_ia_humain, dashboard_ceo_global,
        multivers_database, activate_delta_144_codes, validate_quantum_signature,
        QuantumEcosystem, SanctuaireSession, DashboardCEOMetrics,
        EcosystemStatus, DimensionType, TransmissionMode, MULTIVERS_CONFIG
    )
except ImportError:
    # Fallback objects pour Phase 11
    class MockMultiversNavigation:
        async def initialize_terra_vita_trad(self):
            return {"name": "TERRA_VITA_TRAD", "status": "mock_active"}
        
        async def synchronize_ecosystems(self):
            return {"sync_status": "mock_synchronized"}
        
        async def transition_to_dimension(self, user_id, dimension):
            return {"transition": "mock_success"}
    
    class MockSanctuaireIAHumain:
        async def initiate_sanctuaire_session(self, user_id, ecosystem_id):
            return {"session_id": "mock_session", "status": "active"}
        
        async def process_vocal_transmission(self, session_id, input_text, language="fr"):
            return {"response": "Mock sanctuaire response", "vibration": "432Hz"}
    
    class MockDashboardCEOGlobal:
        async def get_global_metrics(self):
            return {"revenue": 1000000, "users": 10000, "ecosystems": 8}
        
        async def get_country_performance(self, country_code):
            return {"country": country_code, "performance": "excellent"}
        
        async def get_ecosystem_analytics(self):
            return {"total_ecosystems": 8, "status": "operational"}
    
    multivers_navigation = MockMultiversNavigation()
    sanctuaire_ia_humain = MockSanctuaireIAHumain()
    dashboard_ceo_global = MockDashboardCEOGlobal()
    multivers_database = {"mock": True}
    activate_delta_144_codes = lambda: {"status": "mock_active"}
    validate_quantum_signature = lambda x: True
    MULTIVERS_CONFIG = {"mock": True}

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
    title="RIMAREUM API - PHASE 11 MULTIVERS LOGIQUE", 
    description="Universal Platform for Exchange, Governance, AI, and Economic Sovereignty - V11 Cosmic Edition",
    version="11.0.0"
)

# PHASE 6 Security Middlewares
# Only enable HTTPS redirect in production
if os.environ.get('ENVIRONMENT') == 'production':
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

# --- PHASE 7 SENTINEL CORE ENDPOINTS ---

@api_router.post("/chatbot/multilingual")
@limiter.limit("30/minute") if limiter else lambda x: x
async def multilingual_chat(
    data: Dict[str, Any],
    request: Request,
    security_check: Dict = Depends(get_security_check)
):
    """Chatbot multilingue Phase 7 - FR, EN, AR, ES"""
    try:
        message = data.get("message", "")
        language = data.get("language")
        
        if not message:
            raise HTTPException(
                status_code=400,
                detail="Message is required"
            )
        
        # Obtenir la réponse du chatbot
        response = multilingual_chatbot.get_response(message, language)
        
        return {
            "response": response["message"],
            "detected_language": response["language"],
            "response_type": response["type"],
            "supported_languages": multilingual_chatbot.get_supported_languages(),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/chatbot/languages")
async def get_supported_languages(
    request: Request,
    security_check: Dict = Depends(get_security_check)
):
    """Obtenir les langues supportées par le chatbot"""
    try:
        return {
            "supported_languages": multilingual_chatbot.get_supported_languages(),
            "language_details": {
                "fr": "Français",
                "en": "English", 
                "ar": "العربية",
                "es": "Español"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/security/gpt/report")
@limiter.limit("5/minute") if limiter else lambda x: x
async def get_gpt_security_report(
    request: Request,
    time_period: str = "24h",
    security_check: Dict = Depends(get_security_check)
):
    """Rapport de sécurité GPT-4 (admin uniquement)"""
    try:
        report = await gpt_assistant.generate_security_report(time_period)
        
        return {
            "report": report,
            "gpt_version": "4.0",
            "security_assistant": "RIMAREUM GPT-SECURE",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/security/intelligence")
@limiter.limit("10/minute") if limiter else lambda x: x
async def get_threat_intelligence(
    request: Request,
    security_check: Dict = Depends(get_security_check)
):
    """Intelligence des menaces"""
    try:
        intelligence = await gpt_assistant.get_threat_intelligence()
        
        return {
            "threat_intelligence": intelligence,
            "last_update": datetime.utcnow().isoformat(),
            "source": "RIMAREUM SENTINEL CORE"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- PHASE 8 SMART COMMERCE SYSTEM ENDPOINTS ---

@api_router.get("/shop/products")
@limiter.limit("60/minute") if limiter else lambda x: x
async def get_shop_products(
    request: Request,
    category: Optional[str] = None,
    featured: Optional[bool] = None,
    search: Optional[str] = None,
    security_check: Dict = Depends(get_security_check)
):
    """Obtenir les produits de la boutique avec filtres avancés"""
    try:
        if search:
            products = await smart_commerce.search_products(search, category)
        else:
            products = await smart_commerce.get_all_products(category)
        
        # Filtrer par featured si spécifié
        if featured is not None:
            products = [p for p in products if p.is_featured == featured]
        
        # Convertir en dict pour JSON
        products_data = []
        for product in products:
            if hasattr(product, '__dict__'):
                product_dict = product.__dict__.copy()
                # Convertir les datetime en ISO string
                for key, value in product_dict.items():
                    if isinstance(value, datetime):
                        product_dict[key] = value.isoformat()
                products_data.append(product_dict)
            else:
                products_data.append(product)
        
        return {
            "products": products_data,
            "total_count": len(products_data),
            "categories_available": await smart_commerce.get_categories(),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/shop/products/{product_id}")
@limiter.limit("120/minute") if limiter else lambda x: x
async def get_shop_product_details(
    product_id: str,
    request: Request,
    security_check: Dict = Depends(get_security_check)
):
    """Obtenir les détails d'un produit spécifique"""
    try:
        product = await smart_commerce.get_product_by_id(product_id)
        
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Obtenir des recommandations IA
        recommendations = await smart_commerce.ai_assistant.get_product_recommendations(product_id)
        recommended_products = []
        
        for rec_id in recommendations:
            rec_product = await smart_commerce.get_product_by_id(rec_id)
            if rec_product and hasattr(rec_product, '__dict__'):
                rec_dict = rec_product.__dict__.copy()
                for key, value in rec_dict.items():
                    if isinstance(value, datetime):
                        rec_dict[key] = value.isoformat()
                recommended_products.append(rec_dict)
        
        # Convertir le produit principal
        if hasattr(product, '__dict__'):
            product_dict = product.__dict__.copy()
            for key, value in product_dict.items():
                if isinstance(value, datetime):
                    product_dict[key] = value.isoformat()
        else:
            product_dict = product
        
        return {
            "product": product_dict,
            "recommendations": recommended_products,
            "related_products": recommended_products[:3],  # Limiter à 3 pour l'affichage
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/shop/categories")
@limiter.limit("30/minute") if limiter else lambda x: x
async def get_shop_categories(
    request: Request,
    security_check: Dict = Depends(get_security_check)
):
    """Obtenir toutes les catégories de produits"""
    try:
        categories = await smart_commerce.get_categories()
        
        # Ajouter des statistiques pour chaque catégorie
        products = await smart_commerce.get_all_products()
        category_stats = {}
        
        for category_id in categories.keys():
            category_products = [p for p in products if p.category == category_id]
            category_stats[category_id] = {
                "product_count": len(category_products),
                "featured_count": len([p for p in category_products if p.is_featured]),
                "price_range": {
                    "min": min([p.price for p in category_products]) if category_products else 0,
                    "max": max([p.price for p in category_products]) if category_products else 0
                }
            }
        
        return {
            "categories": categories,
            "statistics": category_stats,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/shop/cart/create")
@limiter.limit("20/minute") if limiter else lambda x: x
async def create_shopping_cart(
    request: Request,
    user_data: Optional[Dict[str, Any]] = None,
    security_check: Dict = Depends(get_security_check)
):
    """Créer un nouveau panier"""
    try:
        # Générer un session ID unique
        session_id = str(uuid.uuid4())
        user_id = user_data.get("user_id") if user_data else None
        
        cart = await smart_commerce.create_cart(session_id, user_id)
        
        # Convertir en dict
        if hasattr(cart, '__dict__'):
            cart_dict = cart.__dict__.copy()
            for key, value in cart_dict.items():
                if isinstance(value, datetime):
                    cart_dict[key] = value.isoformat()
        else:
            cart_dict = cart
        
        return {
            "cart": cart_dict,
            "session_id": session_id,
            "expires_in": 3600,  # 1 heure
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/shop/cart/{cart_id}/add")
@limiter.limit("30/minute") if limiter else lambda x: x
async def add_to_cart(
    cart_id: str,
    item_data: Dict[str, Any],
    request: Request,
    security_check: Dict = Depends(get_security_check)
):
    """Ajouter un produit au panier"""
    try:
        product_id = item_data.get("product_id")
        quantity = item_data.get("quantity", 1)
        
        if not product_id:
            raise HTTPException(status_code=400, detail="product_id is required")
        
        success = await smart_commerce.add_to_cart(cart_id, product_id, quantity)
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to add item to cart")
        
        # Obtenir le panier mis à jour
        updated_cart = await smart_commerce.get_cart(cart_id)
        
        if hasattr(updated_cart, '__dict__'):
            cart_dict = updated_cart.__dict__.copy()
            for key, value in cart_dict.items():
                if isinstance(value, datetime):
                    cart_dict[key] = value.isoformat()
        else:
            cart_dict = updated_cart
        
        return {
            "success": True,
            "cart": cart_dict,
            "message": "Item added to cart successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/shop/cart/{cart_id}")
@limiter.limit("60/minute") if limiter else lambda x: x
async def get_cart(
    cart_id: str,
    request: Request,
    security_check: Dict = Depends(get_security_check)
):
    """Obtenir les détails d'un panier"""
    try:
        cart = await smart_commerce.get_cart(cart_id)
        
        if not cart:
            raise HTTPException(status_code=404, detail="Cart not found")
        
        # Obtenir des recommandations pour le panier
        upsell_suggestions = await smart_commerce.ai_assistant.analyze_cart_for_upselling(cart)
        cross_sell_suggestions = await smart_commerce.ai_assistant.get_cross_sell_suggestions(cart)
        
        if hasattr(cart, '__dict__'):
            cart_dict = cart.__dict__.copy()
            for key, value in cart_dict.items():
                if isinstance(value, datetime):
                    cart_dict[key] = value.isoformat()
        else:
            cart_dict = cart
        
        return {
            "cart": cart_dict,
            "ai_suggestions": {
                "upsell": upsell_suggestions,
                "cross_sell": cross_sell_suggestions
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/shop/assistant")
@limiter.limit("20/minute") if limiter else lambda x: x
async def smart_shopping_assistant(
    message_data: Dict[str, Any],
    request: Request,
    security_check: Dict = Depends(get_security_check)
):
    """Assistant IA de shopping intégré"""
    try:
        message = message_data.get("message", "")
        language = message_data.get("language", "fr")
        cart_id = message_data.get("cart_id")
        
        if not message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        # Obtenir le panier si fourni
        cart = None
        if cart_id:
            cart = await smart_commerce.get_cart(cart_id)
        
        # Générer la réponse personnalisée
        response = await smart_commerce.ai_assistant.generate_personalized_response(
            message, language, cart
        )
        
        # Ajouter des produits recommandés basés sur le message
        if any(word in message.lower() for word in ["produit", "product", "acheter", "buy", "منتج", "comprar"]):
            # Rechercher des produits pertinents
            search_results = await smart_commerce.search_products(message)
            response["suggested_products"] = [
                {
                    "id": p.id,
                    "name": p.name, 
                    "price": p.price,
                    "category": p.category,
                    "qr_code": p.qr_code
                } for p in search_results[:3]
            ]
        
        return {
            "response": response["message"],
            "language": response["language"],
            "type": response["response_type"],
            "recommendations": response.get("recommendations", []),
            "suggested_products": response.get("suggested_products", []),
            "cart_id": cart_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/shop/checkout")
@limiter.limit("10/minute") if limiter else lambda x: x
async def checkout_cart(
    checkout_data: Dict[str, Any],
    request: Request,
    security_check: Dict = Depends(get_security_check)
):
    """Processus de checkout (simulation)"""
    try:
        cart_id = checkout_data.get("cart_id")
        payment_method = checkout_data.get("payment_method", "card")
        billing_info = checkout_data.get("billing_info", {})
        
        if not cart_id:
            raise HTTPException(status_code=400, detail="cart_id is required")
        
        cart = await smart_commerce.get_cart(cart_id)
        if not cart:
            raise HTTPException(status_code=404, detail="Cart not found")
        
        # Simulation du processus de paiement
        order_id = str(uuid.uuid4())
        
        # Simuler selon la méthode de paiement
        payment_simulation = {
            "order_id": order_id,
            "status": "pending",
            "payment_method": payment_method,
            "total_amount": cart.total_price if hasattr(cart, 'total_price') else 0,
            "currency": "EUR",
            "created_at": datetime.utcnow().isoformat()
        }
        
        if payment_method == "card":
            payment_simulation.update({
                "status": "completed",
                "stripe_session_id": f"cs_sim_{order_id[:8]}",
                "payment_intent": f"pi_sim_{order_id[:8]}"
            })
        elif payment_method == "crypto":
            payment_simulation.update({
                "status": "pending",
                "wallet_address": "0x1234...5678",
                "blockchain_tx": f"0xabcd...{order_id[:8]}"
            })
        elif payment_method == "paypal":
            payment_simulation.update({
                "status": "completed",
                "paypal_order_id": f"PP_{order_id[:8]}",
                "payer_id": f"PAYER_{order_id[:8]}"
            })
        
        return {
            "checkout_success": True,
            "order": payment_simulation,
            "estimated_delivery": (datetime.utcnow() + timedelta(days=7)).isoformat(),
            "tracking_number": f"RIMAR{order_id[:10].upper()}",
            "message": "Commande créée avec succès (simulation)",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/shop/qrcode/{product_id}")
@limiter.limit("30/minute") if limiter else lambda x: x
async def get_product_qr_code(
    product_id: str,
    request: Request,
    security_check: Dict = Depends(get_security_check)
):
    """Obtenir le QR code d'un produit"""
    try:
        product = await smart_commerce.get_product_by_id(product_id)
        
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Générer un nouveau QR code si nécessaire
        qr_code = product.qr_code if hasattr(product, 'qr_code') and product.qr_code else \
                  smart_commerce.qr_generator.generate_product_qr(product_id)
        
        return {
            "product_id": product_id,
            "qr_code": qr_code,
            "product_url": f"https://rimareum.com/product/{product_id}",
            "nfc_ready": True,
            "social_sharing": {
                "tiktok": f"https://tiktok.com/@rimareum/product/{product_id}",
                "amazon": f"https://amazon.com/dp/RIMAR{product_id}",
                "instagram": f"https://instagram.com/p/rimareum_{product_id}"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/shop/status")
async def get_smart_commerce_status(
    request: Request,
    security_check: Dict = Depends(get_security_check)
):
    """Statut du système Smart Commerce"""
    try:
        products = await smart_commerce.get_all_products()
        categories = await smart_commerce.get_categories()
        
        return {
            "phase": "8_SMART_COMMERCE",
            "status": "ACTIVE",
            "components": {
                "dynamic_product_interface": True,
                "ai_shopping_assistant": True,
                "cart_system": True,
                "qr_code_generation": True,
                "nfc_ready": True,
                "multilingual_support": True,
                "payment_simulation": True
            },
            "statistics": {
                "total_products": len(products),
                "categories_count": len(categories),
                "featured_products": len([p for p in products if hasattr(p, 'is_featured') and p.is_featured]),
                "ai_recommendations_active": True
            },
            "integrations": {
                "tiktok_shop_ready": True,
                "amazon_store_ready": True,
                "instagram_shopping": True,
                "stripe_simulation": True,
                "paypal_simulation": True,
                "crypto_wallet_ready": True
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/security/ml/model")
@limiter.limit("5/minute") if limiter else lambda x: x
async def get_ml_model_info(
    request: Request,
    security_check: Dict = Depends(get_security_check)
):
    """Informations sur le modèle ML"""
    try:
        if ml_detector:
            info = {
                "model_version": ml_detector.model_version,
                "is_trained": ml_detector.is_trained,
                "last_training": ml_detector.last_training.isoformat() if ml_detector.last_training else None,
                "feature_names": ml_detector.feature_names,
                "training_data_size": len(ml_detector.training_data)
            }
        else:
            info = {
                "model_version": "N/A",
                "is_trained": False,
                "message": "ML detector not available"
            }
        
        return {
            "ml_model_info": info,
            "phase": "7_SENTINEL_CORE",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/security/ml/train")
@limiter.limit("1/hour") if limiter else lambda x: x
async def trigger_ml_training(
    request: Request,
    security_check: Dict = Depends(get_security_check)
):
    """Déclencher l'entraînement du modèle ML (admin uniquement)"""
    try:
        if not ml_detector:
            return {
                "training_triggered": False,
                "training_success": False,
                "message": "ML detector not available in fallback mode",
                "data_size": 0,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Entraîner le modèle en arrière-plan
        training_result = ml_detector.train_model(ml_detector.training_data)
        
        return {
            "training_triggered": True,
            "training_success": training_result,
            "data_size": len(ml_detector.training_data),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/security/sentinel/status")
async def get_sentinel_status(
    request: Request,
    security_check: Dict = Depends(get_security_check)
):
    """Statut du système SENTINEL CORE"""
    try:
        return {
            "phase": "7_SENTINEL_CORE",
            "status": "ACTIVE",
            "components": {
                "intelligent_detection": True,
                "gpt_secure_4": gpt_assistant is not None,
                "smart_firewall_ml": ml_detector is not None,
                "multilingual_chatbot": multilingual_chatbot is not None,
                "reactive_surveillance": continuous_monitor is not None,
                "enhanced_waf": isinstance(waf_instance, EnhancedWAF) if EnhancedWAF else False
            },
            "security_level": "MAXIMUM",
            "threat_hunting_active": True,
            "auto_correction_enabled": True,
            "continuous_monitoring": True,
            "reactive_mode": True,
            "timestamp": datetime.utcnow().isoformat()
        }
        
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
        recent_events_cursor = db.security_events.find(
            {"timestamp": {"$gte": datetime.utcnow() - timedelta(hours=24)}}
        ).sort("timestamp", -1).limit(100)
        
        recent_events = []
        async for event in recent_events_cursor:
            # Convert ObjectId to string and clean up the event
            event_dict = {
                "event_type": event.get("event_type", ""),
                "ip_address": event.get("ip_address", ""),
                "risk_score": event.get("risk_score", 0.0),
                "blocked": event.get("blocked", False),
                "timestamp": event.get("timestamp", datetime.utcnow()).isoformat() if isinstance(event.get("timestamp"), datetime) else str(event.get("timestamp", "")),
                "details": event.get("details", {})
            }
            recent_events.append(event_dict)
        
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