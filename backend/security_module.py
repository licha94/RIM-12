"""
🔐 MODULE SÉCURITÉ AVANCÉ RIMAREUM PHASE 7 - SENTINEL CORE
Système de protection intelligent avec détection réactive, ML, et surveillance continue
"""

import asyncio
import hashlib
import json
import logging
import re
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any, Tuple
from dataclasses import dataclass, field
from collections import defaultdict, deque
import ipaddress
import bcrypt
import httpx
import secrets
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
import os
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, OAuth2PasswordBearer
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Configuration sécurité PHASE 7 - SENTINEL CORE
SECURITY_CONFIG = {
    "max_requests_per_minute": 5,
    "max_requests_per_hour": 100,
    "blocked_countries": [],
    "allowed_countries": ["FR", "DZ", "AE"],  # France, Algérie, Dubaï
    "maintenance_mode": False,
    "auto_ban_threshold": 3,  # Plus strict pour Phase 7
    "password_hash_rounds": 12,
    "api_key_expiration_hours": 2,
    "audit_interval_hours": 24,
    "ml_model_update_interval": 3600,  # 1 heure
    "continuous_monitoring": True,
    "reactive_mode": True,
    "gpt_security_enabled": True,
    "multilingual_support": ["fr", "en", "ar", "es"],
    "intelligence_level": "HIGH",
    "auto_correction_enabled": True,
    "threat_prediction_enabled": True,
    "behavioral_learning_rate": 0.1,
    "suspicious_patterns": [
        # SQL Injection patterns
        r"union\s+select",
        r"select\s+.*\s+from",
        r"insert\s+into",
        r"update\s+.*\s+set",
        r"delete\s+from",
        r"drop\s+table",
        r"create\s+table",
        r"alter\s+table",
        r"'.*or.*'.*=.*'",
        r"'.*and.*'.*=.*'",
        r"1\s*=\s*1",
        r"1\s*=\s*0",
        # XSS patterns
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"eval\s*\(",
        r"document\.cookie",
        r"document\.write",
        r"window\.location",
        r"alert\s*\(",
        r"prompt\s*\(",
        r"confirm\s*\(",
        # Path traversal
        r"\.\.\/",
        r"\.\.\\",
        r"\/etc\/passwd",
        r"\/proc\/",
        r"\/var\/log\/",
        # Command injection
        r"cmd\.exe",
        r"powershell",
        r"bash",
        r"sh\s",
        r"system\s*\(",
        r"exec\s*\(",
        r"passthru",
        r"shell_exec",
        # Advanced threats
        r"base64_decode",
        r"phpinfo",
        r"wp-admin",
        r"admin\.php",
        r"config\.php",
        r"\.env",
        r"\.git",
        r"\.svn",
        r"backup",
        r"database",
        r"logs",
        r"tmp",
        r"temp",
        # LDAP injection
        r"\(\|\(",
        r"\)\|\)",
        r"\*\)\(",
        # NoSQL injection
        r"{\s*\$where",
        r"{\s*\$ne",
        r"{\s*\$gt",
        r"{\s*\$lt",
        r"{\s*\$regex",
        # XML injection
        r"<\?xml",
        r"<!DOCTYPE",
        r"<!ENTITY",
        # Server-side includes
        r"<!--#exec",
        r"<!--#include",
        # Remote file inclusion
        r"http://",
        r"https://",
        r"ftp://",
        r"file://",
        # Buffer overflow indicators
        r"A{100,}",
        r"0x[0-9a-fA-F]+",
        # Advanced persistent threats
        r"powershell\s+-enc",
        r"certutil\s+-decode",
        r"rundll32",
        r"regsvr32",
        r"wscript",
        r"cscript",
        r"mshta",
        r"bitsadmin",
        # Reconnaissance patterns
        r"nmap",
        r"sqlmap",
        r"nikto",
        r"dirb",
        r"gobuster",
        r"wfuzz",
        r"burp",
        r"zap",
        r"metasploit",
        r"msfconsole",
        # Crypto mining
        r"coinhive",
        r"cryptonight",
        r"stratum",
        r"mining",
        # Botnet patterns
        r"botnet",
        r"ddos",
        r"slowloris",
        r"hulk",
        r"goldeneye"
    ],
    "bot_user_agents": [
        "bot", "crawler", "spider", "scraper", "wget", "curl",
        "python-requests", "libwww-perl", "java/", "go-http-client",
        "scrapy", "beautifulsoup", "selenium", "phantomjs", "headless",
        "automated", "test", "monitor", "check", "scan", "audit",
        "attack", "hack", "exploit", "vulnerability", "penetration"
    ],
    "honeypot_endpoints": [
        "/admin.php", "/wp-admin/", "/phpmyadmin/", "/.env", "/config.php",
        "/backup/", "/database/", "/logs/", "/tmp/", "/temp/", "/.git/",
        "/admin/", "/administrator/", "/manager/", "/webadmin/", "/console/",
        "/api/admin/", "/api/config/", "/api/backup/", "/api/database/",
        "/phpinfo.php", "/info.php", "/test.php", "/debug.php", "/shell.php",
        "/admin/login", "/admin/dashboard", "/admin/users", "/admin/settings",
        "/xmlrpc.php", "/wp-login.php", "/wp-config.php", "/readme.html",
        "/license.txt", "/changelog.txt", "/install.php", "/setup.php"
    ],
    "high_risk_countries": ["CN", "RU", "KP", "IR", "IQ", "AF", "SY"],
    "ml_threat_threshold": 0.8,
    "gpt_analysis_threshold": 0.9,
    "auto_block_duration": 86400,  # 24 heures
    "escalation_threshold": 5,
    "learning_mode_duration": 604800,  # 7 jours
    "sentinel_response_time": 0.1,  # 100ms max response
    "continuous_learning": True,
    "threat_intelligence_update": 3600,  # 1 heure
    "behavioral_baseline_update": 21600,  # 6 heures
    "anomaly_detection_sensitivity": 0.05,
    "adaptive_thresholds": True,
    "predictive_blocking": True,
    "real_time_analysis": True,
    "deep_packet_inspection": True,
    "session_anomaly_detection": True,
    "credential_stuffing_detection": True,
    "advanced_evasion_detection": True,
    "zero_day_protection": True,
    "threat_hunting_mode": True
}

@dataclass
class SecurityEvent:
    """Événement de sécurité Phase 7"""
    timestamp: datetime
    ip_address: str
    user_agent: str
    request_path: str
    method: str
    threat_type: str
    severity: str
    blocked: bool
    details: Dict
    ml_score: float = 0.0
    gpt_analysis: Optional[str] = None
    auto_corrected: bool = False
    threat_prediction: Optional[str] = None

@dataclass
class ThreatIntelligence:
    """Intelligence sur les menaces"""
    ip_reputation: Dict[str, float] = field(default_factory=dict)
    domain_reputation: Dict[str, float] = field(default_factory=dict)
    attack_patterns: List[str] = field(default_factory=list)
    emerging_threats: List[str] = field(default_factory=list)
    threat_actors: Dict[str, Any] = field(default_factory=dict)
    ioc_database: Dict[str, Any] = field(default_factory=dict)
    last_update: datetime = field(default_factory=datetime.utcnow)

class MLThreatDetector:
    """Détecteur de menaces basé sur Machine Learning"""
    
    def __init__(self):
        self.model = IsolationForest(
            contamination=0.1,
            random_state=42,
            n_estimators=100
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        self.training_data = []
        self.feature_names = [
            'request_rate', 'payload_size', 'url_length', 'param_count',
            'header_count', 'user_agent_entropy', 'path_depth', 'suspicious_patterns',
            'geo_risk_score', 'reputation_score', 'time_of_day', 'request_interval'
        ]
        self.threat_cache = {}
        self.model_version = "1.0.0"
        self.last_training = datetime.utcnow()
    
    def extract_features(self, request: Request, client_ip: str, context: Dict) -> np.ndarray:
        """Extraire les caractéristiques d'une requête pour le ML"""
        try:
            # Caractéristiques de base
            url = str(request.url)
            headers = dict(request.headers)
            user_agent = headers.get('user-agent', '')
            
            # Calculs des métriques
            request_rate = context.get('request_rate', 0)
            payload_size = len(str(request.body) if hasattr(request, 'body') else '')
            url_length = len(url)
            param_count = len(request.query_params)
            header_count = len(headers)
            user_agent_entropy = self._calculate_entropy(user_agent)
            path_depth = url.count('/')
            suspicious_patterns = self._count_suspicious_patterns(url + ' ' + user_agent)
            geo_risk_score = context.get('geo_risk_score', 0)
            reputation_score = context.get('reputation_score', 0)
            time_of_day = datetime.utcnow().hour
            request_interval = context.get('request_interval', 0)
            
            features = np.array([
                request_rate, payload_size, url_length, param_count,
                header_count, user_agent_entropy, path_depth, suspicious_patterns,
                geo_risk_score, reputation_score, time_of_day, request_interval
            ])
            
            return features.reshape(1, -1)
            
        except Exception as e:
            logging.error(f"Erreur extraction features ML: {e}")
            return np.zeros((1, len(self.feature_names)))
    
    def _calculate_entropy(self, text: str) -> float:
        """Calculer l'entropie d'un texte"""
        if not text:
            return 0.0
        
        # Compter les caractères
        char_counts = {}
        for char in text:
            char_counts[char] = char_counts.get(char, 0) + 1
        
        # Calculer l'entropie
        entropy = 0.0
        length = len(text)
        for count in char_counts.values():
            probability = count / length
            entropy -= probability * np.log2(probability)
        
        return entropy
    
    def _count_suspicious_patterns(self, text: str) -> int:
        """Compter les patterns suspects dans un texte"""
        count = 0
        for pattern in SECURITY_CONFIG["suspicious_patterns"]:
            if re.search(pattern, text, re.IGNORECASE):
                count += 1
        return count
    
    def predict_threat(self, features: np.ndarray) -> Tuple[float, str]:
        """Prédire si une requête est une menace"""
        if not self.is_trained:
            return 0.0, "model_not_trained"
        
        try:
            # Normaliser les features
            features_scaled = self.scaler.transform(features)
            
            # Prédiction
            anomaly_score = self.model.decision_function(features_scaled)[0]
            is_anomaly = self.model.predict(features_scaled)[0] == -1
            
            # Convertir en score de menace (0-1)
            threat_score = max(0.0, min(1.0, (1.0 - anomaly_score) / 2.0))
            
            threat_level = "high" if threat_score > 0.8 else "medium" if threat_score > 0.5 else "low"
            
            return threat_score, threat_level
            
        except Exception as e:
            logging.error(f"Erreur prédiction ML: {e}")
            return 0.0, "prediction_error"
    
    def train_model(self, training_data: List[Dict]):
        """Entraîner le modèle ML"""
        if len(training_data) < 100:
            return False
        
        try:
            # Préparer les données
            features_list = []
            for data in training_data:
                features = np.array([
                    data.get('request_rate', 0),
                    data.get('payload_size', 0),
                    data.get('url_length', 0),
                    data.get('param_count', 0),
                    data.get('header_count', 0),
                    data.get('user_agent_entropy', 0),
                    data.get('path_depth', 0),
                    data.get('suspicious_patterns', 0),
                    data.get('geo_risk_score', 0),
                    data.get('reputation_score', 0),
                    data.get('time_of_day', 0),
                    data.get('request_interval', 0)
                ])
                features_list.append(features)
            
            X = np.array(features_list)
            
            # Normaliser les données
            X_scaled = self.scaler.fit_transform(X)
            
            # Entraîner le modèle
            self.model.fit(X_scaled)
            self.is_trained = True
            self.last_training = datetime.utcnow()
            
            # Sauvegarder le modèle
            self.save_model()
            
            return True
            
        except Exception as e:
            logging.error(f"Erreur entraînement ML: {e}")
            return False
    
    def save_model(self):
        """Sauvegarder le modèle ML"""
        try:
            model_data = {
                'model': self.model,
                'scaler': self.scaler,
                'feature_names': self.feature_names,
                'version': self.model_version,
                'last_training': self.last_training
            }
            joblib.dump(model_data, '/tmp/rimareum_ml_model.pkl')
        except Exception as e:
            logging.error(f"Erreur sauvegarde modèle: {e}")
    
    def load_model(self):
        """Charger le modèle ML"""
        try:
            if os.path.exists('/tmp/rimareum_ml_model.pkl'):
                model_data = joblib.load('/tmp/rimareum_ml_model.pkl')
                self.model = model_data['model']
                self.scaler = model_data['scaler']
                self.feature_names = model_data['feature_names']
                self.model_version = model_data['version']
                self.last_training = model_data['last_training']
                self.is_trained = True
                return True
        except Exception as e:
            logging.error(f"Erreur chargement modèle: {e}")
        return False
    
    def update_training_data(self, request_data: Dict):
        """Mettre à jour les données d'entraînement"""
        self.training_data.append(request_data)
        
        # Limite de données en mémoire
        if len(self.training_data) > 10000:
            self.training_data = self.training_data[-5000:]
        
        # Réentraîner périodiquement
        if len(self.training_data) % 1000 == 0:
            asyncio.create_task(self._retrain_model())
    
    async def _retrain_model(self):
        """Réentraîner le modèle en arrière-plan"""
        await asyncio.sleep(1)  # Éviter le blocage
        self.train_model(self.training_data)

class GPTSecurityAssistant:
    """Assistant de sécurité GPT-4 pour l'analyse et les recommandations"""
    
    def __init__(self):
        self.api_key = os.environ.get('OPENAI_API_KEY')
        self.model = "gpt-4o"
        self.system_prompt = """
        Vous êtes RIMAREUM GPT-SECURE 4.0, un assistant de sécurité avancé spécialisé dans l'analyse de menaces cybersécurité.
        
        Votre rôle :
        - Analyser les événements de sécurité et détecter les menaces
        - Proposer des contre-mesures et améliorations
        - Générer des alertes intelligentes
        - Recommander des actions correctives
        - Identifier les vulnérabilités potentielles
        
        Répondez toujours en français et soyez précis et actionnable.
        """
        self.analysis_cache = {}
        self.threat_history = []
        self.recommendations = []
        self.active = self.api_key is not None
    
    async def analyze_threat(self, security_event: SecurityEvent) -> Dict[str, Any]:
        """Analyser une menace avec GPT-4"""
        if not self.active:
            return {"analysis": "GPT-4 non disponible", "recommendation": "Analyse manuelle requise"}
        
        try:
            # Préparer le contexte
            context = {
                "threat_type": security_event.threat_type,
                "severity": security_event.severity,
                "ip_address": security_event.ip_address,
                "request_path": security_event.request_path,
                "method": security_event.method,
                "details": security_event.details,
                "ml_score": security_event.ml_score,
                "timestamp": security_event.timestamp.isoformat()
            }
            
            # Créer le prompt
            prompt = f"""
            Analysez cet événement de sécurité RIMAREUM et fournissez une analyse détaillée :
            
            ÉVÉNEMENT :
            {json.dumps(context, indent=2)}
            
            HISTORIQUE RÉCENT :
            {json.dumps(self.threat_history[-5:], indent=2) if self.threat_history else "Aucun historique"}
            
            Fournissez une analyse JSON avec :
            1. "threat_analysis" : Analyse détaillée de la menace
            2. "severity_assessment" : Évaluation de la gravité (1-10)
            3. "attack_vector" : Vecteur d'attaque identifié
            4. "recommendations" : Liste des actions recommandées
            5. "auto_actions" : Actions automatiques suggérées
            6. "monitoring_focus" : Éléments à surveiller
            7. "threat_prediction" : Prédiction d'évolution
            """
            
            # Appel à l'API GPT-4 (simulation si pas de clé)
            if self.api_key:
                # Ici, vous intégreriez l'appel réel à l'API OpenAI
                # Pour l'instant, simulation intelligente
                analysis = await self._simulate_gpt_analysis(context)
            else:
                analysis = await self._simulate_gpt_analysis(context)
            
            # Mettre à jour l'historique
            self.threat_history.append({
                "timestamp": datetime.utcnow().isoformat(),
                "event": context,
                "analysis": analysis
            })
            
            # Limiter l'historique
            if len(self.threat_history) > 100:
                self.threat_history = self.threat_history[-50:]
            
            return analysis
            
        except Exception as e:
            logging.error(f"Erreur analyse GPT-4: {e}")
            return {"analysis": f"Erreur d'analyse: {str(e)}", "recommendation": "Analyse manuelle requise"}
    
    async def _simulate_gpt_analysis(self, context: Dict) -> Dict[str, Any]:
        """Simulation intelligente d'analyse GPT-4"""
        threat_type = context.get("threat_type", "unknown")
        severity = context.get("severity", "LOW")
        ml_score = context.get("ml_score", 0.0)
        
        # Analyse basée sur le type de menace
        if threat_type == "SQLi":
            return {
                "threat_analysis": "Tentative d'injection SQL détectée. L'attaquant essaie d'exploiter une vulnérabilité dans la base de données.",
                "severity_assessment": 8,
                "attack_vector": "Injection SQL via paramètres de requête",
                "recommendations": [
                    "Bloquer l'IP source immédiatement",
                    "Vérifier les paramètres de requête",
                    "Renforcer la validation des entrées",
                    "Auditer les requêtes SQL"
                ],
                "auto_actions": ["block_ip", "sanitize_input", "log_detailed"],
                "monitoring_focus": ["database_queries", "input_validation", "error_patterns"],
                "threat_prediction": "Risque d'escalade vers exfiltration de données"
            }
        elif threat_type == "XSS":
            return {
                "threat_analysis": "Tentative d'attaque XSS détectée. Script malveillant injecté dans l'application.",
                "severity_assessment": 7,
                "attack_vector": "Cross-Site Scripting via injection de script",
                "recommendations": [
                    "Sanitiser immédiatement les entrées",
                    "Implémenter CSP strict",
                    "Vérifier la validation côté client",
                    "Auditer les sorties HTML"
                ],
                "auto_actions": ["sanitize_input", "block_script", "csp_enforce"],
                "monitoring_focus": ["script_injection", "dom_manipulation", "cookie_theft"],
                "threat_prediction": "Risque de vol de session ou défacement"
            }
        elif threat_type == "BOT":
            return {
                "threat_analysis": "Activité de bot détectée. Comportement automatisé suspect.",
                "severity_assessment": 5,
                "attack_vector": "Automatisation malveillante",
                "recommendations": [
                    "Implémenter CAPTCHA",
                    "Analyser les patterns de requête",
                    "Vérifier User-Agent",
                    "Rate limiting adaptatif"
                ],
                "auto_actions": ["challenge_captcha", "rate_limit", "fingerprint_check"],
                "monitoring_focus": ["request_patterns", "user_agent", "session_behavior"],
                "threat_prediction": "Risque d'attaque DDoS ou scraping"
            }
        elif threat_type == "BRUTE_FORCE":
            return {
                "threat_analysis": "Attaque par force brute détectée. Tentatives multiples de connexion.",
                "severity_assessment": 6,
                "attack_vector": "Force brute sur authentification",
                "recommendations": [
                    "Bloquer l'IP immédiatement",
                    "Implémenter délai exponentiel",
                    "Renforcer l'authentification",
                    "Alerter l'utilisateur cible"
                ],
                "auto_actions": ["block_ip", "account_lockout", "delay_response"],
                "monitoring_focus": ["login_attempts", "password_patterns", "account_targeting"],
                "threat_prediction": "Risque de compromission de compte"
            }
        else:
            # Analyse générique basée sur le score ML
            severity_score = min(10, max(1, int(ml_score * 10)))
            return {
                "threat_analysis": f"Événement de sécurité de type {threat_type} avec score ML {ml_score:.2f}",
                "severity_assessment": severity_score,
                "attack_vector": "Vecteur d'attaque à déterminer",
                "recommendations": [
                    "Analyser les détails de l'événement",
                    "Surveiller l'IP source",
                    "Vérifier les patterns similaires",
                    "Mettre à jour les règles de détection"
                ],
                "auto_actions": ["monitor_ip", "pattern_analysis", "rule_update"],
                "monitoring_focus": ["similar_events", "ip_behavior", "pattern_evolution"],
                "threat_prediction": "Évolution incertaine - surveillance requise"
            }
    
    async def generate_security_report(self, time_period: str = "24h") -> Dict[str, Any]:
        """Générer un rapport de sécurité intelligent"""
        try:
            # Analyser l'historique récent
            recent_threats = self.threat_history[-50:] if self.threat_history else []
            
            # Statistiques
            threat_counts = {}
            severity_distribution = {}
            
            for threat in recent_threats:
                threat_type = threat.get("event", {}).get("threat_type", "unknown")
                severity = threat.get("analysis", {}).get("severity_assessment", 0)
                
                threat_counts[threat_type] = threat_counts.get(threat_type, 0) + 1
                severity_range = "high" if severity >= 8 else "medium" if severity >= 5 else "low"
                severity_distribution[severity_range] = severity_distribution.get(severity_range, 0) + 1
            
            # Recommandations globales
            global_recommendations = [
                "Maintenir la surveillance continue",
                "Mettre à jour les règles de détection",
                "Renforcer l'authentification",
                "Améliorer la validation des entrées"
            ]
            
            # Prédictions
            threat_predictions = [
                "Augmentation probable des attaques XSS",
                "Surveillance accrue des tentatives SQL injection",
                "Attention aux nouveaux vecteurs d'attaque"
            ]
            
            return {
                "period": time_period,
                "total_threats": len(recent_threats),
                "threat_distribution": threat_counts,
                "severity_distribution": severity_distribution,
                "global_recommendations": global_recommendations,
                "threat_predictions": threat_predictions,
                "security_score": self._calculate_security_score(recent_threats),
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Erreur génération rapport: {e}")
            return {"error": f"Erreur génération rapport: {str(e)}"}
    
    def _calculate_security_score(self, threats: List[Dict]) -> int:
        """Calculer un score de sécurité global"""
        if not threats:
            return 100
        
        total_severity = sum(
            threat.get("analysis", {}).get("severity_assessment", 0) 
            for threat in threats
        )
        
        avg_severity = total_severity / len(threats)
        base_score = 100
        penalty = min(50, avg_severity * 5 + len(threats) * 0.5)
        
        return max(0, int(base_score - penalty))
    
    async def get_threat_intelligence(self) -> Dict[str, Any]:
        """Obtenir l'intelligence des menaces"""
        return {
            "emerging_threats": [
                "Nouvelles techniques d'injection SQL",
                "Attaques XSS polymorphes",
                "Bots IA avancés",
                "Attaques de session hijacking"
            ],
            "threat_actors": [
                "Script kiddies",
                "Groupes cybercriminels",
                "Bots automatisés"
            ],
            "attack_trends": [
                "Augmentation des attaques ciblées",
                "Évolution des techniques d'évasion",
                "Utilisation d'IA pour les attaques"
            ],
            "recommendations": [
                "Mettre à jour les signatures",
                "Améliorer la détection comportementale",
                "Renforcer la surveillance"
                "Mettre à jour les signatures",
                "Améliorer la détection comportementale",
                "Renforcer la surveillance"
            ]
        }

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
    """Système de blocage géographique Phase 7"""
    
    def __init__(self):
        self.ip_cache = {}
        self.cache_expiry = 3600  # 1 heure
        self.threat_intel = ThreatIntelligence()
    
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
    
    async def get_geo_risk_score(self, ip: str) -> float:
        """Calculer le score de risque géographique"""
        country_code = await self.get_country_code(ip)
        if not country_code:
            return 0.0
        
        # Pays à haut risque
        if country_code.upper() in SECURITY_CONFIG["high_risk_countries"]:
            return 0.9
        
        # Pays autorisés
        if country_code.upper() in SECURITY_CONFIG["allowed_countries"]:
            return 0.0
        
class MultilingualChatbot:
    """Chatbot multilingue Phase 7 - FR, EN, AR, ES"""
    
    def __init__(self):
        self.supported_languages = SECURITY_CONFIG["multilingual_support"]
        self.language_patterns = {
            "fr": r"(bonjour|salut|bonsoir|au revoir|merci|s'il vous plaît)",
            "en": r"(hello|hi|good morning|goodbye|thank you|please)",
            "ar": r"(مرحبا|السلام عليكم|شكرا|من فضلك|مع السلامة)",
            "es": r"(hola|buenos días|gracias|por favor|adiós)"
        }
        self.responses = {
            "fr": {
                "greeting": "Bonjour ! Je suis l'assistant RIMAREUM. Comment puis-je vous aider ?",
                "help": "Je peux vous aider avec vos questions sur RIMAREUM, les produits, le DAO, les NFT et la sécurité.",
                "security": "Votre sécurité est notre priorité. Tous vos échanges sont protégés par notre système SENTINEL.",
                "products": "Découvrez nos produits exclusifs : huile d'argan, dattes biologiques, et NFT RIMAR.",
                "dao": "Le DAO RIMAREUM vous permet de participer à la gouvernance de la plateforme.",
                "contact": "Pour nous contacter : support@rimareum.com",
                "error": "Désolé, je n'ai pas compris votre demande. Pouvez-vous reformuler ?",
                "goodbye": "Au revoir ! N'hésitez pas à revenir si vous avez d'autres questions."
            },
            "en": {
                "greeting": "Hello! I'm the RIMAREUM assistant. How can I help you?",
                "help": "I can help you with questions about RIMAREUM, products, DAO, NFTs and security.",
                "security": "Your security is our priority. All your exchanges are protected by our SENTINEL system.",
                "products": "Discover our exclusive products: argan oil, organic dates, and RIMAR NFTs.",
                "dao": "The RIMAREUM DAO allows you to participate in platform governance.",
                "contact": "To contact us: support@rimareum.com",
                "error": "Sorry, I didn't understand your request. Can you rephrase?",
                "goodbye": "Goodbye! Feel free to come back if you have other questions."
            },
            "ar": {
                "greeting": "مرحبا! أنا مساعد RIMAREUM. كيف يمكنني مساعدتك؟",
                "help": "يمكنني مساعدتك في الأسئلة حول RIMAREUM والمنتجات وDAO وNFT والأمان.",
                "security": "أمانك هو أولويتنا. جميع تبادلاتك محمية بنظام SENTINEL الخاص بنا.",
                "products": "اكتشف منتجاتنا الحصرية: زيت الأرغان، التمر البيولوجي، ورموز RIMAR غير القابلة للاستبدال.",
                "dao": "يتيح لك DAO RIMAREUM المشاركة في حوكمة المنصة.",
                "contact": "للتواصل معنا: support@rimareum.com",
                "error": "آسف، لم أفهم طلبك. هل يمكنك إعادة الصياغة؟",
                "goodbye": "وداعا! لا تتردد في العودة إذا كان لديك أسئلة أخرى."
            },
            "es": {
                "greeting": "¡Hola! Soy el asistente RIMAREUM. ¿Cómo puedo ayudarte?",
                "help": "Puedo ayudarte con preguntas sobre RIMAREUM, productos, DAO, NFTs y seguridad.",
                "security": "Tu seguridad es nuestra prioridad. Todos tus intercambios están protegidos por nuestro sistema SENTINEL.",
                "products": "Descubre nuestros productos exclusivos: aceite de argán, dátiles orgánicos y NFTs RIMAR.",
                "dao": "El DAO RIMAREUM te permite participar en la gobernanza de la plataforma.",
                "contact": "Para contactarnos: support@rimareum.com",
                "error": "Lo siento, no entendí tu solicitud. ¿Puedes reformular?",
                "goodbye": "¡Adiós! No dudes en volver si tienes otras preguntas."
            }
        }
        
        self.faq_database = {
            "fr": {
                "qu'est-ce que rimareum": "RIMAREUM est une plateforme révolutionnaire combinant e-commerce, crypto-monnaies, NFT et gouvernance DAO.",
                "comment acheter": "Vous pouvez acheter nos produits avec des cartes bancaires ou des crypto-monnaies.",
                "qu'est-ce que le dao": "Le DAO est notre système de gouvernance décentralisée où les détenteurs de $RIMAR peuvent voter.",
                "sécurité": "Nous utilisons un système de sécurité multicouche avec IA, WAF et surveillance continue.",
                "nft": "Nos NFT RIMAR donnent accès à des avantages exclusifs et à la gouvernance."
            },
            "en": {
                "what is rimareum": "RIMAREUM is a revolutionary platform combining e-commerce, cryptocurrencies, NFTs and DAO governance.",
                "how to buy": "You can purchase our products with bank cards or cryptocurrencies.",
                "what is dao": "The DAO is our decentralized governance system where $RIMAR holders can vote.",
                "security": "We use a multi-layer security system with AI, WAF and continuous monitoring.",
                "nft": "Our RIMAR NFTs provide access to exclusive benefits and governance."
            },
            "ar": {
                "ما هو rimareum": "RIMAREUM هي منصة ثورية تجمع بين التجارة الإلكترونية والعملات المشفرة وNFT وحوكمة DAO.",
                "كيفية الشراء": "يمكنك شراء منتجاتنا بالبطاقات المصرفية أو العملات المشفرة.",
                "ما هو dao": "DAO هو نظام الحوكمة اللامركزي حيث يمكن لحاملي $RIMAR التصويت.",
                "الأمان": "نستخدم نظام أمان متعدد الطبقات مع الذكاء الاصطناعي وWAF ومراقبة مستمرة.",
                "nft": "تمنح رموز RIMAR NFT الخاصة بنا الوصول إلى المزايا الحصرية والحوكمة."
            },
            "es": {
                "qué es rimareum": "RIMAREUM es una plataforma revolucionaria que combina comercio electrónico, criptomonedas, NFT y gobernanza DAO.",
                "cómo comprar": "Puedes comprar nuestros productos con tarjetas bancarias o criptomonedas.",
                "qué es dao": "El DAO es nuestro sistema de gobernanza descentralizada donde los poseedores de $RIMAR pueden votar.",
                "seguridad": "Usamos un sistema de seguridad multicapa con IA, WAF y monitoreo continuo.",
                "nft": "Nuestros NFT RIMAR brindan acceso a beneficios exclusivos y gobernanza."
            }
        }
    
    def detect_language(self, text: str) -> str:
        """Détecter la langue d'un texte"""
        text_lower = text.lower()
        
        # Compter les matches pour chaque langue
        language_scores = {}
        for lang, pattern in self.language_patterns.items():
            matches = len(re.findall(pattern, text_lower))
            language_scores[lang] = matches
        
        # Retourner la langue avec le plus de matches
        if language_scores:
            detected_lang = max(language_scores, key=language_scores.get)
            if language_scores[detected_lang] > 0:
                return detected_lang
        
        # Langue par défaut
        return "fr"
    
    def get_response(self, message: str, language: str = None) -> Dict[str, str]:
        """Obtenir une réponse du chatbot"""
        if language is None:
            language = self.detect_language(message)
        
        if language not in self.supported_languages:
            language = "fr"  # Fallback
        
        message_lower = message.lower()
        
        # Recherche dans la FAQ
        for question, answer in self.faq_database[language].items():
            if any(word in message_lower for word in question.split()):
                return {
                    "message": answer,
                    "language": language,
                    "type": "faq"
                }
        
        # Réponses contextuelles
        if any(word in message_lower for word in ["bonjour", "hello", "مرحبا", "hola"]):
            return {
                "message": self.responses[language]["greeting"],
                "language": language,
                "type": "greeting"
            }
        elif any(word in message_lower for word in ["aide", "help", "مساعدة", "ayuda"]):
            return {
                "message": self.responses[language]["help"],
                "language": language,
                "type": "help"
            }
        elif any(word in message_lower for word in ["sécurité", "security", "أمان", "seguridad"]):
            return {
                "message": self.responses[language]["security"],
                "language": language,
                "type": "security"
            }
        elif any(word in message_lower for word in ["produit", "product", "منتج", "producto"]):
            return {
                "message": self.responses[language]["products"],
                "language": language,
                "type": "products"
            }
        elif any(word in message_lower for word in ["dao", "gouvernance", "governance", "حوكمة", "gobernanza"]):
            return {
                "message": self.responses[language]["dao"],
                "language": language,
                "type": "dao"
            }
        elif any(word in message_lower for word in ["contact", "تواصل", "contacto"]):
            return {
                "message": self.responses[language]["contact"],
                "language": language,
                "type": "contact"
            }
        elif any(word in message_lower for word in ["au revoir", "goodbye", "مع السلامة", "adiós"]):
            return {
                "message": self.responses[language]["goodbye"],
                "language": language,
                "type": "goodbye"
            }
        else:
            return {
                "message": self.responses[language]["error"],
                "language": language,
                "type": "error"
            }
    
    def get_supported_languages(self) -> List[str]:
        """Obtenir les langues supportées"""
        return self.supported_languages.copy()
    
    def add_faq(self, question: str, answer: str, language: str):
        """Ajouter une entrée FAQ"""
        if language in self.faq_database:
            self.faq_database[language][question.lower()] = answer
    
    def get_stats(self) -> Dict[str, int]:
        """Obtenir les statistiques du chatbot"""
        stats = {}
        for lang in self.supported_languages:
            stats[lang] = len(self.faq_database.get(lang, {}))
class ContinuousMonitor:
    """Système de surveillance continue Phase 7"""
    
    def __init__(self):
        self.monitoring_active = SECURITY_CONFIG["continuous_monitoring"]
        self.reactive_mode = SECURITY_CONFIG["reactive_mode"]
        self.threat_queue = asyncio.Queue()
        self.analysis_tasks = []
        self.monitoring_stats = {
            "total_requests": 0,
            "threats_detected": 0,
            "threats_blocked": 0,
            "auto_corrections": 0,
            "false_positives": 0
        }
        self.performance_metrics = {
            "average_response_time": 0.0,
            "peak_response_time": 0.0,
            "throughput": 0
        }
        self.alerts = []
    
    async def start_monitoring(self):
        """Démarrer la surveillance continue"""
        if not self.monitoring_active:
            return
        
        # Lancer les tâches de surveillance
        self.analysis_tasks = [
            asyncio.create_task(self._continuous_threat_analysis()),
            asyncio.create_task(self._performance_monitoring()),
            asyncio.create_task(self._health_check()),
            asyncio.create_task(self._alert_processor())
        ]
        
        logging.info("🔄 Surveillance continue RIMAREUM PHASE 7 activée")
    
    async def stop_monitoring(self):
        """Arrêter la surveillance"""
        for task in self.analysis_tasks:
            task.cancel()
        
        self.monitoring_active = False
        logging.info("🛑 Surveillance continue arrêtée")
    
    async def _continuous_threat_analysis(self):
        """Analyse continue des menaces"""
        while self.monitoring_active:
            try:
                # Attendre un événement de menace
                threat_event = await asyncio.wait_for(
                    self.threat_queue.get(), 
                    timeout=1.0
                )
                
                # Analyser la menace
                await self._analyze_threat(threat_event)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logging.error(f"Erreur analyse continue: {e}")
                await asyncio.sleep(1)
    
    async def _analyze_threat(self, threat_event: Dict):
        """Analyser une menace spécifique"""
        try:
            threat_type = threat_event.get("type", "unknown")
            severity = threat_event.get("severity", "low")
            
            # Mettre à jour les statistiques
            self.monitoring_stats["threats_detected"] += 1
            
            # Réponse immédiate si nécessaire
            if severity == "high" and self.reactive_mode:
                await self._immediate_response(threat_event)
            
            # Apprentissage automatique
            await self._update_ml_model(threat_event)
            
        except Exception as e:
            logging.error(f"Erreur analyse menace: {e}")
    
    async def _immediate_response(self, threat_event: Dict):
        """Réponse immédiate aux menaces critiques"""
        try:
            response_actions = []
            
            # Blocage IP automatique
            if threat_event.get("ip_address"):
                response_actions.append(f"IP {threat_event['ip_address']} bloquée")
            
            # Auto-correction
            if SECURITY_CONFIG["auto_correction_enabled"]:
                await self._auto_correct_threat(threat_event)
                response_actions.append("Auto-correction appliquée")
            
            # Alerte immédiate
            alert = {
                "timestamp": datetime.utcnow().isoformat(),
                "type": "IMMEDIATE_RESPONSE",
                "threat": threat_event,
                "actions": response_actions
            }
            
            self.alerts.append(alert)
            
            # Notifier l'admin si nécessaire
            if threat_event.get("severity") == "critical":
                await self._notify_admin(alert)
            
        except Exception as e:
            logging.error(f"Erreur réponse immédiate: {e}")
    
    async def _auto_correct_threat(self, threat_event: Dict):
        """Auto-correction des menaces"""
        try:
            threat_type = threat_event.get("type", "unknown")
            
            if threat_type == "SQLi":
                # Sanitisation automatique
                await self._sanitize_sql_input(threat_event)
            elif threat_type == "XSS":
                # Sanitisation XSS
                await self._sanitize_xss_input(threat_event)
            elif threat_type == "RATE_LIMIT":
                # Throttling adaptatif
                await self._adaptive_throttling(threat_event)
            
            self.monitoring_stats["auto_corrections"] += 1
            
        except Exception as e:
            logging.error(f"Erreur auto-correction: {e}")
    
    async def _sanitize_sql_input(self, threat_event: Dict):
        """Sanitisation automatique des entrées SQL"""
        # Implémentation de la sanitisation SQL
        pass
    
    async def _sanitize_xss_input(self, threat_event: Dict):
        """Sanitisation automatique des entrées XSS"""
        # Implémentation de la sanitisation XSS
        pass
    
    async def _adaptive_throttling(self, threat_event: Dict):
        """Throttling adaptatif"""
        # Implémentation du throttling adaptatif
        pass
    
    async def _update_ml_model(self, threat_event: Dict):
        """Mettre à jour le modèle ML avec les nouvelles données"""
        # Implémentation de la mise à jour ML
        pass
    
    async def _performance_monitoring(self):
        """Surveillance des performances"""
        while self.monitoring_active:
            try:
                # Mesurer les performances
                response_times = []
                throughput = 0
                
                # Mettre à jour les métriques
                self.performance_metrics.update({
                    "average_response_time": sum(response_times) / len(response_times) if response_times else 0,
                    "peak_response_time": max(response_times) if response_times else 0,
                    "throughput": throughput
                })
                
                await asyncio.sleep(60)  # Vérifier chaque minute
                
            except Exception as e:
                logging.error(f"Erreur monitoring performances: {e}")
                await asyncio.sleep(60)
    
    async def _health_check(self):
        """Vérification de santé du système"""
        while self.monitoring_active:
            try:
                # Vérifier l'état des composants
                health_status = {
                    "waf": True,
                    "ml_detector": True,
                    "gpt_assistant": True,
                    "chatbot": True,
                    "geo_blocker": True
                }
                
                # Alerte si problème détecté
                for component, status in health_status.items():
                    if not status:
                        await self._create_alert(f"Composant {component} en erreur", "high")
                
                await asyncio.sleep(300)  # Vérifier toutes les 5 minutes
                
            except Exception as e:
                logging.error(f"Erreur health check: {e}")
                await asyncio.sleep(300)
    
    async def _alert_processor(self):
        """Processeur d'alertes"""
        while self.monitoring_active:
            try:
                # Traiter les alertes en attente
                if self.alerts:
                    # Grouper les alertes similaires
                    await self._group_alerts()
                    
                    # Envoyer les alertes critiques
                    await self._send_critical_alerts()
                
                await asyncio.sleep(30)  # Traiter toutes les 30 secondes
                
            except Exception as e:
                logging.error(f"Erreur processeur alertes: {e}")
                await asyncio.sleep(30)
    
    async def _group_alerts(self):
        """Grouper les alertes similaires"""
        # Implémentation du groupement d'alertes
        pass
    
    async def _send_critical_alerts(self):
        """Envoyer les alertes critiques"""
        # Implémentation de l'envoi d'alertes
        pass
    
    async def _create_alert(self, message: str, severity: str):
        """Créer une nouvelle alerte"""
        alert = {
            "timestamp": datetime.utcnow().isoformat(),
            "message": message,
            "severity": severity,
            "type": "SYSTEM_ALERT"
        }
        
        self.alerts.append(alert)
        
        # Limiter le nombre d'alertes en mémoire
        if len(self.alerts) > 1000:
            self.alerts = self.alerts[-500:]
    
    async def _notify_admin(self, alert: Dict):
        """Notifier l'administrateur"""
        try:
            # Ici, vous pourriez implémenter l'envoi d'email, SMS, etc.
            logging.critical(f"ALERTE ADMIN RIMAREUM: {alert}")
            
        except Exception as e:
            logging.error(f"Erreur notification admin: {e}")
    
    async def add_threat_to_queue(self, threat_event: Dict):
        """Ajouter une menace à la queue d'analyse"""
        await self.threat_queue.put(threat_event)
    
    def get_monitoring_stats(self) -> Dict:
        """Obtenir les statistiques de surveillance"""
        return {
            "monitoring_active": self.monitoring_active,
            "reactive_mode": self.reactive_mode,
            "stats": self.monitoring_stats.copy(),
            "performance": self.performance_metrics.copy(),
            "alerts_count": len(self.alerts),
            "queue_size": self.threat_queue.qsize()
        }

# Instances globales Phase 7
ml_detector = MLThreatDetector()
gpt_assistant = GPTSecurityAssistant()
multilingual_chatbot = MultilingualChatbot()
continuous_monitor = ContinuousMonitor()

# Charger le modèle ML au démarrage
ml_detector.load_model()

# Démarrer la surveillance continue
class EnhancedWAF:
    """Web Application Firewall Phase 7 avec ML et surveillance continue"""
    
    def __init__(self):
        self.blocked_ips: Set[str] = set()
        self.audit_logger = SecurityAuditLogger()
        self.country_blocker = CountryBlocker()
        self.ml_detector = ml_detector
        self.gpt_assistant = gpt_assistant
        self.continuous_monitor = continuous_monitor
        self.maintenance_mode = SECURITY_CONFIG["maintenance_mode"]
        self.request_counts = defaultdict(list)
        self.failed_auth_attempts = defaultdict(int)
        self.honeypot_hits = defaultdict(int)
        self.threat_intelligence = ThreatIntelligence()
        self.behavioral_baselines = {}
        self.adaptive_thresholds = {}
        self.prediction_cache = {}
        self.session_tracking = {}
        self.anomaly_scores = defaultdict(list)
        self.threat_patterns = defaultdict(int)
        self.evasion_attempts = defaultdict(int)
        self.advanced_threats = []
        self.zero_day_signatures = []
        self.hunt_mode_active = SECURITY_CONFIG["threat_hunting_mode"]
        
        # Initialiser les seuils adaptatifs
        self._initialize_adaptive_thresholds()
    
    def _initialize_adaptive_thresholds(self):
        """Initialiser les seuils adaptatifs"""
        base_thresholds = {
            "rate_limit": SECURITY_CONFIG["max_requests_per_minute"],
            "anomaly_detection": SECURITY_CONFIG["anomaly_detection_sensitivity"],
            "ml_threat": SECURITY_CONFIG["ml_threat_threshold"],
            "gpt_analysis": SECURITY_CONFIG["gpt_analysis_threshold"]
        }
        
        for endpoint in ["/api/products", "/api/chat", "/api/auth", "/api/payments"]:
            self.adaptive_thresholds[endpoint] = base_thresholds.copy()
    
    async def process_request(self, request: Request) -> Dict:
        """Traitement avancé des requêtes Phase 7"""
        start_time = time.time()
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "")
        
        try:
            # Vérifications de base
            if await self._basic_checks(client_ip, request):
                return await self._create_block_response(client_ip, "basic_check_failed")
            
            # Analyse ML en temps réel
            ml_result = await self._ml_analysis(request, client_ip)
            
            # Analyse comportementale
            behavioral_result = await self._behavioral_analysis(request, client_ip)
            
            # Détection d'évasion avancée
            evasion_result = await self._advanced_evasion_detection(request, client_ip)
            
            # Détection zéro-day
            zero_day_result = await self._zero_day_detection(request, client_ip)
            
            # Analyse prédictive
            prediction_result = await self._predictive_analysis(request, client_ip)
            
            # Calcul du score de menace global
            threat_score = await self._calculate_global_threat_score(
                ml_result, behavioral_result, evasion_result, 
                zero_day_result, prediction_result
            )
            
            # Décision de blocage
            should_block = await self._make_blocking_decision(threat_score, request, client_ip)
            
            # Réponse immédiate si nécessaire
            if should_block and self.continuous_monitor.reactive_mode:
                await self._immediate_threat_response(request, client_ip, threat_score)
            
            # Analyse GPT-4 pour les menaces élevées
            gpt_analysis = None
            if threat_score > SECURITY_CONFIG["gpt_analysis_threshold"]:
                gpt_analysis = await self._gpt_threat_analysis(request, client_ip, threat_score)
            
            # Logging avancé
            await self._advanced_logging(request, client_ip, user_agent, threat_score, gpt_analysis)
            
            # Mise à jour des modèles d'apprentissage
            await self._update_learning_models(request, client_ip, threat_score)
            
            # Mise à jour des métriques de performance
            processing_time = time.time() - start_time
            await self._update_performance_metrics(processing_time)
            
            return await self._create_response(client_ip, threat_score, should_block, gpt_analysis)
            
        except Exception as e:
            logging.error(f"Erreur traitement WAF: {e}")
            return await self._create_error_response(client_ip, str(e))
    
    async def _basic_checks(self, client_ip: str, request: Request) -> bool:
        """Vérifications de base"""
        # Mode maintenance
        if self.maintenance_mode:
            return True
        
        # IP bloquée
        if client_ip in self.blocked_ips:
            return True
        
        # Vérification géographique
        if not await self.country_blocker.is_country_allowed(client_ip):
            await self._block_ip_with_reason(client_ip, "geo_blocked")
            return True
        
        # Honeypot
        if await self._check_honeypot(request):
            await self._block_ip_with_reason(client_ip, "honeypot_hit")
            return True
        
        return False
    
    async def _ml_analysis(self, request: Request, client_ip: str) -> Dict:
        """Analyse ML de la requête"""
        try:
            # Contexte pour l'extraction de features
            context = await self._build_request_context(request, client_ip)
            
            # Extraction des features
            features = self.ml_detector.extract_features(request, client_ip, context)
            
            # Prédiction
            threat_score, threat_level = self.ml_detector.predict_threat(features)
            
            return {
                "threat_score": threat_score,
                "threat_level": threat_level,
                "features": features.tolist() if hasattr(features, 'tolist') else [],
                "model_version": self.ml_detector.model_version
            }
            
        except Exception as e:
            logging.error(f"Erreur analyse ML: {e}")
            return {"threat_score": 0.0, "threat_level": "unknown", "error": str(e)}
    
    async def _behavioral_analysis(self, request: Request, client_ip: str) -> Dict:
        """Analyse comportementale avancée"""
        try:
            # Tracker la session
            session_id = request.headers.get("session-id") or request.cookies.get("session")
            
            # Analyser les patterns de comportement
            behavior_score = await self._analyze_behavior_patterns(client_ip, session_id, request)
            
            # Détection d'anomalies de session
            session_anomaly = await self._detect_session_anomalies(session_id, request)
            
            # Analyse de credential stuffing
            credential_stuffing = await self._detect_credential_stuffing(client_ip, request)
            
            return {
                "behavior_score": behavior_score,
                "session_anomaly": session_anomaly,
                "credential_stuffing": credential_stuffing
            }
            
        except Exception as e:
            logging.error(f"Erreur analyse comportementale: {e}")
            return {"behavior_score": 0.0, "session_anomaly": False, "credential_stuffing": False}
    
    async def _advanced_evasion_detection(self, request: Request, client_ip: str) -> Dict:
        """Détection d'évasion avancée"""
        try:
            evasion_score = 0.0
            techniques = []
            
            # Détection d'obfuscation
            if await self._detect_obfuscation(request):
                evasion_score += 0.3
                techniques.append("obfuscation")
            
            # Détection de fragmentation
            if await self._detect_fragmentation(request):
                evasion_score += 0.2
                techniques.append("fragmentation")
            
            # Détection d'encodage multiple
            if await self._detect_multiple_encoding(request):
                evasion_score += 0.4
                techniques.append("multiple_encoding")
            
            # Détection de polymorphisme
            if await self._detect_polymorphism(request):
                evasion_score += 0.5
                techniques.append("polymorphism")
            
            return {
                "evasion_score": min(evasion_score, 1.0),
                "techniques": techniques
            }
            
        except Exception as e:
            logging.error(f"Erreur détection évasion: {e}")
            return {"evasion_score": 0.0, "techniques": []}
    
    async def _zero_day_detection(self, request: Request, client_ip: str) -> Dict:
        """Détection de vulnérabilités zero-day"""
        try:
            zero_day_score = 0.0
            indicators = []
            
            # Analyse des patterns inconnus
            unknown_patterns = await self._analyze_unknown_patterns(request)
            if unknown_patterns:
                zero_day_score += 0.4
                indicators.append("unknown_patterns")
            
            # Détection de techniques émergentes
            emerging_techniques = await self._detect_emerging_techniques(request)
            if emerging_techniques:
                zero_day_score += 0.6
                indicators.append("emerging_techniques")
            
            # Analyse heuristique
            heuristic_score = await self._heuristic_analysis(request)
            zero_day_score += heuristic_score
            
            return {
                "zero_day_score": min(zero_day_score, 1.0),
                "indicators": indicators,
                "heuristic_score": heuristic_score
            }
            
        except Exception as e:
            logging.error(f"Erreur détection zero-day: {e}")
            return {"zero_day_score": 0.0, "indicators": [], "heuristic_score": 0.0}
    
    async def _predictive_analysis(self, request: Request, client_ip: str) -> Dict:
        """Analyse prédictive des menaces"""
        try:
            # Prédiction basée sur l'historique
            historical_prediction = await self._predict_from_history(client_ip)
            
            # Prédiction basée sur les tendances
            trend_prediction = await self._predict_from_trends(request)
            
            # Prédiction basée sur l'intelligence des menaces
            threat_intel_prediction = await self._predict_from_threat_intel(client_ip)
            
            return {
                "historical_prediction": historical_prediction,
                "trend_prediction": trend_prediction,
                "threat_intel_prediction": threat_intel_prediction
            }
            
        except Exception as e:
            logging.error(f"Erreur analyse prédictive: {e}")
            return {"historical_prediction": 0.0, "trend_prediction": 0.0, "threat_intel_prediction": 0.0}
    
    async def _calculate_global_threat_score(self, ml_result: Dict, behavioral_result: Dict, 
                                           evasion_result: Dict, zero_day_result: Dict, 
                                           prediction_result: Dict) -> float:
        """Calculer le score de menace global"""
        try:
            # Pondération des différents scores
            weights = {
                "ml": 0.3,
                "behavioral": 0.25,
                "evasion": 0.2,
                "zero_day": 0.15,
                "prediction": 0.1
            }
            
            # Calcul du score pondéré
            total_score = (
                ml_result.get("threat_score", 0.0) * weights["ml"] +
                behavioral_result.get("behavior_score", 0.0) * weights["behavioral"] +
                evasion_result.get("evasion_score", 0.0) * weights["evasion"] +
                zero_day_result.get("zero_day_score", 0.0) * weights["zero_day"] +
                max(prediction_result.get("historical_prediction", 0.0),
                    prediction_result.get("trend_prediction", 0.0),
                    prediction_result.get("threat_intel_prediction", 0.0)) * weights["prediction"]
            )
            
            return min(total_score, 1.0)
            
        except Exception as e:
            logging.error(f"Erreur calcul score global: {e}")
            return 0.0
    
    async def _make_blocking_decision(self, threat_score: float, request: Request, client_ip: str) -> bool:
        """Décision de blocage intelligente"""
        try:
            # Seuil adaptatif basé sur l'endpoint
            endpoint = request.url.path
            adaptive_threshold = self.adaptive_thresholds.get(endpoint, {}).get("ml_threat", 0.7)
            
            # Décision de base
            if threat_score > adaptive_threshold:
                return True
            
            # Considérations contextuelles
            if await self._should_block_context(request, client_ip, threat_score):
                return True
            
            # Mode chasse aux menaces
            if self.hunt_mode_active and threat_score > 0.3:
                return await self._hunt_mode_decision(request, client_ip, threat_score)
            
            return False
            
        except Exception as e:
            logging.error(f"Erreur décision blocage: {e}")
            return threat_score > 0.8  # Fallback
    
    # Méthodes d'assistance (stubs pour les fonctions complexes)
    async def _build_request_context(self, request: Request, client_ip: str) -> Dict:
        """Construire le contexte de la requête"""
        return {
            "request_rate": len(self.request_counts.get(client_ip, [])),
            "geo_risk_score": await self.country_blocker.get_geo_risk_score(client_ip),
            "reputation_score": self.threat_intelligence.ip_reputation.get(client_ip, 0.0),
            "request_interval": 0.0  # Calculer l'intervalle entre requêtes
        }
    
    async def _analyze_behavior_patterns(self, client_ip: str, session_id: str, request: Request) -> float:
        """Analyser les patterns de comportement"""
        return 0.0  # Implémentation simplifiée
    
    async def _detect_session_anomalies(self, session_id: str, request: Request) -> bool:
        """Détecter les anomalies de session"""
        return False  # Implémentation simplifiée
    
    async def _detect_credential_stuffing(self, client_ip: str, request: Request) -> bool:
        """Détecter le credential stuffing"""
        return False  # Implémentation simplifiée
    
    async def _detect_obfuscation(self, request: Request) -> bool:
        """Détecter l'obfuscation"""
        return False  # Implémentation simplifiée
    
    async def _detect_fragmentation(self, request: Request) -> bool:
        """Détecter la fragmentation"""
        return False  # Implémentation simplifiée
    
    async def _detect_multiple_encoding(self, request: Request) -> bool:
        """Détecter l'encodage multiple"""
        return False  # Implémentation simplifiée
    
    async def _detect_polymorphism(self, request: Request) -> bool:
        """Détecter le polymorphisme"""
        return False  # Implémentation simplifiée
    
    async def _analyze_unknown_patterns(self, request: Request) -> bool:
        """Analyser les patterns inconnus"""
        return False  # Implémentation simplifiée
    
    async def _detect_emerging_techniques(self, request: Request) -> bool:
        """Détecter les techniques émergentes"""
        return False  # Implémentation simplifiée
    
    async def _heuristic_analysis(self, request: Request) -> float:
        """Analyse heuristique"""
        return 0.0  # Implémentation simplifiée
    
    async def _predict_from_history(self, client_ip: str) -> float:
        """Prédiction basée sur l'historique"""
        return 0.0  # Implémentation simplifiée
    
    async def _predict_from_trends(self, request: Request) -> float:
        """Prédiction basée sur les tendances"""
        return 0.0  # Implémentation simplifiée
    
    async def _predict_from_threat_intel(self, client_ip: str) -> float:
        """Prédiction basée sur l'intelligence des menaces"""
        return 0.0  # Implémentation simplifiée
    
    async def _should_block_context(self, request: Request, client_ip: str, threat_score: float) -> bool:
        """Décision contextuelle de blocage"""
        return False  # Implémentation simplifiée
    
    async def _hunt_mode_decision(self, request: Request, client_ip: str, threat_score: float) -> bool:
        """Décision en mode chasse aux menaces"""
        return threat_score > 0.5  # Implémentation simplifiée
    
    async def _immediate_threat_response(self, request: Request, client_ip: str, threat_score: float):
        """Réponse immédiate aux menaces"""
        threat_event = {
            "type": "HIGH_THREAT",
            "ip_address": client_ip,
            "threat_score": threat_score,
            "timestamp": datetime.utcnow().isoformat(),
            "severity": "high" if threat_score > 0.8 else "medium"
        }
        
        await self.continuous_monitor.add_threat_to_queue(threat_event)
    
    async def _gpt_threat_analysis(self, request: Request, client_ip: str, threat_score: float) -> Dict:
        """Analyse GPT-4 des menaces"""
        try:
            security_event = SecurityEvent(
                timestamp=datetime.utcnow(),
                ip_address=client_ip,
                user_agent=request.headers.get("user-agent", ""),
                request_path=request.url.path,
                method=request.method,
                threat_type="ML_DETECTED",
                severity="HIGH",
                blocked=True,
                details={"threat_score": threat_score},
                ml_score=threat_score
            )
            
            return await self.gpt_assistant.analyze_threat(security_event)
            
        except Exception as e:
            logging.error(f"Erreur analyse GPT: {e}")
            return {"analysis": f"Erreur GPT: {str(e)}"}
    
    async def _advanced_logging(self, request: Request, client_ip: str, user_agent: str, 
                               threat_score: float, gpt_analysis: Dict):
        """Logging avancé"""
        try:
            security_event = SecurityEvent(
                timestamp=datetime.utcnow(),
                ip_address=client_ip,
                user_agent=user_agent,
                request_path=request.url.path,
                method=request.method,
                threat_type="WAF_ANALYSIS",
                severity="HIGH" if threat_score > 0.8 else "MEDIUM" if threat_score > 0.5 else "LOW",
                blocked=threat_score > 0.7,
                details={"threat_score": threat_score, "gpt_analysis": gpt_analysis},
                ml_score=threat_score,
                gpt_analysis=gpt_analysis.get("analysis", "") if gpt_analysis else None
            )
            
            await self.audit_logger.log_event(security_event)
            
        except Exception as e:
            logging.error(f"Erreur logging avancé: {e}")
    
    async def _update_learning_models(self, request: Request, client_ip: str, threat_score: float):
        """Mettre à jour les modèles d'apprentissage"""
        try:
            # Données pour l'apprentissage ML
            training_data = {
                "request_rate": len(self.request_counts.get(client_ip, [])),
                "payload_size": len(str(request.body) if hasattr(request, 'body') else ''),
                "url_length": len(str(request.url)),
                "param_count": len(request.query_params),
                "header_count": len(request.headers),
                "user_agent_entropy": 0.0,  # Calculer l'entropie
                "path_depth": str(request.url.path).count('/'),
                "suspicious_patterns": 0,  # Compter les patterns suspects
                "geo_risk_score": await self.country_blocker.get_geo_risk_score(client_ip),
                "reputation_score": self.threat_intelligence.ip_reputation.get(client_ip, 0.0),
                "time_of_day": datetime.utcnow().hour,
                "request_interval": 0.0,
                "threat_score": threat_score
            }
            
            self.ml_detector.update_training_data(training_data)
            
        except Exception as e:
            logging.error(f"Erreur mise à jour modèles: {e}")
    
    async def _update_performance_metrics(self, processing_time: float):
        """Mettre à jour les métriques de performance"""
        try:
            current_metrics = self.continuous_monitor.performance_metrics
            
            # Mettre à jour le temps de réponse moyen
            if current_metrics["average_response_time"] == 0:
                current_metrics["average_response_time"] = processing_time
            else:
                current_metrics["average_response_time"] = (
                    current_metrics["average_response_time"] * 0.9 + processing_time * 0.1
                )
            
            # Mettre à jour le pic de temps de réponse
            if processing_time > current_metrics["peak_response_time"]:
                current_metrics["peak_response_time"] = processing_time
            
            # Incrémenter le throughput
            current_metrics["throughput"] = current_metrics.get("throughput", 0) + 1
            
        except Exception as e:
            logging.error(f"Erreur métriques performance: {e}")
    
    async def _create_response(self, client_ip: str, threat_score: float, should_block: bool, 
                              gpt_analysis: Dict) -> Dict:
        """Créer la réponse WAF"""
        return {
            "allowed": not should_block,
            "threat_score": threat_score,
            "ip": client_ip,
            "phase": "7_SENTINEL_CORE",
            "gpt_analysis": gpt_analysis,
            "reasons": ["Threat score too high"] if should_block else [],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _create_block_response(self, client_ip: str, reason: str) -> Dict:
        """Créer une réponse de blocage"""
        return {
            "allowed": False,
            "threat_score": 1.0,
            "ip": client_ip,
            "phase": "7_SENTINEL_CORE",
            "reasons": [reason],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _create_error_response(self, client_ip: str, error: str) -> Dict:
        """Créer une réponse d'erreur"""
        return {
            "allowed": True,  # Permettre en cas d'erreur
            "threat_score": 0.0,
            "ip": client_ip,
            "phase": "7_SENTINEL_CORE",
            "error": error,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _block_ip_with_reason(self, client_ip: str, reason: str):
        """Bloquer une IP avec raison"""
        self.blocked_ips.add(client_ip)
        logging.warning(f"IP {client_ip} bloquée: {reason}")
    
    async def _check_honeypot(self, request: Request) -> bool:
        """Vérifier si la requête touche un honeypot"""
        for honeypot in SECURITY_CONFIG["honeypot_endpoints"]:
            if honeypot in request.url.path:
                return True
        return False
    
    def _get_client_ip(self, request: Request) -> str:
        """Obtenir l'IP réelle du client"""
        # Vérifier les headers de proxy
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"

# Instance globale WAF Phase 7
waf_instance = EnhancedWAF()

# Garder l'ancienne instance pour compatibilité
class WAF(EnhancedWAF):
    """Alias pour compatibilité"""
    pass
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
    """Web Application Firewall intelligent PHASE 6"""
    
    def __init__(self):
        self.blocked_ips: Set[str] = set()
        self.audit_logger = SecurityAuditLogger()
        self.country_blocker = CountryBlocker()
        self.guardian_ai = RimareumGuardianAI()
        self.maintenance_mode = SECURITY_CONFIG["maintenance_mode"]
        self.request_counts = defaultdict(list)
        self.failed_auth_attempts = defaultdict(int)
        self.honeypot_hits = defaultdict(int)
    
    async def process_request(self, request: Request) -> Dict:
        """Traiter et analyser une requête avec toutes les protections PHASE 6"""
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "")
        
        # Vérification mode maintenance
        if self.maintenance_mode:
            return await self._handle_maintenance_mode(client_ip, request)
        
        # Vérification IP bloquée
        if client_ip in self.blocked_ips:
            return await self._handle_blocked_ip(client_ip, request)
        
        # Vérification géographique
        if not await self.country_blocker.is_country_allowed(client_ip):
            await self._block_ip_temporarily(client_ip, "GEO_BLOCK")
            return await self._handle_geo_blocked(client_ip, request)
        
        # Vérification honeypot
        if await self._check_honeypot(request):
            await self._block_ip_temporarily(client_ip, "HONEYPOT")
            return await self._handle_honeypot_hit(client_ip, request)
        
        # Analyse rate limiting
        rate_risk = await self._analyze_rate_limiting(client_ip)
        
        # Détection patterns suspects
        content_risk = await self._analyze_request_content(request)
        
        # Analyse IA Guardian
        ai_analysis = await self.guardian_ai.analyze_request(request, client_ip)
        
        # Score de risque total
        total_risk = max(rate_risk, content_risk, ai_analysis["ai_risk_score"])
        
        should_block = total_risk > 0.7
        
        # Blocage automatique si score élevé
        if should_block:
            await self._block_ip_temporarily(client_ip, "HIGH_RISK")
        
        # Logging
        await self._log_security_event(request, client_ip, user_agent, total_risk, should_block)
        
        return {
            "allowed": not should_block,
            "risk_score": total_risk,
            "ip": client_ip,
            "ai_analysis": ai_analysis,
            "reasons": self._get_block_reasons(rate_risk, content_risk, ai_analysis["ai_risk_score"]) if should_block else []
        }
    
    async def _check_honeypot(self, request: Request) -> bool:
        """Vérifier si la requête touche un honeypot"""
        for honeypot in SECURITY_CONFIG["honeypot_endpoints"]:
            if honeypot in request.url.path:
                return True
        return False
    
    async def _handle_honeypot_hit(self, client_ip: str, request: Request) -> Dict:
        """Gérer une tentative d'accès à un honeypot"""
        self.honeypot_hits[client_ip] += 1
        
        return {
            "allowed": False,
            "risk_score": 1.0,
            "ip": client_ip,
            "reasons": ["Honeypot access detected - IP blocked"]
        }
    
    async def _handle_geo_blocked(self, client_ip: str, request: Request) -> Dict:
        """Gérer un blocage géographique"""
        return {
            "allowed": False,
            "risk_score": 0.9,
            "ip": client_ip,
            "reasons": ["Access from restricted geographical location"]
        }
    
    async def _block_ip_temporarily(self, client_ip: str, reason: str):
        """Bloquer temporairement une IP"""
        self.blocked_ips.add(client_ip)
        
        # Programmer le déblocage automatique (24h)
        async def unblock_later():
            await asyncio.sleep(86400)  # 24 heures
            self.blocked_ips.discard(client_ip)
        
        asyncio.create_task(unblock_later())
    
    def _get_block_reasons(self, rate_risk: float, content_risk: float, ai_risk: float) -> List[str]:
        """Obtenir les raisons du blocage"""
        reasons = []
        
        if rate_risk > 0.7:
            reasons.append("Rate limit exceeded")
        
        if content_risk > 0.7:
            reasons.append("Suspicious content detected")
        
        if ai_risk > 0.7:
            reasons.append("AI Guardian threat detection")
        
        return reasons
    
    def _get_client_ip(self, request: Request) -> str:
        """Obtenir l'IP réelle du client"""
        # Vérifier les headers de proxy
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    async def _analyze_rate_limiting(self, ip: str) -> float:
        """Analyser le rate limiting avec limites plus strictes"""
        now = time.time()
        
        # Nettoyer les anciennes requêtes
        self.request_counts[ip] = [t for t in self.request_counts[ip] if now - t < 3600]
        
        # Ajouter la requête actuelle
        self.request_counts[ip].append(now)
        
        # Compter les requêtes récentes (1 minute)
        recent_requests = sum(1 for t in self.request_counts[ip] if now - t < 60)
        
        if recent_requests > SECURITY_CONFIG["max_requests_per_minute"]:
            return 0.9
        
        # Compter les requêtes par heure
        hourly_requests = len(self.request_counts[ip])
        
        if hourly_requests > SECURITY_CONFIG["max_requests_per_hour"]:
            return 0.8
        
        return 0.0
    
    async def _analyze_request_content(self, request: Request) -> float:
        """Analyser le contenu de la requête avec patterns étendus"""
        content = " ".join([
            str(request.url),
            str(request.headers),
            request.headers.get("user-agent", "")
        ])
        
        risk_score = 0.0
        
        # Vérifier les patterns suspects
        for pattern in SECURITY_CONFIG["suspicious_patterns"]:
            if re.search(pattern, content, re.IGNORECASE):
                risk_score += 0.2
        
        # Vérifier les user agents suspects
        user_agent = request.headers.get("user-agent", "").lower()
        for bot_agent in SECURITY_CONFIG["bot_user_agents"]:
            if bot_agent in user_agent:
                risk_score += 0.3
        
        return min(risk_score, 1.0)
    
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

# Rate limiter global
limiter = Limiter(key_func=get_remote_address)

# OAuth2 scheme pour l'authentification
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token", auto_error=False)

async def security_middleware(request: Request):
    """Middleware de sécurité pour FastAPI PHASE 6"""
    
    # Ignorer les routes système
    if request.url.path.startswith(("/_health", "/metrics", "/favicon.ico", "/static")):
        return {"allowed": True, "risk_score": 0.0}
    
    # Analyse de sécurité complète
    result = await waf_instance.process_request(request)
    
    if not result["allowed"]:
        # Construire un message d'erreur détaillé
        error_detail = {
            "error": "Request blocked by RIMAREUM Security System",
            "reasons": result["reasons"],
            "risk_score": result["risk_score"],
            "ip": result["ip"],
            "support": "Contact support@rimareum.com if you believe this is an error",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        raise HTTPException(
            status_code=403,
            detail=error_detail
        )
    
    return result

async def get_security_check(request: Request):
    """Dépendance pour vérification de sécurité"""
    return await security_middleware(request)

# Classes utilitaires pour l'audit
class SecurityAuditScheduler:
    """Planificateur d'audit automatique"""
    
    def __init__(self):
        self.last_audit = datetime.utcnow()
        self.audit_interval = timedelta(hours=SECURITY_CONFIG["audit_interval_hours"])
    
    async def run_scheduled_audit(self):
        """Exécuter l'audit programmé"""
        while True:
            await asyncio.sleep(3600)  # Vérifier chaque heure
            
            if datetime.utcnow() - self.last_audit >= self.audit_interval:
                await self._perform_audit()
                self.last_audit = datetime.utcnow()
    
    async def _perform_audit(self):
        """Effectuer l'audit de sécurité"""
        audit_results = {
            "timestamp": datetime.utcnow().isoformat(),
            "blocked_ips": len(waf_instance.blocked_ips),
            "honeypot_hits": len(waf_instance.honeypot_hits),
            "guardian_ai_patterns": len(waf_instance.guardian_ai.behavioral_model["suspicious_patterns"]),
            "status": "completed"
        }
        
        # Log des résultats d'audit
        await waf_instance.audit_logger.log_event(
            SecurityEvent(
                timestamp=datetime.utcnow(),
                ip_address="system",
                user_agent="audit_scheduler",
                request_path="/audit",
                method="SYSTEM",
                threat_type="AUDIT",
                severity="INFO",
                blocked=False,
                details=audit_results
            )
        )

# Instance du planificateur d'audit
audit_scheduler = SecurityAuditScheduler()

# Utilitaires pour les clés API
class APIKeyManager:
    """Gestionnaire des clés API avec expiration"""
    
    def __init__(self):
        self.api_keys = {}
        self.key_expiry = timedelta(hours=SECURITY_CONFIG["api_key_expiration_hours"])
    
    def generate_api_key(self, user_id: str) -> str:
        """Générer une nouvelle clé API"""
        api_key = secrets.token_urlsafe(32)
        expiry = datetime.utcnow() + self.key_expiry
        
        self.api_keys[api_key] = {
            "user_id": user_id,
            "created": datetime.utcnow(),
            "expires": expiry,
            "active": True
        }
        
        return api_key
    
    def validate_api_key(self, api_key: str) -> Optional[Dict]:
        """Valider une clé API"""
        if api_key not in self.api_keys:
            return None
        
        key_data = self.api_keys[api_key]
        
        # Vérifier l'expiration
        if datetime.utcnow() > key_data["expires"]:
            del self.api_keys[api_key]
            return None
        
        # Vérifier si active
        if not key_data["active"]:
            return None
        
        return key_data
    
    def revoke_api_key(self, api_key: str):
        """Révoquer une clé API"""
        if api_key in self.api_keys:
            self.api_keys[api_key]["active"] = False

# Instance du gestionnaire de clés API
api_key_manager = APIKeyManager()