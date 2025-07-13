"""
🔐 MODULE SÉCURITÉ AVANCÉ RIMAREUM PHASE 6
Système de protection intelligent avec WAF, anti-bot, audit, détection d'attaques, et IA Guardian
"""

import asyncio
import hashlib
import json
import logging
import re
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass
from collections import defaultdict, deque
import ipaddress
import bcrypt
import httpx
import secrets
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, OAuth2PasswordBearer
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import os

# Configuration sécurité PHASE 6
SECURITY_CONFIG = {
    "max_requests_per_minute": 5,  # Réduit pour plus de sécurité
    "max_requests_per_hour": 100,
    "blocked_countries": [],  # Liste ISO codes pays bloqués
    "allowed_countries": ["FR", "DZ", "AE"],  # France, Algérie, Dubaï
    "maintenance_mode": False,
    "auto_ban_threshold": 5,  # Plus strict
    "password_hash_rounds": 12,  # bcrypt rounds
    "api_key_expiration_hours": 2,  # Expiration API keys
    "audit_interval_hours": 24,  # Audit automatique
    "suspicious_patterns": [
        r"union\s+select",
        r"<script[^>]*>",
        r"javascript:",
        r"eval\s*\(",
        r"document\.cookie",
        r"alert\s*\(",
        r"\.\.\/",
        r"etc\/passwd",
        r"\/proc\/",
        r"cmd\.exe",
        r"powershell",
        r"base64_decode",
        r"system\s*\(",
        r"exec\s*\(",
        r"phpinfo",
        r"wp-admin",
        r"admin\.php",
    ],
    "bot_user_agents": [
        "bot", "crawler", "spider", "scraper", "wget", "curl",
        "python-requests", "libwww-perl", "java/", "go-http-client",
        "scrapy", "beautifulsoup", "selenium", "phantomjs"
    ],
    "honeypot_endpoints": [
        "/admin.php", "/wp-admin/", "/phpmyadmin/", "/.env",
        "/config.php", "/backup/", "/database/", "/logs/"
    ]
}

@dataclass
class SecurityEvent:
    """Événement de sécurité"""
    timestamp: datetime
    ip_address: str
    user_agent: str
    request_path: str
    method: str
    threat_type: str
    severity: str
    blocked: bool
    details: Dict

class PasswordHasher:
    """Gestionnaire de hashage des mots de passe SHA256 + bcrypt"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hasher un mot de passe avec SHA256 + bcrypt"""
        # Première étape: SHA256
        sha256_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Deuxième étape: bcrypt avec salt
        salt = bcrypt.gensalt(rounds=SECURITY_CONFIG["password_hash_rounds"])
        bcrypt_hash = bcrypt.hashpw(sha256_hash.encode(), salt)
        
        return bcrypt_hash.decode()
    
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """Vérifier un mot de passe"""
        try:
            # Recalculer SHA256
            sha256_hash = hashlib.sha256(password.encode()).hexdigest()
            
            # Vérifier avec bcrypt
            return bcrypt.checkpw(sha256_hash.encode(), hashed_password.encode())
        except Exception:
            return False

class CountryBlocker:
    """Système de blocage géographique"""
    
    def __init__(self):
        self.ip_cache = {}
        self.cache_expiry = 3600  # 1 heure
    
    async def get_country_code(self, ip: str) -> Optional[str]:
        """Obtenir le code pays d'une IP via ipapi.co"""
        if ip in self.ip_cache:
            cached_data = self.ip_cache[ip]
            if time.time() - cached_data["timestamp"] < self.cache_expiry:
                return cached_data["country"]
        
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"https://ipapi.co/{ip}/country/")
                if response.status_code == 200:
                    country_code = response.text.strip()
                    
                    # Mettre en cache
                    self.ip_cache[ip] = {
                        "country": country_code,
                        "timestamp": time.time()
                    }
                    
                    return country_code
        except Exception as e:
            logging.error(f"Erreur géolocalisation IP {ip}: {e}")
        
        return None
    
    async def is_country_allowed(self, ip: str) -> bool:
        """Vérifier si le pays est autorisé"""
        if not SECURITY_CONFIG["allowed_countries"]:
            return True
        
        country_code = await self.get_country_code(ip)
        if not country_code:
            return True  # Autoriser si impossible de déterminer
        
        return country_code.upper() in SECURITY_CONFIG["allowed_countries"]

class RimareumGuardianAI:
    """Intelligence artificielle de surveillance RIMAREUM"""
    
    def __init__(self):
        self.request_patterns = defaultdict(list)
        self.behavioral_model = {
            "normal_patterns": set(),
            "suspicious_patterns": set(),
            "learning_mode": True
        }
        self.threat_scores = defaultdict(float)
    
    async def analyze_request(self, request: Request, client_ip: str) -> Dict:
        """Analyser une requête avec l'IA Guardian"""
        
        # Extraire les caractéristiques de la requête
        features = self._extract_features(request, client_ip)
        
        # Analyser les patterns
        pattern_score = await self._analyze_patterns(features)
        
        # Analyser le comportement
        behavior_score = await self._analyze_behavior(client_ip, features)
        
        # Score final
        ai_risk_score = max(pattern_score, behavior_score)
        
        # Apprentissage automatique
        if self.behavioral_model["learning_mode"]:
            await self._learn_from_request(features, ai_risk_score)
        
        return {
            "ai_risk_score": ai_risk_score,
            "pattern_score": pattern_score,
            "behavior_score": behavior_score,
            "features": features
        }
    
    def _extract_features(self, request: Request, client_ip: str) -> Dict:
        """Extraire les caractéristiques d'une requête"""
        return {
            "path": request.url.path,
            "method": request.method,
            "user_agent": request.headers.get("user-agent", ""),
            "content_length": request.headers.get("content-length", 0),
            "referer": request.headers.get("referer", ""),
            "accept": request.headers.get("accept", ""),
            "ip": client_ip,
            "timestamp": time.time()
        }
    
    async def _analyze_patterns(self, features: Dict) -> float:
        """Analyser les patterns de requête"""
        risk_score = 0.0
        
        # Vérifier les patterns suspects connus
        request_content = " ".join([
            features["path"],
            features["user_agent"],
            features["referer"]
        ])
        
        for pattern in SECURITY_CONFIG["suspicious_patterns"]:
            if re.search(pattern, request_content, re.IGNORECASE):
                risk_score += 0.3
        
        # Vérifier les honeypots
        for honeypot in SECURITY_CONFIG["honeypot_endpoints"]:
            if honeypot in features["path"]:
                risk_score += 0.8
        
        return min(risk_score, 1.0)
    
    async def _analyze_behavior(self, client_ip: str, features: Dict) -> float:
        """Analyser le comportement de l'utilisateur"""
        now = time.time()
        
        # Ajouter aux patterns récents
        self.request_patterns[client_ip].append({
            "timestamp": now,
            "path": features["path"],
            "method": features["method"]
        })
        
        # Nettoyer les anciens patterns (garder 1 heure)
        self.request_patterns[client_ip] = [
            p for p in self.request_patterns[client_ip]
            if now - p["timestamp"] < 3600
        ]
        
        recent_requests = self.request_patterns[client_ip]
        
        # Analyser la fréquence
        if len(recent_requests) > 50:  # Trop de requêtes
            return 0.7
        
        # Analyser la diversité des chemins
        unique_paths = set(r["path"] for r in recent_requests)
        if len(unique_paths) > 20:  # Trop de chemins différents
            return 0.6
        
        return 0.0
    
    async def _learn_from_request(self, features: Dict, risk_score: float):
        """Apprentissage automatique à partir des requêtes"""
        pattern_key = f"{features['method']}:{features['path']}"
        
        if risk_score < 0.3:
            self.behavioral_model["normal_patterns"].add(pattern_key)
        elif risk_score > 0.7:
            self.behavioral_model["suspicious_patterns"].add(pattern_key)

class SecurityAuditLogger:
    """Journal d'audit sécurisé"""
    
    def __init__(self):
        self.logger = logging.getLogger("rimareum_security")
        self.logger.setLevel(logging.INFO)
        
        # Handler pour fichier de log
        try:
            handler = logging.FileHandler("/tmp/rimareum_security.log")
        except:
            handler = logging.StreamHandler()  # Fallback to console
            
        formatter = logging.Formatter(
            '%(asctime)s - RIMAREUM_SEC - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    async def log_event(self, event: SecurityEvent):
        """Enregistrer un événement de sécurité"""
        log_data = {
            "timestamp": event.timestamp.isoformat(),
            "ip": event.ip_address,
            "user_agent": event.user_agent,
            "path": event.request_path,
            "method": event.method,
            "threat_type": event.threat_type,
            "severity": event.severity,
            "blocked": event.blocked,
            "details": event.details
        }
        
        self.logger.info(json.dumps(log_data))
        
        # Alertes critiques
        if event.severity == "HIGH":
            await self.send_alert(event)
    
    async def send_alert(self, event: SecurityEvent):
        """Envoyer alerte pour événements critiques"""
        alert_message = f"""
        🚨 ALERTE SÉCURITÉ RIMAREUM 🚨
        
        Menace détectée: {event.threat_type}
        IP: {event.ip_address}
        Chemin: {event.request_path}
        Sévérité: {event.severity}
        Bloqué: {event.blocked}
        
        Timestamp: {event.timestamp}
        """
        
        print(alert_message)  # Console pour le moment

class WAF:
    """Web Application Firewall intelligent"""
    
    def __init__(self):
        self.blocked_ips: Set[str] = set()
        self.audit_logger = SecurityAuditLogger()
        self.maintenance_mode = SECURITY_CONFIG["maintenance_mode"]
        self.request_counts = defaultdict(list)
    
    async def process_request(self, request: Request) -> Dict:
        """Traiter et analyser une requête"""
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "")
        
        # Vérification mode maintenance
        if self.maintenance_mode:
            return await self._handle_maintenance_mode(client_ip, request)
        
        # Vérification IP bloquée
        if client_ip in self.blocked_ips:
            return await self._handle_blocked_ip(client_ip, request)
        
        # Analyse rate limiting
        risk_score = await self._analyze_rate_limiting(client_ip)
        
        # Détection patterns suspects
        content_risk = await self._analyze_request_content(request)
        
        # Score de risque total
        total_risk = max(risk_score, content_risk)
        
        should_block = total_risk > 0.7
        
        # Logging
        await self._log_security_event(request, client_ip, user_agent, total_risk, should_block)
        
        return {
            "allowed": not should_block,
            "risk_score": total_risk,
            "ip": client_ip,
            "reasons": ["High risk score"] if should_block else []
        }
    
    def _get_client_ip(self, request: Request) -> str:
        """Obtenir l'IP réelle du client"""
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
    
    async def _analyze_rate_limiting(self, ip: str) -> float:
        """Analyser le rate limiting"""
        now = time.time()
        
        # Nettoyer les anciennes requêtes
        self.request_counts[ip] = [t for t in self.request_counts[ip] if now - t < 3600]
        
        # Ajouter la requête actuelle
        self.request_counts[ip].append(now)
        
        # Compter les requêtes récentes
        recent_requests = sum(1 for t in self.request_counts[ip] if now - t < 60)
        
        if recent_requests > SECURITY_CONFIG["max_requests_per_minute"]:
            return 0.8
        
        return 0.0
    
    async def _analyze_request_content(self, request: Request) -> float:
        """Analyser le contenu de la requête"""
        content = str(request.url) + " " + str(request.headers)
        
        for pattern in SECURITY_CONFIG["suspicious_patterns"]:
            if re.search(pattern, content, re.IGNORECASE):
                return 0.9
        
        return 0.0
    
    async def _handle_blocked_ip(self, ip: str, request: Request) -> Dict:
        """Gérer une IP bloquée"""
        return {
            "allowed": False,
            "risk_score": 1.0,
            "ip": ip,
            "reasons": ["IP address is blocked"]
        }
    
    async def _handle_maintenance_mode(self, ip: str, request: Request) -> Dict:
        """Gérer le mode maintenance"""
        return {
            "allowed": False,
            "risk_score": 0.0,
            "ip": ip,
            "reasons": ["Platform in maintenance mode"]
        }
    
    async def _log_security_event(self, request: Request, ip: str, user_agent: str, 
                                 risk_score: float, blocked: bool):
        """Enregistrer un événement de sécurité"""
        severity = "HIGH" if risk_score > 0.8 else "MEDIUM" if risk_score > 0.5 else "LOW"
        
        event = SecurityEvent(
            timestamp=datetime.utcnow(),
            ip_address=ip,
            user_agent=user_agent,
            request_path=str(request.url.path),
            method=request.method,
            threat_type="SECURITY_CHECK",
            severity=severity,
            blocked=blocked,
            details={"risk_score": risk_score}
        )
        
        await self.audit_logger.log_event(event)

# Instance globale du WAF
waf_instance = WAF()

async def security_middleware(request: Request):
    """Middleware de sécurité pour FastAPI"""
    
    # Ignorer les routes système
    if request.url.path.startswith(("/_health", "/metrics", "/favicon.ico")):
        return {"allowed": True, "risk_score": 0.0}
    
    # Analyse de sécurité
    result = await waf_instance.process_request(request)
    
    if not result["allowed"]:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "Request blocked by security system",
                "reasons": result["reasons"],
                "support": "Contact support@rimareum.com if you believe this is an error"
            }
        )
    
    return result

async def get_security_check(request: Request):
    """Dépendance pour vérification de sécurité"""
    return await security_middleware(request)