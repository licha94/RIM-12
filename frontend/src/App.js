import React, { useState, useEffect, createContext, useContext } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Context pour la gestion d'état globale
const AppContext = createContext();

const useApp = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error("useApp doit être utilisé dans AppProvider");
  }
  return context;
};

// Hook d'intégration Wallet
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
        console.error("Échec de la connexion du portefeuille:", error);
        // Simuler la connexion du portefeuille pour la démo
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
      // Simuler la connexion du portefeuille pour la démo
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

// Composant Header avec Navigation
const Header = () => {
  const { wallet, currentPage, setCurrentPage } = useApp();

  const navItems = [
    { id: 'home', label: 'Accueil' },
    { id: 'products', label: 'Produits' },
    { id: 'nft', label: 'Marché NFT' },
    { id: 'dao', label: 'Gouvernance DAO' },
    { id: 'ai', label: 'Assistant IA' },
    { id: 'account', label: 'Mon Compte' },
    { id: 'about', label: 'À Propos' },
    { id: 'contact', label: 'Contact' },
    { id: 'legal', label: 'Mentions Légales' },
    { id: 'track', label: 'Suivi Commande' }
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
                  Déconnecter
                </button>
              </div>
            ) : (
              <button
                onClick={wallet.connectWallet}
                className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 px-6 py-2 rounded-lg font-semibold transition shadow-lg"
              >
                Connecter Portefeuille
              </button>
            )}
          </div>
        </div>
        
        {/* Navigation Mobile */}
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

// Page d'Accueil
const HomePage = () => {
  const { setCurrentPage } = useApp();
  
  return (
    <div className="min-h-screen">
      {/* Section Hero */}
      <section className="relative bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900 text-white py-20">
        <div className="absolute inset-0 opacity-30">
          <img 
            src="https://images.unsplash.com/photo-1640161704729-cbe966a08476?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzR8MHwxfHNlYXJjaHwxfHxjcnlwdG9jdXJyZW5jeXxlbnwwfHx8fDE3NTIzNDM2NDR8MA&ixlib=rb-4.1.0&q=85"
            alt="Cryptomonnaie"
            className="w-full h-full object-cover"
          />
        </div>
        <div className="relative container mx-auto px-4 text-center">
          <h1 className="text-6xl font-bold mb-6 bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
            RIMAREUM – Marché Quantique pour les Visionnaires
          </h1>
          <p className="text-xl mb-8 max-w-4xl mx-auto text-gray-300">
            L'écosystème révolutionnaire où le commerce physique rencontre la souveraineté numérique. 
            Échangez des produits premium, créez des NFT exclusifs, participez à la gouvernance DAO, 
            et bénéficiez d'une assistance IA dans notre marché quantique.
          </p>
          <div className="flex flex-col sm:flex-row justify-center space-y-4 sm:space-y-0 sm:space-x-6">
            <button 
              onClick={() => setCurrentPage('products')}
              className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 px-8 py-4 rounded-lg font-semibold transition shadow-lg"
            >
              Explorer les Produits
            </button>
            <button 
              onClick={() => setCurrentPage('dao')}
              className="border-2 border-blue-400 text-blue-400 hover:bg-blue-400 hover:text-white px-8 py-4 rounded-lg font-semibold transition"
            >
              Rejoindre la DAO
            </button>
          </div>
        </div>
      </section>

      {/* Aperçu des Fonctionnalités */}
      <section className="py-20 bg-gray-800">
        <div className="container mx-auto px-4">
          <h2 className="text-4xl font-bold text-center text-white mb-12">
            Écosystème de Commerce Quantique
          </h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            <div className="bg-gradient-to-br from-blue-900 to-purple-900 p-6 rounded-lg">
              <h3 className="text-xl font-semibold text-blue-300 mb-3">Produits Premium</h3>
              <p className="text-gray-300">Huile d'argan marocaine authentique, dattes Medjool bio et articles exclusifs.</p>
            </div>
            <div className="bg-gradient-to-br from-purple-900 to-pink-900 p-6 rounded-lg">
              <h3 className="text-xl font-semibold text-purple-300 mb-3">Marché NFT</h3>
              <p className="text-gray-300">Créez et échangez des NFT RIMAR exclusifs avec utilité réelle et pouvoir de gouvernance.</p>
            </div>
            <div className="bg-gradient-to-br from-green-900 to-blue-900 p-6 rounded-lg">
              <h3 className="text-xl font-semibold text-green-300 mb-3">Gouvernance DAO</h3>
              <p className="text-gray-300">Façonnez l'avenir grâce aux votes décentralisés et aux décisions communautaires.</p>
            </div>
            <div className="bg-gradient-to-br from-yellow-900 to-orange-900 p-6 rounded-lg">
              <h3 className="text-xl font-semibold text-yellow-300 mb-3">Assistant IA</h3>
              <p className="text-gray-300">Guidance alimentée par GPT pour tous vos besoins de marché et crypto.</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

// Page Produits
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
      console.error("Erreur lors du chargement des produits:", error);
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
          alert("Veuillez connecter votre portefeuille pour utiliser les paiements crypto !");
          return;
        }
        alert(`Paiement crypto pour ${product.name} initié ! La transaction sera traitée avec ${product.crypto_price} tokens $RIMAR.`);
      }
    } catch (error) {
      console.error("Erreur de paiement:", error);
      alert("Échec de la configuration du paiement. Veuillez réessayer.");
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-white text-xl">Chargement des produits...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 py-12">
      <div className="container mx-auto px-4">
        <h1 className="text-4xl font-bold text-center text-white mb-12">
          Produits Premium
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
                  {product.category === 'physical' ? 'PHYSIQUE' : 
                   product.category === 'nft' ? 'NFT' : 
                   product.category.toUpperCase()}
                </span>
                <h3 className="text-xl font-semibold text-white mb-2">{product.name}</h3>
                <p className="text-gray-400 mb-4">{product.description}</p>
                <div className="flex justify-between items-center mb-4">
                  <span className="text-2xl font-bold text-blue-400">{product.price}€</span>
                  <span className="text-sm text-gray-500">{product.crypto_price} $RIMAR</span>
                </div>
                <div className="flex space-x-2">
                  <button 
                    onClick={() => handlePurchase(product, 'card')}
                    className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-3 px-4 rounded-lg transition font-semibold"
                  >
                    Acheter par Carte
                  </button>
                  <button 
                    onClick={() => handlePurchase(product, 'crypto')}
                    className="flex-1 bg-purple-600 hover:bg-purple-700 text-white py-3 px-4 rounded-lg transition font-semibold"
                  >
                    Acheter en Crypto
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

// Page Marché NFT
const NFTPage = () => {
  const { wallet } = useApp();
  
  const nfts = [
    {
      id: 1,
      name: "Gardien RIMAR #001",
      description: "NFT exclusif octroyant des droits de vote avec pouvoir de gouvernance de la plateforme",
      price: "0.1 ETH",
      image: "https://images.unsplash.com/photo-1639322537228-f710d846310a?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1Nzh8MHwxfHNlYXJjaHwxfHxibG9ja2NoYWlufGVufDB8fHx8MTc1MjM5MTk5OHww&ixlib=rb-4.1.0&q=85",
      attributes: ["Droits de Gouvernance", "Accès Exclusif", "Édition Limitée"]
    },
    {
      id: 2,
      name: "Clé RIMAR #045",
      description: "Clé d'accès à la plateforme avec avantages premium et récompenses",
      price: "0.05 ETH",
      image: "https://images.unsplash.com/photo-1639754390580-2e7437267698?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzR8MHwxfHNlYXJjaHwyfHxjcnlwdG9jdXJyZW5jeXxlbnwwfHx8fDE3NTIzNDM2NDR8MA&ixlib=rb-4.1.0&q=85",
      attributes: ["Accès Premium", "Multiplicateur de Récompenses", "Fonctionnalités Anticipées"]
    },
    {
      id: 3,
      name: "Artefact Quantique #777",
      description: "Artefact quantique rare aux propriétés mystiques et pouvoirs uniques",
      price: "0.25 ETH",
      image: "https://images.unsplash.com/photo-1640161704729-cbe966a08476?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzR8MHwxfHNlYXJjaHwxfHxjcnlwdG9jdXJyZW5jeXxlbnwwfHx8fDE3NTIzNDM2NDR8MA&ixlib=rb-4.1.0&q=85",
      attributes: ["Pouvoir Quantique", "Ultra Rare", "Propriétés Mystiques"]
    }
  ];

  const handleMintNFT = (nft) => {
    if (!wallet.isConnected) {
      alert("Veuillez connecter votre portefeuille pour créer des NFT !");
      return;
    }
    alert(`Création de ${nft.name} pour ${nft.price} ! (Mode simulation)`);
  };

  return (
    <div className="min-h-screen bg-gray-900 py-12">
      <div className="container mx-auto px-4">
        <h1 className="text-4xl font-bold text-center text-white mb-12">
          Marché NFT Exclusif
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
                  <h4 className="text-sm font-semibold text-blue-300 mb-2">Attributs :</h4>
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
                  <span className="text-sm text-gray-500">Édition Limitée</span>
                </div>
                
                <button 
                  onClick={() => handleMintNFT(nft)}
                  className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white py-3 px-4 rounded-lg transition font-semibold"
                >
                  {wallet.isConnected ? 'Créer NFT' : 'Connecter Portefeuille'}
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// Page Gouvernance DAO
const DAOPage = () => {
  const { wallet } = useApp();
  const [hasVoted, setHasVoted] = useState(false);

  const proposals = [
    {
      id: 1,
      title: "Expansion vers les Produits d'Énergie Durable",
      description: "RIMAREUM devrait-elle ajouter des panneaux solaires et des solutions d'énergie durable à notre gamme de produits ?",
      yesVotes: 847,
      noVotes: 234,
      endDate: "15/08/2025",
      status: "Active"
    },
    {
      id: 2,
      title: "Réduction des Frais de Création NFT",
      description: "Proposition pour réduire les frais de création de NFT de 50% afin d'améliorer l'accessibilité.",
      yesVotes: 1203,
      noVotes: 156,
      endDate: "30/07/2025",
      status: "Active"
    }
  ];

  const handleVote = (proposalId, vote) => {
    if (!wallet.isConnected) {
      alert("Veuillez connecter votre portefeuille pour voter !");
      return;
    }
    setHasVoted(true);
    alert(`Voté ${vote.toUpperCase()} pour la proposition ${proposalId} ! Votre vote a été enregistré.`);
  };

  const joinDAO = () => {
    if (!wallet.isConnected) {
      alert("Veuillez connecter votre portefeuille pour rejoindre la DAO !");
      return;
    }
    alert("Bienvenue dans la DAO RIMAREUM ! Vous avez maintenant des droits de vote et un pouvoir de gouvernance.");
  };

  return (
    <div className="min-h-screen bg-gray-900 py-12">
      <div className="container mx-auto px-4">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-white mb-4">
            Gouvernance DAO
          </h1>
          <p className="text-xl text-gray-300 mb-8">
            Façonnez l'avenir de RIMAREUM grâce à la prise de décision décentralisée
          </p>
          
          {!wallet.isConnected && (
            <button 
              onClick={joinDAO}
              className="bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700 px-8 py-3 rounded-lg font-semibold transition text-white"
            >
              Connecter Portefeuille pour Rejoindre DAO
            </button>
          )}
        </div>

        {/* Statistiques DAO */}
        <div className="grid md:grid-cols-4 gap-6 mb-12">
          <div className="bg-gray-800 rounded-lg p-6 text-center">
            <h3 className="text-2xl font-bold text-blue-400 mb-2">2</h3>
            <p className="text-gray-400">Propositions Actives</p>
          </div>
          <div className="bg-gray-800 rounded-lg p-6 text-center">
            <h3 className="text-2xl font-bold text-green-400 mb-2">2,440</h3>
            <p className="text-gray-400">Votes Exprimés</p>
          </div>
          <div className="bg-gray-800 rounded-lg p-6 text-center">
            <h3 className="text-2xl font-bold text-purple-400 mb-2">1,247</h3>
            <p className="text-gray-400">Membres DAO</p>
          </div>
          <div className="bg-gray-800 rounded-lg p-6 text-center">
            <h3 className="text-2xl font-bold text-yellow-400 mb-2">{wallet.balance?.rimar_balance || 0}</h3>
            <p className="text-gray-400">Votre Pouvoir de Vote</p>
          </div>
        </div>

        {/* Propositions Actives */}
        <div className="space-y-6">
          <h2 className="text-2xl font-bold text-white mb-6">Propositions Actives</h2>
          
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
                  <span>OUI : {proposal.yesVotes} votes</span>
                  <span>NON : {proposal.noVotes} votes</span>
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
                    onClick={() => handleVote(proposal.id, 'oui')}
                    className="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-lg transition"
                  >
                    Voter OUI
                  </button>
                  <button 
                    onClick={() => handleVote(proposal.id, 'non')}
                    className="bg-red-600 hover:bg-red-700 text-white px-6 py-2 rounded-lg transition"
                  >
                    Voter NON
                  </button>
                </div>
              ) : wallet.isConnected && hasVoted ? (
                <p className="text-green-400">✓ Vous avez voté sur cette proposition</p>
              ) : (
                <p className="text-gray-500">Connectez votre portefeuille pour voter</p>
              )}
              
              <p className="text-sm text-gray-500 mt-4">
                Vote se termine le : {proposal.endDate}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// Page Assistant IA
const AIPage = () => {
  const [messages, setMessages] = useState([
    { role: "assistant", content: "Bonjour ! Je suis votre Assistant IA RIMAREUM. Comment puis-je vous aider aujourd'hui ?" }
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
      console.error("Erreur de chat:", error);
      const errorMessage = { 
        role: "assistant", 
        content: "Je suis actuellement en mode simulation. Posez-moi des questions sur les produits RIMAREUM, les cryptos, les NFT ou la gouvernance DAO !" 
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
          Assistant IA
        </h1>
        <p className="text-center text-gray-400 mb-8">
          Obtenez une aide intelligente sur les produits, cryptos, NFT et fonctionnalités de la plateforme
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
                placeholder="Posez des questions sur les produits, crypto, DAO ou autre chose..."
                className="flex-1 bg-gray-700 text-white px-4 py-3 rounded-lg border border-gray-600 focus:outline-none focus:border-blue-400"
                disabled={loading}
              />
              <button 
                onClick={sendMessage}
                disabled={loading || !inputMessage.trim()}
                className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white px-6 py-3 rounded-lg transition font-semibold"
              >
                Envoyer
              </button>
            </div>
            
            <div className="mt-4 flex flex-wrap gap-2">
              {["Quels produits vendez-vous ?", "Comment créer des NFT ?", "Expliquer le vote DAO", "Options de paiement crypto"].map((suggestion, index) => (
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

// Page Mon Compte
const AccountPage = () => {
  const { wallet } = useApp();
  const [activeTab, setActiveTab] = useState('apercu');

  const orderHistory = [
    { id: "CMD-001", product: "Huile d'Argan Marocaine Premium", amount: "49,99€", status: "Livré", date: "10/07/2025" },
    { id: "CMD-002", product: "Dattes Medjool Bio", amount: "24,99€", status: "Expédié", date: "12/07/2025" }
  ];

  const nftInventory = [
    { id: "NFT-001", name: "Gardien RIMAR #001", acquired: "05/07/2025" },
    { id: "NFT-002", name: "Clé RIMAR #045", acquired: "08/07/2025" }
  ];

  if (!wallet.isConnected) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-white mb-4">Mon Compte</h1>
          <p className="text-gray-400 mb-8">Connectez votre portefeuille pour voir les détails de votre compte</p>
          <button 
            onClick={wallet.connectWallet}
            className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-lg font-semibold transition"
          >
            Connecter Portefeuille
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 py-12">
      <div className="container mx-auto px-4">
        <h1 className="text-4xl font-bold text-white mb-8">Mon Compte</h1>
        
        {/* Aperçu du Compte */}
        <div className="bg-gray-800 rounded-lg p-6 mb-8">
          <div className="grid md:grid-cols-3 gap-6">
            <div>
              <h3 className="text-lg font-semibold text-white mb-2">Adresse Portefeuille</h3>
              <p className="text-blue-400 font-mono">{wallet.account}</p>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-white mb-2">Solde $RIMAR</h3>
              <p className="text-green-400 text-2xl font-bold">{wallet.balance?.rimar_balance || 0}</p>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-white mb-2">Solde ETH</h3>
              <p className="text-blue-400 text-2xl font-bold">{wallet.balance?.eth_balance || 0}</p>
            </div>
          </div>
        </div>

        {/* Onglets */}
        <div className="mb-8">
          <div className="flex space-x-4 border-b border-gray-700">
            {['apercu', 'commandes', 'nfts'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`py-2 px-4 font-semibold capitalize ${
                  activeTab === tab 
                    ? 'text-blue-400 border-b-2 border-blue-400' 
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                {tab === 'apercu' ? 'Aperçu' : tab === 'commandes' ? 'Commandes' : 'NFTs'}
              </button>
            ))}
          </div>
        </div>

        {/* Contenu des Onglets */}
        {activeTab === 'apercu' && (
          <div className="grid md:grid-cols-2 gap-8">
            <div className="bg-gray-800 rounded-lg p-6">
              <h3 className="text-xl font-semibold text-white mb-4">Activité Récente</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-400">Dernière Connexion</span>
                  <span className="text-white">Aujourd'hui, 14h30</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Votes DAO Exprimés</span>
                  <span className="text-white">3</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">NFTs Possédés</span>
                  <span className="text-white">{wallet.balance?.nft_count || 0}</span>
                </div>
              </div>
            </div>
            
            <div className="bg-gray-800 rounded-lg p-6">
              <h3 className="text-xl font-semibold text-white mb-4">Récompenses & Avantages</h3>
              <div className="space-y-3">
                <div className="p-3 bg-blue-900 rounded-lg">
                  <p className="text-blue-300 font-semibold">Membre DAO</p>
                  <p className="text-gray-400 text-sm">Droits de vote complets</p>
                </div>
                <div className="p-3 bg-purple-900 rounded-lg">
                  <p className="text-purple-300 font-semibold">Détenteur NFT</p>
                  <p className="text-gray-400 text-sm">Accès exclusif</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'commandes' && (
          <div className="bg-gray-800 rounded-lg overflow-hidden">
            <div className="p-6 border-b border-gray-700">
              <h3 className="text-xl font-semibold text-white">Historique des Commandes</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-700">
                  <tr>
                    <th className="text-left p-4 text-gray-300">ID Commande</th>
                    <th className="text-left p-4 text-gray-300">Produit</th>
                    <th className="text-left p-4 text-gray-300">Montant</th>
                    <th className="text-left p-4 text-gray-300">Statut</th>
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
                          order.status === 'Livré' ? 'bg-green-600 text-white' : 'bg-yellow-600 text-white'
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
                <p className="text-gray-400 mb-4">Acquis le : {nft.acquired}</p>
                <div className="flex space-x-2">
                  <button className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded transition">
                    Voir Détails
                  </button>
                  <button className="flex-1 bg-purple-600 hover:bg-purple-700 text-white py-2 px-4 rounded transition">
                    Transférer
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

// Page À Propos
const AboutPage = () => {
  const { wallet } = useApp();
  
  return (
    <div className="min-h-screen bg-gray-900 py-12">
      <div className="container mx-auto px-4 max-w-4xl">
        <h1 className="text-4xl font-bold text-center text-white mb-8">
          À Propos de RIMAREUM
        </h1>
        
        <div className="space-y-8">
          <section className="bg-gray-800 rounded-lg p-8">
            <h2 className="text-2xl font-bold text-blue-400 mb-4">Notre Vision Cosmique</h2>
            <p className="text-gray-300 leading-relaxed">
              RIMAREUM représente la convergence entre la sagesse ancestrale et la technologie quantique, 
              créant un marché révolutionnaire qui transcende les frontières traditionnelles. 
              Nous envisageons un futur où le commerce, la gouvernance et l'intelligence artificielle 
              s'unissent pour favoriser l'évolution de l'humanité vers une civilisation spatiale.
            </p>
          </section>

          <section className="bg-gray-800 rounded-lg p-8">
            <h2 className="text-2xl font-bold text-purple-400 mb-4">La Mission RIMAREUM</h2>
            <p className="text-gray-300 leading-relaxed mb-4">
              Notre mission est de démocratiser l'accès aux produits premium, aux actifs numériques 
              et à la gouvernance décentralisée grâce à la technologie blockchain de pointe. 
              Nous croyons en la création de valeur qui s'étend au-delà de la Terre, préparant l'humanité 
              au commerce et à la gouvernance interplanétaires.
            </p>
            <ul className="list-disc list-inside text-gray-300 space-y-2">
              <li>Fournir des produits authentiques et premium des meilleures régions de la Terre</li>
              <li>Permettre un crypto-commerce fluide avec l'écosystème de tokens $RIMAR</li>
              <li>Favoriser la gouvernance communautaire grâce aux mécanismes DAO</li>
              <li>Relier les mondes physique et numérique via la technologie NFT</li>
              <li>Faire progresser l'assistance IA pour une expérience utilisateur améliorée</li>
            </ul>
          </section>

          <section className="bg-gray-800 rounded-lg p-8">
            <h2 className="text-2xl font-bold text-green-400 mb-4">Nos Valeurs</h2>
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-lg font-semibold text-white mb-2">Authenticité</h3>
                <p className="text-gray-400">Chaque produit est sourcé directement de son origine, garantissant pureté et qualité.</p>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-white mb-2">Innovation</h3>
                <p className="text-gray-400">Pionnier de la fusion entre commerce traditionnel et technologie de l'ère quantique.</p>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-white mb-2">Communauté</h3>
                <p className="text-gray-400">Autonomiser la prise de décision collective grâce à la gouvernance décentralisée.</p>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-white mb-2">Durabilité</h3>
                <p className="text-gray-400">Construire des systèmes qui nourrissent à la fois la Terre et les mondes futurs.</p>
              </div>
            </div>
          </section>

          <section className="bg-gray-800 rounded-lg p-8">
            <h2 className="text-2xl font-bold text-yellow-400 mb-4">Le Voyage Quantique</h2>
            <p className="text-gray-300 leading-relaxed">
              Fondé par des visionnaires qui comprennent que le commerce est le fondement de la civilisation, 
              RIMAREUM a commencé comme un rêve de créer le premier véritable marché quantique. 
              Notre plateforme sert de terrain d'entraînement pour l'humanité aux systèmes économiques 
              dont nous aurons besoin en nous étendant au-delà de la Terre, combinant la sagesse des anciennes routes commerciales 
              avec les possibilités illimitées du domaine quantique.
            </p>
          </section>

          <section className="bg-gradient-to-r from-blue-900 to-purple-900 rounded-lg p-8 text-center">
            <h2 className="text-2xl font-bold text-white mb-4">Rejoignez la Révolution Quantique</h2>
            <p className="text-gray-200 mb-6">
              Faites partie des âmes courageuses qui façonnent l'avenir du commerce et de la gouvernance.
            </p>
            <button 
              onClick={wallet.isConnected ? null : wallet.connectWallet}
              className={`px-8 py-3 rounded-lg font-semibold transition ${
                wallet.isConnected 
                  ? 'bg-green-600 text-white cursor-default' 
                  : 'bg-white text-blue-900 hover:bg-gray-100'
              }`}
            >
              {wallet.isConnected ? '✓ Portefeuille Connecté' : 'Connecter Votre Portefeuille'}
            </button>
          </section>
        </div>
      </div>
    </div>
  );
};

// Page Contact
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
    // Simuler l'envoi du formulaire
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
          Contacter RIMAREUM
        </h1>
        
        <div className="grid md:grid-cols-2 gap-8">
          <div className="bg-gray-800 rounded-lg p-8">
            <h2 className="text-2xl font-bold text-blue-400 mb-6">Nous Contacter</h2>
            
            {submitted && (
              <div className="mb-6 p-4 bg-green-600 text-white rounded-lg">
                Merci ! Votre message a été envoyé avec succès.
              </div>
            )}
            
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-white mb-2">Nom</label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  placeholder="Votre nom complet"
                  className="w-full bg-gray-700 text-white px-4 py-3 rounded-lg border border-gray-600 focus:outline-none focus:border-blue-400"
                  required
                />
              </div>
              
              <div>
                <label className="block text-white mb-2">E-mail</label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  placeholder="votre.email@exemple.com"
                  className="w-full bg-gray-700 text-white px-4 py-3 rounded-lg border border-gray-600 focus:outline-none focus:border-blue-400"
                  required
                />
              </div>
              
              <div>
                <label className="block text-white mb-2">Sujet</label>
                <select
                  name="subject"
                  value={formData.subject}
                  onChange={handleChange}
                  className="w-full bg-gray-700 text-white px-4 py-3 rounded-lg border border-gray-600 focus:outline-none focus:border-blue-400"
                  required
                >
                  <option value="">Sélectionnez un sujet</option>
                  <option value="general">Demande Générale</option>
                  <option value="products">Question Produit</option>
                  <option value="nft">Support NFT</option>
                  <option value="dao">Gouvernance DAO</option>
                  <option value="technical">Support Technique</option>
                  <option value="partnership">Partenariat</option>
                </select>
              </div>
              
              <div>
                <label className="block text-white mb-2">Message</label>
                <textarea
                  name="message"
                  value={formData.message}
                  onChange={handleChange}
                  rows="5"
                  placeholder="Décrivez votre demande en détail..."
                  className="w-full bg-gray-700 text-white px-4 py-3 rounded-lg border border-gray-600 focus:outline-none focus:border-blue-400"
                  required
                ></textarea>
              </div>
              
              <button
                type="submit"
                className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 px-6 rounded-lg font-semibold transition"
              >
                Envoyer le Message
              </button>
            </form>
          </div>
          
          <div className="space-y-6">
            <div className="bg-gray-800 rounded-lg p-6">
              <h3 className="text-xl font-semibold text-white mb-4">Informations de Contact</h3>
              <div className="space-y-3">
                <div>
                  <h4 className="text-blue-400 font-semibold">E-mail</h4>
                  <p className="text-gray-300">contact@rimareum.com</p>
                </div>
                <div>
                  <h4 className="text-blue-400 font-semibold">Support</h4>
                  <p className="text-gray-300">support@rimareum.com</p>
                </div>
                <div>
                  <h4 className="text-blue-400 font-semibold">Partenariats</h4>
                  <p className="text-gray-300">partenaires@rimareum.com</p>
                </div>
              </div>
            </div>
            
            <div className="bg-gray-800 rounded-lg p-6">
              <h3 className="text-xl font-semibold text-white mb-4">Communauté</h3>
              <div className="space-y-3">
                <a href="#" className="block text-blue-400 hover:text-blue-300 transition">
                  📱 Communauté Discord
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
              <h3 className="text-xl font-semibold text-white mb-4">Heures d'Ouverture</h3>
              <div className="space-y-2 text-gray-300">
                <p>Lundi - Vendredi : 9h00 - 18h00 UTC</p>
                <p>Samedi : 10h00 - 16h00 UTC</p>
                <p>Dimanche : Fermé</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Page Mentions Légales
const LegalPage = () => {
  const [activeSection, setActiveSection] = useState('cgu');

  const sections = [
    { id: 'cgu', title: 'Conditions Générales d\'Utilisation' },
    { id: 'privacy', title: 'Politique de Confidentialité' },
    { id: 'gdpr', title: 'Conformité RGPD' },
    { id: 'cookies', title: 'Politique des Cookies' },
    { id: 'cgv', title: 'Conditions Générales de Vente' }
  ];

  return (
    <div className="min-h-screen bg-gray-900 py-12">
      <div className="container mx-auto px-4 max-w-6xl">
        <h1 className="text-4xl font-bold text-center text-white mb-8">
          Mentions Légales
        </h1>
        
        <div className="grid md:grid-cols-4 gap-8">
          {/* Barre Latérale */}
          <div className="md:col-span-1">
            <div className="bg-gray-800 rounded-lg p-4 sticky top-4">
              <h3 className="text-lg font-semibold text-white mb-4">Sections Légales</h3>
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
          
          {/* Contenu */}
          <div className="md:col-span-3">
            <div className="bg-gray-800 rounded-lg p-8">
              {activeSection === 'cgu' && (
                <div>
                  <h2 className="text-2xl font-bold text-white mb-6">Conditions Générales d'Utilisation</h2>
                  <div className="space-y-4 text-gray-300">
                    <p><strong>Dernière mise à jour :</strong> 13 juillet 2025</p>
                    
                    <h3 className="text-xl font-semibold text-blue-400 mt-6">1. Acceptation des Conditions</h3>
                    <p>
                      En accédant et en utilisant la plateforme RIMAREUM, vous acceptez et vous engagez à respecter les termes 
                      et dispositions de cet accord. Si vous n'acceptez pas de vous conformer aux dispositions ci-dessus, veuillez ne pas utiliser ce service.
                    </p>
                    
                    <h3 className="text-xl font-semibold text-blue-400 mt-6">2. Description de la Plateforme</h3>
                    <p>
                      RIMAREUM est un marché quantique combinant e-commerce, cryptomonnaie, NFT et gouvernance DAO. 
                      Nous facilitons l'achat de produits premium, d'actifs numériques et la participation à la gouvernance décentralisée.
                    </p>
                    
                    <h3 className="text-xl font-semibold text-blue-400 mt-6">3. Responsabilités de l'Utilisateur</h3>
                    <ul className="list-disc list-inside space-y-2">
                      <li>Fournir des informations exactes et véridiques</li>
                      <li>Maintenir la sécurité de votre portefeuille et compte</li>
                      <li>Respecter toutes les lois et réglementations applicables</li>
                      <li>Respecter les droits de propriété intellectuelle</li>
                      <li>Utiliser la plateforme uniquement à des fins légales</li>
                    </ul>
                    
                    <h3 className="text-xl font-semibold text-blue-400 mt-6">4. Cryptomonnaies et NFT</h3>
                    <p>
                      Le trading de cryptomonnaies et NFT implique des risques significatifs. Les prix peuvent fluctuer dramatiquement. 
                      Vous reconnaissez que RIMAREUM n'est pas responsable de la volatilité du marché ou des pertes encourues lors des échanges.
                    </p>
                    
                    <h3 className="text-xl font-semibold text-blue-400 mt-6">5. Gouvernance DAO</h3>
                    <p>
                      La participation à la gouvernance DAO est volontaire. Les droits de vote sont liés aux détentions de tokens $RIMAR. 
                      Tous les votes sont définitifs et contraignants pour la communauté.
                    </p>
                    
                    <h3 className="text-xl font-semibold text-blue-400 mt-6">6. Limitation de Responsabilité</h3>
                    <p>
                      RIMAREUM ne sera pas responsable de dommages indirects, accessoires, spéciaux, consécutifs ou punitifs 
                      résultant de votre utilisation de la plateforme.
                    </p>
                  </div>
                </div>
              )}

              {activeSection === 'privacy' && (
                <div>
                  <h2 className="text-2xl font-bold text-white mb-6">Politique de Confidentialité</h2>
                  <div className="space-y-4 text-gray-300">
                    <p><strong>Dernière mise à jour :</strong> 13 juillet 2025</p>
                    
                    <h3 className="text-xl font-semibold text-blue-400 mt-6">Informations que Nous Collectons</h3>
                    <ul className="list-disc list-inside space-y-2">
                      <li>Adresses de portefeuille et données de transaction</li>
                      <li>Analyses d'utilisation et interactions avec la plateforme</li>
                      <li>Préférences de communication</li>
                      <li>Informations sur l'appareil et le navigateur</li>
                    </ul>
                    
                    <h3 className="text-xl font-semibold text-blue-400 mt-6">Comment Nous Utilisons les Informations</h3>
                    <ul className="list-disc list-inside space-y-2">
                      <li>Fournir et améliorer nos services</li>
                      <li>Traiter les transactions et commandes</li>
                      <li>Communiquer les mises à jour importantes</li>
                      <li>Assurer la sécurité de la plateforme</li>
                      <li>Respecter les obligations légales</li>
                    </ul>
                    
                    <h3 className="text-xl font-semibold text-blue-400 mt-6">Protection des Données</h3>
                    <p>
                      Nous mettons en place des mesures de sécurité standard de l'industrie pour protéger vos informations personnelles. 
                      Vos données de portefeuille ne sont jamais stockées sur nos serveurs, et toutes les transactions sont sécurisées par la technologie blockchain.
                    </p>
                    
                    <h3 className="text-xl font-semibold text-blue-400 mt-6">Services Tiers</h3>
                    <p>
                      Nous pouvons utiliser des services tiers pour l'analyse, le traitement des paiements et d'autres fonctionnalités. 
                      Ces services ont leurs propres politiques de confidentialité qui régissent l'utilisation de vos informations.
                    </p>
                  </div>
                </div>
              )}

              {activeSection === 'gdpr' && (
                <div>
                  <h2 className="text-2xl font-bold text-white mb-6">Conformité RGPD</h2>
                  <div className="space-y-4 text-gray-300">
                    <p>
                      RIMAREUM s'engage à protéger la confidentialité et les données personnelles de tous les utilisateurs, 
                      y compris ceux de l'Union européenne, conformément au Règlement général sur la protection des données (RGPD).
                    </p>
                    
                    <h3 className="text-xl font-semibold text-blue-400 mt-6">Vos Droits Sous le RGPD</h3>
                    <ul className="list-disc list-inside space-y-2">
                      <li><strong>Droit d'Accès :</strong> Demander des informations sur vos données personnelles</li>
                      <li><strong>Droit de Rectification :</strong> Corriger les données personnelles inexactes</li>
                      <li><strong>Droit à l'Effacement :</strong> Demander la suppression de vos données personnelles</li>
                      <li><strong>Droit à la Portabilité :</strong> Recevoir vos données dans un format structuré</li>
                      <li><strong>Droit d'Opposition :</strong> S'opposer au traitement de vos données personnelles</li>
                      <li><strong>Droit de Limitation :</strong> Limiter la façon dont nous traitons vos données</li>
                    </ul>
                    
                    <h3 className="text-xl font-semibold text-blue-400 mt-6">Base Légale pour le Traitement</h3>
                    <p>Nous traitons vos données personnelles sur la base de :</p>
                    <ul className="list-disc list-inside space-y-2">
                      <li>Nécessité contractuelle pour les services de la plateforme</li>
                      <li>Intérêts commerciaux légitimes</li>
                      <li>Exigences de conformité légale</li>
                      <li>Votre consentement explicite lorsque requis</li>
                    </ul>
                    
                    <h3 className="text-xl font-semibold text-blue-400 mt-6">Contacter Notre DPO</h3>
                    <p>
                      Pour les demandes liées au RGPD, contactez notre Délégué à la Protection des Données à : 
                      <span className="text-blue-400"> confidentialite@rimareum.com</span>
                    </p>
                  </div>
                </div>
              )}

              {activeSection === 'cookies' && (
                <div>
                  <h2 className="text-2xl font-bold text-white mb-6">Politique des Cookies</h2>
                  <div className="space-y-4 text-gray-300">
                    <p>
                      RIMAREUM utilise des cookies et technologies similaires pour améliorer votre expérience, 
                      analyser l'utilisation et fournir du contenu personnalisé.
                    </p>
                    
                    <h3 className="text-xl font-semibold text-blue-400 mt-6">Types de Cookies que Nous Utilisons</h3>
                    
                    <div className="space-y-4">
                      <div>
                        <h4 className="font-semibold text-white">Cookies Essentiels</h4>
                        <p>Requis pour les fonctionnalités de base de la plateforme, y compris les connexions de portefeuille et les sessions utilisateur.</p>
                      </div>
                      
                      <div>
                        <h4 className="font-semibold text-white">Cookies d'Analyse</h4>
                        <p>Nous aident à comprendre comment vous utilisez la plateforme pour améliorer nos services.</p>
                      </div>
                      
                      <div>
                        <h4 className="font-semibold text-white">Cookies de Préférence</h4>
                        <p>Mémorisent vos paramètres et préférences pour une expérience personnalisée.</p>
                      </div>
                      
                      <div>
                        <h4 className="font-semibold text-white">Cookies Marketing</h4>
                        <p>Utilisés pour diffuser des publicités pertinentes et suivre l'efficacité des campagnes.</p>
                      </div>
                    </div>
                    
                    <h3 className="text-xl font-semibold text-blue-400 mt-6">Gestion des Cookies</h3>
                    <p>
                      Vous pouvez contrôler les cookies via les paramètres de votre navigateur. Cependant, désactiver certains cookies 
                      peut limiter les fonctionnalités de la plateforme. Les cookies essentiels ne peuvent pas être désactivés sans affecter les fonctionnalités principales.
                    </p>
                    
                    <h3 className="text-xl font-semibold text-blue-400 mt-6">Cookies Tiers</h3>
                    <p>
                      Certains cookies sont définis par des services tiers que nous utilisons pour l'analyse, les paiements et d'autres fonctionnalités. 
                      Ceux-ci sont régis par la politique de confidentialité respective du tiers.
                    </p>
                  </div>
                </div>
              )}

              {activeSection === 'cgv' && (
                <div>
                  <h2 className="text-2xl font-bold text-white mb-6">Conditions Générales de Vente</h2>
                  <div className="space-y-4 text-gray-300">
                    <p><strong>Dernière mise à jour :</strong> 13 juillet 2025</p>
                    
                    <h3 className="text-xl font-semibold text-blue-400 mt-6">1. Champ d'Application</h3>
                    <p>
                      Les présentes Conditions Générales de Vente (CGV) s'appliquent à toutes les ventes de produits physiques, 
                      NFT et services numériques proposés sur la plateforme RIMAREUM.
                    </p>
                    
                    <h3 className="text-xl font-semibold text-blue-400 mt-6">2. Produits et Prix</h3>
                    <ul className="list-disc list-inside space-y-2">
                      <li>Les prix sont exprimés en euros (€) et en tokens $RIMAR</li>
                      <li>Les prix incluent la TVA applicable</li>
                      <li>Les frais de livraison sont indiqués avant validation de commande</li>
                      <li>RIMAREUM se réserve le droit de modifier les prix à tout moment</li>
                    </ul>
                    
                    <h3 className="text-xl font-semibold text-blue-400 mt-6">3. Commande et Paiement</h3>
                    <p>
                      Les commandes peuvent être payées par carte bancaire via Stripe ou par cryptomonnaie. 
                      Le paiement est exigible immédiatement à la commande.
                    </p>
                    
                    <h3 className="text-xl font-semibold text-blue-400 mt-6">4. Livraison</h3>
                    <ul className="list-disc list-inside space-y-2">
                      <li>Livraison sous 3-7 jours ouvrés pour les produits physiques</li>
                      <li>Livraison instantanée pour les NFT et produits numériques</li>
                      <li>Frais de port calculés selon destination</li>
                    </ul>
                    
                    <h3 className="text-xl font-semibold text-blue-400 mt-6">5. Droit de Rétractation</h3>
                    <p>
                      Conformément au Code de la consommation, vous disposez d'un délai de 14 jours pour exercer votre droit de rétractation 
                      pour les produits physiques. Les NFT et produits numériques ne sont pas rétractables.
                    </p>
                    
                    <h3 className="text-xl font-semibold text-blue-400 mt-6">6. Garanties</h3>
                    <p>
                      Tous nos produits physiques bénéficient de la garantie légale de conformité et de la garantie contre les vices cachés.
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

// Page Suivi Commande
const TrackOrderPage = () => {
  const [orderId, setOrderId] = useState('');
  const [orderStatus, setOrderStatus] = useState(null);
  const [loading, setLoading] = useState(false);

  const trackOrder = () => {
    if (!orderId.trim()) {
      alert('Veuillez entrer un ID de commande valide');
      return;
    }
    
    setLoading(true);
    // Simuler un appel API
    setTimeout(() => {
      const mockStatuses = [
        { status: 'En Préparation', description: 'Votre commande est en cours de préparation', date: '13/07/2025' },
        { status: 'Expédiée', description: 'Commande expédiée via Livraison Express', date: '14/07/2025' },
        { status: 'En Transit', description: 'Le colis est en route vers vous', date: '15/07/2025' },
        { status: 'Livrée', description: 'Livré avec succès à votre adresse', date: '16/07/2025' }
      ];
      
      setOrderStatus({
        orderId: orderId,
        currentStatus: 'En Transit',
        estimatedDelivery: '16/07/2025',
        trackingSteps: mockStatuses
      });
      setLoading(false);
    }, 1500);
  };

  return (
    <div className="min-h-screen bg-gray-900 py-12">
      <div className="container mx-auto px-4 max-w-4xl">
        <h1 className="text-4xl font-bold text-center text-white mb-8">
          Suivi de Commande
        </h1>
        
        <div className="bg-gray-800 rounded-lg p-8 mb-8">
          <h2 className="text-2xl font-bold text-blue-400 mb-6">Détails de la Commande</h2>
          
          <div className="flex space-x-4">
            <input
              type="text"
              value={orderId}
              onChange={(e) => setOrderId(e.target.value)}
              placeholder="Entrez l'ID de commande (ex: CMD-001, CMD-002)"
              className="flex-1 bg-gray-700 text-white px-4 py-3 rounded-lg border border-gray-600 focus:outline-none focus:border-blue-400"
            />
            <button
              onClick={trackOrder}
              disabled={loading}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white px-8 py-3 rounded-lg font-semibold transition"
            >
              {loading ? 'Recherche...' : 'Suivre Commande'}
            </button>
          </div>
          
          <div className="mt-4 text-gray-400 text-sm">
            Essayez les IDs d'exemple : CMD-001, CMD-002, ou NFT-001
          </div>
        </div>

        {orderStatus && (
          <div className="bg-gray-800 rounded-lg p-8">
            <h3 className="text-xl font-bold text-white mb-6">Statut de la Commande</h3>
            
            <div className="grid md:grid-cols-3 gap-6 mb-8">
              <div className="text-center">
                <h4 className="text-lg font-semibold text-blue-400 mb-2">ID Commande</h4>
                <p className="text-white font-mono">{orderStatus.orderId}</p>
              </div>
              <div className="text-center">
                <h4 className="text-lg font-semibold text-green-400 mb-2">Statut Actuel</h4>
                <p className="text-white">{orderStatus.currentStatus}</p>
              </div>
              <div className="text-center">
                <h4 className="text-lg font-semibold text-purple-400 mb-2">Livraison Estimée</h4>
                <p className="text-white">{orderStatus.estimatedDelivery}</p>
              </div>
            </div>

            <div className="space-y-4">
              <h4 className="text-lg font-semibold text-white mb-4">Chronologie de Suivi</h4>
              {orderStatus.trackingSteps.map((step, index) => (
                <div key={index} className="flex items-center space-x-4 p-4 bg-gray-700 rounded-lg">
                  <div className={`w-4 h-4 rounded-full ${
                    index <= 2 ? 'bg-green-500' : 'bg-gray-500'
                  }`}></div>
                  <div className="flex-1">
                    <h5 className="font-semibold text-white">{step.status}</h5>
                    <p className="text-gray-400">{step.description}</p>
                  </div>
                  <div className="text-gray-400 text-sm">{step.date}</div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// Composant Footer
const Footer = () => {
  const { setCurrentPage } = useApp();
  
  return (
    <footer className="bg-gray-900 text-white py-12 border-t border-gray-700">
      <div className="container mx-auto px-4">
        <div className="grid md:grid-cols-4 gap-8">
          <div>
            <h3 className="text-xl font-bold text-blue-400 mb-4">RIMAREUM</h3>
            <p className="text-gray-400 mb-4">
              Marché Quantique pour les Visionnaires. E-commerce révolutionnaire rencontre l'innovation crypto.
            </p>
            <div className="flex space-x-4">
              <a href="#" className="text-gray-400 hover:text-blue-400 transition">Discord</a>
              <a href="#" className="text-gray-400 hover:text-blue-400 transition">Twitter</a>
              <a href="#" className="text-gray-400 hover:text-blue-400 transition">Telegram</a>
            </div>
          </div>
          
          <div>
            <h4 className="font-semibold mb-4">Produits</h4>
            <ul className="space-y-2 text-gray-400">
              <li><button onClick={() => setCurrentPage('products')} className="hover:text-white transition">Produits Premium</button></li>
              <li><button onClick={() => setCurrentPage('nft')} className="hover:text-white transition">Marché NFT</button></li>
              <li><button onClick={() => setCurrentPage('ai')} className="hover:text-white transition">Assistant IA</button></li>
            </ul>
          </div>
          
          <div>
            <h4 className="font-semibold mb-4">Plateforme</h4>
            <ul className="space-y-2 text-gray-400">
              <li><button onClick={() => setCurrentPage('dao')} className="hover:text-white transition">Gouvernance DAO</button></li>
              <li><button onClick={() => setCurrentPage('account')} className="hover:text-white transition">Mon Compte</button></li>
              <li><button onClick={() => setCurrentPage('track')} className="hover:text-white transition">Suivi Commande</button></li>
            </ul>
          </div>
          
          <div>
            <h4 className="font-semibold mb-4">Support</h4>
            <ul className="space-y-2 text-gray-400">
              <li><button onClick={() => setCurrentPage('contact')} className="hover:text-white transition">Nous Contacter</button></li>
              <li><button onClick={() => setCurrentPage('about')} className="hover:text-white transition">À Propos</button></li>
              <li><button onClick={() => setCurrentPage('legal')} className="hover:text-white transition">Mentions Légales</button></li>
            </ul>
          </div>
        </div>
        
        <div className="border-t border-gray-700 pt-8 mt-8 text-center text-gray-400">
          <p>&copy; 2025 RIMAREUM. Tous droits réservés. Marché Quantique pour les Visionnaires.</p>
          <div className="mt-2 space-x-4">
            <button onClick={() => setCurrentPage('legal')} className="hover:text-white transition">Mentions Légales</button>
            <span>•</span>
            <button onClick={() => setCurrentPage('legal')} className="hover:text-white transition">Conditions Générales de Vente</button>
            <span>•</span>
            <button onClick={() => setCurrentPage('legal')} className="hover:text-white transition">Politique de Confidentialité</button>
          </div>
        </div>
      </div>
    </footer>
  );
};

// Composant Principal App
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
      case 'track':
        return <TrackOrderPage />;
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