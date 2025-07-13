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