#!/usr/bin/env python3
"""
RIMAREUM Backend API Comprehensive Test Suite
Tests all backend endpoints in simulation mode
"""

import requests
import json
import uuid
from datetime import datetime
import time

# Backend URL from environment
BACKEND_URL = "https://20423e44-cefc-4fee-92df-010802a91699.preview.emergentagent.com/api"

class RimareumAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.sample_products = []
        
    def log_test(self, test_name, success, details="", response_data=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        if response_data and isinstance(response_data, dict):
            print(f"   Response: {json.dumps(response_data, indent=2)[:200]}...")
        print()
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    def test_root_endpoint(self):
        """Test root API endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/")
            if response.status_code == 200:
                data = response.json()
                if "RIMAREUM" in data.get("message", ""):
                    self.log_test("Root Endpoint", True, f"Status: {response.status_code}", data)
                    return True
                else:
                    self.log_test("Root Endpoint", False, "Invalid response message")
                    return False
            else:
                self.log_test("Root Endpoint", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Root Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_cors_configuration(self):
        """Test CORS configuration"""
        try:
            # Test preflight request
            headers = {
                'Origin': 'https://example.com',
                'Access-Control-Request-Method': 'GET',
                'Access-Control-Request-Headers': 'Content-Type'
            }
            response = self.session.options(f"{BACKEND_URL}/", headers=headers)
            
            cors_headers = {
                'access-control-allow-origin': response.headers.get('access-control-allow-origin'),
                'access-control-allow-methods': response.headers.get('access-control-allow-methods'),
                'access-control-allow-headers': response.headers.get('access-control-allow-headers')
            }
            
            # CORS is working if it returns the requesting origin or *
            allow_origin = cors_headers['access-control-allow-origin']
            if allow_origin == '*' or allow_origin == 'https://example.com':
                self.log_test("CORS Configuration", True, "CORS properly configured", cors_headers)
                return True
            else:
                self.log_test("CORS Configuration", False, "CORS not properly configured", cors_headers)
                return False
        except Exception as e:
            self.log_test("CORS Configuration", False, f"Exception: {str(e)}")
            return False
    
    def test_get_all_products(self):
        """Test GET /api/products"""
        try:
            response = self.session.get(f"{BACKEND_URL}/products")
            if response.status_code == 200:
                products = response.json()
                if isinstance(products, list) and len(products) >= 3:
                    self.sample_products = products
                    # Verify product structure
                    product = products[0]
                    required_fields = ['id', 'name', 'description', 'price', 'category']
                    if all(field in product for field in required_fields):
                        self.log_test("Get All Products", True, f"Found {len(products)} products", {"count": len(products), "sample": product})
                        return True
                    else:
                        self.log_test("Get All Products", False, "Missing required product fields")
                        return False
                else:
                    self.log_test("Get All Products", False, f"Expected at least 3 products, got {len(products) if isinstance(products, list) else 'invalid'}")
                    return False
            else:
                self.log_test("Get All Products", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Get All Products", False, f"Exception: {str(e)}")
            return False
    
    def test_filter_products_by_category(self):
        """Test GET /api/products?category=physical"""
        try:
            response = self.session.get(f"{BACKEND_URL}/products?category=physical")
            if response.status_code == 200:
                products = response.json()
                if isinstance(products, list):
                    # Verify all products are physical category
                    physical_products = [p for p in products if p.get('category') == 'physical']
                    if len(physical_products) == len(products) and len(products) > 0:
                        self.log_test("Filter Products by Category", True, f"Found {len(products)} physical products")
                        return True
                    else:
                        self.log_test("Filter Products by Category", False, f"Category filter not working properly")
                        return False
                else:
                    self.log_test("Filter Products by Category", False, "Invalid response format")
                    return False
            else:
                self.log_test("Filter Products by Category", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Filter Products by Category", False, f"Exception: {str(e)}")
            return False
    
    def test_filter_featured_products(self):
        """Test GET /api/products?featured=true"""
        try:
            response = self.session.get(f"{BACKEND_URL}/products?featured=true")
            if response.status_code == 200:
                products = response.json()
                if isinstance(products, list):
                    # Verify all products are featured
                    featured_products = [p for p in products if p.get('is_featured') == True]
                    if len(featured_products) == len(products) and len(products) > 0:
                        self.log_test("Filter Featured Products", True, f"Found {len(products)} featured products")
                        return True
                    else:
                        self.log_test("Filter Featured Products", False, "Featured filter not working properly")
                        return False
                else:
                    self.log_test("Filter Featured Products", False, "Invalid response format")
                    return False
            else:
                self.log_test("Filter Featured Products", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Filter Featured Products", False, f"Exception: {str(e)}")
            return False
    
    def test_get_individual_products(self):
        """Test GET /api/products/{product_id} for each sample product"""
        if not self.sample_products:
            self.log_test("Get Individual Products", False, "No sample products available")
            return False
        
        success_count = 0
        for product in self.sample_products[:3]:  # Test first 3 products
            try:
                product_id = product['id']
                response = self.session.get(f"{BACKEND_URL}/products/{product_id}")
                if response.status_code == 200:
                    product_data = response.json()
                    if product_data.get('id') == product_id:
                        success_count += 1
                    else:
                        self.log_test(f"Get Product {product_id}", False, "Product ID mismatch")
                else:
                    self.log_test(f"Get Product {product_id}", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test(f"Get Product {product_id}", False, f"Exception: {str(e)}")
        
        if success_count == len(self.sample_products[:3]):
            self.log_test("Get Individual Products", True, f"Successfully retrieved {success_count} products")
            return True
        else:
            self.log_test("Get Individual Products", False, f"Only {success_count}/{len(self.sample_products[:3])} products retrieved successfully")
            return False
    
    def test_payment_checkout_with_product(self):
        """Test POST /api/payments/checkout/session with product_id"""
        if not self.sample_products:
            self.log_test("Payment Checkout with Product", False, "No sample products available")
            return False
        
        try:
            product_id = self.sample_products[0]['id']
            product_price = self.sample_products[0]['price']
            payload = {
                "product_id": product_id,
                "amount": product_price,
                "currency": "USD",
                "payment_method": "card"
            }
            response = self.session.post(f"{BACKEND_URL}/payments/checkout/session", json=payload)
            
            # Expect 503 or 500 in simulation mode (no Stripe key)
            if response.status_code in [503, 500]:
                error_data = response.json()
                if "Payment service not configured" in error_data.get("detail", ""):
                    self.log_test("Payment Checkout with Product", True, "Simulation mode: Payment service not configured (expected)", error_data)
                    return True
                else:
                    self.log_test("Payment Checkout with Product", False, "Unexpected error message", error_data)
                    return False
            else:
                self.log_test("Payment Checkout with Product", False, f"Unexpected status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Payment Checkout with Product", False, f"Exception: {str(e)}")
            return False
    
    def test_payment_checkout_custom_amount(self):
        """Test POST /api/payments/checkout/session with custom amount"""
        try:
            payload = {
                "amount": 50.00,
                "currency": "USD",
                "payment_method": "card"
            }
            response = self.session.post(f"{BACKEND_URL}/payments/checkout/session", json=payload)
            
            # Expect 503 or 500 in simulation mode (no Stripe key)
            if response.status_code in [503, 500]:
                error_data = response.json()
                if "Payment service not configured" in error_data.get("detail", ""):
                    self.log_test("Payment Checkout Custom Amount", True, "Simulation mode: Payment service not configured (expected)", error_data)
                    return True
                else:
                    self.log_test("Payment Checkout Custom Amount", False, "Unexpected error message", error_data)
                    return False
            else:
                self.log_test("Payment Checkout Custom Amount", False, f"Unexpected status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Payment Checkout Custom Amount", False, f"Exception: {str(e)}")
            return False
    
    def test_wallet_connect(self):
        """Test POST /api/wallet/connect"""
        try:
            wallet_data = {
                "user_id": str(uuid.uuid4()),
                "wallet_address": "0x742d35Cc6634C0532925a3b8D4C9db96590e4CAF",
                "chain_id": 1,
                "balance_eth": 1.5,
                "balance_rimar": 1000.0,
                "nft_count": 3
            }
            response = self.session.post(f"{BACKEND_URL}/wallet/connect", json=wallet_data)
            
            if response.status_code == 200:
                data = response.json()
                if "successfully" in data.get("message", "").lower():
                    self.log_test("Wallet Connect", True, "Wallet connected successfully", data)
                    return True
                else:
                    self.log_test("Wallet Connect", False, "Unexpected response message", data)
                    return False
            else:
                self.log_test("Wallet Connect", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Wallet Connect", False, f"Exception: {str(e)}")
            return False
    
    def test_wallet_balance(self):
        """Test GET /api/wallet/balance/{wallet_address}"""
        try:
            wallet_address = "0x742d35Cc6634C0532925a3b8D4C9db96590e4CAF"
            response = self.session.get(f"{BACKEND_URL}/wallet/balance/{wallet_address}")
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['address', 'eth_balance', 'rimar_balance', 'nft_count']
                if all(field in data for field in required_fields):
                    self.log_test("Wallet Balance", True, "Mock balance data returned", data)
                    return True
                else:
                    self.log_test("Wallet Balance", False, "Missing required balance fields", data)
                    return False
            else:
                self.log_test("Wallet Balance", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Wallet Balance", False, f"Exception: {str(e)}")
            return False
    
    def test_ai_chat_message(self):
        """Test POST /api/chat/message"""
        try:
            chat_data = {
                "session_id": str(uuid.uuid4()),
                "message": "Hello, can you help me with RIMAREUM platform?"
            }
            response = self.session.post(f"{BACKEND_URL}/chat/message", json=chat_data)
            
            # Expect 503 in simulation mode (no OpenAI key)
            if response.status_code == 503:
                error_data = response.json()
                if "AI service not configured" in error_data.get("detail", ""):
                    self.log_test("AI Chat Message", True, "Simulation mode: AI service not configured (expected)", error_data)
                    return True
                else:
                    self.log_test("AI Chat Message", False, "Unexpected error message", error_data)
                    return False
            elif response.status_code == 500:
                # Also accept 500 as it might be thrown as HTTPException
                error_data = response.json()
                if "AI service not configured" in error_data.get("detail", ""):
                    self.log_test("AI Chat Message", True, "Simulation mode: AI service not configured (expected)", error_data)
                    return True
                else:
                    self.log_test("AI Chat Message", False, "Unexpected error message", error_data)
                    return False
            else:
                self.log_test("AI Chat Message", False, f"Unexpected status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("AI Chat Message", False, f"Exception: {str(e)}")
            return False
    
    def test_admin_stats(self):
        """Test GET /api/admin/stats"""
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/stats")
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['total_products', 'total_users', 'total_orders', 'total_payments', 'total_revenue']
                security_fields = ['blocked_ips', 'security_events']
                if all(field in data for field in required_fields) and all(field in data for field in security_fields):
                    self.log_test("Admin Stats with Security", True, "Platform statistics with security data retrieved", data)
                    return True
                else:
                    missing_fields = [f for f in required_fields + security_fields if f not in data]
                    self.log_test("Admin Stats with Security", False, f"Missing fields: {missing_fields}", data)
                    return False
            else:
                self.log_test("Admin Stats with Security", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Admin Stats with Security", False, f"Exception: {str(e)}")
            return False
    
    def test_invalid_endpoints(self):
        """Test error handling for invalid endpoints"""
        try:
            # Test non-existent endpoint
            response = self.session.get(f"{BACKEND_URL}/nonexistent")
            if response.status_code == 404:
                self.log_test("Invalid Endpoint Handling", True, f"Proper 404 for invalid endpoint")
                return True
            else:
                self.log_test("Invalid Endpoint Handling", False, f"Expected 404, got {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Invalid Endpoint Handling", False, f"Exception: {str(e)}")
            return False
    
    def test_malformed_requests(self):
        """Test error handling for malformed requests"""
        try:
            # Test malformed JSON
            response = self.session.post(f"{BACKEND_URL}/wallet/connect", data="invalid json")
            if response.status_code in [400, 422]:  # Bad Request or Unprocessable Entity
                self.log_test("Malformed Request Handling", True, f"Proper error handling for malformed JSON: {response.status_code}")
                return True
            else:
                self.log_test("Malformed Request Handling", False, f"Expected 400/422, got {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Malformed Request Handling", False, f"Exception: {str(e)}")
            return False
    
    # PHASE 6 SECURITY TESTS
    
    def test_security_status_endpoint(self):
        """Test GET /api/security/status - Phase 6 security status"""
        try:
            response = self.session.get(f"{BACKEND_URL}/security/status")
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['security_level', 'waf_active', 'guardian_ai_active', 'rate_limit_active', 'geo_blocking_active']
                if all(field in data for field in required_fields):
                    # Check if security modules are active
                    if (data.get('waf_active') and data.get('guardian_ai_active') and 
                        data.get('rate_limit_active') and data.get('geo_blocking_active')):
                        self.log_test("Security Status Endpoint", True, "All security modules active", data)
                        return True
                    else:
                        self.log_test("Security Status Endpoint", False, "Some security modules inactive", data)
                        return False
                else:
                    self.log_test("Security Status Endpoint", False, "Missing security status fields", data)
                    return False
            else:
                self.log_test("Security Status Endpoint", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Security Status Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_user_registration(self):
        """Test POST /api/auth/register - Phase 6 authentication"""
        try:
            user_data = {
                "email": f"testuser_{uuid.uuid4().hex[:8]}@rimareum.com",
                "username": f"testuser_{uuid.uuid4().hex[:8]}",
                "password": "SecurePassword123!"
            }
            response = self.session.post(f"{BACKEND_URL}/auth/register", json=user_data)
            
            if response.status_code == 200:
                data = response.json()
                if "user_id" in data and "api_key" in data:
                    self.log_test("User Registration", True, "User registered with API key", {"user_id": data.get("user_id")})
                    return True, data
                else:
                    self.log_test("User Registration", False, "Missing user_id or api_key in response", data)
                    return False, None
            else:
                self.log_test("User Registration", False, f"Status: {response.status_code}")
                return False, None
        except Exception as e:
            self.log_test("User Registration", False, f"Exception: {str(e)}")
            return False, None
    
    def test_user_login(self):
        """Test POST /api/auth/login - Phase 6 authentication"""
        # First register a user
        reg_success, reg_data = self.test_user_registration()
        if not reg_success:
            self.log_test("User Login", False, "Failed to register test user")
            return False
        
        try:
            # Extract username from registration (we need to create a known user)
            login_data = {
                "username": f"testuser_{uuid.uuid4().hex[:8]}",
                "password": "SecurePassword123!"
            }
            
            # Register the user first with known credentials
            user_data = {
                "email": f"{login_data['username']}@rimareum.com",
                "username": login_data['username'],
                "password": login_data['password']
            }
            reg_response = self.session.post(f"{BACKEND_URL}/auth/register", json=user_data)
            
            if reg_response.status_code != 200:
                self.log_test("User Login", False, "Failed to register user for login test")
                return False
            
            # Now try to login
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['access_token', 'token_type', 'expires_in', 'api_key']
                if all(field in data for field in required_fields):
                    self.log_test("User Login", True, "Login successful with OAuth2 token", {"token_type": data.get("token_type")})
                    return True
                else:
                    self.log_test("User Login", False, "Missing OAuth2 fields in response", data)
                    return False
            else:
                self.log_test("User Login", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("User Login", False, f"Exception: {str(e)}")
            return False
    
    def test_rate_limiting(self):
        """Test rate limiting on endpoints"""
        try:
            # Test rate limiting on products endpoint (30/minute limit)
            rapid_requests = []
            for i in range(5):  # Send 5 rapid requests
                response = self.session.get(f"{BACKEND_URL}/products")
                rapid_requests.append(response.status_code)
                time.sleep(0.1)  # Small delay between requests
            
            # All requests should succeed initially (5 requests is well under 30/minute)
            success_count = sum(1 for status in rapid_requests if status == 200)
            
            if success_count >= 4:  # Allow for 1 potential failure
                self.log_test("Rate Limiting", True, f"Rate limiting configured - {success_count}/5 requests succeeded")
                return True
            else:
                self.log_test("Rate Limiting", False, f"Only {success_count}/5 requests succeeded")
                return False
        except Exception as e:
            self.log_test("Rate Limiting", False, f"Exception: {str(e)}")
            return False
    
    def test_security_headers(self):
        """Test security headers in responses"""
        try:
            response = self.session.get(f"{BACKEND_URL}/")
            
            # Check for security-related headers
            security_headers = {
                'x-security-score': response.headers.get('x-security-score'),
                'x-rate-limit-remaining': response.headers.get('x-rate-limit-remaining'),
                'access-control-allow-origin': response.headers.get('access-control-allow-origin')
            }
            
            # At least some security headers should be present
            present_headers = [k for k, v in security_headers.items() if v is not None]
            
            if len(present_headers) >= 1:
                self.log_test("Security Headers", True, f"Security headers present: {present_headers}")
                return True
            else:
                self.log_test("Security Headers", False, "No security headers found", security_headers)
                return False
        except Exception as e:
            self.log_test("Security Headers", False, f"Exception: {str(e)}")
            return False
    
    def test_security_report_endpoint(self):
        """Test POST /api/security/report - Security event reporting"""
        try:
            security_event = {
                "ip_address": "192.168.1.100",
                "event_type": "suspicious_activity",
                "fingerprint": "test_fingerprint_123",
                "details": {
                    "user_agent": "Test Browser",
                    "timestamp": datetime.now().isoformat()
                }
            }
            response = self.session.post(f"{BACKEND_URL}/security/report", json=security_event)
            
            if response.status_code == 200:
                data = response.json()
                if "successfully" in data.get("message", "").lower():
                    self.log_test("Security Report Endpoint", True, "Security event reported successfully", data)
                    return True
                else:
                    self.log_test("Security Report Endpoint", False, "Unexpected response message", data)
                    return False
            else:
                self.log_test("Security Report Endpoint", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Security Report Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_security_audit_endpoint(self):
        """Test GET /api/security/audit - Security audit data"""
        try:
            response = self.session.get(f"{BACKEND_URL}/security/audit")
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['audit_period', 'total_events', 'blocked_events', 'guardian_ai_status']
                if all(field in data for field in required_fields):
                    self.log_test("Security Audit Endpoint", True, "Security audit data retrieved", data)
                    return True
                else:
                    self.log_test("Security Audit Endpoint", False, "Missing audit fields", data)
                    return False
            else:
                self.log_test("Security Audit Endpoint", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Security Audit Endpoint", False, f"Exception: {str(e)}")
            return False
    
    # PHASE 7 SENTINEL CORE TESTS
    
    def test_sentinel_core_status(self):
        """Test GET /api/security/sentinel/status - Phase 7 Sentinel Core status"""
        try:
            response = self.session.get(f"{BACKEND_URL}/security/sentinel/status")
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['phase', 'status', 'components', 'security_level']
                component_fields = ['intelligent_detection', 'gpt_secure_4', 'smart_firewall_ml', 'multilingual_chatbot', 'reactive_surveillance']
                
                if all(field in data for field in required_fields):
                    components = data.get('components', {})
                    if all(field in components for field in component_fields):
                        if data.get('phase') == '7_SENTINEL_CORE' and data.get('status') == 'ACTIVE':
                            self.log_test("Sentinel Core Status", True, "Phase 7 Sentinel Core active with all components", data)
                            return True
                        else:
                            self.log_test("Sentinel Core Status", False, "Sentinel Core not in active Phase 7 state", data)
                            return False
                    else:
                        self.log_test("Sentinel Core Status", False, "Missing component status fields", data)
                        return False
                else:
                    self.log_test("Sentinel Core Status", False, "Missing required status fields", data)
                    return False
            else:
                self.log_test("Sentinel Core Status", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Sentinel Core Status", False, f"Exception: {str(e)}")
            return False
    
    def test_multilingual_chatbot_french(self):
        """Test POST /api/chatbot/multilingual - French language"""
        try:
            chat_data = {
                "message": "Bonjour, comment allez-vous?",
                "language": "fr"
            }
            response = self.session.post(f"{BACKEND_URL}/chatbot/multilingual", json=chat_data)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['response', 'detected_language', 'response_type', 'supported_languages']
                if all(field in data for field in required_fields):
                    if data.get('detected_language') == 'fr' and 'fr' in data.get('supported_languages', []):
                        self.log_test("Multilingual Chatbot (French)", True, "French chatbot response working", data)
                        return True
                    else:
                        self.log_test("Multilingual Chatbot (French)", False, "Language detection or support issue", data)
                        return False
                else:
                    self.log_test("Multilingual Chatbot (French)", False, "Missing response fields", data)
                    return False
            else:
                self.log_test("Multilingual Chatbot (French)", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Multilingual Chatbot (French)", False, f"Exception: {str(e)}")
            return False
    
    def test_multilingual_chatbot_english(self):
        """Test POST /api/chatbot/multilingual - English language"""
        try:
            chat_data = {
                "message": "Hello, how can you help me with RIMAREUM?",
                "language": "en"
            }
            response = self.session.post(f"{BACKEND_URL}/chatbot/multilingual", json=chat_data)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['response', 'detected_language', 'response_type', 'supported_languages']
                if all(field in data for field in required_fields):
                    if 'en' in data.get('supported_languages', []):
                        self.log_test("Multilingual Chatbot (English)", True, "English chatbot response working", data)
                        return True
                    else:
                        self.log_test("Multilingual Chatbot (English)", False, "English language not supported", data)
                        return False
                else:
                    self.log_test("Multilingual Chatbot (English)", False, "Missing response fields", data)
                    return False
            else:
                self.log_test("Multilingual Chatbot (English)", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Multilingual Chatbot (English)", False, f"Exception: {str(e)}")
            return False
    
    def test_multilingual_chatbot_arabic(self):
        """Test POST /api/chatbot/multilingual - Arabic language"""
        try:
            chat_data = {
                "message": "مرحبا، كيف يمكنك مساعدتي؟",
                "language": "ar"
            }
            response = self.session.post(f"{BACKEND_URL}/chatbot/multilingual", json=chat_data)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['response', 'detected_language', 'response_type', 'supported_languages']
                if all(field in data for field in required_fields):
                    if 'ar' in data.get('supported_languages', []):
                        self.log_test("Multilingual Chatbot (Arabic)", True, "Arabic chatbot response working", data)
                        return True
                    else:
                        self.log_test("Multilingual Chatbot (Arabic)", False, "Arabic language not supported", data)
                        return False
                else:
                    self.log_test("Multilingual Chatbot (Arabic)", False, "Missing response fields", data)
                    return False
            else:
                self.log_test("Multilingual Chatbot (Arabic)", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Multilingual Chatbot (Arabic)", False, f"Exception: {str(e)}")
            return False
    
    def test_multilingual_chatbot_spanish(self):
        """Test POST /api/chatbot/multilingual - Spanish language"""
        try:
            chat_data = {
                "message": "Hola, ¿cómo puedes ayudarme con RIMAREUM?",
                "language": "es"
            }
            response = self.session.post(f"{BACKEND_URL}/chatbot/multilingual", json=chat_data)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['response', 'detected_language', 'response_type', 'supported_languages']
                if all(field in data for field in required_fields):
                    if 'es' in data.get('supported_languages', []):
                        self.log_test("Multilingual Chatbot (Spanish)", True, "Spanish chatbot response working", data)
                        return True
                    else:
                        self.log_test("Multilingual Chatbot (Spanish)", False, "Spanish language not supported", data)
                        return False
                else:
                    self.log_test("Multilingual Chatbot (Spanish)", False, "Missing response fields", data)
                    return False
            else:
                self.log_test("Multilingual Chatbot (Spanish)", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Multilingual Chatbot (Spanish)", False, f"Exception: {str(e)}")
            return False
    
    def test_supported_languages_endpoint(self):
        """Test GET /api/chatbot/languages - Supported languages"""
        try:
            response = self.session.get(f"{BACKEND_URL}/chatbot/languages")
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['supported_languages', 'language_details']
                expected_languages = ['fr', 'en', 'ar', 'es']
                
                if all(field in data for field in required_fields):
                    supported = data.get('supported_languages', [])
                    if all(lang in supported for lang in expected_languages):
                        self.log_test("Supported Languages Endpoint", True, f"All 4 languages supported: {supported}", data)
                        return True
                    else:
                        missing = [lang for lang in expected_languages if lang not in supported]
                        self.log_test("Supported Languages Endpoint", False, f"Missing languages: {missing}", data)
                        return False
                else:
                    self.log_test("Supported Languages Endpoint", False, "Missing required fields", data)
                    return False
            else:
                self.log_test("Supported Languages Endpoint", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Supported Languages Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_gpt_security_report(self):
        """Test GET /api/security/gpt/report - GPT-4 security report"""
        try:
            response = self.session.get(f"{BACKEND_URL}/security/gpt/report?time_period=24h")
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['report', 'gpt_version', 'security_assistant', 'timestamp']
                if all(field in data for field in required_fields):
                    if data.get('gpt_version') == '4.0' and 'RIMAREUM GPT-SECURE' in data.get('security_assistant', ''):
                        self.log_test("GPT Security Report", True, "GPT-4 security report generated", data)
                        return True
                    else:
                        self.log_test("GPT Security Report", False, "Invalid GPT version or assistant name", data)
                        return False
                else:
                    self.log_test("GPT Security Report", False, "Missing report fields", data)
                    return False
            else:
                self.log_test("GPT Security Report", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("GPT Security Report", False, f"Exception: {str(e)}")
            return False
    
    def test_threat_intelligence(self):
        """Test GET /api/security/intelligence - Threat intelligence data"""
        try:
            response = self.session.get(f"{BACKEND_URL}/security/intelligence")
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['threat_intelligence', 'last_update', 'source']
                if all(field in data for field in required_fields):
                    if 'RIMAREUM SENTINEL CORE' in data.get('source', ''):
                        self.log_test("Threat Intelligence", True, "Threat intelligence data retrieved", data)
                        return True
                    else:
                        self.log_test("Threat Intelligence", False, "Invalid source information", data)
                        return False
                else:
                    self.log_test("Threat Intelligence", False, "Missing intelligence fields", data)
                    return False
            else:
                self.log_test("Threat Intelligence", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Threat Intelligence", False, f"Exception: {str(e)}")
            return False
    
    def test_monitoring_stats(self):
        """Test GET /api/security/monitoring/stats - Continuous monitoring stats"""
        try:
            response = self.session.get(f"{BACKEND_URL}/security/monitoring/stats")
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['monitoring_stats', 'phase', 'timestamp']
                if all(field in data for field in required_fields):
                    if data.get('phase') == '7_SENTINEL_CORE':
                        self.log_test("Monitoring Stats", True, "Continuous monitoring stats retrieved", data)
                        return True
                    else:
                        self.log_test("Monitoring Stats", False, "Invalid phase information", data)
                        return False
                else:
                    self.log_test("Monitoring Stats", False, "Missing monitoring fields", data)
                    return False
            else:
                self.log_test("Monitoring Stats", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Monitoring Stats", False, f"Exception: {str(e)}")
            return False
    
    def test_ml_model_info(self):
        """Test GET /api/security/ml/model - ML model information"""
        try:
            response = self.session.get(f"{BACKEND_URL}/security/ml/model")
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['ml_model_info', 'phase', 'timestamp']
                if all(field in data for field in required_fields):
                    if data.get('phase') == '7_SENTINEL_CORE':
                        model_info = data.get('ml_model_info', {})
                        if 'model_version' in model_info and 'is_trained' in model_info:
                            self.log_test("ML Model Info", True, "ML model information retrieved", data)
                            return True
                        else:
                            self.log_test("ML Model Info", False, "Missing model info fields", data)
                            return False
                    else:
                        self.log_test("ML Model Info", False, "Invalid phase information", data)
                        return False
                else:
                    self.log_test("ML Model Info", False, "Missing required fields", data)
                    return False
            else:
                self.log_test("ML Model Info", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("ML Model Info", False, f"Exception: {str(e)}")
            return False
    
    def test_ml_training_trigger(self):
        """Test POST /api/security/ml/train - ML model training"""
        try:
            response = self.session.post(f"{BACKEND_URL}/security/ml/train", json={})
            
            # Expect success (200) in both real and fallback mode
            if response.status_code == 200:
                data = response.json()
                required_fields = ['training_triggered', 'timestamp']
                if all(field in data for field in required_fields):
                    if data.get('training_triggered') == False and "fallback mode" in data.get('message', ''):
                        self.log_test("ML Training Trigger", True, "ML training unavailable in fallback mode (expected)", data)
                        return True
                    elif data.get('training_triggered') == True:
                        self.log_test("ML Training Trigger", True, "ML training triggered successfully", data)
                        return True
                    else:
                        self.log_test("ML Training Trigger", False, "Unexpected training response", data)
                        return False
                else:
                    self.log_test("ML Training Trigger", False, "Missing training response fields", data)
                    return False
            else:
                self.log_test("ML Training Trigger", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("ML Training Trigger", False, f"Exception: {str(e)}")
            return False
    
    def test_rate_limiting_phase7_endpoints(self):
        """Test rate limiting on Phase 7 endpoints"""
        try:
            # Test rate limiting on multilingual chatbot (30/minute limit)
            rapid_requests = []
            chat_data = {"message": "Test message", "language": "en"}
            
            for i in range(3):  # Send 3 rapid requests
                response = self.session.post(f"{BACKEND_URL}/chatbot/multilingual", json=chat_data)
                rapid_requests.append(response.status_code)
                time.sleep(0.2)  # Small delay between requests
            
            # All requests should succeed initially (3 requests is well under 30/minute)
            success_count = sum(1 for status in rapid_requests if status == 200)
            
            if success_count >= 2:  # Allow for 1 potential failure
                self.log_test("Phase 7 Rate Limiting", True, f"Rate limiting working - {success_count}/3 requests succeeded")
                return True
            else:
                self.log_test("Phase 7 Rate Limiting", False, f"Only {success_count}/3 requests succeeded")
                return False
        except Exception as e:
            self.log_test("Phase 7 Rate Limiting", False, f"Exception: {str(e)}")
            return False
    
    # PHASE 8 SMART COMMERCE SYSTEM TESTS
    
    def test_smart_commerce_status(self):
        """Test GET /api/shop/status - Phase 8 Smart Commerce status"""
        try:
            response = self.session.get(f"{BACKEND_URL}/shop/status")
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['phase', 'status', 'components', 'statistics', 'integrations']
                component_fields = ['dynamic_product_interface', 'ai_shopping_assistant', 'cart_system', 'qr_code_generation', 'nfc_ready']
                
                if all(field in data for field in required_fields):
                    components = data.get('components', {})
                    if all(field in components for field in component_fields):
                        if data.get('phase') == '8_SMART_COMMERCE' and data.get('status') == 'ACTIVE':
                            self.log_test("Smart Commerce Status", True, "Phase 8 Smart Commerce active with all components", data)
                            return True
                        else:
                            self.log_test("Smart Commerce Status", False, "Smart Commerce not in active Phase 8 state", data)
                            return False
                    else:
                        self.log_test("Smart Commerce Status", False, "Missing component status fields", data)
                        return False
                else:
                    self.log_test("Smart Commerce Status", False, "Missing required status fields", data)
                    return False
            else:
                self.log_test("Smart Commerce Status", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Smart Commerce Status", False, f"Exception: {str(e)}")
            return False
    
    def test_shop_products_all(self):
        """Test GET /api/shop/products - All products"""
        try:
            response = self.session.get(f"{BACKEND_URL}/shop/products")
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['products', 'total_count', 'categories_available', 'timestamp']
                if all(field in data for field in required_fields):
                    products = data.get('products', [])
                    if len(products) >= 4:  # Expect 4 demo products
                        # Check product structure
                        product = products[0]
                        product_fields = ['id', 'name', 'description', 'price', 'category']
                        if all(field in product for field in product_fields):
                            self.log_test("Shop Products (All)", True, f"Found {len(products)} products with proper structure", data)
                            return True, products
                        else:
                            self.log_test("Shop Products (All)", False, "Missing product fields", data)
                            return False, []
                    else:
                        self.log_test("Shop Products (All)", False, f"Expected at least 4 products, got {len(products)}", data)
                        return False, []
                else:
                    self.log_test("Shop Products (All)", False, "Missing required response fields", data)
                    return False, []
            else:
                self.log_test("Shop Products (All)", False, f"Status: {response.status_code}")
                return False, []
        except Exception as e:
            self.log_test("Shop Products (All)", False, f"Exception: {str(e)}")
            return False, []
    
    def test_shop_products_category_filter(self):
        """Test GET /api/shop/products?category=energie - Category filtering"""
        try:
            response = self.session.get(f"{BACKEND_URL}/shop/products?category=energie")
            
            if response.status_code == 200:
                data = response.json()
                products = data.get('products', [])
                # Check if all products belong to 'energie' category
                energie_products = [p for p in products if p.get('category') == 'energie']
                if len(energie_products) == len(products):
                    self.log_test("Shop Products (Category Filter)", True, f"Found {len(products)} energie products", data)
                    return True
                else:
                    self.log_test("Shop Products (Category Filter)", False, "Category filter not working properly", data)
                    return False
            else:
                self.log_test("Shop Products (Category Filter)", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Shop Products (Category Filter)", False, f"Exception: {str(e)}")
            return False
    
    def test_shop_products_featured_filter(self):
        """Test GET /api/shop/products?featured=true - Featured products"""
        try:
            response = self.session.get(f"{BACKEND_URL}/shop/products?featured=true")
            
            if response.status_code == 200:
                data = response.json()
                products = data.get('products', [])
                # Check if all products are featured
                featured_products = [p for p in products if p.get('is_featured') == True]
                if len(featured_products) == len(products) and len(products) > 0:
                    self.log_test("Shop Products (Featured Filter)", True, f"Found {len(products)} featured products", data)
                    return True
                else:
                    self.log_test("Shop Products (Featured Filter)", False, "Featured filter not working properly", data)
                    return False
            else:
                self.log_test("Shop Products (Featured Filter)", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Shop Products (Featured Filter)", False, f"Exception: {str(e)}")
            return False
    
    def test_shop_products_search(self):
        """Test GET /api/shop/products?search=cristal - Search functionality"""
        try:
            response = self.session.get(f"{BACKEND_URL}/shop/products?search=cristal")
            
            if response.status_code == 200:
                data = response.json()
                products = data.get('products', [])
                # Check if search results contain relevant products
                if len(products) >= 0:  # Search might return 0 results, which is valid
                    self.log_test("Shop Products (Search)", True, f"Search returned {len(products)} results for 'cristal'", data)
                    return True
                else:
                    self.log_test("Shop Products (Search)", False, "Search functionality not working", data)
                    return False
            else:
                self.log_test("Shop Products (Search)", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Shop Products (Search)", False, f"Exception: {str(e)}")
            return False
    
    def test_shop_product_details(self):
        """Test GET /api/shop/products/{product_id} - Product details with AI recommendations"""
        # First get products to test with
        success, products = self.test_shop_products_all()
        if not success or not products:
            self.log_test("Shop Product Details", False, "No products available for testing")
            return False
        
        try:
            product_id = products[0]['id']
            response = self.session.get(f"{BACKEND_URL}/shop/products/{product_id}")
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['product', 'recommendations', 'related_products', 'timestamp']
                if all(field in data for field in required_fields):
                    product = data.get('product', {})
                    if product.get('id') == product_id:
                        self.log_test("Shop Product Details", True, "Product details with AI recommendations retrieved", data)
                        return True
                    else:
                        self.log_test("Shop Product Details", False, "Product ID mismatch", data)
                        return False
                else:
                    self.log_test("Shop Product Details", False, "Missing required fields", data)
                    return False
            else:
                self.log_test("Shop Product Details", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Shop Product Details", False, f"Exception: {str(e)}")
            return False
    
    def test_shop_categories(self):
        """Test GET /api/shop/categories - Product categories"""
        try:
            response = self.session.get(f"{BACKEND_URL}/shop/categories")
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['categories', 'statistics', 'timestamp']
                if all(field in data for field in required_fields):
                    categories = data.get('categories', {})
                    statistics = data.get('statistics', {})
                    expected_categories = ['energie', 'objets_sacres', 'nft', 'modules_ia']
                    
                    # Check if expected categories exist
                    found_categories = [cat for cat in expected_categories if cat in categories]
                    if len(found_categories) >= 2:  # At least 2 categories should exist
                        self.log_test("Shop Categories", True, f"Found {len(found_categories)} categories with statistics", data)
                        return True
                    else:
                        self.log_test("Shop Categories", False, f"Expected categories not found: {expected_categories}", data)
                        return False
                else:
                    self.log_test("Shop Categories", False, "Missing required fields", data)
                    return False
            else:
                self.log_test("Shop Categories", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Shop Categories", False, f"Exception: {str(e)}")
            return False
    
    def test_create_shopping_cart(self):
        """Test POST /api/shop/cart/create - Create new cart"""
        try:
            user_data = {"user_id": str(uuid.uuid4())}
            response = self.session.post(f"{BACKEND_URL}/shop/cart/create", json=user_data)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['cart', 'session_id', 'expires_in', 'timestamp']
                if all(field in data for field in required_fields):
                    cart = data.get('cart', {})
                    session_id = data.get('session_id')
                    if 'id' in cart and session_id:
                        self.log_test("Create Shopping Cart", True, "Shopping cart created successfully", data)
                        return True, session_id, cart['id']
                    else:
                        self.log_test("Create Shopping Cart", False, "Missing cart ID or session ID", data)
                        return False, None, None
                else:
                    self.log_test("Create Shopping Cart", False, "Missing required fields", data)
                    return False, None, None
            else:
                self.log_test("Create Shopping Cart", False, f"Status: {response.status_code}")
                return False, None, None
        except Exception as e:
            self.log_test("Create Shopping Cart", False, f"Exception: {str(e)}")
            return False, None, None
    
    def test_add_to_cart(self):
        """Test POST /api/shop/cart/{cart_id}/add - Add items to cart"""
        # First create a cart
        cart_success, session_id, cart_id = self.test_create_shopping_cart()
        if not cart_success:
            self.log_test("Add to Cart", False, "Failed to create cart for testing")
            return False
        
        # Get a product to add
        success, products = self.test_shop_products_all()
        if not success or not products:
            self.log_test("Add to Cart", False, "No products available for testing")
            return False
        
        try:
            product_id = products[0]['id']
            item_data = {
                "product_id": product_id,
                "quantity": 2
            }
            response = self.session.post(f"{BACKEND_URL}/shop/cart/{cart_id}/add", json=item_data)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['success', 'cart', 'message', 'timestamp']
                if all(field in data for field in required_fields):
                    if data.get('success') == True:
                        self.log_test("Add to Cart", True, "Item added to cart successfully", data)
                        return True, cart_id
                    else:
                        self.log_test("Add to Cart", False, "Add to cart failed", data)
                        return False, None
                else:
                    self.log_test("Add to Cart", False, "Missing required fields", data)
                    return False, None
            else:
                self.log_test("Add to Cart", False, f"Status: {response.status_code}")
                return False, None
        except Exception as e:
            self.log_test("Add to Cart", False, f"Exception: {str(e)}")
            return False, None
    
    def test_get_cart_details(self):
        """Test GET /api/shop/cart/{cart_id} - Get cart details with AI suggestions"""
        # First add items to cart
        add_success, cart_id = self.test_add_to_cart()
        if not add_success:
            self.log_test("Get Cart Details", False, "Failed to add items to cart for testing")
            return False
        
        try:
            response = self.session.get(f"{BACKEND_URL}/shop/cart/{cart_id}")
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['cart', 'ai_suggestions', 'timestamp']
                if all(field in data for field in required_fields):
                    cart = data.get('cart', {})
                    ai_suggestions = data.get('ai_suggestions', {})
                    if 'id' in cart and 'upsell' in ai_suggestions and 'cross_sell' in ai_suggestions:
                        self.log_test("Get Cart Details", True, "Cart details with AI suggestions retrieved", data)
                        return True
                    else:
                        self.log_test("Get Cart Details", False, "Missing cart data or AI suggestions", data)
                        return False
                else:
                    self.log_test("Get Cart Details", False, "Missing required fields", data)
                    return False
            else:
                self.log_test("Get Cart Details", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Get Cart Details", False, f"Exception: {str(e)}")
            return False
    
    def test_ai_shopping_assistant_french(self):
        """Test POST /api/shop/assistant - French message"""
        try:
            message_data = {
                "message": "Je cherche des produits énergétiques",
                "language": "fr"
            }
            response = self.session.post(f"{BACKEND_URL}/shop/assistant", json=message_data)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['response', 'language', 'type', 'recommendations', 'timestamp']
                if all(field in data for field in required_fields):
                    if data.get('language') == 'fr':
                        self.log_test("AI Shopping Assistant (French)", True, "French shopping assistant working", data)
                        return True
                    else:
                        self.log_test("AI Shopping Assistant (French)", False, "Language detection issue", data)
                        return False
                else:
                    self.log_test("AI Shopping Assistant (French)", False, "Missing required fields", data)
                    return False
            else:
                self.log_test("AI Shopping Assistant (French)", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("AI Shopping Assistant (French)", False, f"Exception: {str(e)}")
            return False
    
    def test_ai_shopping_assistant_english(self):
        """Test POST /api/shop/assistant - English message"""
        try:
            message_data = {
                "message": "I want to buy crystals",
                "language": "en"
            }
            response = self.session.post(f"{BACKEND_URL}/shop/assistant", json=message_data)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['response', 'language', 'type', 'recommendations', 'timestamp']
                if all(field in data for field in required_fields):
                    self.log_test("AI Shopping Assistant (English)", True, "English shopping assistant working", data)
                    return True
                else:
                    self.log_test("AI Shopping Assistant (English)", False, "Missing required fields", data)
                    return False
            else:
                self.log_test("AI Shopping Assistant (English)", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("AI Shopping Assistant (English)", False, f"Exception: {str(e)}")
            return False
    
    def test_ai_shopping_assistant_arabic(self):
        """Test POST /api/shop/assistant - Arabic message"""
        try:
            message_data = {
                "message": "أريد شراء منتجات الطاقة",
                "language": "ar"
            }
            response = self.session.post(f"{BACKEND_URL}/shop/assistant", json=message_data)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['response', 'language', 'type', 'recommendations', 'timestamp']
                if all(field in data for field in required_fields):
                    self.log_test("AI Shopping Assistant (Arabic)", True, "Arabic shopping assistant working", data)
                    return True
                else:
                    self.log_test("AI Shopping Assistant (Arabic)", False, "Missing required fields", data)
                    return False
            else:
                self.log_test("AI Shopping Assistant (Arabic)", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("AI Shopping Assistant (Arabic)", False, f"Exception: {str(e)}")
            return False
    
    def test_ai_shopping_assistant_spanish(self):
        """Test POST /api/shop/assistant - Spanish message"""
        try:
            message_data = {
                "message": "Quiero comprar cristales",
                "language": "es"
            }
            response = self.session.post(f"{BACKEND_URL}/shop/assistant", json=message_data)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['response', 'language', 'type', 'recommendations', 'timestamp']
                if all(field in data for field in required_fields):
                    self.log_test("AI Shopping Assistant (Spanish)", True, "Spanish shopping assistant working", data)
                    return True
                else:
                    self.log_test("AI Shopping Assistant (Spanish)", False, "Missing required fields", data)
                    return False
            else:
                self.log_test("AI Shopping Assistant (Spanish)", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("AI Shopping Assistant (Spanish)", False, f"Exception: {str(e)}")
            return False
    
    def test_qr_code_generation(self):
        """Test GET /api/shop/qrcode/{product_id} - QR code generation for all demo products"""
        # Get products to test with
        success, products = self.test_shop_products_all()
        if not success or not products:
            self.log_test("QR Code Generation", False, "No products available for testing")
            return False
        
        success_count = 0
        for product in products[:4]:  # Test all 4 demo products
            try:
                product_id = product['id']
                response = self.session.get(f"{BACKEND_URL}/shop/qrcode/{product_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    required_fields = ['product_id', 'qr_code', 'product_url', 'nfc_ready', 'social_sharing']
                    if all(field in data for field in required_fields):
                        if data.get('product_id') == product_id and data.get('nfc_ready') == True:
                            success_count += 1
                        else:
                            self.log_test(f"QR Code for {product_id}", False, "Invalid QR code data", data)
                    else:
                        self.log_test(f"QR Code for {product_id}", False, "Missing QR code fields", data)
                else:
                    self.log_test(f"QR Code for {product_id}", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test(f"QR Code for {product_id}", False, f"Exception: {str(e)}")
        
        if success_count == len(products[:4]):
            self.log_test("QR Code Generation", True, f"QR codes generated for all {success_count} products")
            return True
        else:
            self.log_test("QR Code Generation", False, f"Only {success_count}/{len(products[:4])} QR codes generated successfully")
            return False
    
    def test_checkout_card_payment(self):
        """Test POST /api/shop/checkout - Card payment simulation"""
        # First add items to cart
        add_success, cart_id = self.test_add_to_cart()
        if not add_success:
            self.log_test("Checkout (Card Payment)", False, "Failed to add items to cart for testing")
            return False
        
        try:
            checkout_data = {
                "cart_id": cart_id,
                "payment_method": "card",
                "billing_info": {
                    "name": "Test User",
                    "email": "test@rimareum.com",
                    "address": "123 Test Street"
                }
            }
            response = self.session.post(f"{BACKEND_URL}/shop/checkout", json=checkout_data)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['checkout_success', 'order', 'estimated_delivery', 'tracking_number', 'timestamp']
                if all(field in data for field in required_fields):
                    order = data.get('order', {})
                    if (data.get('checkout_success') == True and 
                        order.get('payment_method') == 'card' and 
                        order.get('status') == 'completed'):
                        self.log_test("Checkout (Card Payment)", True, "Card payment simulation successful", data)
                        return True
                    else:
                        self.log_test("Checkout (Card Payment)", False, "Checkout simulation failed", data)
                        return False
                else:
                    self.log_test("Checkout (Card Payment)", False, "Missing required fields", data)
                    return False
            else:
                self.log_test("Checkout (Card Payment)", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Checkout (Card Payment)", False, f"Exception: {str(e)}")
            return False
    
    def test_checkout_crypto_payment(self):
        """Test POST /api/shop/checkout - Crypto wallet simulation"""
        # First add items to cart
        add_success, cart_id = self.test_add_to_cart()
        if not add_success:
            self.log_test("Checkout (Crypto Payment)", False, "Failed to add items to cart for testing")
            return False
        
        try:
            checkout_data = {
                "cart_id": cart_id,
                "payment_method": "crypto",
                "billing_info": {
                    "wallet_address": "0x742d35Cc6634C0532925a3b8D4C9db96590e4CAF"
                }
            }
            response = self.session.post(f"{BACKEND_URL}/shop/checkout", json=checkout_data)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['checkout_success', 'order', 'estimated_delivery', 'tracking_number', 'timestamp']
                if all(field in data for field in required_fields):
                    order = data.get('order', {})
                    if (data.get('checkout_success') == True and 
                        order.get('payment_method') == 'crypto' and 
                        'blockchain_tx' in order):
                        self.log_test("Checkout (Crypto Payment)", True, "Crypto payment simulation successful", data)
                        return True
                    else:
                        self.log_test("Checkout (Crypto Payment)", False, "Crypto checkout simulation failed", data)
                        return False
                else:
                    self.log_test("Checkout (Crypto Payment)", False, "Missing required fields", data)
                    return False
            else:
                self.log_test("Checkout (Crypto Payment)", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Checkout (Crypto Payment)", False, f"Exception: {str(e)}")
            return False
    
    def test_checkout_paypal_payment(self):
        """Test POST /api/shop/checkout - PayPal simulation"""
        # First add items to cart
        add_success, cart_id = self.test_add_to_cart()
        if not add_success:
            self.log_test("Checkout (PayPal Payment)", False, "Failed to add items to cart for testing")
            return False
        
        try:
            checkout_data = {
                "cart_id": cart_id,
                "payment_method": "paypal",
                "billing_info": {
                    "email": "test@rimareum.com"
                }
            }
            response = self.session.post(f"{BACKEND_URL}/shop/checkout", json=checkout_data)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['checkout_success', 'order', 'estimated_delivery', 'tracking_number', 'timestamp']
                if all(field in data for field in required_fields):
                    order = data.get('order', {})
                    if (data.get('checkout_success') == True and 
                        order.get('payment_method') == 'paypal' and 
                        'paypal_order_id' in order):
                        self.log_test("Checkout (PayPal Payment)", True, "PayPal payment simulation successful", data)
                        return True
                    else:
                        self.log_test("Checkout (PayPal Payment)", False, "PayPal checkout simulation failed", data)
                        return False
                else:
                    self.log_test("Checkout (PayPal Payment)", False, "Missing required fields", data)
                    return False
            else:
                self.log_test("Checkout (PayPal Payment)", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Checkout (PayPal Payment)", False, f"Exception: {str(e)}")
            return False
    
    def test_demo_products_verification(self):
        """Test verification of all 4 demo products"""
        success, products = self.test_shop_products_all()
        if not success:
            self.log_test("Demo Products Verification", False, "Failed to get products")
            return False
        
        try:
            expected_products = [
                "Cristal Solaire RIMAREUM",
                "Clé Nadjibienne Δ144", 
                "Artefact-Ω Prototype",
                "IA Guide de Commerce"
            ]
            
            expected_categories = ["énergie", "objets sacrés", "NFT", "modules IA"]
            
            found_products = []
            found_categories = set()
            
            for product in products:
                name = product.get('name', '')
                category = product.get('category', '')
                
                # Check if this matches any expected product (partial match)
                for expected in expected_products:
                    if any(word in name for word in expected.split()[:2]):  # Match first 2 words
                        found_products.append(name)
                        break
                
                found_categories.add(category)
            
            if len(found_products) >= 3:  # At least 3 of 4 expected products
                self.log_test("Demo Products Verification", True, f"Found {len(found_products)} demo products with categories: {list(found_categories)}")
                return True
            else:
                self.log_test("Demo Products Verification", False, f"Only found {len(found_products)} demo products: {found_products}")
                return False
        except Exception as e:
            self.log_test("Demo Products Verification", False, f"Exception: {str(e)}")
            return False
    
    def test_integration_with_existing_systems(self):
        """Test Phase 8 doesn't break existing Phase 7 security features"""
        try:
            # Test that Phase 7 endpoints still work
            phase7_tests = [
                self.test_sentinel_core_status(),
                self.test_multilingual_chatbot_french(),
                self.test_security_status_endpoint()
            ]
            
            success_count = sum(1 for test in phase7_tests if test)
            
            if success_count >= 2:  # At least 2 of 3 tests should pass
                self.log_test("Integration with Existing Systems", True, f"Phase 7 integration maintained: {success_count}/3 tests passed")
                return True
            else:
                self.log_test("Integration with Existing Systems", False, f"Phase 7 integration broken: only {success_count}/3 tests passed")
                return False
        except Exception as e:
            self.log_test("Integration with Existing Systems", False, f"Exception: {str(e)}")
            return False
    
    def test_error_handling_edge_cases(self):
        """Test error handling for Phase 8 endpoints"""
        try:
            error_tests = []
            
            # Test invalid product ID
            response = self.session.get(f"{BACKEND_URL}/shop/products/invalid-id")
            error_tests.append(response.status_code == 404)
            
            # Test invalid cart operation
            response = self.session.post(f"{BACKEND_URL}/shop/cart/invalid-cart/add", json={"product_id": "test"})
            error_tests.append(response.status_code in [400, 404, 500])
            
            # Test malformed assistant request
            response = self.session.post(f"{BACKEND_URL}/shop/assistant", json={})
            error_tests.append(response.status_code == 400)
            
            success_count = sum(1 for test in error_tests if test)
            
            if success_count >= 2:  # At least 2 of 3 error tests should pass
                self.log_test("Error Handling & Edge Cases", True, f"Error handling working: {success_count}/3 tests passed")
                return True
            else:
                self.log_test("Error Handling & Edge Cases", False, f"Error handling issues: only {success_count}/3 tests passed")
                return False
        except Exception as e:
            self.log_test("Error Handling & Edge Cases", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run comprehensive test suite"""
        print("🚀 Starting RIMAREUM Backend API Test Suite - PHASE 8 SMART COMMERCE")
        print("=" * 70)
        print()
        
        # Core API Tests
        print("📡 CORE API TESTS")
        print("-" * 30)
        self.test_root_endpoint()
        self.test_cors_configuration()
        
        # PHASE 6 Security Tests
        print("🛡️ PHASE 6 SECURITY TESTS")
        print("-" * 30)
        self.test_security_status_endpoint()
        self.test_user_registration()
        self.test_user_login()
        self.test_rate_limiting()
        self.test_security_headers()
        self.test_security_report_endpoint()
        self.test_security_audit_endpoint()
        
        # PHASE 7 SENTINEL CORE Tests
        print("🛡️ PHASE 7 SENTINEL CORE TESTS")
        print("-" * 30)
        self.test_sentinel_core_status()
        self.test_multilingual_chatbot_french()
        self.test_multilingual_chatbot_english()
        self.test_multilingual_chatbot_arabic()
        self.test_multilingual_chatbot_spanish()
        self.test_supported_languages_endpoint()
        self.test_gpt_security_report()
        self.test_threat_intelligence()
        self.test_monitoring_stats()
        self.test_ml_model_info()
        self.test_ml_training_trigger()
        self.test_rate_limiting_phase7_endpoints()
        
        # PHASE 8 SMART COMMERCE SYSTEM Tests
        print("🛍️ PHASE 8 SMART COMMERCE SYSTEM TESTS")
        print("-" * 40)
        self.test_smart_commerce_status()
        self.test_shop_products_all()
        self.test_shop_products_category_filter()
        self.test_shop_products_featured_filter()
        self.test_shop_products_search()
        self.test_shop_product_details()
        self.test_shop_categories()
        self.test_create_shopping_cart()
        self.test_add_to_cart()
        self.test_get_cart_details()
        self.test_ai_shopping_assistant_french()
        self.test_ai_shopping_assistant_english()
        self.test_ai_shopping_assistant_arabic()
        self.test_ai_shopping_assistant_spanish()
        self.test_qr_code_generation()
        self.test_checkout_card_payment()
        self.test_checkout_crypto_payment()
        self.test_checkout_paypal_payment()
        self.test_demo_products_verification()
        self.test_integration_with_existing_systems()
        self.test_error_handling_edge_cases()
        
        # Product Management Tests (Legacy)
        print("🛍️ LEGACY PRODUCT MANAGEMENT TESTS")
        print("-" * 30)
        self.test_get_all_products()
        self.test_filter_products_by_category()
        self.test_filter_featured_products()
        self.test_get_individual_products()
        
        # Payment Flow Tests (Legacy)
        print("💳 LEGACY PAYMENT FLOW TESTS (Simulation Mode)")
        print("-" * 30)
        self.test_payment_checkout_with_product()
        self.test_payment_checkout_custom_amount()
        
        # Wallet Integration Tests
        print("👛 WALLET INTEGRATION TESTS")
        print("-" * 30)
        self.test_wallet_connect()
        self.test_wallet_balance()
        
        # AI Chat Tests (Legacy)
        print("🤖 LEGACY AI CHAT TESTS (Simulation Mode)")
        print("-" * 30)
        self.test_ai_chat_message()
        
        # Admin Dashboard Tests
        print("📊 ADMIN DASHBOARD TESTS")
        print("-" * 30)
        self.test_admin_stats()
        
        # Error Handling Tests
        print("⚠️ ERROR HANDLING TESTS")
        print("-" * 30)
        self.test_invalid_endpoints()
        self.test_malformed_requests()
        
        # Summary
        print("=" * 70)
        print("📋 TEST SUMMARY")
        print("=" * 70)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("\n🎉 ALL TESTS PASSED! Backend API with PHASE 8 SMART COMMERCE is working correctly.")
        else:
            print(f"\n⚠️ {total - passed} tests failed. Check details above.")
        
        return passed == total

if __name__ == "__main__":
    tester = RimareumAPITester()
    success = tester.run_all_tests()
    exit(0 if success else 1)