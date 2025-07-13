/**
 * 🛡️ RIMAREUM PHASE 6 - Frontend Security Module
 * Client-side security utilities for threat detection and protection
 */

import FingerprintJS from '@fingerprintjs/fingerprintjs';
import DOMPurify from 'dompurify';

// Security configuration
const SECURITY_CONFIG = {
  api_url: process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001',
  fingerprint_timeout: 5000,
  xss_check_enabled: true,
  rate_limit_check: true,
  console_log_disabled: process.env.NODE_ENV === 'production'
};

// Initialize fingerprint
let fingerprintPromise = null;

/**
 * Initialize fingerprint detection
 */
export const initializeFingerprint = async () => {
  if (!fingerprintPromise) {
    fingerprintPromise = FingerprintJS.load({
      timeout: SECURITY_CONFIG.fingerprint_timeout
    });
  }
  return fingerprintPromise;
};

/**
 * Get device fingerprint
 */
export const getDeviceFingerprint = async () => {
  try {
    const fp = await initializeFingerprint();
    const result = await fp.get();
    return result.visitorId;
  } catch (error) {
    console.error('Fingerprint error:', error);
    return null;
  }
};

/**
 * Sanitize input to prevent XSS
 */
export const sanitizeInput = (input) => {
  if (!SECURITY_CONFIG.xss_check_enabled) return input;
  
  if (typeof input !== 'string') return input;
  
  // Use DOMPurify to sanitize
  return DOMPurify.sanitize(input, {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a'],
    ALLOWED_ATTR: ['href']
  });
};

/**
 * Detect potential XSS attempts
 */
export const detectXSS = (input) => {
  if (!input || typeof input !== 'string') return false;
  
  const xssPatterns = [
    /<script[^>]*>.*?<\/script>/gi,
    /javascript:/gi,
    /on\w+\s*=/gi,
    /eval\s*\(/gi,
    /expression\s*\(/gi,
    /<iframe[^>]*>/gi,
    /<object[^>]*>/gi,
    /<embed[^>]*>/gi
  ];
  
  return xssPatterns.some(pattern => pattern.test(input));
};

/**
 * Rate limiting checker
 */
class RateLimiter {
  constructor() {
    this.requests = new Map();
    this.limits = {
      chat: { max: 10, window: 60000 }, // 10 requests per minute
      payment: { max: 5, window: 60000 }, // 5 requests per minute
      default: { max: 30, window: 60000 } // 30 requests per minute
    };
  }

  checkLimit(endpoint, type = 'default') {
    const now = Date.now();
    const key = `${endpoint}_${type}`;
    
    if (!this.requests.has(key)) {
      this.requests.set(key, []);
    }
    
    const requests = this.requests.get(key);
    const limit = this.limits[type] || this.limits.default;
    
    // Remove old requests outside the window
    const validRequests = requests.filter(time => now - time < limit.window);
    
    if (validRequests.length >= limit.max) {
      return false; // Rate limit exceeded
    }
    
    validRequests.push(now);
    this.requests.set(key, validRequests);
    return true;
  }
}

export const rateLimiter = new RateLimiter();

/**
 * Security event reporter
 */
export const reportSecurityEvent = async (eventType, details = {}) => {
  try {
    const fingerprint = await getDeviceFingerprint();
    
    const event = {
      event_type: eventType,
      ip_address: 'client-side', // Will be determined by backend
      fingerprint,
      details: {
        ...details,
        timestamp: new Date().toISOString(),
        user_agent: navigator.userAgent,
        url: window.location.href
      }
    };
    
    await fetch(`${SECURITY_CONFIG.api_url}/api/security/report`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(event)
    });
  } catch (error) {
    console.error('Security event reporting failed:', error);
  }
};

/**
 * Console log disabler for production
 */
export const disableConsoleInProduction = () => {
  if (SECURITY_CONFIG.console_log_disabled) {
    const methods = ['log', 'debug', 'info', 'warn', 'error'];
    methods.forEach(method => {
      console[method] = () => {};
    });
  }
};

/**
 * Security monitoring service
 */
export class SecurityMonitor {
  constructor() {
    this.isInitialized = false;
    this.securityScore = 100;
    this.threats = [];
  }

  async initialize() {
    if (this.isInitialized) return;
    
    try {
      // Initialize fingerprint
      await initializeFingerprint();
      
      // Disable console in production
      disableConsoleInProduction();
      
      // Start monitoring
      this.startMonitoring();
      
      this.isInitialized = true;
      console.log('🛡️ RIMAREUM Security Monitor initialized');
    } catch (error) {
      console.error('Security Monitor initialization failed:', error);
    }
  }

  startMonitoring() {
    // Monitor for suspicious activities
    this.monitorDevTools();
    this.monitorRapidClicks();
    this.monitorSuspiciousInputs();
  }

  monitorDevTools() {
    // Basic dev tools detection
    setInterval(() => {
      const threshold = 160;
      if (window.outerHeight - window.innerHeight > threshold || 
          window.outerWidth - window.innerWidth > threshold) {
        this.reportThreat('DEV_TOOLS_DETECTED');
      }
    }, 5000);
  }

  monitorRapidClicks() {
    let clickCount = 0;
    let lastClick = 0;

    document.addEventListener('click', () => {
      const now = Date.now();
      if (now - lastClick < 100) {
        clickCount++;
        if (clickCount > 10) {
          this.reportThreat('RAPID_CLICKING');
          clickCount = 0;
        }
      } else {
        clickCount = 0;
      }
      lastClick = now;
    });
  }

  monitorSuspiciousInputs() {
    document.addEventListener('input', (event) => {
      const value = event.target.value;
      if (detectXSS(value)) {
        this.reportThreat('XSS_ATTEMPT', { input: value });
        event.target.value = sanitizeInput(value);
      }
    });
  }

  reportThreat(threatType, details = {}) {
    this.threats.push({
      type: threatType,
      timestamp: new Date().toISOString(),
      details
    });
    
    this.securityScore = Math.max(0, this.securityScore - 10);
    
    reportSecurityEvent(threatType, details);
  }

  getSecurityStatus() {
    return {
      score: this.securityScore,
      threats: this.threats.slice(-10), // Last 10 threats
      isInitialized: this.isInitialized
    };
  }
}

// Global security monitor instance
export const securityMonitor = new SecurityMonitor();

// Auto-initialize on import
if (typeof window !== 'undefined') {
  securityMonitor.initialize();
}