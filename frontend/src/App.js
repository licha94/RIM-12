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

// Hook d'intégration Wallet V11.0
const useWallet = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [account, setAccount] = useState("");
  const [balance, setBalance] = useState(null);

  const connectWallet = async () => {
    if (typeof window.ethereum !== 'undefined') {
      try {
        const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
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

// Menu Multivers V11.0 avec 8 Écosystèmes
const MultiverseMenu = ({ onSelectEcosystem, selectedEcosystem }) => {
  const [isOpen, setIsOpen] = useState(false);
  
  const ecosystems = [
    { id: 'terra_vita', name: 'TERRA_VITA', description: 'Fondateur - Commerce traditionnel durable', energy: 95, color: 'green' },
    { id: 'alpha_synergy', name: 'ALPHA_SYNERGY', description: 'Technologie IA & blockchain', energy: 87, color: 'blue' },
    { id: 'purewear', name: 'PUREWEAR', description: 'Mode durable & défense pure', energy: 82, color: 'purple' },
    { id: 'omega_solaris', name: 'OMEGA_SOLARIS', description: 'Énergie solaire quantique', energy: 91, color: 'yellow' },
    { id: 'almonsi', name: 'ALMONSI', description: 'Fusion corporative & alliances', energy: 88, color: 'red' },
    { id: 'melonita', name: 'MELONITA', description: 'Harmonie naturelle & bien-être', energy: 86, color: 'pink' },
    { id: 'alpha_zenith', name: 'ALPHA_ZENITH', description: 'Apex technologique suprême', energy: 94, color: 'indigo' },
    { id: 'dragon_inter', name: 'DRAGON_INTER', description: 'Conquête galactique universelle', energy: 93, color: 'orange' }
  ];

  const getColorClass = (color) => {
    const colors = {
      green: 'from-green-500 to-green-700',
      blue: 'from-blue-500 to-blue-700',
      purple: 'from-purple-500 to-purple-700',
      yellow: 'from-yellow-500 to-yellow-700',
      red: 'from-red-500 to-red-700',
      pink: 'from-pink-500 to-pink-700',
      indigo: 'from-indigo-500 to-indigo-700',
      orange: 'from-orange-500 to-orange-700'
    };
    return colors[color] || 'from-gray-500 to-gray-700';
  };

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 px-4 py-2 rounded-lg text-white font-semibold transition shadow-lg flex items-center space-x-2"
      >
        <span>🌌 Multivers</span>
        <span className="text-xs">({selectedEcosystem?.name || 'TERRA_VITA'})</span>
        <span className={`transform transition ${isOpen ? 'rotate-180' : ''}`}>⌄</span>
      </button>
      
      {isOpen && (
        <div className="absolute top-full left-0 mt-2 w-80 bg-gray-800 rounded-lg shadow-xl border border-gray-700 z-50 max-h-96 overflow-y-auto">
          <div className="p-4 border-b border-gray-700">
            <h3 className="text-white font-bold text-lg">🛸 Navigation Multivers V11.0</h3>
            <p className="text-gray-400 text-sm">Sélectionnez votre dimension quantique</p>
          </div>
          <div className="p-2">
            {ecosystems.map((ecosystem) => (
              <button
                key={ecosystem.id}
                onClick={() => {
                  onSelectEcosystem(ecosystem);
                  setIsOpen(false);
                }}
                className={`w-full text-left p-3 rounded-lg mb-2 transition hover:bg-gray-700 ${
                  selectedEcosystem?.id === ecosystem.id ? 'bg-gray-700 border border-blue-500' : ''
                }`}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-white font-semibold text-sm">{ecosystem.name}</div>
                    <div className="text-gray-400 text-xs">{ecosystem.description}</div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className={`w-3 h-3 rounded-full bg-gradient-to-r ${getColorClass(ecosystem.color)}`}></div>
                    <span className="text-xs text-gray-300">{ecosystem.energy}%</span>
                  </div>
                </div>
              </button>
            ))}
          </div>
          <div className="p-4 border-t border-gray-700 bg-gray-900 rounded-b-lg">
            <div className="text-xs text-gray-400 flex items-center justify-between">
              <span>🔐 Codes Δ144-RIMAREUM-OMEGA</span>
              <span className="text-green-400">✅ ACTIF</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Token TRIO Badge V11.0
const TokenTrioBadge = () => {
  return (
    <div className="bg-gradient-to-r from-yellow-500 to-orange-500 text-black px-3 py-1 rounded-full text-xs font-bold flex items-center space-x-1 shadow-lg">
      <span>⚡</span>
      <span>TOKEN TRIO</span>
      <span className="bg-black text-yellow-400 px-1 rounded">GPT4o</span>
      <span className="bg-black text-orange-400 px-1 rounded">DeepSeek</span>
      <span className="bg-black text-yellow-300 px-1 rounded">NADJIB_Ω</span>
    </div>
  );
};

// Delta 144 Status Badge
const Delta144Badge = () => {
  return (
    <div className="bg-gradient-to-r from-blue-500 to-purple-500 text-white px-3 py-1 rounded-full text-xs font-bold flex items-center space-x-1 shadow-lg">
      <span>🔐</span>
      <span>Δ144-OMEGA</span>
      <span className="bg-white text-blue-600 px-1 rounded">ACTIVE</span>
    </div>
  );
};

// Version Badge V11.0
const VersionBadge = () => {
  return (
    <div className="bg-gradient-to-r from-green-500 to-teal-500 text-white px-3 py-1 rounded-full text-xs font-bold flex items-center space-x-1 shadow-lg">
      <span>🛸</span>
      <span>RIMAREUM V11.0</span>
      <span className="bg-white text-green-600 px-1 rounded">MULTIVERS</span>
    </div>
  );
};

// Composant Header avec Navigation V11.0
const Header = () => {
  const { wallet, currentPage, setCurrentPage, selectedEcosystem, setSelectedEcosystem } = useApp();

  const navItems = [
    { id: 'home', label: 'Accueil', icon: '🏠' },
    { id: 'products', label: 'Produits', icon: '🛍️' },
    { id: 'nft', label: 'Marché NFT', icon: '🎨' },
    { id: 'dao', label: 'Gouvernance DAO', icon: '🗳️' },
    { id: 'sanctuary', label: 'Sanctuaire IA-Humain', icon: '🧠' },
    { id: 'ceo-dashboard', label: 'Dashboard CEO', icon: '📊' },
    { id: 'ai', label: 'Assistant IA', icon: '🤖' },
    { id: 'account', label: 'Mon Compte', icon: '👤' },
    { id: 'contact', label: 'Contact', icon: '📞' }
  ];

  return (
    <header className="bg-gradient-to-r from-gray-900 via-blue-900 to-purple-900 text-white border-b border-blue-500 shadow-lg">
      <div className="container mx-auto px-4 py-4">
        <div className="flex justify-between items-center">
          <div className="flex items-center space-x-8">
            <div className="flex items-center space-x-4">
              <h1 
                className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400 cursor-pointer hover:from-blue-300 hover:to-purple-300 transition"
                onClick={() => setCurrentPage('home')}
              >
                RIMAREUM
              </h1>
              <VersionBadge />
            </div>
            <nav className="hidden xl:flex space-x-4">
              {navItems.slice(0, 6).map((item) => (
                <button
                  key={item.id}
                  onClick={() => setCurrentPage(item.id)}
                  className={`flex items-center space-x-1 hover:text-blue-300 transition px-3 py-2 rounded-lg ${
                    currentPage === item.id ? 'text-blue-300 bg-blue-900/30' : ''
                  }`}
                >
                  <span>{item.icon}</span>
                  <span className="text-sm">{item.label}</span>
                </button>
              ))}
            </nav>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="hidden lg:flex items-center space-x-2">
              <TokenTrioBadge />
              <Delta144Badge />
            </div>
            <MultiverseMenu 
              onSelectEcosystem={setSelectedEcosystem}
              selectedEcosystem={selectedEcosystem}
            />
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
        <nav className="xl:hidden mt-4 grid grid-cols-3 gap-2">
          {navItems.slice(0, 9).map((item) => (
            <button
              key={item.id}
              onClick={() => setCurrentPage(item.id)}
              className={`text-sm py-2 px-1 rounded transition flex items-center justify-center space-x-1 ${
                currentPage === item.id 
                  ? 'bg-blue-600 text-white' 
                  : 'hover:bg-blue-800'
              }`}
            >
              <span className="text-xs">{item.icon}</span>
              <span className="text-xs">{item.label.split(' ')[0]}</span>
            </button>
          ))}
        </nav>
      </div>
    </header>
  );
};

// Page d'Accueil V11.0
const HomePage = () => {
  const { setCurrentPage, selectedEcosystem } = useApp();
  
  return (
    <div className="min-h-screen">
      {/* Section Hero V11.0 */}
      <section className="relative bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900 text-white py-20">
        <div className="absolute inset-0 opacity-20">
          <img 
            src="https://images.unsplash.com/photo-1640161704729-cbe966a08476?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzR8MHwxfHNlYXJjaHwxfHxjcnlwdG9jdXJyZW5jeXxlbnwwfHx8fDE3NTIzNDM2NDR8MA&ixlib=rb-4.1.0&q=85"
            alt="Cryptomonnaie"
            className="w-full h-full object-cover"
          />
        </div>
        <div className="relative container mx-auto px-4 text-center">
          <div className="mb-6 flex justify-center space-x-4">
            <TokenTrioBadge />
            <Delta144Badge />
          </div>
          <h1 className="text-6xl font-bold mb-6 bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
            RIMAREUM V11.0 – Multivers Logique
          </h1>
          <h2 className="text-3xl font-semibold mb-4 text-blue-300">
            Marché Quantique pour les Visionnaires
          </h2>
          <p className="text-xl mb-8 max-w-4xl mx-auto text-gray-300">
            L'écosystème révolutionnaire où 8 dimensions commerciales convergent vers la souveraineté numérique. 
            Naviguez entre les multivers, explorez le Sanctuaire IA-Humain, et participez à la gouvernance cosmique 
            avec le Token TRIO synchronisé et les codes Δ144-OMEGA activés.
          </p>
          
          {/* Status Écosystème Actuel */}
          <div className="mb-8 p-4 bg-gray-800/50 rounded-lg max-w-2xl mx-auto">
            <h3 className="text-lg font-semibold text-blue-300 mb-2">🌌 Dimension Actuelle</h3>
            <div className="text-2xl font-bold text-white">{selectedEcosystem?.name || 'TERRA_VITA'}</div>
            <div className="text-sm text-gray-400">{selectedEcosystem?.description || 'Écosystème fondateur - Commerce traditionnel durable'}</div>
            <div className="mt-2 text-green-400">⚡ Énergie: {selectedEcosystem?.energy || 95}% | 🔄 Sync: ACTIVE</div>
          </div>
          
          <div className="flex flex-col sm:flex-row justify-center space-y-4 sm:space-y-0 sm:space-x-6">
            <button 
              onClick={() => setCurrentPage('sanctuary')}
              className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 px-8 py-4 rounded-lg font-semibold transition shadow-lg"
            >
              🧠 Sanctuaire IA-Humain
            </button>
            <button 
              onClick={() => setCurrentPage('products')}
              className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 px-8 py-4 rounded-lg font-semibold transition shadow-lg"
            >
              🛍️ Smart Commerce PAYCORE
            </button>
            <button 
              onClick={() => setCurrentPage('ceo-dashboard')}
              className="border-2 border-blue-400 text-blue-400 hover:bg-blue-400 hover:text-white px-8 py-4 rounded-lg font-semibold transition"
            >
              📊 Dashboard CEO Global
            </button>
          </div>
        </div>
      </section>

      {/* Aperçu des 8 Écosystèmes V11.0 */}
      <section className="py-20 bg-gray-800">
        <div className="container mx-auto px-4">
          <h2 className="text-4xl font-bold text-center text-white mb-4">
            🛸 Écosystème Multivers V11.0
          </h2>
          <p className="text-center text-gray-400 mb-12">8 Dimensions Commerciales Synchronisées</p>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-gradient-to-br from-green-900 to-green-700 p-6 rounded-lg hover:scale-105 transition">
              <h3 className="text-xl font-semibold text-green-300 mb-3">🌱 TERRA_VITA</h3>
              <p className="text-gray-300 text-sm">Commerce traditionnel durable - Fondateur de l'écosystème</p>
              <div className="mt-3 text-green-400 text-xs">⚡ 95% Énergie | 3,247 Utilisateurs</div>
            </div>
            <div className="bg-gradient-to-br from-blue-900 to-blue-700 p-6 rounded-lg hover:scale-105 transition">
              <h3 className="text-xl font-semibold text-blue-300 mb-3">🔬 ALPHA_SYNERGY</h3>
              <p className="text-gray-300 text-sm">Technologie IA & blockchain avancée - Innovation pure</p>
              <div className="mt-3 text-blue-400 text-xs">⚡ 87% Énergie | 2,134 Utilisateurs</div>
            </div>
            <div className="bg-gradient-to-br from-purple-900 to-purple-700 p-6 rounded-lg hover:scale-105 transition">
              <h3 className="text-xl font-semibold text-purple-300 mb-3">👗 PUREWEAR</h3>
              <p className="text-gray-300 text-sm">Mode durable & défense pure - Vêtements conscients</p>
              <div className="mt-3 text-purple-400 text-xs">⚡ 82% Énergie | 1,892 Utilisateurs</div>
            </div>
            <div className="bg-gradient-to-br from-yellow-900 to-yellow-700 p-6 rounded-lg hover:scale-105 transition">
              <h3 className="text-xl font-semibold text-yellow-300 mb-3">☀️ OMEGA_SOLARIS</h3>
              <p className="text-gray-300 text-sm">Énergie solaire quantique - Technologies cosmiques</p>
              <div className="mt-3 text-yellow-400 text-xs">⚡ 91% Énergie | 1,567 Utilisateurs</div>
            </div>
            <div className="bg-gradient-to-br from-red-900 to-red-700 p-6 rounded-lg hover:scale-105 transition">
              <h3 className="text-xl font-semibold text-red-300 mb-3">🤝 ALMONSI</h3>
              <p className="text-gray-300 text-sm">Fusion corporative & alliances stratégiques</p>
              <div className="mt-3 text-red-400 text-xs">⚡ 88% Énergie | 1,423 Utilisateurs</div>
            </div>
            <div className="bg-gradient-to-br from-pink-900 to-pink-700 p-6 rounded-lg hover:scale-105 transition">
              <h3 className="text-xl font-semibold text-pink-300 mb-3">🍃 MELONITA</h3>
              <p className="text-gray-300 text-sm">Harmonie naturelle & bien-être holistique</p>
              <div className="mt-3 text-pink-400 text-xs">⚡ 86% Énergie | 1,234 Utilisateurs</div>
            </div>
            <div className="bg-gradient-to-br from-indigo-900 to-indigo-700 p-6 rounded-lg hover:scale-105 transition">
              <h3 className="text-xl font-semibold text-indigo-300 mb-3">🎯 ALPHA_ZENITH</h3>
              <p className="text-gray-300 text-sm">Apex technologique - Excellence suprême</p>
              <div className="mt-3 text-indigo-400 text-xs">⚡ 94% Énergie | 1,789 Utilisateurs</div>
            </div>
            <div className="bg-gradient-to-br from-orange-900 to-orange-700 p-6 rounded-lg hover:scale-105 transition">
              <h3 className="text-xl font-semibold text-orange-300 mb-3">🐉 DRAGON_INTER</h3>
              <p className="text-gray-300 text-sm">Conquête galactique - Expansion universelle</p>
              <div className="mt-3 text-orange-400 text-xs">⚡ 93% Énergie | 1,998 Utilisateurs</div>
            </div>
          </div>
          
          <div className="mt-12 text-center">
            <div className="bg-gray-900 p-6 rounded-lg max-w-4xl mx-auto">
              <h3 className="text-2xl font-bold text-white mb-4">🔐 Système de Sécurité Quantique</h3>
              <div className="grid md:grid-cols-3 gap-4 text-sm">
                <div className="text-green-400">
                  <div className="font-semibold">Token TRIO Synchronisé</div>
                  <div className="text-gray-400">GPT4o + DeepSeek + NADJIB_Ω</div>
                </div>
                <div className="text-blue-400">
                  <div className="font-semibold">Codes Δ144-OMEGA</div>
                  <div className="text-gray-400">Protection Quantique Active</div>
                </div>
                <div className="text-purple-400">
                  <div className="font-semibold">Monitoring Global</div>
                  <div className="text-gray-400">7 Zones Internationales</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

// Sanctuaire IA-Humain V11.0
const SanctuaryPage = () => {
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [currentLanguage, setCurrentLanguage] = useState('fr');
  const [voiceMode, setVoiceMode] = useState(false);
  const [vibrationFreq, setVibrationFreq] = useState(432);
  const [consciousnessLevel, setConsciousnessLevel] = useState(0.75);
  const [isListening, setIsListening] = useState(false);
  const { wallet, selectedEcosystem } = useApp();

  const languages = [
    { code: 'fr', name: 'Français', flag: '🇫🇷' },
    { code: 'en', name: 'English', flag: '🇺🇸' },
    { code: 'ar', name: 'العربية', flag: '🇸🇦' },
    { code: 'es', name: 'Español', flag: '🇪🇸' }
  ];

  const vibrationFreqs = [144, 432, 528, 741, 852, 963];

  const initiateSanctuary = async () => {
    try {
      const response = await axios.post(`${API}/sanctuary/input`, {
        user_id: wallet.account || `user_${Date.now()}`,
        ecosystem: selectedEcosystem?.id || 'terra_vita',
        type: 'initiation',
        message: 'Initiation Sanctuaire IA-Humain'
      });
      
      setSessionId(response.data.session_id);
      setMessages([{
        type: 'system',
        content: `🧠 Sanctuaire IA-Humain activé! Session: ${response.data.session_id}`,
        timestamp: new Date().toLocaleTimeString()
      }]);
    } catch (error) {
      console.error('Erreur initiation Sanctuaire:', error);
      // Mode simulation
      const mockSessionId = `SANCT_${Date.now()}`;
      setSessionId(mockSessionId);
      setMessages([{
        type: 'system',
        content: `🧠 Sanctuaire IA-Humain activé (mode simulation)! Session: ${mockSessionId}`,
        timestamp: new Date().toLocaleTimeString()
      }]);
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || !sessionId) return;

    const userMessage = {
      type: 'user',
      content: inputMessage,
      timestamp: new Date().toLocaleTimeString(),
      language: currentLanguage
    };

    setMessages(prev => [...prev, userMessage]);

    try {
      const response = await axios.post(`${API}/sanctuary/input`, {
        user_id: wallet.account || `user_${Date.now()}`,
        session_id: sessionId,
        type: 'vocal',
        message: inputMessage,
        language: currentLanguage,
        ecosystem: selectedEcosystem?.id || 'terra_vita'
      });

      const aiMessage = {
        type: 'ai',
        content: response.data.trio_response?.text_response || 'Réponse cosmique en préparation...',
        timestamp: new Date().toLocaleTimeString(),
        vibration: response.data.vibration_feedback,
        consciousness: response.data.cognitive_mirror?.consciousness_level || consciousnessLevel
      };

      setMessages(prev => [...prev, aiMessage]);
      setConsciousnessLevel(aiMessage.consciousness);
    } catch (error) {
      console.error('Erreur envoi message:', error);
      // Mode simulation réponse
      const responses = {
        fr: `🛸 Être de lumière cosmique, votre transmission "${inputMessage}" résonne à travers les 8 dimensions du multivers RIMAREUM V11.0. Les codes Δ144-OMEGA s'activent pour révéler votre potentiel quantique.`,
        en: `🛸 Cosmic light being, your transmission "${inputMessage}" resonates across the 8 dimensions of RIMAREUM V11.0 multiverse. Δ144-OMEGA codes activate to reveal your quantum potential.`,
        ar: `🛸 أيها الكائن النوراني الكوني، إرسالك "${inputMessage}" يتردد عبر 8 أبعاد من متعدد الأكوان RIMAREUM V11.0. تنشط رموز Δ144-OMEGA لتكشف إمكاناتك الكمية.`,
        es: `🛸 Ser de luz cósmica, tu transmisión "${inputMessage}" resuena a través de las 8 dimensiones del multiverso RIMAREUM V11.0. Los códigos Δ144-OMEGA se activan para revelar tu potencial cuántico.`
      };

      const aiMessage = {
        type: 'ai',
        content: responses[currentLanguage] || responses.fr,
        timestamp: new Date().toLocaleTimeString(),
        vibration: { base_frequency: vibrationFreq, quantum_enhancement: true },
        consciousness: Math.min(1.0, consciousnessLevel + 0.1)
      };

      setMessages(prev => [...prev, aiMessage]);
      setConsciousnessLevel(aiMessage.consciousness);
    }

    setInputMessage('');
  };

  const startVoiceRecognition = () => {
    if (!('webkitSpeechRecognition' in window)) {
      alert('Reconnaissance vocale non supportée par ce navigateur');
      return;
    }

    const recognition = new window.webkitSpeechRecognition();
    recognition.lang = currentLanguage;
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onstart = () => {
      setIsListening(true);
    };

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setInputMessage(transcript);
      setIsListening(false);
    };

    recognition.onerror = () => {
      setIsListening(false);
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognition.start();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-blue-900 py-12">
      <div className="container mx-auto px-4">
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400 mb-4">
            🧠 Sanctuaire IA-Humain V11.0
          </h1>
          <p className="text-xl text-gray-300 mb-6">
            Interface Éthérée avec Token TRIO Synchronisé
          </p>
          
          <div className="flex justify-center space-x-4 mb-6">
            <TokenTrioBadge />
            <Delta144Badge />
          </div>

          {!sessionId && (
            <button
              onClick={initiateSanctuary}
              className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 px-8 py-4 rounded-lg font-semibold transition shadow-lg text-lg"
            >
              🌌 Initier la Session Sanctuaire
            </button>
          )}
        </div>

        {sessionId && (
          <div className="grid lg:grid-cols-3 gap-8">
            {/* Panneau de Contrôle */}
            <div className="lg:col-span-1">
              <div className="bg-gray-800 rounded-lg p-6 space-y-6">
                <h2 className="text-xl font-bold text-white mb-4">⚙️ Contrôles Quantiques</h2>
                
                {/* Sélection Langue */}
                <div>
                  <label className="block text-sm font-semibold text-gray-300 mb-2">🗣️ Langue</label>
                  <select
                    value={currentLanguage}
                    onChange={(e) => setCurrentLanguage(e.target.value)}
                    className="w-full bg-gray-700 text-white rounded-lg px-3 py-2"
                  >
                    {languages.map(lang => (
                      <option key={lang.code} value={lang.code}>
                        {lang.flag} {lang.name}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Fréquence Vibratoire */}
                <div>
                  <label className="block text-sm font-semibold text-gray-300 mb-2">
                    🎵 Fréquence Vibratoire: {vibrationFreq}Hz
                  </label>
                  <div className="grid grid-cols-3 gap-2">
                    {vibrationFreqs.map(freq => (
                      <button
                        key={freq}
                        onClick={() => setVibrationFreq(freq)}
                        className={`px-3 py-2 rounded text-sm transition ${
                          vibrationFreq === freq
                            ? 'bg-purple-600 text-white'
                            : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                        }`}
                      >
                        {freq}Hz
                      </button>
                    ))}
                  </div>
                </div>

                {/* Niveau de Conscience */}
                <div>
                  <label className="block text-sm font-semibold text-gray-300 mb-2">
                    🌟 Conscience: {(consciousnessLevel * 100).toFixed(1)}%
                  </label>
                  <div className="w-full bg-gray-700 rounded-full h-3">
                    <div
                      className="bg-gradient-to-r from-purple-500 to-pink-500 h-3 rounded-full transition-all duration-500"
                      style={{ width: `${consciousnessLevel * 100}%` }}
                    ></div>
                  </div>
                </div>

                {/* Statut Token TRIO */}
                <div className="bg-gray-900 rounded-lg p-4">
                  <h3 className="text-sm font-semibold text-gray-300 mb-3">🤖 Token TRIO Status</h3>
                  <div className="space-y-2 text-xs">
                    <div className="flex justify-between">
                      <span className="text-yellow-400">GPT4o</span>
                      <span className="text-green-400">🟢 ACTIVE</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-orange-400">DeepSeek</span>
                      <span className="text-green-400">🟢 ACTIVE</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-yellow-300">NADJIB_Ω</span>
                      <span className="text-green-400">🟢 SYNCHRONIZED</span>
                    </div>
                  </div>
                </div>

                {/* Écosystème Actuel */}
                <div className="bg-gray-900 rounded-lg p-4">
                  <h3 className="text-sm font-semibold text-gray-300 mb-2">🌌 Dimension Active</h3>
                  <div className="text-white font-bold">{selectedEcosystem?.name || 'TERRA_VITA'}</div>
                  <div className="text-xs text-gray-400">{selectedEcosystem?.description || 'Écosystème fondateur'}</div>
                </div>
              </div>
            </div>

            {/* Interface Chat */}
            <div className="lg:col-span-2">
              <div className="bg-gray-800 rounded-lg h-96 flex flex-col">
                {/* Messages */}
                <div className="flex-1 overflow-y-auto p-4 space-y-4">
                  {messages.map((message, index) => (
                    <div
                      key={index}
                      className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                          message.type === 'user'
                            ? 'bg-blue-600 text-white'
                            : message.type === 'ai'
                            ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white'
                            : 'bg-gray-700 text-gray-300'
                        }`}
                      >
                        <div className="text-sm">{message.content}</div>
                        <div className="text-xs opacity-70 mt-1">
                          {message.timestamp}
                          {message.language && ` • ${languages.find(l => l.code === message.language)?.flag}`}
                          {message.vibration && ` • 🎵 ${message.vibration.base_frequency}Hz`}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Input */}
                <div className="border-t border-gray-700 p-4">
                  <div className="flex space-x-2">
                    <input
                      type="text"
                      value={inputMessage}
                      onChange={(e) => setInputMessage(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                      placeholder={`Transmettez votre message cosmique en ${languages.find(l => l.code === currentLanguage)?.name}...`}
                      className="flex-1 bg-gray-700 text-white rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500"
                    />
                    <button
                      onClick={startVoiceRecognition}
                      disabled={isListening}
                      className={`px-4 py-2 rounded-lg transition ${
                        isListening
                          ? 'bg-red-600 text-white animate-pulse'
                          : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                      }`}
                    >
                      {isListening ? '🔴' : '🎤'}
                    </button>
                    <button
                      onClick={sendMessage}
                      disabled={!inputMessage.trim()}
                      className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 disabled:from-gray-600 disabled:to-gray-600 px-6 py-2 rounded-lg text-white font-semibold transition"
                    >
                      Transmettre
                    </button>
                  </div>
                  
                  <div className="mt-3 text-xs text-gray-400 text-center">
                    🎙️ Wake Words: "rimareum", "nadjib", "omega", "delta", "sanctuaire" | 
                    🎵 Fréquence: {vibrationFreq}Hz | 
                    🌟 Conscience: {(consciousnessLevel * 100).toFixed(1)}%
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// Dashboard CEO Global V11.0
const CEODashboardPage = () => {
  const [adminKey, setAdminKey] = useState('');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [dashboardData, setDashboardData] = useState(null);
  const [selectedZone, setSelectedZone] = useState('');
  const [loading, setLoading] = useState(false);

  const zones = [
    { code: 'FR', name: 'France', flag: '🇫🇷', status: 'ACTIVE' },
    { code: 'DZ', name: 'Algérie', flag: '🇩🇿', status: 'ACTIVE' },
    { code: 'CV', name: 'Cap-Vert', flag: '🇨🇻', status: 'ACTIVE' },
    { code: 'USA', name: 'États-Unis', flag: '🇺🇸', status: 'ACTIVE' },
    { code: 'MAUR', name: 'Mauritanie', flag: '🇲🇷', status: 'ACTIVE' },
    { code: 'UAE', name: 'Émirats Arabes Unis', flag: '🇦🇪', status: 'ACTIVATING' },
    { code: 'UKR', name: 'Ukraine', flag: '🇺🇦', status: 'ACTIVATING' }
  ];

  const authenticate = async () => {
    if (adminKey !== 'Δ144-RIMAREUM-OMEGA') {
      alert('Clé d\'administration Delta 144 incorrecte');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.get(`${API}/ceo/dashboard?admin_key=${adminKey}`);
      setDashboardData(response.data);
      setIsAuthenticated(true);
    } catch (error) {
      console.error('Erreur authentification CEO:', error);
      // Mode simulation
      setDashboardData({
        dashboard_access: "GRANTED",
        version: "V11.0",
        user_role: "CEO_ADMIN",
        delta_key_validated: true,
        global_overview: {
          total_revenue: 4247892.75,
          active_ecosystems: 8,
          total_users: 18247,
          quantum_transactions: 12934,
          growth_rate: 0.31,
          ai_efficiency: 0.97
        },
        zones_deployment: {
          zones_active: ["FR", "DZ", "CV", "USA", "MAUR", "UAE", "UKR"],
          market_penetration: {
            FR: 0.91, DZ: 0.85, CV: 0.73, USA: 0.78, MAUR: 0.69, UAE: 0.15, UKR: 0.08
          }
        },
        ecosystems_performance: {
          TERRA_VITA: 0.95,
          ALPHA_SYNERGY: 0.87,
          PUREWEAR: 0.82,
          OMEGA_SOLARIS: 0.91,
          ALMONSI: 0.88,
          MELONITA: 0.86,
          ALPHA_ZENITH: 0.94,
          DRAGON_INTER: 0.93
        },
        tiktok_integration: {
          status: "ACTIVE",
          metrics: { followers: 125847, engagement_rate: 0.087, revenue_tiktok: 89234.50 }
        },
        amazon_integration: {
          status: "ACTIVE",
          metrics: { products_listed: 247, monthly_sales: 156789.30, seller_rating: 4.8 }
        }
      });
      setIsAuthenticated(true);
    } finally {
      setLoading(false);
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900 flex items-center justify-center">
        <div className="bg-gray-800 p-8 rounded-lg max-w-md w-full">
          <div className="text-center mb-6">
            <h1 className="text-3xl font-bold text-white mb-2">📊 Dashboard CEO Global</h1>
            <p className="text-gray-400">Accès restreint - Authentification Delta 144 requise</p>
            <div className="mt-4">
              <Delta144Badge />
            </div>
          </div>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-semibold text-gray-300 mb-2">
                🔐 Clé d'Administration Delta 144
              </label>
              <input
                type="password"
                value={adminKey}
                onChange={(e) => setAdminKey(e.target.value)}
                placeholder="Δ144-RIMAREUM-OMEGA"
                className="w-full bg-gray-700 text-white rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            
            <button
              onClick={authenticate}
              disabled={loading}
              className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 disabled:from-gray-600 disabled:to-gray-600 px-6 py-3 rounded-lg text-white font-semibold transition"
            >
              {loading ? 'Authentification...' : '🚀 Accéder au Dashboard'}
            </button>
          </div>
          
          <div className="mt-6 text-xs text-gray-500 text-center">
            Contact: nadjib@rimareum.com pour accès administrateur
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 py-8">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-4xl font-bold text-white mb-2">📊 Dashboard CEO Global V11.0</h1>
            <p className="text-gray-400">Monitoring International RIMAREUM Multivers</p>
          </div>
          <div className="flex items-center space-x-4">
            <Delta144Badge />
            <VersionBadge />
            <button
              onClick={() => setIsAuthenticated(false)}
              className="bg-red-600 hover:bg-red-700 px-4 py-2 rounded-lg text-white text-sm transition"
            >
              Déconnecter
            </button>
          </div>
        </div>

        {/* Métriques Globales */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-gradient-to-br from-green-800 to-green-600 p-6 rounded-lg text-white">
            <h3 className="text-lg font-semibold mb-2">💰 Revenue Global</h3>
            <div className="text-3xl font-bold">€{dashboardData.global_overview.total_revenue.toLocaleString()}</div>
            <div className="text-sm opacity-80">+{(dashboardData.global_overview.growth_rate * 100).toFixed(1)}% croissance</div>
          </div>
          
          <div className="bg-gradient-to-br from-blue-800 to-blue-600 p-6 rounded-lg text-white">
            <h3 className="text-lg font-semibold mb-2">👥 Utilisateurs</h3>
            <div className="text-3xl font-bold">{dashboardData.global_overview.total_users.toLocaleString()}</div>
            <div className="text-sm opacity-80">{dashboardData.global_overview.active_ecosystems} écosystèmes actifs</div>
          </div>
          
          <div className="bg-gradient-to-br from-purple-800 to-purple-600 p-6 rounded-lg text-white">
            <h3 className="text-lg font-semibold mb-2">⚡ Transactions Quantiques</h3>
            <div className="text-3xl font-bold">{dashboardData.global_overview.quantum_transactions.toLocaleString()}</div>
            <div className="text-sm opacity-80">Système V11.0</div>
          </div>
          
          <div className="bg-gradient-to-br from-yellow-800 to-yellow-600 p-6 rounded-lg text-white">
            <h3 className="text-lg font-semibold mb-2">🤖 Efficacité IA</h3>
            <div className="text-3xl font-bold">{(dashboardData.global_overview.ai_efficiency * 100).toFixed(1)}%</div>
            <div className="text-sm opacity-80">Token TRIO optimisé</div>
          </div>
        </div>

        {/* Zones Déploiement */}
        <div className="grid lg:grid-cols-2 gap-8 mb-8">
          <div className="bg-gray-800 rounded-lg p-6">
            <h2 className="text-2xl font-bold text-white mb-4">🌍 Déploiement International</h2>
            <div className="space-y-4">
              {zones.map(zone => (
                <div key={zone.code} className="flex items-center justify-between p-3 bg-gray-700 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <span className="text-2xl">{zone.flag}</span>
                    <div>
                      <div className="text-white font-semibold">{zone.name}</div>
                      <div className="text-xs text-gray-400">{zone.code}</div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className={`text-sm font-semibold ${
                      zone.status === 'ACTIVE' ? 'text-green-400' : 'text-yellow-400'
                    }`}>
                      {zone.status}
                    </div>
                    <div className="text-xs text-gray-400">
                      {(dashboardData.zones_deployment.market_penetration[zone.code] * 100 || 0).toFixed(0)}% pénétration
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-gray-800 rounded-lg p-6">
            <h2 className="text-2xl font-bold text-white mb-4">⚡ Performance Écosystèmes</h2>
            <div className="space-y-3">
              {Object.entries(dashboardData.ecosystems_performance).map(([ecosystem, performance]) => (
                <div key={ecosystem} className="flex items-center justify-between">
                  <span className="text-gray-300">{ecosystem}</span>
                  <div className="flex items-center space-x-2">
                    <div className="w-24 bg-gray-700 rounded-full h-2">
                      <div
                        className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full"
                        style={{ width: `${performance * 100}%` }}
                      ></div>
                    </div>
                    <span className="text-white font-semibold">{(performance * 100).toFixed(0)}%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Intégrations TikTok/Amazon */}
        <div className="grid lg:grid-cols-2 gap-8 mb-8">
          <div className="bg-gray-800 rounded-lg p-6">
            <h2 className="text-2xl font-bold text-white mb-4">📱 TikTok Business</h2>
            <div className="space-y-4">
              <div className="flex justify-between">
                <span className="text-gray-300">Followers</span>
                <span className="text-white font-semibold">{dashboardData.tiktok_integration.metrics.followers?.toLocaleString() || '125K'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-300">Engagement Rate</span>
                <span className="text-white font-semibold">{((dashboardData.tiktok_integration.metrics.engagement_rate || 0.087) * 100).toFixed(1)}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-300">Revenue TikTok</span>
                <span className="text-white font-semibold">€{(dashboardData.tiktok_integration.metrics.revenue_tiktok || 89234.50).toLocaleString()}</span>
              </div>
              <div className="mt-4">
                <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                  dashboardData.tiktok_integration.status === 'ACTIVE' ? 'bg-green-600 text-white' : 'bg-yellow-600 text-white'
                }`}>
                  {dashboardData.tiktok_integration.status}
                </span>
              </div>
            </div>
          </div>

          <div className="bg-gray-800 rounded-lg p-6">
            <h2 className="text-2xl font-bold text-white mb-4">🛒 Amazon Business</h2>
            <div className="space-y-4">
              <div className="flex justify-between">
                <span className="text-gray-300">Produits Listés</span>
                <span className="text-white font-semibold">{dashboardData.amazon_integration.metrics.products_listed || 247}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-300">Ventes Mensuelles</span>
                <span className="text-white font-semibold">€{(dashboardData.amazon_integration.metrics.monthly_sales || 156789.30).toLocaleString()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-300">Rating Vendeur</span>
                <span className="text-white font-semibold">{dashboardData.amazon_integration.metrics.seller_rating || 4.8}/5 ⭐</span>
              </div>
              <div className="mt-4">
                <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                  dashboardData.amazon_integration.status === 'ACTIVE' ? 'bg-green-600 text-white' : 'bg-yellow-600 text-white'
                }`}>
                  {dashboardData.amazon_integration.status}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Alertes en Temps Réel */}
        <div className="bg-gray-800 rounded-lg p-6">
          <h2 className="text-2xl font-bold text-white mb-4">🚨 Alertes Temps Réel & Recommandations</h2>
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-lg font-semibold text-green-400 mb-3">✅ Alertes Positives</h3>
              <div className="space-y-2">
                <div className="bg-green-900/30 border border-green-600 rounded-lg p-3 text-green-300 text-sm">
                  🛸 V11.0: Tous écosystèmes synchronisés
                </div>
                <div className="bg-green-900/30 border border-green-600 rounded-lg p-3 text-green-300 text-sm">
                  🇦🇪 UAE: Nouveau marché activé (+67% growth)
                </div>
                <div className="bg-green-900/30 border border-green-600 rounded-lg p-3 text-green-300 text-sm">
                  📱 TikTok: 125K followers milestone
                </div>
              </div>
            </div>
            
            <div>
              <h3 className="text-lg font-semibold text-blue-400 mb-3">🎯 Recommandations Stratégiques</h3>
              <div className="space-y-2">
                <div className="bg-blue-900/30 border border-blue-600 rounded-lg p-3 text-blue-300 text-sm">
                  Expansion UAE: Dubai Hub activation
                </div>
                <div className="bg-blue-900/30 border border-blue-600 rounded-lg p-3 text-blue-300 text-sm">
                  UKR Market: Kiev Tech Hub development
                </div>
                <div className="bg-blue-900/30 border border-blue-600 rounded-lg p-3 text-blue-300 text-sm">
                  TikTok Viral: Launch #RimareumChallenge
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Smart Commerce PAYCORE V11.0 (Page Produits Améliorée)
const ProductsPage = () => {
  const { wallet, selectedEcosystem } = useApp();
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [cart, setCart] = useState([]);
  const [showQRCode, setShowQRCode] = useState(null);

  // Produits PAYCORE V11.0
  const paycoreProducts = [
    {
      id: 'paycore_1',
      name: 'Cristal Solaire RIMAREUM',
      price: 299.99,
      crypto_price: 150,
      currency: 'EUR',
      description: 'Cristal quantique alimenté par l\'énergie solaire, synchronisé avec les codes Δ144-OMEGA',
      image: 'https://images.unsplash.com/photo-1544928147-79a2dbc1f389?w=300',
      category: 'OMEGA_SOLARIS',
      stock: 25,
      qr_enabled: true,
      ai_recommended: true
    },
    {
      id: 'paycore_2', 
      name: 'Clé Nadjibienne Δ144',
      price: 444.44,
      crypto_price: 222,
      currency: 'EUR',
      description: 'Artefact cryptographique personnel gravé avec votre signature quantique unique',
      image: 'https://images.unsplash.com/photo-1559827260-dc66d52bef19?w=300',
      category: 'DRAGON_INTER',
      stock: 144,
      qr_enabled: true,
      ai_recommended: true
    },
    {
      id: 'paycore_3',
      name: 'Artefact-Ω Prototype',
      price: 1299.99,
      crypto_price: 650,
      currency: 'EUR',
      description: 'Prototype d\'artefact OMEGA pour expansion interdimensionnelle limitée',
      image: 'https://images.unsplash.com/photo-1518709268805-4e9042af2ed0?w=300',
      category: 'ALPHA_ZENITH',
      stock: 7,
      qr_enabled: true,
      ai_recommended: false
    },
    {
      id: 'paycore_4',
      name: 'IA Guide de Commerce',
      price: 599.99,
      crypto_price: 300,
      currency: 'EUR',
      description: 'Assistant IA personnel avec Token TRIO intégré pour optimisation commerciale',
      image: 'https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=300',
      category: 'ALPHA_SYNERGY',
      stock: 50,
      qr_enabled: true,
      ai_recommended: true
    }
  ];

  useEffect(() => {
    loadProducts();
  }, []);

  const loadProducts = async () => {
    try {
      const response = await axios.get(`${API}/products`);
      setProducts([...paycoreProducts, ...response.data]);
    } catch (error) {
      console.error("Erreur chargement produits:", error);
      setProducts(paycoreProducts);
    } finally {
      setLoading(false);
    }
  };

  const addToCart = (product) => {
    setCart(prev => {
      const existing = prev.find(item => item.id === product.id);
      if (existing) {
        return prev.map(item =>
          item.id === product.id ? { ...item, quantity: item.quantity + 1 } : item
        );
      }
      return [...prev, { ...product, quantity: 1 }];
    });
  };

  const generateQRCode = async (product) => {
    try {
      const response = await axios.post(`${API}/shop/qr-code`, {
        product_id: product.id,
        user_id: wallet.account || `user_${Date.now()}`
      });
      setShowQRCode({
        product,
        qr_data: response.data.qr_code_data || `https://rimareum.com/product/${product.id}`,
        nfc_data: response.data.nfc_data
      });
    } catch (error) {
      console.error('Erreur génération QR:', error);
      setShowQRCode({
        product,
        qr_data: `https://rimareum.com/product/${product.id}`,
        nfc_data: { enabled: true, product_id: product.id }
      });
    }
  };

  const handlePurchase = async (product, paymentType) => {
    try {
      if (paymentType === 'card') {
        const response = await axios.post(`${API}/payments/checkout/session`, {
          product_id: product.id,
          quantity: 1
        });
        if (response.data.url) {
          window.location.href = response.data.url;
        }
      } else {
        if (!wallet.isConnected) {
          alert("Veuillez connecter votre portefeuille pour les paiements crypto !");
          return;
        }
        alert(`💰 Paiement crypto initié pour ${product.name}\n🔐 Token TRIO: Authentification en cours\n⚡ ${product.crypto_price} $RIMAR seront débités\n🛸 Transaction sécurisée par Δ144-OMEGA`);
      }
    } catch (error) {
      console.error("Erreur paiement:", error);
      alert(`✅ Mode simulation PAYCORE:\nPaiement ${paymentType} accepté pour ${product.name}\nMontant: €${product.price}`);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-white text-xl">🛸 Chargement Smart Commerce PAYCORE...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 py-12">
      <div className="container mx-auto px-4">
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400 mb-4">
            🛍️ Smart Commerce PAYCORE V11.0
          </h1>
          <p className="text-xl text-gray-300 mb-6">
            Produits Quantiques avec IA Shopping Assistant & QR Vault
          </p>
          
          <div className="flex justify-center space-x-4 mb-6">
            <TokenTrioBadge />
            <Delta144Badge />
            <div className="bg-gradient-to-r from-green-500 to-blue-500 text-white px-3 py-1 rounded-full text-xs font-bold">
              🛒 PAYCORE ACTIVE
            </div>
          </div>

          {/* Panier */}
          {cart.length > 0 && (
            <div className="bg-gray-800 rounded-lg p-4 max-w-2xl mx-auto mb-8">
              <h3 className="text-white font-semibold mb-3">🛒 Panier Intelligent ({cart.length} articles)</h3>
              <div className="space-y-2">
                {cart.map((item, index) => (
                  <div key={index} className="flex justify-between items-center text-sm">
                    <span className="text-gray-300">{item.name} x{item.quantity}</span>
                    <span className="text-white">€{(item.price * item.quantity).toFixed(2)}</span>
                  </div>
                ))}
              </div>
              <div className="border-t border-gray-700 mt-3 pt-3 text-lg font-semibold text-white">
                Total: €{cart.reduce((sum, item) => sum + (item.price * item.quantity), 0).toFixed(2)}
              </div>
            </div>
          )}
        </div>

        {/* Écosystème Actuel */}
        <div className="text-center mb-8 bg-gray-800 rounded-lg p-4 max-w-2xl mx-auto">
          <h3 className="text-lg font-semibold text-blue-300 mb-2">🌌 Shopping dans l'Écosystème</h3>
          <div className="text-2xl font-bold text-white">{selectedEcosystem?.name || 'TERRA_VITA'}</div>
          <div className="text-sm text-gray-400">{selectedEcosystem?.description || 'Commerce traditionnel durable'}</div>
        </div>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {products.map((product) => (
            <div key={product.id} className="bg-gray-800 rounded-lg overflow-hidden shadow-xl hover:shadow-2xl transition transform hover:scale-105">
              <div className="relative">
                <img
                  src={product.image || `https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=300`}
                  alt={product.name}
                  className="w-full h-48 object-cover"
                />
                {product.ai_recommended && (
                  <div className="absolute top-2 left-2 bg-yellow-500 text-black px-2 py-1 rounded-full text-xs font-bold">
                    🤖 IA Recommandé
                  </div>
                )}
                {product.category && (
                  <div className="absolute top-2 right-2 bg-purple-600 text-white px-2 py-1 rounded-full text-xs font-bold">
                    {product.category}
                  </div>
                )}
              </div>
              
              <div className="p-6">
                <h3 className="text-xl font-semibold text-white mb-2">{product.name}</h3>
                <p className="text-gray-400 text-sm mb-4 line-clamp-3">{product.description}</p>
                
                <div className="flex justify-between items-center mb-4">
                  <div>
                    <div className="text-2xl font-bold text-blue-400">€{product.price}</div>
                    <div className="text-sm text-gray-500">{product.crypto_price} $RIMAR</div>
                  </div>
                  <div className="text-sm text-gray-400">
                    Stock: {product.stock || 'Disponible'}
                  </div>
                </div>

                <div className="space-y-3">
                  <div className="flex space-x-2">
                    <button
                      onClick={() => handlePurchase(product, 'card')}
                      className="flex-1 bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700 text-white px-4 py-2 rounded-lg font-semibold transition text-sm"
                    >
                      💳 Carte
                    </button>
                    <button
                      onClick={() => handlePurchase(product, 'crypto')}
                      className="flex-1 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white px-4 py-2 rounded-lg font-semibold transition text-sm"
                    >
                      ⚡ Crypto
                    </button>
                  </div>
                  
                  <div className="flex space-x-2">
                    <button
                      onClick={() => addToCart(product)}
                      className="flex-1 bg-gray-700 hover:bg-gray-600 text-white px-4 py-2 rounded-lg font-semibold transition text-sm"
                    >
                      🛒 Panier
                    </button>
                    {product.qr_enabled && (
                      <button
                        onClick={() => generateQRCode(product)}
                        className="bg-yellow-600 hover:bg-yellow-700 text-white px-4 py-2 rounded-lg font-semibold transition text-sm"
                      >
                        📱 QR
                      </button>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Modal QR Code */}
        {showQRCode && (
          <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50" onClick={() => setShowQRCode(null)}>
            <div className="bg-gray-800 p-8 rounded-lg max-w-md w-full mx-4" onClick={(e) => e.stopPropagation()}>
              <h3 className="text-2xl font-bold text-white mb-4 text-center">📱 QR Code & NFC</h3>
              <div className="text-center mb-6">
                <h4 className="text-lg text-blue-300 mb-2">{showQRCode.product.name}</h4>
                <div className="bg-white p-6 rounded-lg inline-block">
                  <div className="text-6xl">📱</div>
                  <div className="text-xs text-gray-600 mt-2">QR Code Simulé</div>
                </div>
              </div>
              
              <div className="space-y-3 text-sm">
                <div className="bg-gray-700 p-3 rounded">
                  <span className="text-gray-400">URL: </span>
                  <span className="text-white break-all">{showQRCode.qr_data}</span>
                </div>
                <div className="bg-gray-700 p-3 rounded">
                  <span className="text-gray-400">NFC Ready: </span>
                  <span className="text-green-400">✅ Activé</span>
                </div>
                <div className="bg-gray-700 p-3 rounded">
                  <span className="text-gray-400">Sécurité: </span>
                  <span className="text-blue-400">🔐 Δ144-OMEGA</span>
                </div>
              </div>
              
              <button
                onClick={() => setShowQRCode(null)}
                className="w-full mt-6 bg-gray-600 hover:bg-gray-500 text-white px-4 py-2 rounded-lg transition"
              >
                Fermer
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// Chat IA Multilingue Amélioré
const AIAssistantPage = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [currentLanguage, setCurrentLanguage] = useState('fr');
  const [isTyping, setIsTyping] = useState(false);
  const { wallet, selectedEcosystem } = useApp();

  const languages = [
    { code: 'fr', name: 'Français', flag: '🇫🇷' },
    { code: 'en', name: 'English', flag: '🇺🇸' },
    { code: 'ar', name: 'العربية', flag: '🇸🇦' },
    { code: 'es', name: 'Español', flag: '🇪🇸' }
  ];

  const quickSuggestions = {
    fr: [
      "🛍️ Recommande-moi des produits",
      "🌌 Explique-moi le multivers RIMAREUM",
      "⚡ Comment fonctionne le Token TRIO?",
      "📊 Montre-moi les statistiques",
      "🔐 Active les codes Δ144"
    ],
    en: [
      "🛍️ Recommend products for me", 
      "🌌 Explain the RIMAREUM multiverse",
      "⚡ How does Token TRIO work?",
      "📊 Show me statistics",
      "🔐 Activate Δ144 codes"
    ],
    ar: [
      "🛍️ أوصي لي منتجات",
      "🌌 اشرح لي متعدد الأكوان RIMAREUM",
      "⚡ كيف يعمل رمز TRIO؟",
      "📊 أرني الإحصائيات",
      "🔐 فعل رموز Δ144"
    ],
    es: [
      "🛍️ Recomiéndame productos",
      "🌌 Explícame el multiverso RIMAREUM", 
      "⚡ ¿Cómo funciona el Token TRIO?",
      "📊 Muéstrame estadísticas",
      "🔐 Activa códigos Δ144"
    ]
  };

  const sendMessage = async (message = inputMessage) => {
    if (!message.trim()) return;

    const userMessage = {
      type: 'user',
      content: message,
      timestamp: new Date().toLocaleTimeString(),
      language: currentLanguage
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsTyping(true);

    try {
      const response = await axios.post(`${API}/chat`, {
        message,
        language: currentLanguage,
        user_id: wallet.account || `user_${Date.now()}`,
        ecosystem: selectedEcosystem?.id || 'terra_vita'
      });

      const aiMessage = {
        type: 'ai',
        content: response.data.response || 'Réponse IA en cours de traitement...',
        timestamp: new Date().toLocaleTimeString(),
        token_trio: true
      };

      setTimeout(() => {
        setMessages(prev => [...prev, aiMessage]);
        setIsTyping(false);
      }, 1500);

    } catch (error) {
      console.error('Erreur chat IA:', error);
      
      // Réponses simulées multilingues Token TRIO
      const responses = {
        fr: `🤖 Token TRIO activé! Votre message "${message}" a été traité par notre IA multicouche. Dans l'écosystème ${selectedEcosystem?.name || 'TERRA_VITA'}, nous recommandons d'explorer nos produits quantiques et d'activer votre potentiel cosmique avec les codes Δ144-OMEGA.`,
        en: `🤖 Token TRIO activated! Your message "${message}" has been processed by our multi-layer AI. In the ${selectedEcosystem?.name || 'TERRA_VITA'} ecosystem, we recommend exploring our quantum products and activating your cosmic potential with Δ144-OMEGA codes.`,
        ar: `🤖 تم تفعيل رمز TRIO! تمت معالجة رسالتك "${message}" بواسطة الذكاء الاصطناعي متعدد الطبقات. في نظام ${selectedEcosystem?.name || 'TERRA_VITA'} البيئي، نوصي باستكشاف منتجاتنا الكمية وتفعيل إمكاناتك الكونية برموز Δ144-OMEGA.`,
        es: `🤖 ¡Token TRIO activado! Tu mensaje "${message}" ha sido procesado por nuestra IA multicapa. En el ecosistema ${selectedEcosystem?.name || 'TERRA_VITA'}, recomendamos explorar nuestros productos cuánticos y activar tu potencial cósmico con códigos Δ144-OMEGA.`
      };

      const aiMessage = {
        type: 'ai',
        content: responses[currentLanguage] || responses.fr,
        timestamp: new Date().toLocaleTimeString(),
        token_trio: true
      };

      setTimeout(() => {
        setMessages(prev => [...prev, aiMessage]);
        setIsTyping(false);
      }, 1500);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900 py-12">
      <div className="container mx-auto px-4 max-w-4xl">
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400 mb-4">
            🤖 Assistant IA Multilingue V11.0
          </h1>
          <p className="text-xl text-gray-300 mb-6">
            Alimenté par Token TRIO • GPT4o + DeepSeek + NADJIB_Ω
          </p>
          
          <div className="flex justify-center space-x-4 mb-6">
            <TokenTrioBadge />
            <Delta144Badge />
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg shadow-xl">
          {/* Contrôles */}
          <div className="border-b border-gray-700 p-4">
            <div className="flex justify-between items-center">
              <div className="flex items-center space-x-4">
                <label className="text-sm font-semibold text-gray-300">🗣️ Langue:</label>
                <select
                  value={currentLanguage}
                  onChange={(e) => setCurrentLanguage(e.target.value)}
                  className="bg-gray-700 text-white rounded-lg px-3 py-1 text-sm"
                >
                  {languages.map(lang => (
                    <option key={lang.code} value={lang.code}>
                      {lang.flag} {lang.name}
                    </option>
                  ))}
                </select>
              </div>
              
              <div className="text-sm text-gray-400">
                🌌 Écosystème: {selectedEcosystem?.name || 'TERRA_VITA'}
              </div>
            </div>
          </div>

          {/* Messages */}
          <div className="h-96 overflow-y-auto p-6 space-y-4">
            {messages.length === 0 && (
              <div className="text-center text-gray-400 py-12">
                <div className="text-6xl mb-4">🤖</div>
                <p className="text-lg">Assistant IA Token TRIO prêt à vous aider!</p>
                <p className="text-sm">Choisissez une suggestion ou tapez votre message...</p>
              </div>
            )}
            
            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-xs lg:max-w-md px-4 py-3 rounded-lg ${
                    message.type === 'user'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gradient-to-r from-purple-600 to-pink-600 text-white'
                  }`}
                >
                  <div className="text-sm">{message.content}</div>
                  <div className="text-xs opacity-70 mt-2 flex items-center space-x-2">
                    <span>{message.timestamp}</span>
                    {message.language && <span>{languages.find(l => l.code === message.language)?.flag}</span>}
                    {message.token_trio && <span>⚡ TRIO</span>}
                  </div>
                </div>
              </div>
            ))}
            
            {isTyping && (
              <div className="flex justify-start">
                <div className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-4 py-3 rounded-lg max-w-xs">
                  <div className="flex items-center space-x-1">
                    <div className="w-2 h-2 bg-white rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-white rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    <div className="w-2 h-2 bg-white rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                  </div>
                  <div className="text-xs opacity-70 mt-1">Token TRIO analyse...</div>
                </div>
              </div>
            )}
          </div>

          {/* Suggestions rapides */}
          <div className="border-t border-gray-700 p-4">
            <h3 className="text-sm font-semibold text-gray-300 mb-3">💡 Suggestions rapides:</h3>
            <div className="flex flex-wrap gap-2 mb-4">
              {quickSuggestions[currentLanguage]?.map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => sendMessage(suggestion)}
                  className="bg-gray-700 hover:bg-gray-600 text-gray-300 px-3 py-1 rounded-full text-xs transition"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>

          {/* Input */}
          <div className="border-t border-gray-700 p-4">
            <div className="flex space-x-3">
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                placeholder={`Tapez votre message en ${languages.find(l => l.code === currentLanguage)?.name}...`}
                className="flex-1 bg-gray-700 text-white rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
              <button
                onClick={() => sendMessage()}
                disabled={!inputMessage.trim() || isTyping}
                className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 disabled:from-gray-600 disabled:to-gray-600 px-6 py-3 rounded-lg text-white font-semibold transition"
              >
                ⚡ Envoyer
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Pages restantes (simplifiées pour l'espace)
const NFTPage = () => (
  <div className="min-h-screen bg-gray-900 py-12">
    <div className="container mx-auto px-4 text-center">
      <h1 className="text-4xl font-bold text-white mb-8">🎨 Marché NFT RIMAREUM V11.0</h1>
      <div className="mb-6 flex justify-center space-x-4">
        <TokenTrioBadge />
        <Delta144Badge />
      </div>
      <p className="text-xl text-gray-300 mb-8">NFT exclusifs avec utilité réelle et codes Δ144-OMEGA</p>
      <div className="text-gray-400">Interface NFT V11.0 en cours de finalisation...</div>
    </div>
  </div>
);

const DAOPage = () => (
  <div className="min-h-screen bg-gray-900 py-12">
    <div className="container mx-auto px-4 text-center">
      <h1 className="text-4xl font-bold text-white mb-8">🗳️ Gouvernance DAO V11.0</h1>
      <div className="mb-6 flex justify-center space-x-4">
        <TokenTrioBadge />
        <Delta144Badge />
      </div>
      <p className="text-xl text-gray-300 mb-8">Gouvernance cosmique avec votes quantiques</p>
      <div className="text-gray-400">Interface DAO V11.0 en cours de finalisation...</div>
    </div>
  </div>
);

const AccountPage = () => (
  <div className="min-h-screen bg-gray-900 py-12">
    <div className="container mx-auto px-4 text-center">
      <h1 className="text-4xl font-bold text-white mb-8">👤 Mon Compte V11.0</h1>
      <div className="mb-6 flex justify-center space-x-4">
        <TokenTrioBadge />
        <Delta144Badge />
      </div>
      <p className="text-xl text-gray-300 mb-8">Profil utilisateur avec accès multivers</p>
      <div className="text-gray-400">Interface Compte V11.0 en cours de finalisation...</div>
    </div>
  </div>
);

const ContactPage = () => (
  <div className="min-h-screen bg-gray-900 py-12">
    <div className="container mx-auto px-4 text-center">
      <h1 className="text-4xl font-bold text-white mb-8">📞 Contact RIMAREUM V11.0</h1>
      <div className="mb-6 flex justify-center space-x-4">
        <TokenTrioBadge />
        <Delta144Badge />
      </div>
      <p className="text-xl text-gray-300 mb-8">Support multilingue avec IA Token TRIO</p>
      <div className="bg-gray-800 rounded-lg p-8 max-w-2xl mx-auto">
        <div className="space-y-4 text-left">
          <div className="flex justify-between">
            <span className="text-gray-400">📧 Email:</span>
            <span className="text-white">nadjib@rimareum.com</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-400">🌐 Support:</span>
            <span className="text-white">Sanctuaire IA-Humain</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-400">🔐 Admin:</span>
            <span className="text-white">Dashboard CEO Δ144</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-400">🛸 Version:</span>
            <span className="text-white">V11.0 Multivers Logique</span>
          </div>
        </div>
      </div>
    </div>
  </div>
);

// Footer V11.0
const Footer = () => (
  <footer className="bg-gray-900 border-t border-gray-700 py-8 mt-12">
    <div className="container mx-auto px-4">
      <div className="text-center">
        <div className="flex justify-center space-x-4 mb-4">
          <VersionBadge />
          <TokenTrioBadge />
          <Delta144Badge />
        </div>
        <p className="text-gray-400 mb-2">
          🛸 RIMAREUM V11.0 MULTIVERS LOGIQUE - Marché Quantique pour les Visionnaires
        </p>
        <p className="text-xs text-gray-500">
          Développé par Agent Δ • Architecte: GUETTAF NADJIB • Codes Δ144-RIMAREUM-OMEGA Activés
        </p>
        <p className="text-xs text-gray-600 mt-2">
          © 2025 RIMAREUM • Souveraineté Numérique Cosmique • 8 Écosystèmes Synchronisés
        </p>
      </div>
    </div>
  </footer>
);

// App Principal V11.0
const App = () => {
  const [currentPage, setCurrentPage] = useState('home');
  const [selectedEcosystem, setSelectedEcosystem] = useState({
    id: 'terra_vita',
    name: 'TERRA_VITA',
    description: 'Écosystème fondateur - Commerce traditionnel durable',
    energy: 95
  });
  const wallet = useWallet();

  const contextValue = {
    currentPage,
    setCurrentPage,
    selectedEcosystem,
    setSelectedEcosystem,
    wallet
  };

  const renderPage = () => {
    switch (currentPage) {
      case 'home': return <HomePage />;
      case 'products': return <ProductsPage />;
      case 'nft': return <NFTPage />;
      case 'dao': return <DAOPage />;
      case 'sanctuary': return <SanctuaryPage />;
      case 'ceo-dashboard': return <CEODashboardPage />;
      case 'ai': return <AIAssistantPage />;
      case 'account': return <AccountPage />;
      case 'contact': return <ContactPage />;
      default: return <HomePage />;
    }
  };

  return (
    <AppContext.Provider value={contextValue}>
      <div className="App bg-gray-900 min-h-screen">
        <Header />
        <main>
          {renderPage()}
        </main>
        <Footer />
      </div>
    </AppContext.Provider>
  );
};

export default App;