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
            payload = {
                "product_id": product_id,
                "quantity": 1
            }
            response = self.session.post(f"{BACKEND_URL}/payments/checkout/session", json=payload)
            
            # Expect 503 in simulation mode (no Stripe key)
            if response.status_code == 503:
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
                "amount": 50.00
            }
            response = self.session.post(f"{BACKEND_URL}/payments/checkout/session", json=payload)
            
            # Expect 503 in simulation mode (no Stripe key)
            if response.status_code == 503:
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
                "balance": 1.5
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
                required_fields = ['total_products', 'total_users', 'total_orders', 'total_payments', 'revenue']
                if all(field in data for field in required_fields):
                    self.log_test("Admin Stats", True, "Platform statistics retrieved", data)
                    return True
                else:
                    self.log_test("Admin Stats", False, "Missing required stats fields", data)
                    return False
            else:
                self.log_test("Admin Stats", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Admin Stats", False, f"Exception: {str(e)}")
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
    
    def run_all_tests(self):
        """Run comprehensive test suite"""
        print("🚀 Starting RIMAREUM Backend API Test Suite")
        print("=" * 60)
        print()
        
        # Core API Tests
        print("📡 CORE API TESTS")
        print("-" * 30)
        self.test_root_endpoint()
        self.test_cors_configuration()
        
        # Product Management Tests
        print("🛍️ PRODUCT MANAGEMENT TESTS")
        print("-" * 30)
        self.test_get_all_products()
        self.test_filter_products_by_category()
        self.test_filter_featured_products()
        self.test_get_individual_products()
        
        # Payment Flow Tests
        print("💳 PAYMENT FLOW TESTS (Simulation Mode)")
        print("-" * 30)
        self.test_payment_checkout_with_product()
        self.test_payment_checkout_custom_amount()
        
        # Wallet Integration Tests
        print("👛 WALLET INTEGRATION TESTS")
        print("-" * 30)
        self.test_wallet_connect()
        self.test_wallet_balance()
        
        # AI Chat Tests
        print("🤖 AI CHAT TESTS (Simulation Mode)")
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
        print("=" * 60)
        print("📋 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("\n🎉 ALL TESTS PASSED! Backend API is working correctly in simulation mode.")
        else:
            print(f"\n⚠️ {total - passed} tests failed. Check details above.")
        
        return passed == total

if __name__ == "__main__":
    tester = RimareumAPITester()
    success = tester.run_all_tests()
    exit(0 if success else 1)