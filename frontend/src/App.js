import React, { useState, useEffect, createContext, useContext } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Context for global state management
const AppContext = createContext();

const useApp = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error("useApp must be used within AppProvider");
  }
  return context;
};

// Wallet Integration (simplified for MVP)
const useWallet = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [account, setAccount] = useState("");
  const [balance, setBalance] = useState(null);

  const connectWallet = async () => {
    if (typeof window.ethereum !== 'undefined') {
      try {
        const accounts = await window.ethereum.request({ method: 'eth_request_accounts' });
        setAccount(accounts[0]);
        setIsConnected(true);
        
        // Get balance (mock for MVP)
        const response = await axios.get(`${API}/wallet/balance/${accounts[0]}`);
        setBalance(response.data);
        
        return accounts[0];
      } catch (error) {
        console.error("Wallet connection failed:", error);
        alert("Wallet connection failed. For MVP, we'll simulate the connection.");
        // Simulate wallet connection for demo
        const mockAccount = "0x" + Math.random().toString(16).substr(2, 40);
        setAccount(mockAccount);
        setIsConnected(true);
        setBalance({
          address: mockAccount,
          eth_balance: 1.5,
          rimar_balance: 1000.0,
          nft_count: 5
        });
        return mockAccount;
      }
    } else {
      alert("MetaMask not detected. For MVP, we'll simulate the connection.");
      // Simulate wallet connection for demo
      const mockAccount = "0x" + Math.random().toString(16).substr(2, 40);
      setAccount(mockAccount);
      setIsConnected(true);
      setBalance({
        address: mockAccount,
        eth_balance: 1.5,
        rimar_balance: 1000.0,
        nft_count: 5
      });
      return mockAccount;
    }
  };

  const disconnectWallet = () => {
    setIsConnected(false);
    setAccount("");
    setBalance(null);
  };

  return { isConnected, account, balance, connectWallet, disconnectWallet };
};

// Header Component
const Header = () => {
  const { wallet } = useApp();

  return (
    <header className="bg-black text-white border-b border-gray-800">
      <div className="container mx-auto px-4 py-4 flex justify-between items-center">
        <div className="flex items-center space-x-4">
          <h1 className="text-2xl font-bold text-blue-400">RIMAREUM</h1>
          <nav className="hidden md:flex space-x-6">
            <a href="#home" className="hover:text-blue-400 transition">Home</a>
            <a href="#products" className="hover:text-blue-400 transition">Products</a>
            <a href="#nft" className="hover:text-blue-400 transition">NFT</a>
            <a href="#dao" className="hover:text-blue-400 transition">DAO</a>
            <a href="#ai" className="hover:text-blue-400 transition">AI Assistant</a>
          </nav>
        </div>
        
        <div className="flex items-center space-x-4">
          {wallet.isConnected ? (
            <div className="flex items-center space-x-2">
              <div className="text-sm">
                <div className="text-blue-400">{wallet.account.slice(0, 6)}...{wallet.account.slice(-4)}</div>
                <div className="text-xs text-gray-400">
                  {wallet.balance?.rimar_balance || 0} $RIMAR
                </div>
              </div>
              <button
                onClick={wallet.disconnectWallet}
                className="bg-red-600 hover:bg-red-700 px-3 py-2 rounded text-sm transition"
              >
                Disconnect
              </button>
            </div>
          ) : (
            <button
              onClick={wallet.connectWallet}
              className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded font-semibold transition"
            >
              Connect Wallet
            </button>
          )}
        </div>
      </div>
    </header>
  );
};

// Hero Section
const HeroSection = () => {
  return (
    <section id="home" className="relative bg-black text-white py-20">
      <div className="absolute inset-0 opacity-20">
        <img 
          src="https://images.unsplash.com/photo-1640161704729-cbe966a08476?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzR8MHwxfHNlYXJjaHwxfHxjcnlwdG9jdXJyZW5jeXxlbnwwfHx8fDE3NTIzNDM2NDR8MA&ixlib=rb-4.1.0&q=85"
          alt="Cryptocurrency"
          className="w-full h-full object-cover"
        />
      </div>
      <div className="relative container mx-auto px-4 text-center">
        <h1 className="text-6xl font-bold mb-6">
          Welcome to <span className="text-blue-400">RIMAREUM</span>
        </h1>
        <p className="text-xl mb-8 max-w-3xl mx-auto text-gray-300">
          The revolutionary platform combining e-commerce, crypto payments, NFT marketplace, 
          DAO governance, and AI assistance. Trade physical products, digital assets, and shape the future together.
        </p>
        <div className="flex justify-center space-x-4">
          <button className="bg-blue-600 hover:bg-blue-700 px-8 py-3 rounded-lg font-semibold transition">
            Explore Products
          </button>
          <button className="border border-blue-400 text-blue-400 hover:bg-blue-400 hover:text-black px-8 py-3 rounded-lg font-semibold transition">
            Join DAO
          </button>
        </div>
      </div>
    </section>
  );
};

// Products Section
const ProductsSection = () => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    try {
      const response = await axios.get(`${API}/products?featured=true`);
      setProducts(response.data);
    } catch (error) {
      console.error("Error fetching products:", error);
    } finally {
      setLoading(false);
    }
  };

  const handlePurchase = async (product) => {
    try {
      const response = await axios.post(`${API}/payments/checkout/session`, {
        product_id: product.id,
        quantity: 1
      }, {
        headers: {
          'Origin': window.location.origin
        }
      });

      if (response.data.url) {
        window.location.href = response.data.url;
      }
    } catch (error) {
      console.error("Payment error:", error);
      alert("Payment setup failed. Please try again.");
    }
  };

  if (loading) {
    return (
      <section id="products" className="py-20 bg-gray-900">
        <div className="container mx-auto px-4 text-center">
          <div className="text-white">Loading products...</div>
        </div>
      </section>
    );
  }

  return (
    <section id="products" className="py-20 bg-gray-900">
      <div className="container mx-auto px-4">
        <h2 className="text-4xl font-bold text-center text-white mb-12">
          Featured Products
        </h2>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {products.map((product) => (
            <div key={product.id} className="bg-gray-800 rounded-lg overflow-hidden shadow-lg hover:shadow-xl transition">
              <img 
                src={product.image_url || "https://via.placeholder.com/400x300"}
                alt={product.name}
                className="w-full h-48 object-cover"
              />
              <div className="p-6">
                <h3 className="text-xl font-semibold text-white mb-2">{product.name}</h3>
                <p className="text-gray-400 mb-4">{product.description}</p>
                <div className="flex justify-between items-center mb-4">
                  <span className="text-2xl font-bold text-blue-400">${product.price}</span>
                  <span className="text-sm text-gray-500">{product.crypto_price} $RIMAR</span>
                </div>
                <div className="flex space-x-2">
                  <button 
                    onClick={() => handlePurchase(product)}
                    className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded transition"
                  >
                    Buy with Card
                  </button>
                  <button className="flex-1 bg-purple-600 hover:bg-purple-700 text-white py-2 px-4 rounded transition">
                    Buy with Crypto
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

// AI Chat Component
const AIChatSection = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState("");
  const [sessionId] = useState(() => Math.random().toString(36).substr(2, 9));
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage = { role: "user", content: inputMessage };
    setMessages(prev => [...prev, userMessage]);
    setInputMessage("");
    setLoading(true);

    try {
      const response = await axios.post(`${API}/chat/message`, {
        session_id: sessionId,
        message: inputMessage
      });

      const aiMessage = { role: "assistant", content: response.data.response };
      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error("Chat error:", error);
      const errorMessage = { role: "assistant", content: "Sorry, I'm not available right now. Please try again later." };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section id="ai" className="py-20 bg-black">
      <div className="container mx-auto px-4">
        <h2 className="text-4xl font-bold text-center text-white mb-12">
          AI Assistant
        </h2>
        
        <div className="max-w-4xl mx-auto bg-gray-800 rounded-lg p-6">
          <div className="h-96 overflow-y-auto mb-4 border border-gray-700 rounded p-4 bg-gray-900">
            {messages.length === 0 ? (
              <div className="text-gray-500 text-center">
                Ask me anything about RIMAREUM, crypto, NFTs, or our products!
              </div>
            ) : (
              messages.map((msg, index) => (
                <div key={index} className={`mb-4 ${msg.role === 'user' ? 'text-right' : 'text-left'}`}>
                  <div className={`inline-block max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                    msg.role === 'user' 
                      ? 'bg-blue-600 text-white' 
                      : 'bg-gray-700 text-gray-200'
                  }`}>
                    {msg.content}
                  </div>
                </div>
              ))
            )}
            {loading && (
              <div className="text-left">
                <div className="inline-block bg-gray-700 text-gray-200 px-4 py-2 rounded-lg">
                  Thinking...
                </div>
              </div>
            )}
          </div>
          
          <div className="flex space-x-2">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
              placeholder="Ask about products, crypto, DAO, or anything else..."
              className="flex-1 bg-gray-700 text-white px-4 py-2 rounded border border-gray-600 focus:outline-none focus:border-blue-400"
              disabled={loading}
            />
            <button 
              onClick={sendMessage}
              disabled={loading || !inputMessage.trim()}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white px-6 py-2 rounded transition"
            >
              Send
            </button>
          </div>
        </div>
      </div>
    </section>
  );
};

// DAO Section
const DAOSection = () => {
  const { wallet } = useApp();
  
  return (
    <section id="dao" className="py-20 bg-gray-900">
      <div className="container mx-auto px-4 text-center">
        <h2 className="text-4xl font-bold text-white mb-12">
          Decentralized Governance
        </h2>
        
        <div className="max-w-4xl mx-auto">
          <div className="bg-gray-800 rounded-lg p-8 mb-8">
            <h3 className="text-2xl font-semibold text-white mb-4">Current Proposal</h3>
            <p className="text-gray-400 mb-6">
              "Should RIMAREUM expand into sustainable energy products?"
            </p>
            
            {wallet.isConnected ? (
              <div className="space-y-4">
                <div className="flex justify-center space-x-4">
                  <button className="bg-green-600 hover:bg-green-700 px-8 py-3 rounded transition">
                    Vote YES
                  </button>
                  <button className="bg-red-600 hover:bg-red-700 px-8 py-3 rounded transition">
                    Vote NO
                  </button>
                </div>
                <div className="text-sm text-gray-500">
                  Your voting power: {wallet.balance?.rimar_balance || 0} $RIMAR
                </div>
              </div>
            ) : (
              <div className="text-gray-500">
                Connect your wallet to participate in governance
              </div>
            )}
          </div>
          
          <div className="grid md:grid-cols-3 gap-6 text-center">
            <div className="bg-gray-800 rounded-lg p-6">
              <h4 className="text-xl font-semibold text-blue-400 mb-2">Active Proposals</h4>
              <div className="text-3xl font-bold text-white">3</div>
            </div>
            <div className="bg-gray-800 rounded-lg p-6">
              <h4 className="text-xl font-semibold text-blue-400 mb-2">Total Votes</h4>
              <div className="text-3xl font-bold text-white">1,247</div>
            </div>
            <div className="bg-gray-800 rounded-lg p-6">
              <h4 className="text-xl font-semibold text-blue-400 mb-2">DAO Members</h4>
              <div className="text-3xl font-bold text-white">892</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

// NFT Section
const NFTSection = () => {
  const nfts = [
    {
      id: 1,
      name: "RIMAR Guardian #001",
      description: "Exclusive voting rights NFT",
      price: "0.1 ETH",
      image: "https://images.unsplash.com/photo-1639322537228-f710d846310a?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1Nzh8MHwxfHNlYXJjaHwxfHxibG9ja2NoYWlufGVufDB8fHx8MTc1MjM5MTk5OHww&ixlib=rb-4.1.0&q=85"
    },
    {
      id: 2,
      name: "RIMAR Key #045",
      description: "Platform access key with benefits",
      price: "0.05 ETH",
      image: "https://images.unsplash.com/photo-1639754390580-2e7437267698?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzR8MHwxfHNlYXJjaHwyfHxjcnlwdG9jdXJyZW5jeXxlbnwwfHx8fDE3NTIzNDM2NDR8MA&ixlib=rb-4.1.0&q=85"
    }
  ];

  return (
    <section id="nft" className="py-20 bg-black">
      <div className="container mx-auto px-4">
        <h2 className="text-4xl font-bold text-center text-white mb-12">
          Exclusive NFTs
        </h2>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {nfts.map((nft) => (
            <div key={nft.id} className="bg-gray-800 rounded-lg overflow-hidden shadow-lg hover:shadow-xl transition">
              <img 
                src={nft.image}
                alt={nft.name}
                className="w-full h-48 object-cover"
              />
              <div className="p-6">
                <h3 className="text-xl font-semibold text-white mb-2">{nft.name}</h3>
                <p className="text-gray-400 mb-4">{nft.description}</p>
                <div className="flex justify-between items-center">
                  <span className="text-xl font-bold text-purple-400">{nft.price}</span>
                  <button className="bg-purple-600 hover:bg-purple-700 text-white py-2 px-4 rounded transition">
                    Mint NFT
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

// Payment Success/Cancel Pages
const PaymentSuccess = () => {
  const [status, setStatus] = useState('checking');
  
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const sessionId = urlParams.get('session_id');
    
    if (sessionId) {
      checkPaymentStatus(sessionId);
    }
  }, []);

  const checkPaymentStatus = async (sessionId) => {
    try {
      const response = await axios.get(`${API}/payments/checkout/status/${sessionId}`);
      if (response.data.payment_status === 'paid') {
        setStatus('success');
      } else {
        setStatus('pending');
      }
    } catch (error) {
      console.error('Payment status check failed:', error);
      setStatus('error');
    }
  };

  return (
    <div className="min-h-screen bg-black text-white flex items-center justify-center">
      <div className="text-center">
        {status === 'checking' && <div>Checking payment status...</div>}
        {status === 'success' && (
          <div>
            <h1 className="text-4xl font-bold text-green-400 mb-4">Payment Successful!</h1>
            <p className="text-gray-400 mb-8">Thank you for your purchase on RIMAREUM.</p>
            <button 
              onClick={() => window.location.href = '/'}
              className="bg-blue-600 hover:bg-blue-700 px-8 py-3 rounded transition"
            >
              Return to Home
            </button>
          </div>
        )}
        {status === 'pending' && <div>Payment is still processing...</div>}
        {status === 'error' && <div>Error checking payment status</div>}
      </div>
    </div>
  );
};

// Footer
const Footer = () => {
  return (
    <footer className="bg-black text-white py-12 border-t border-gray-800">
      <div className="container mx-auto px-4">
        <div className="grid md:grid-cols-4 gap-8">
          <div>
            <h3 className="text-xl font-bold text-blue-400 mb-4">RIMAREUM</h3>
            <p className="text-gray-400">
              Revolutionary platform for e-commerce, crypto, NFTs, and DAO governance.
            </p>
          </div>
          <div>
            <h4 className="font-semibold mb-4">Products</h4>
            <ul className="space-y-2 text-gray-400">
              <li>Physical Goods</li>
              <li>Digital Assets</li>
              <li>NFT Marketplace</li>
              <li>AI Services</li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold mb-4">Platform</h4>
            <ul className="space-y-2 text-gray-400">
              <li>DAO Governance</li>
              <li>Wallet Integration</li>
              <li>Crypto Payments</li>
              <li>AI Assistant</li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold mb-4">Community</h4>
            <ul className="space-y-2 text-gray-400">
              <li>Discord</li>
              <li>Twitter</li>
              <li>Telegram</li>
              <li>GitHub</li>
            </ul>
          </div>
        </div>
        <div className="border-t border-gray-800 pt-8 mt-8 text-center text-gray-400">
          <p>&copy; 2025 RIMAREUM. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
};

// Main App Component
const App = () => {
  const wallet = useWallet();
  const [currentPage, setCurrentPage] = useState('home');

  // Check URL for routing
  useEffect(() => {
    const path = window.location.pathname;
    if (path.includes('/payment/success')) {
      setCurrentPage('success');
    } else {
      setCurrentPage('home');
    }
  }, []);

  const contextValue = {
    wallet,
    currentPage,
    setCurrentPage
  };

  if (currentPage === 'success') {
    return (
      <AppContext.Provider value={contextValue}>
        <PaymentSuccess />
      </AppContext.Provider>
    );
  }

  return (
    <AppContext.Provider value={contextValue}>
      <div className="App bg-black min-h-screen">
        <Header />
        <HeroSection />
        <ProductsSection />
        <NFTSection />
        <DAOSection />
        <AIChatSection />
        <Footer />
      </div>
    </AppContext.Provider>
  );
};

export default App;