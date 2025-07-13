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

// Wallet Integration Hook
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
        
        const response = await axios.get(`${API}/wallet/balance/${accounts[0]}`);
        setBalance(response.data);
        
        return accounts[0];
      } catch (error) {
        console.error("Wallet connection failed:", error);
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

// Header Component with Navigation
const Header = () => {
  const { wallet, currentPage, setCurrentPage } = useApp();

  const navItems = [
    { id: 'home', label: 'Home' },
    { id: 'products', label: 'Products' },
    { id: 'nft', label: 'NFT Marketplace' },
    { id: 'dao', label: 'DAO Governance' },
    { id: 'ai', label: 'AI Assistant' },
    { id: 'account', label: 'My Account' },
    { id: 'about', label: 'About Us' },
    { id: 'contact', label: 'Contact' },
    { id: 'legal', label: 'Legal' },
    { id: 'track', label: 'Track Order' }
  ];

  return (
    <header className="bg-gradient-to-r from-gray-900 to-blue-900 text-white border-b border-blue-500 shadow-lg">
      <div className="container mx-auto px-4 py-4">
        <div className="flex justify-between items-center">
          <div className="flex items-center space-x-8">
            <h1 
              className="text-2xl font-bold text-blue-300 cursor-pointer hover:text-blue-200 transition"
              onClick={() => setCurrentPage('home')}
            >
              RIMAREUM
            </h1>
            <nav className="hidden lg:flex space-x-6">
              {navItems.map((item) => (
                <button
                  key={item.id}
                  onClick={() => setCurrentPage(item.id)}
                  className={`hover:text-blue-300 transition ${
                    currentPage === item.id ? 'text-blue-300 border-b border-blue-300' : ''
                  }`}
                >
                  {item.label}
                </button>
              ))}
            </nav>
          </div>
          
          <div className="flex items-center space-x-4">
            {wallet.isConnected ? (
              <div className="flex items-center space-x-3">
                <div className="text-sm">
                  <div className="text-blue-300">{wallet.account.slice(0, 6)}...{wallet.account.slice(-4)}</div>
                  <div className="text-xs text-gray-400">
                    {wallet.balance?.rimar_balance || 0} $RIMAR
                  </div>
                </div>
                <button
                  onClick={wallet.disconnectWallet}
                  className="bg-red-600 hover:bg-red-700 px-3 py-2 rounded-lg text-sm transition"
                >
                  Disconnect
                </button>
              </div>
            ) : (
              <button
                onClick={wallet.connectWallet}
                className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 px-6 py-2 rounded-lg font-semibold transition shadow-lg"
              >
                Connect Wallet
              </button>
            )}
          </div>
        </div>
        
        {/* Mobile Navigation */}
        <nav className="lg:hidden mt-4 grid grid-cols-3 gap-2">
          {navItems.slice(0, 10).map((item) => (
            <button
              key={item.id}
              onClick={() => setCurrentPage(item.id)}
              className={`text-sm py-2 px-1 rounded transition ${
                currentPage === item.id 
                  ? 'bg-blue-600 text-white' 
                  : 'hover:bg-blue-800'
              }`}
            >
              {item.label}
            </button>
          ))}
        </nav>
      </div>
    </header>
  );
};

// Home Page
const HomePage = () => {
  const { setCurrentPage } = useApp();
  
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900 text-white py-20">
        <div className="absolute inset-0 opacity-30">
          <img 
            src="https://images.unsplash.com/photo-1640161704729-cbe966a08476?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzR8MHwxfHNlYXJjaHwxfHxjcnlwdG9jdXJyZW5jeXxlbnwwfHx8fDE3NTIzNDM2NDR8MA&ixlib=rb-4.1.0&q=85"
            alt="Cryptocurrency"
            className="w-full h-full object-cover"
          />
        </div>
        <div className="relative container mx-auto px-4 text-center">
          <h1 className="text-6xl font-bold mb-6 bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
            RIMAREUM – Quantum Marketplace for the Brave
          </h1>
          <p className="text-xl mb-8 max-w-4xl mx-auto text-gray-300">
            The revolutionary ecosystem where physical commerce meets digital sovereignty. 
            Trade premium products, mint exclusive NFTs, participate in DAO governance, 
            and experience AI-powered assistance in our quantum marketplace.
          </p>
          <div className="flex flex-col sm:flex-row justify-center space-y-4 sm:space-y-0 sm:space-x-6">
            <button 
              onClick={() => setCurrentPage('products')}
              className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 px-8 py-4 rounded-lg font-semibold transition shadow-lg"
            >
              Explore Products
            </button>
            <button 
              onClick={() => setCurrentPage('dao')}
              className="border-2 border-blue-400 text-blue-400 hover:bg-blue-400 hover:text-white px-8 py-4 rounded-lg font-semibold transition"
            >
              Join DAO
            </button>
          </div>
        </div>
      </section>

      {/* Features Overview */}
      <section className="py-20 bg-gray-800">
        <div className="container mx-auto px-4">
          <h2 className="text-4xl font-bold text-center text-white mb-12">
            Quantum Commerce Ecosystem
          </h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            <div className="bg-gradient-to-br from-blue-900 to-purple-900 p-6 rounded-lg">
              <h3 className="text-xl font-semibold text-blue-300 mb-3">Premium Products</h3>
              <p className="text-gray-300">Authentic Moroccan Argan Oil, organic Medjool dates, and exclusive items.</p>
            </div>
            <div className="bg-gradient-to-br from-purple-900 to-pink-900 p-6 rounded-lg">
              <h3 className="text-xl font-semibold text-purple-300 mb-3">NFT Marketplace</h3>
              <p className="text-gray-300">Mint and trade exclusive RIMAR NFTs with real utility and governance power.</p>
            </div>
            <div className="bg-gradient-to-br from-green-900 to-blue-900 p-6 rounded-lg">
              <h3 className="text-xl font-semibold text-green-300 mb-3">DAO Governance</h3>
              <p className="text-gray-300">Shape the future through decentralized voting and community decisions.</p>
            </div>
            <div className="bg-gradient-to-br from-yellow-900 to-orange-900 p-6 rounded-lg">
              <h3 className="text-xl font-semibold text-yellow-300 mb-3">AI Assistant</h3>
              <p className="text-gray-300">GPT-powered guidance for all your marketplace and crypto needs.</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

// Products Page
const ProductsPage = () => {
  const { wallet } = useApp();
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    try {
      const response = await axios.get(`${API}/products`);
      setProducts(response.data);
    } catch (error) {
      console.error("Error fetching products:", error);
    } finally {
      setLoading(false);
    }
  };

  const handlePurchase = async (product, paymentType) => {
    try {
      if (paymentType === 'card') {
        const response = await axios.post(`${API}/payments/checkout/session`, {
          product_id: product.id,
          quantity: 1
        }, {
          headers: { 'Origin': window.location.origin }
        });

        if (response.data.url) {
          window.location.href = response.data.url;
        }
      } else {
        if (!wallet.isConnected) {
          alert("Please connect your wallet to use crypto payments!");
          return;
        }
        alert(`Crypto payment for ${product.name} initiated! Transaction will be processed with ${product.crypto_price} $RIMAR tokens.`);
      }
    } catch (error) {
      console.error("Payment error:", error);
      alert("Payment setup failed. Please try again.");
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading products...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 py-12">
      <div className="container mx-auto px-4">
        <h1 className="text-4xl font-bold text-center text-white mb-12">
          Premium Products
        </h1>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {products.map((product) => (
            <div key={product.id} className="bg-gray-800 rounded-lg overflow-hidden shadow-xl hover:shadow-2xl transition">
              <img 
                src={product.image_url || "https://via.placeholder.com/400x300"}
                alt={product.name}
                className="w-full h-64 object-cover"
              />
              <div className="p-6">
                <span className={`inline-block px-3 py-1 rounded-full text-xs font-semibold mb-3 ${
                  product.category === 'physical' ? 'bg-green-600 text-white' :
                  product.category === 'nft' ? 'bg-purple-600 text-white' :
                  'bg-blue-600 text-white'
                }`}>
                  {product.category.toUpperCase()}
                </span>
                <h3 className="text-xl font-semibold text-white mb-2">{product.name}</h3>
                <p className="text-gray-400 mb-4">{product.description}</p>
                <div className="flex justify-between items-center mb-4">
                  <span className="text-2xl font-bold text-blue-400">${product.price}</span>
                  <span className="text-sm text-gray-500">{product.crypto_price} $RIMAR</span>
                </div>
                <div className="flex space-x-2">
                  <button 
                    onClick={() => handlePurchase(product, 'card')}
                    className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-3 px-4 rounded-lg transition font-semibold"
                  >
                    Buy with Card
                  </button>
                  <button 
                    onClick={() => handlePurchase(product, 'crypto')}
                    className="flex-1 bg-purple-600 hover:bg-purple-700 text-white py-3 px-4 rounded-lg transition font-semibold"
                  >
                    Buy with Crypto
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// NFT Marketplace Page
const NFTPage = () => {
  const { wallet } = useApp();
  
  const nfts = [
    {
      id: 1,
      name: "RIMAR Guardian #001",
      description: "Exclusive voting rights NFT with platform governance power",
      price: "0.1 ETH",
      image: "https://images.unsplash.com/photo-1639322537228-f710d846310a?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1Nzh8MHwxfHNlYXJjaHwxfHxibG9ja2NoYWlufGVufDB8fHx8MTc1MjM5MTk5OHww&ixlib=rb-4.1.0&q=85",
      attributes: ["Governance Rights", "Exclusive Access", "Limited Edition"]
    },
    {
      id: 2,
      name: "RIMAR Key #045",
      description: "Platform access key with premium benefits and rewards",
      price: "0.05 ETH",
      image: "https://images.unsplash.com/photo-1639754390580-2e7437267698?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzR8MHwxfHNlYXJjaHwyfHxjcnlwdG9jdXJyZW5jeXxlbnwwfHx8fDE3NTIzNDM2NDR8MA&ixlib=rb-4.1.0&q=85",
      attributes: ["Premium Access", "Reward Multiplier", "Early Features"]
    },
    {
      id: 3,
      name: "Quantum Artifact #777",
      description: "Rare quantum artifact with mystical properties and power",
      price: "0.25 ETH",
      image: "https://images.unsplash.com/photo-1640161704729-cbe966a08476?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzR8MHwxfHNlYXJjaHwxfHxjcnlwdG9jdXJyZW5jeXxlbnwwfHx8fDE3NTIzNDM2NDR8MA&ixlib=rb-4.1.0&q=85",
      attributes: ["Quantum Power", "Ultra Rare", "Mystical Properties"]
    }
  ];

  const handleMintNFT = (nft) => {
    if (!wallet.isConnected) {
      alert("Please connect your wallet to mint NFTs!");
      return;
    }
    alert(`Minting ${nft.name} for ${nft.price}! (Simulation mode)`);
  };

  return (
    <div className="min-h-screen bg-gray-900 py-12">
      <div className="container mx-auto px-4">
        <h1 className="text-4xl font-bold text-center text-white mb-12">
          Exclusive NFT Marketplace
        </h1>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {nfts.map((nft) => (
            <div key={nft.id} className="bg-gray-800 rounded-lg overflow-hidden shadow-xl hover:shadow-2xl transition group">
              <div className="relative overflow-hidden">
                <img 
                  src={nft.image}
                  alt={nft.name}
                  className="w-full h-64 object-cover group-hover:scale-105 transition duration-300"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent opacity-0 group-hover:opacity-100 transition"></div>
              </div>
              <div className="p-6">
                <h3 className="text-xl font-semibold text-white mb-2">{nft.name}</h3>
                <p className="text-gray-400 mb-4">{nft.description}</p>
                
                <div className="mb-4">
                  <h4 className="text-sm font-semibold text-blue-300 mb-2">Attributes:</h4>
                  <div className="flex flex-wrap gap-2">
                    {nft.attributes.map((attr, index) => (
                      <span key={index} className="px-2 py-1 bg-blue-900 text-blue-300 rounded text-xs">
                        {attr}
                      </span>
                    ))}
                  </div>
                </div>
                
                <div className="flex justify-between items-center mb-4">
                  <span className="text-2xl font-bold text-purple-400">{nft.price}</span>
                  <span className="text-sm text-gray-500">Limited Edition</span>
                </div>
                
                <button 
                  onClick={() => handleMintNFT(nft)}
                  className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white py-3 px-4 rounded-lg transition font-semibold"
                >
                  {wallet.isConnected ? 'Mint NFT' : 'Connect Wallet to Mint'}
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// DAO Governance Page
const DAOPage = () => {
  const { wallet } = useApp();
  const [hasVoted, setHasVoted] = useState(false);

  const proposals = [
    {
      id: 1,
      title: "Expand into Sustainable Energy Products",
      description: "Should RIMAREUM add solar panels and sustainable energy solutions to our product lineup?",
      yesVotes: 847,
      noVotes: 234,
      endDate: "2025-08-15",
      status: "Active"
    },
    {
      id: 2,
      title: "Reduce NFT Minting Fees",
      description: "Proposal to reduce NFT minting fees by 50% to increase accessibility.",
      yesVotes: 1203,
      noVotes: 156,
      endDate: "2025-07-30",
      status: "Active"
    }
  ];

  const handleVote = (proposalId, vote) => {
    if (!wallet.isConnected) {
      alert("Please connect your wallet to vote!");
      return;
    }
    setHasVoted(true);
    alert(`Voted ${vote.toUpperCase()} on proposal ${proposalId}! Your vote has been recorded.`);
  };

  const joinDAO = () => {
    if (!wallet.isConnected) {
      alert("Please connect your wallet to join the DAO!");
      return;
    }
    alert("Welcome to RIMAREUM DAO! You now have voting rights and governance power.");
  };

  return (
    <div className="min-h-screen bg-gray-900 py-12">
      <div className="container mx-auto px-4">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-white mb-4">
            DAO Governance
          </h1>
          <p className="text-xl text-gray-300 mb-8">
            Shape the future of RIMAREUM through decentralized decision-making
          </p>
          
          {!wallet.isConnected && (
            <button 
              onClick={joinDAO}
              className="bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700 px-8 py-3 rounded-lg font-semibold transition text-white"
            >
              Connect Wallet to Join DAO
            </button>
          )}
        </div>

        {/* DAO Stats */}
        <div className="grid md:grid-cols-4 gap-6 mb-12">
          <div className="bg-gray-800 rounded-lg p-6 text-center">
            <h3 className="text-2xl font-bold text-blue-400 mb-2">2</h3>
            <p className="text-gray-400">Active Proposals</p>
          </div>
          <div className="bg-gray-800 rounded-lg p-6 text-center">
            <h3 className="text-2xl font-bold text-green-400 mb-2">2,440</h3>
            <p className="text-gray-400">Total Votes Cast</p>
          </div>
          <div className="bg-gray-800 rounded-lg p-6 text-center">
            <h3 className="text-2xl font-bold text-purple-400 mb-2">1,247</h3>
            <p className="text-gray-400">DAO Members</p>
          </div>
          <div className="bg-gray-800 rounded-lg p-6 text-center">
            <h3 className="text-2xl font-bold text-yellow-400 mb-2">{wallet.balance?.rimar_balance || 0}</h3>
            <p className="text-gray-400">Your Voting Power</p>
          </div>
        </div>

        {/* Active Proposals */}
        <div className="space-y-6">
          <h2 className="text-2xl font-bold text-white mb-6">Active Proposals</h2>
          
          {proposals.map((proposal) => (
            <div key={proposal.id} className="bg-gray-800 rounded-lg p-6">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-xl font-semibold text-white mb-2">{proposal.title}</h3>
                  <p className="text-gray-400 mb-4">{proposal.description}</p>
                </div>
                <span className="px-3 py-1 bg-green-600 text-white rounded-full text-sm">
                  {proposal.status}
                </span>
              </div>
              
              <div className="mb-6">
                <div className="flex justify-between text-sm text-gray-400 mb-2">
                  <span>YES: {proposal.yesVotes} votes</span>
                  <span>NO: {proposal.noVotes} votes</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div 
                    className="bg-green-500 h-2 rounded-full" 
                    style={{ width: `${(proposal.yesVotes / (proposal.yesVotes + proposal.noVotes)) * 100}%` }}
                  ></div>
                </div>
              </div>
              
              {wallet.isConnected && !hasVoted ? (
                <div className="flex space-x-4">
                  <button 
                    onClick={() => handleVote(proposal.id, 'yes')}
                    className="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-lg transition"
                  >
                    Vote YES
                  </button>
                  <button 
                    onClick={() => handleVote(proposal.id, 'no')}
                    className="bg-red-600 hover:bg-red-700 text-white px-6 py-2 rounded-lg transition"
                  >
                    Vote NO
                  </button>
                </div>
              ) : wallet.isConnected && hasVoted ? (
                <p className="text-green-400">✓ You have voted on this proposal</p>
              ) : (
                <p className="text-gray-500">Connect your wallet to vote</p>
              )}
              
              <p className="text-sm text-gray-500 mt-4">
                Voting ends: {proposal.endDate}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// AI Assistant Page
const AIPage = () => {
  const [messages, setMessages] = useState([
    { role: "assistant", content: "Hello! I'm your RIMAREUM AI Assistant. How can I help you today?" }
  ]);
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
      const errorMessage = { 
        role: "assistant", 
        content: "I'm currently in simulation mode. Ask me about RIMAREUM products, crypto, NFTs, or DAO governance!" 
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 py-12">
      <div className="container mx-auto px-4 max-w-4xl">
        <h1 className="text-4xl font-bold text-center text-white mb-8">
          AI Assistant
        </h1>
        <p className="text-center text-gray-400 mb-8">
          Get intelligent help with products, crypto, NFTs, and platform features
        </p>
        
        <div className="bg-gray-800 rounded-lg shadow-xl">
          <div className="h-96 overflow-y-auto p-6 border-b border-gray-700">
            {messages.map((msg, index) => (
              <div key={index} className={`mb-4 ${msg.role === 'user' ? 'text-right' : 'text-left'}`}>
                <div className={`inline-block max-w-xs lg:max-w-md px-4 py-3 rounded-lg ${
                  msg.role === 'user' 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-gray-700 text-gray-200'
                }`}>
                  {msg.content}
                </div>
              </div>
            ))}
            {loading && (
              <div className="text-left">
                <div className="inline-block bg-gray-700 text-gray-200 px-4 py-3 rounded-lg">
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                    <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                  </div>
                </div>
              </div>
            )}
          </div>
          
          <div className="p-6">
            <div className="flex space-x-3">
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                placeholder="Ask about products, crypto, DAO, or anything else..."
                className="flex-1 bg-gray-700 text-white px-4 py-3 rounded-lg border border-gray-600 focus:outline-none focus:border-blue-400"
                disabled={loading}
              />
              <button 
                onClick={sendMessage}
                disabled={loading || !inputMessage.trim()}
                className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white px-6 py-3 rounded-lg transition font-semibold"
              >
                Send
              </button>
            </div>
            
            <div className="mt-4 flex flex-wrap gap-2">
              {["What products do you sell?", "How do I mint NFTs?", "Explain DAO voting", "Crypto payment options"].map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => setInputMessage(suggestion)}
                  className="px-3 py-1 bg-gray-700 text-gray-300 rounded-full text-sm hover:bg-gray-600 transition"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// My Account Page
const AccountPage = () => {
  const { wallet } = useApp();
  const [activeTab, setActiveTab] = useState('overview');

  const orderHistory = [
    { id: "ORD-001", product: "Premium Moroccan Argan Oil", amount: "$49.99", status: "Delivered", date: "2025-07-10" },
    { id: "ORD-002", product: "Organic Medjool Dates", amount: "$24.99", status: "Shipped", date: "2025-07-12" }
  ];

  const nftInventory = [
    { id: "NFT-001", name: "RIMAR Guardian #001", acquired: "2025-07-05" },
    { id: "NFT-002", name: "RIMAR Key #045", acquired: "2025-07-08" }
  ];

  if (!wallet.isConnected) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-white mb-4">My Account</h1>
          <p className="text-gray-400 mb-8">Connect your wallet to view your account details</p>
          <button 
            onClick={wallet.connectWallet}
            className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-lg font-semibold transition"
          >
            Connect Wallet
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 py-12">
      <div className="container mx-auto px-4">
        <h1 className="text-4xl font-bold text-white mb-8">My Account</h1>
        
        {/* Account Overview */}
        <div className="bg-gray-800 rounded-lg p-6 mb-8">
          <div className="grid md:grid-cols-3 gap-6">
            <div>
              <h3 className="text-lg font-semibold text-white mb-2">Wallet Address</h3>
              <p className="text-blue-400 font-mono">{wallet.account}</p>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-white mb-2">$RIMAR Balance</h3>
              <p className="text-green-400 text-2xl font-bold">{wallet.balance?.rimar_balance || 0}</p>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-white mb-2">ETH Balance</h3>
              <p className="text-blue-400 text-2xl font-bold">{wallet.balance?.eth_balance || 0}</p>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="mb-8">
          <div className="flex space-x-4 border-b border-gray-700">
            {['overview', 'orders', 'nfts'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`py-2 px-4 font-semibold capitalize ${
                  activeTab === tab 
                    ? 'text-blue-400 border-b-2 border-blue-400' 
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                {tab}
              </button>
            ))}
          </div>
        </div>

        {/* Tab Content */}
        {activeTab === 'overview' && (
          <div className="grid md:grid-cols-2 gap-8">
            <div className="bg-gray-800 rounded-lg p-6">
              <h3 className="text-xl font-semibold text-white mb-4">Recent Activity</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-400">Last Login</span>
                  <span className="text-white">Today, 2:30 PM</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">DAO Votes Cast</span>
                  <span className="text-white">3</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">NFTs Owned</span>
                  <span className="text-white">{wallet.balance?.nft_count || 0}</span>
                </div>
              </div>
            </div>
            
            <div className="bg-gray-800 rounded-lg p-6">
              <h3 className="text-xl font-semibold text-white mb-4">Rewards & Benefits</h3>
              <div className="space-y-3">
                <div className="p-3 bg-blue-900 rounded-lg">
                  <p className="text-blue-300 font-semibold">DAO Member</p>
                  <p className="text-gray-400 text-sm">Full voting rights</p>
                </div>
                <div className="p-3 bg-purple-900 rounded-lg">
                  <p className="text-purple-300 font-semibold">NFT Holder</p>
                  <p className="text-gray-400 text-sm">Exclusive access</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'orders' && (
          <div className="bg-gray-800 rounded-lg overflow-hidden">
            <div className="p-6 border-b border-gray-700">
              <h3 className="text-xl font-semibold text-white">Order History</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-700">
                  <tr>
                    <th className="text-left p-4 text-gray-300">Order ID</th>
                    <th className="text-left p-4 text-gray-300">Product</th>
                    <th className="text-left p-4 text-gray-300">Amount</th>
                    <th className="text-left p-4 text-gray-300">Status</th>
                    <th className="text-left p-4 text-gray-300">Date</th>
                  </tr>
                </thead>
                <tbody>
                  {orderHistory.map((order) => (
                    <tr key={order.id} className="border-b border-gray-700">
                      <td className="p-4 text-blue-400 font-mono">{order.id}</td>
                      <td className="p-4 text-white">{order.product}</td>
                      <td className="p-4 text-green-400">{order.amount}</td>
                      <td className="p-4">
                        <span className={`px-2 py-1 rounded-full text-xs ${
                          order.status === 'Delivered' ? 'bg-green-600 text-white' : 'bg-yellow-600 text-white'
                        }`}>
                          {order.status}
                        </span>
                      </td>
                      <td className="p-4 text-gray-400">{order.date}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {activeTab === 'nfts' && (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {nftInventory.map((nft) => (
              <div key={nft.id} className="bg-gray-800 rounded-lg p-6">
                <h4 className="text-lg font-semibold text-white mb-2">{nft.name}</h4>
                <p className="text-gray-400 mb-4">Acquired: {nft.acquired}</p>
                <div className="flex space-x-2">
                  <button className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded transition">
                    View Details
                  </button>
                  <button className="flex-1 bg-purple-600 hover:bg-purple-700 text-white py-2 px-4 rounded transition">
                    Transfer
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

// About Us Page
const AboutPage = () => {
  const { wallet } = useApp();
  
  return (
    <div className="min-h-screen bg-gray-900 py-12">
      <div className="container mx-auto px-4 max-w-4xl">
        <h1 className="text-4xl font-bold text-center text-white mb-8">
          About RIMAREUM
        </h1>
        
        <div className="space-y-8">
          <section className="bg-gray-800 rounded-lg p-8">
            <h2 className="text-2xl font-bold text-blue-400 mb-4">Our Cosmic Vision</h2>
            <p className="text-gray-300 leading-relaxed">
              RIMAREUM represents the convergence of ancient wisdom and quantum technology, 
              creating a revolutionary marketplace that transcends traditional boundaries. 
              We envision a future where commerce, governance, and artificial intelligence 
              unite to empower humanity's evolution into a space-faring civilization.
            </p>
          </section>

          <section className="bg-gray-800 rounded-lg p-8">
            <h2 className="text-2xl font-bold text-purple-400 mb-4">The RIMAREUM Mission</h2>
            <p className="text-gray-300 leading-relaxed mb-4">
              Our mission is to democratize access to premium products, digital assets, 
              and decentralized governance through cutting-edge blockchain technology. 
              We believe in creating value that extends beyond Earth, preparing humanity 
              for interplanetary commerce and governance.
            </p>
            <ul className="list-disc list-inside text-gray-300 space-y-2">
              <li>Provide authentic, premium products sourced from Earth's finest regions</li>
              <li>Enable seamless crypto-commerce with $RIMAR token ecosystem</li>
              <li>Foster community governance through DAO mechanisms</li>
              <li>Bridge physical and digital realms through NFT technology</li>
              <li>Advance AI assistance for enhanced user experience</li>
            </ul>
          </section>

          <section className="bg-gray-800 rounded-lg p-8">
            <h2 className="text-2xl font-bold text-green-400 mb-4">Our Values</h2>
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-lg font-semibold text-white mb-2">Authenticity</h3>
                <p className="text-gray-400">Every product is sourced directly from origin, ensuring purity and quality.</p>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-white mb-2">Innovation</h3>
                <p className="text-gray-400">Pioneering the fusion of traditional commerce with quantum-age technology.</p>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-white mb-2">Community</h3>
                <p className="text-gray-400">Empowering collective decision-making through decentralized governance.</p>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-white mb-2">Sustainability</h3>
                <p className="text-gray-400">Building systems that nurture both Earth and future worlds.</p>
              </div>
            </div>
          </section>

          <section className="bg-gray-800 rounded-lg p-8">
            <h2 className="text-2xl font-bold text-yellow-400 mb-4">The Quantum Journey</h2>
            <p className="text-gray-300 leading-relaxed">
              Founded by visionaries who understand that commerce is the foundation of civilization, 
              RIMAREUM began as a dream to create the first truly quantum marketplace. 
              Our platform serves as humanity's training ground for the economic systems 
              we'll need as we expand beyond Earth, combining the wisdom of ancient trade 
              routes with the limitless possibilities of the quantum realm.
            </p>
          </section>

          <section className="bg-gradient-to-r from-blue-900 to-purple-900 rounded-lg p-8 text-center">
            <h2 className="text-2xl font-bold text-white mb-4">Join the Quantum Revolution</h2>
            <p className="text-gray-200 mb-6">
              Be part of the brave souls shaping the future of commerce and governance.
            </p>
            <button 
              onClick={wallet.isConnected ? null : wallet.connectWallet}
              className={`px-8 py-3 rounded-lg font-semibold transition ${
                wallet.isConnected 
                  ? 'bg-green-600 text-white cursor-default' 
                  : 'bg-white text-blue-900 hover:bg-gray-100'
              }`}
            >
              {wallet.isConnected ? '✓ Wallet Connected' : 'Connect Your Wallet'}
            </button>
          </section>
        </div>
      </div>
    </div>
  );
};

// Contact Page
const ContactPage = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    message: ''
  });
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    // Simulate form submission
    setSubmitted(true);
    setTimeout(() => setSubmitted(false), 3000);
    setFormData({ name: '', email: '', subject: '', message: '' });
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div className="min-h-screen bg-gray-900 py-12">
      <div className="container mx-auto px-4 max-w-4xl">
        <h1 className="text-4xl font-bold text-center text-white mb-8">
          Contact RIMAREUM
        </h1>
        
        <div className="grid md:grid-cols-2 gap-8">
          <div className="bg-gray-800 rounded-lg p-8">
            <h2 className="text-2xl font-bold text-blue-400 mb-6">Get in Touch</h2>
            
            {submitted && (
              <div className="mb-6 p-4 bg-green-600 text-white rounded-lg">
                Thank you! Your message has been sent successfully.
              </div>
            )}
            
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-white mb-2">Name</label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  className="w-full bg-gray-700 text-white px-4 py-3 rounded-lg border border-gray-600 focus:outline-none focus:border-blue-400"
                  required
                />
              </div>
              
              <div>
                <label className="block text-white mb-2">Email</label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  className="w-full bg-gray-700 text-white px-4 py-3 rounded-lg border border-gray-600 focus:outline-none focus:border-blue-400"
                  required
                />
              </div>
              
              <div>
                <label className="block text-white mb-2">Subject</label>
                <select
                  name="subject"
                  value={formData.subject}
                  onChange={handleChange}
                  className="w-full bg-gray-700 text-white px-4 py-3 rounded-lg border border-gray-600 focus:outline-none focus:border-blue-400"
                  required
                >
                  <option value="">Select a subject</option>
                  <option value="general">General Inquiry</option>
                  <option value="products">Product Question</option>
                  <option value="nft">NFT Support</option>
                  <option value="dao">DAO Governance</option>
                  <option value="technical">Technical Support</option>
                  <option value="partnership">Partnership</option>
                </select>
              </div>
              
              <div>
                <label className="block text-white mb-2">Message</label>
                <textarea
                  name="message"
                  value={formData.message}
                  onChange={handleChange}
                  rows="5"
                  className="w-full bg-gray-700 text-white px-4 py-3 rounded-lg border border-gray-600 focus:outline-none focus:border-blue-400"
                  required
                ></textarea>
              </div>
              
              <button
                type="submit"
                className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 px-6 rounded-lg font-semibold transition"
              >
                Send Message
              </button>
            </form>
          </div>
          
          <div className="space-y-6">
            <div className="bg-gray-800 rounded-lg p-6">
              <h3 className="text-xl font-semibold text-white mb-4">Contact Information</h3>
              <div className="space-y-3">
                <div>
                  <h4 className="text-blue-400 font-semibold">Email</h4>
                  <p className="text-gray-300">contact@rimareum.com</p>
                </div>
                <div>
                  <h4 className="text-blue-400 font-semibold">Support</h4>
                  <p className="text-gray-300">support@rimareum.com</p>
                </div>
                <div>
                  <h4 className="text-blue-400 font-semibold">Partnerships</h4>
                  <p className="text-gray-300">partners@rimareum.com</p>
                </div>
              </div>
            </div>
            
            <div className="bg-gray-800 rounded-lg p-6">
              <h3 className="text-xl font-semibold text-white mb-4">Community</h3>
              <div className="space-y-3">
                <a href="#" className="block text-blue-400 hover:text-blue-300 transition">
                  📱 Discord Community
                </a>
                <a href="#" className="block text-blue-400 hover:text-blue-300 transition">
                  🐦 Twitter @RIMAREUM
                </a>
                <a href="#" className="block text-blue-400 hover:text-blue-300 transition">
                  💬 Telegram
                </a>
                <a href="#" className="block text-blue-400 hover:text-blue-300 transition">
                  📚 Documentation
                </a>
              </div>
            </div>
            
            <div className="bg-gray-800 rounded-lg p-6">
              <h3 className="text-xl font-semibold text-white mb-4">Office Hours</h3>
              <div className="space-y-2 text-gray-300">
                <p>Monday - Friday: 9:00 AM - 6:00 PM UTC</p>
                <p>Saturday: 10:00 AM - 4:00 PM UTC</p>
                <p>Sunday: Closed</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Legal Page
const LegalPage = () => {
  const [activeSection, setActiveSection] = useState('terms');

  const sections = [
    { id: 'terms', title: 'Terms of Service' },
    { id: 'privacy', title: 'Privacy Policy' },
    { id: 'gdpr', title: 'GDPR Compliance' },
    { id: 'cookies', title: 'Cookie Policy' }
  ];

  return (
    <div className="min-h-screen bg-gray-900 py-12">
      <div className="container mx-auto px-4 max-w-6xl">
        <h1 className="text-4xl font-bold text-center text-white mb-8">
          Legal Information
        </h1>
        
        <div className="grid md:grid-cols-4 gap-8">
          {/* Sidebar */}
          <div className="md:col-span-1">
            <div className="bg-gray-800 rounded-lg p-4 sticky top-4">
              <h3 className="text-lg font-semibold text-white mb-4">Legal Sections</h3>
              <nav className="space-y-2">
                {sections.map((section) => (
                  <button
                    key={section.id}
                    onClick={() => setActiveSection(section.id)}
                    className={`block w-full text-left px-3 py-2 rounded transition ${
                      activeSection === section.id 
                        ? 'bg-blue-600 text-white' 
                        : 'text-gray-400 hover:text-white hover:bg-gray-700'
                    }`}
                  >
                    {section.title}
                  </button>
                ))}
              </nav>
            </div>
          </div>
          
          {/* Content */}
          <div className="md:col-span-3">
            <div className="bg-gray-800 rounded-lg p-8">
              {activeSection === 'terms' && (
                <div>
                  <h2 className="text-2xl font-bold text-white mb-6">Terms of Service</h2>
                  <div className="space-y-4 text-gray-300">
                    <p><strong>Last Updated:</strong> July 13, 2025</p>
                    
                    <h3 className="text-xl font-semibold text-blue-400 mt-6">1. Acceptance of Terms</h3>
                    <p>
                      By accessing and using RIMAREUM platform, you accept and agree to be bound by the terms 
                      and provision of this agreement. If you do not agree to abide by the above, please do not use this service.
                    </p>
                    
                    <h3 className="text-xl font-semibold text-blue-400 mt-6">2. Platform Description</h3>
                    <p>
                      RIMAREUM is a quantum marketplace combining e-commerce, cryptocurrency, NFTs, and DAO governance. 
                      We facilitate the purchase of premium products, digital assets, and participation in decentralized governance.
                    </p>
                    
                    <h3 className="text-xl font-semibold text-blue-400 mt-6">3. User Responsibilities</h3>
                    <ul className="list-disc list-inside space-y-2">
                      <li>Provide accurate and truthful information</li>
                      <li>Maintain the security of your wallet and account</li>
                      <li>Comply with all applicable laws and regulations</li>
                      <li>Respect intellectual property rights</li>
                      <li>Use the platform for lawful purposes only</li>
                    </ul>
                    
                    <h3 className="text-xl font-semibold text-blue-400 mt-6">4. Cryptocurrency and NFTs</h3>
                    <p>
                      Trading in cryptocurrencies and NFTs involves significant risk. Prices can fluctuate dramatically. 
                      You acknowledge that RIMAREUM is not responsible for market volatility or losses incurred through trading.
                    </p>
                    
                    <h3 className="text-xl font-semibold text-blue-400 mt-6">5. DAO Governance</h3>
                    <p>
                      Participation in DAO governance is voluntary. Voting rights are tied to $RIMAR token holdings. 
                      All votes are final and binding upon the community.
                    </p>
                    
                    <h3 className="text-xl font-semibold text-blue-400 mt-6">6. Limitation of Liability</h3>
                    <p>
                      RIMAREUM shall not be liable for any indirect, incidental, special, consequential, or punitive damages 
                      resulting from your use of the platform.
                    </p>
                  </div>
                </div>
              )}

              {activeSection === 'privacy' && (
                <div>
                  <h2 className="text-2xl font-bold text-white mb-6">Privacy Policy</h2>
                  <div className="space-y-4 text-gray-300">
                    <p><strong>Last Updated:</strong> July 13, 2025</p>
                    
                    <h3 className="text-xl font-semibold text-blue-400 mt-6">Information We Collect</h3>
                    <ul className="list-disc list-inside space-y-2">
                      <li>Wallet addresses and transaction data</li>
                      <li>Usage analytics and platform interactions</li>
                      <li>Communication preferences</li>
                      <li>Device and browser information</li>
                    </ul>
                    
                    <h3 className="text-xl font-semibold text-blue-400 mt-6">How We Use Information</h3>
                    <ul className="list-disc list-inside space-y-2">
                      <li>Provide and improve our services</li>
                      <li>Process transactions and orders</li>
                      <li>Communicate important updates</li>
                      <li>Ensure platform security</li>
                      <li>Comply with legal obligations</li>
                    </ul>
                    
                    <h3 className="text-xl font-semibold text-blue-400 mt-6">Data Protection</h3>
                    <p>
                      We implement industry-standard security measures to protect your personal information. 
                      Your wallet data is never stored on our servers, and all transactions are secured by blockchain technology.
                    </p>
                    
                    <h3 className="text-xl font-semibold text-blue-400 mt-6">Third-Party Services</h3>
                    <p>
                      We may use third-party services for analytics, payment processing, and other functionality. 
                      These services have their own privacy policies that govern the use of your information.
                    </p>
                  </div>
                </div>
              )}

              {activeSection === 'gdpr' && (
                <div>
                  <h2 className="text-2xl font-bold text-white mb-6">GDPR Compliance</h2>
                  <div className="space-y-4 text-gray-300">
                    <p>
                      RIMAREUM is committed to protecting the privacy and personal data of all users, 
                      including those in the European Union, in accordance with the General Data Protection Regulation (GDPR).
                    </p>
                    
                    <h3 className="text-xl font-semibold text-blue-400 mt-6">Your Rights Under GDPR</h3>
                    <ul className="list-disc list-inside space-y-2">
                      <li><strong>Right to Access:</strong> Request information about your personal data</li>
                      <li><strong>Right to Rectification:</strong> Correct inaccurate personal data</li>
                      <li><strong>Right to Erasure:</strong> Request deletion of your personal data</li>
                      <li><strong>Right to Portability:</strong> Receive your data in a structured format</li>
                      <li><strong>Right to Object:</strong> Object to processing of your personal data</li>
                      <li><strong>Right to Restrict:</strong> Limit how we process your data</li>
                    </ul>
                    
                    <h3 className="text-xl font-semibold text-blue-400 mt-6">Legal Basis for Processing</h3>
                    <p>We process your personal data based on:</p>
                    <ul className="list-disc list-inside space-y-2">
                      <li>Contractual necessity for platform services</li>
                      <li>Legitimate business interests</li>
                      <li>Legal compliance requirements</li>
                      <li>Your explicit consent where required</li>
                    </ul>
                    
                    <h3 className="text-xl font-semibold text-blue-400 mt-6">Contact Our DPO</h3>
                    <p>
                      For GDPR-related inquiries, contact our Data Protection Officer at: 
                      <span className="text-blue-400"> privacy@rimareum.com</span>
                    </p>
                  </div>
                </div>
              )}

              {activeSection === 'cookies' && (
                <div>
                  <h2 className="text-2xl font-bold text-white mb-6">Cookie Policy</h2>
                  <div className="space-y-4 text-gray-300">
                    <p>
                      RIMAREUM uses cookies and similar technologies to enhance your experience, 
                      analyze usage, and provide personalized content.
                    </p>
                    
                    <h3 className="text-xl font-semibold text-blue-400 mt-6">Types of Cookies We Use</h3>
                    
                    <div className="space-y-4">
                      <div>
                        <h4 className="font-semibold text-white">Essential Cookies</h4>
                        <p>Required for basic platform functionality, including wallet connections and user sessions.</p>
                      </div>
                      
                      <div>
                        <h4 className="font-semibold text-white">Analytics Cookies</h4>
                        <p>Help us understand how you use the platform to improve our services.</p>
                      </div>
                      
                      <div>
                        <h4 className="font-semibold text-white">Preference Cookies</h4>
                        <p>Remember your settings and preferences for a personalized experience.</p>
                      </div>
                      
                      <div>
                        <h4 className="font-semibold text-white">Marketing Cookies</h4>
                        <p>Used to deliver relevant advertisements and track campaign effectiveness.</p>
                      </div>
                    </div>
                    
                    <h3 className="text-xl font-semibold text-blue-400 mt-6">Managing Cookies</h3>
                    <p>
                      You can control cookies through your browser settings. However, disabling certain cookies 
                      may limit platform functionality. Essential cookies cannot be disabled without affecting core features.
                    </p>
                    
                    <h3 className="text-xl font-semibold text-blue-400 mt-6">Third-Party Cookies</h3>
                    <p>
                      Some cookies are set by third-party services we use for analytics, payments, and other functionality. 
                      These are governed by the respective third party's privacy policy.
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Footer Component
const Footer = () => {
  const { setCurrentPage } = useApp();
  
  return (
    <footer className="bg-gray-900 text-white py-12 border-t border-gray-700">
      <div className="container mx-auto px-4">
        <div className="grid md:grid-cols-4 gap-8">
          <div>
            <h3 className="text-xl font-bold text-blue-400 mb-4">RIMAREUM</h3>
            <p className="text-gray-400 mb-4">
              Quantum Marketplace for the Brave. Revolutionary e-commerce meets crypto innovation.
            </p>
            <div className="flex space-x-4">
              <a href="#" className="text-gray-400 hover:text-blue-400 transition">Discord</a>
              <a href="#" className="text-gray-400 hover:text-blue-400 transition">Twitter</a>
              <a href="#" className="text-gray-400 hover:text-blue-400 transition">Telegram</a>
            </div>
          </div>
          
          <div>
            <h4 className="font-semibold mb-4">Products</h4>
            <ul className="space-y-2 text-gray-400">
              <li><button onClick={() => setCurrentPage('products')} className="hover:text-white transition">Premium Products</button></li>
              <li><button onClick={() => setCurrentPage('nft')} className="hover:text-white transition">NFT Marketplace</button></li>
              <li><button onClick={() => setCurrentPage('ai')} className="hover:text-white transition">AI Assistant</button></li>
            </ul>
          </div>
          
          <div>
            <h4 className="font-semibold mb-4">Platform</h4>
            <ul className="space-y-2 text-gray-400">
              <li><button onClick={() => setCurrentPage('dao')} className="hover:text-white transition">DAO Governance</button></li>
              <li><button onClick={() => setCurrentPage('account')} className="hover:text-white transition">My Account</button></li>
              <li><a href="#" className="hover:text-white transition">Documentation</a></li>
            </ul>
          </div>
          
          <div>
            <h4 className="font-semibold mb-4">Support</h4>
            <ul className="space-y-2 text-gray-400">
              <li><button onClick={() => setCurrentPage('contact')} className="hover:text-white transition">Contact Us</button></li>
              <li><button onClick={() => setCurrentPage('about')} className="hover:text-white transition">About Us</button></li>
              <li><button onClick={() => setCurrentPage('legal')} className="hover:text-white transition">Legal</button></li>
            </ul>
          </div>
        </div>
        
        <div className="border-t border-gray-700 pt-8 mt-8 text-center text-gray-400">
          <p>&copy; 2025 RIMAREUM. All rights reserved. Quantum Marketplace for the Brave.</p>
        </div>
      </div>
    </footer>
  );
};

// Main App Component
const App = () => {
  const wallet = useWallet();
  const [currentPage, setCurrentPage] = useState('home');

  const contextValue = {
    wallet,
    currentPage,
    setCurrentPage
  };

  const renderCurrentPage = () => {
    switch (currentPage) {
      case 'home':
        return <HomePage />;
      case 'products':
        return <ProductsPage />;
      case 'nft':
        return <NFTPage />;
      case 'dao':
        return <DAOPage />;
      case 'ai':
        return <AIPage />;
      case 'account':
        return <AccountPage />;
      case 'about':
        return <AboutPage />;
      case 'contact':
        return <ContactPage />;
      case 'legal':
        return <LegalPage />;
      default:
        return <HomePage />;
    }
  };

  return (
    <AppContext.Provider value={contextValue}>
      <div className="App bg-gray-900 min-h-screen">
        <Header />
        {renderCurrentPage()}
        <Footer />
      </div>
    </AppContext.Provider>
  );
};

export default App;