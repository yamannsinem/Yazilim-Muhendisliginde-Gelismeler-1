import React, { useState, useEffect } from 'react';
import { 
  Brain, 
  Lock, 
  CheckSquare, 
  Bell, 
  LogOut, 
  Plus, 
  User, 
  Shield, 
  Calendar, 
  ChevronRight,
  LayoutDashboard,
  Loader2,
  Star
} from 'lucide-react';

// API Adresi (FastAPI backend'inin çalıştığı adres)
const API_URL = "http://127.0.0.1:8000";

export default function App() {
  // --- STATE YÖNETİMİ ---
  const [view, setView] = useState('login'); // login, register, dashboard
  const [user, setUser] = useState(null);    // { id, token, name }
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  // Veri State'leri
  const [tasks, setTasks] = useState([]);
  const [passwords, setPasswords] = useState([]);
  const [reminders, setReminders] = useState([]);
  const [activeTab, setActiveTab] = useState('tasks'); // tasks, passwords, reminders

  // Form Input State'leri
  const [formData, setFormData] = useState({
    email: '', password: '', fullName: '', 
    title: '', description: '', 
    account: '', username: '', 
    note: '', time: ''
  });

  // Input değişimlerini yakala
  const handleInputChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  // --- API FONKSİYONLARI ---

  // Verileri Çekme
  const fetchData = async (userId) => {
    setLoading(true);
    try {
      const [tasksRes, passRes, remRes] = await Promise.all([
        fetch(`${API_URL}/api/tasks/${userId}`),
        fetch(`${API_URL}/api/passwords/${userId}`),
        fetch(`${API_URL}/api/reminders/${userId}`)
      ]);

      if (tasksRes.ok) setTasks(await tasksRes.json());
      if (passRes.ok) setPasswords(await passRes.json());
      if (remRes.ok) setReminders(await remRes.json());
    } catch (err) {
      setError("API'ye bağlanılamadı. Backend çalışıyor mu?");
    } finally {
      setLoading(false);
    }
  };

  // Giriş Yap
  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const res = await fetch(`${API_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: formData.email, password: formData.password })
      });
      const data = await res.json();
      
      if (res.ok) {
        setUser({ id: data.user_id, token: data.token });
        setView('dashboard');
        fetchData(data.user_id);
      } else {
        setError(data.detail || "Giriş başarısız");
      }
    } catch (err) {
      setError("Sunucuya ulaşılamadı");
    } finally {
      setLoading(false);
    }
  };

  // Kayıt Ol
  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const res = await fetch(`${API_URL}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          email: formData.email, 
          password: formData.password,
          full_name: formData.fullName
        })
      });
      
      if (res.ok) {
        alert("Kayıt başarılı! Giriş yapabilirsiniz.");
        setView('login');
      } else {
        const data = await res.json();
        setError(data.detail || "Kayıt başarısız");
      }
    } catch (err) {
      setError("Sunucuya ulaşılamadı");
    } finally {
      setLoading(false);
    }
  };

  // Veri Ekleme (Generic)
  const handleAddItem = async (type) => {
    if (!user) return;
    
    let endpoint = '';
    let body = {};

    if (type === 'task') {
      endpoint = `/api/tasks/${user.id}`;
      body = { title: formData.title, description: formData.description };
    } else if (type === 'password') {
      endpoint = `/api/passwords/${user.id}`;
      body = { account: formData.account, username: formData.username, password: formData.password };
    } else if (type === 'reminder') {
      endpoint = `/api/reminders/${user.id}`;
      body = { note: formData.note, time: formData.time };
    }

    try {
      const res = await fetch(`${API_URL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });

      if (res.ok) {
        fetchData(user.id); // Listeyi yenile
        // Formu temizle
        setFormData({ ...formData, title: '', description: '', account: '', username: '', note: '', time: '' }); 
      }
    } catch (err) {
      alert("Ekleme başarısız");
    }
  };

  // --- COMPONENTLER ---

  const AuthScreen = () => (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-700 p-4">
      <div className="bg-white/95 backdrop-blur-xl rounded-3xl shadow-2xl w-full max-w-md overflow-hidden border border-white/20">
        <div className="p-8">
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-gradient-to-tr from-blue-500 to-purple-500 text-white mb-4 shadow-lg transform rotate-3 hover:rotate-0 transition-transform duration-300">
              <Star size={40} fill="white" />
            </div>
            <h1 className="text-3xl font-extrabold text-gray-800 tracking-tight">Kişisel Asistan</h1>
            <p className="text-gray-500 mt-2 font-medium">Hayatını Düzenle, Zamanı Yakala</p>
          </div>

          {error && (
            <div className="bg-red-50 text-red-600 p-4 rounded-xl mb-6 text-sm text-center border border-red-100 flex items-center justify-center gap-2">
              <div className="w-2 h-2 bg-red-500 rounded-full"></div>
              {error}
            </div>
          )}

          <form onSubmit={view === 'login' ? handleLogin : handleRegister} className="space-y-5">
            {view === 'register' && (
              <div>
                <label className="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-1 ml-1">Ad Soyad</label>
                <input 
                  name="fullName"
                  type="text" 
                  required
                  className="w-full px-4 py-3 rounded-xl bg-gray-50 border border-gray-200 focus:bg-white focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition-all font-medium"
                  placeholder="İsim Soyisim"
                  onChange={handleInputChange}
                />
              </div>
            )}
            <div>
              <label className="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-1 ml-1">E-posta</label>
              <input 
                name="email"
                type="email" 
                required
                className="w-full px-4 py-3 rounded-xl bg-gray-50 border border-gray-200 focus:bg-white focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition-all font-medium"
                placeholder="ornek@mail.com"
                onChange={handleInputChange}
              />
            </div>
            <div>
              <label className="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-1 ml-1">Şifre</label>
              <input 
                name="password"
                type="password" 
                required
                className="w-full px-4 py-3 rounded-xl bg-gray-50 border border-gray-200 focus:bg-white focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition-all font-medium"
                placeholder="••••••••"
                onChange={handleInputChange}
              />
            </div>

            <button 
              disabled={loading}
              className="w-full bg-gray-900 hover:bg-black text-white font-bold py-4 rounded-xl transition-all transform active:scale-95 flex justify-center items-center shadow-xl shadow-gray-900/20 mt-2"
            >
              {loading ? <Loader2 className="animate-spin" /> : (view === 'login' ? 'Giriş Yap' : 'Kayıt Ol')}
            </button>
          </form>

          <div className="mt-8 text-center">
            <button 
              onClick={() => { setError(''); setView(view === 'login' ? 'register' : 'login'); }}
              className="text-indigo-600 hover:text-indigo-800 text-sm font-semibold hover:underline decoration-2 underline-offset-2 transition-all"
            >
              {view === 'login' ? "Hesabın yok mu? Kayıt Ol" : "Zaten hesabın var mı? Giriş Yap"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  const Dashboard = () => (
    <div className="min-h-screen bg-gray-50 flex flex-col md:flex-row font-sans">
      {/* Sidebar */}
      <aside className="bg-white w-full md:w-72 flex-shrink-0 flex flex-col border-r border-gray-200 shadow-sm z-10">
        <div className="p-6 flex items-center gap-3 border-b border-gray-100">
          <div className="w-10 h-10 bg-indigo-600 rounded-xl flex items-center justify-center text-white shadow-lg shadow-indigo-200">
            <Star size={20} fill="white" />
          </div>
          <span className="font-bold text-xl text-gray-800 tracking-tight">Asistanım</span>
        </div>
        
        <nav className="flex-1 p-4 space-y-2">
          <NavButton 
            active={activeTab === 'tasks'} 
            onClick={() => setActiveTab('tasks')} 
            icon={<CheckSquare size={20} />} 
            label="Görevler" 
            color="text-blue-500"
          />
          <NavButton 
            active={activeTab === 'passwords'} 
            onClick={() => setActiveTab('passwords')} 
            icon={<Lock size={20} />} 
            label="Şifre Kasası" 
            color="text-purple-500"
          />
          <NavButton 
            active={activeTab === 'reminders'} 
            onClick={() => setActiveTab('reminders')} 
            icon={<Bell size={20} />} 
            label="Hatırlatıcılar" 
            color="text-orange-500"
          />
        </nav>

        <div className="p-4 border-t border-gray-100 bg-gray-50/50">
          <button 
            onClick={() => { setUser(null); setView('login'); }}
            className="flex items-center gap-3 text-gray-600 hover:text-red-600 hover:bg-red-50 transition-all w-full px-4 py-3 rounded-xl font-medium group"
          >
            <LogOut size={20} className="group-hover:rotate-12 transition-transform" />
            <span>Çıkış Yap</span>
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 p-4 md:p-8 overflow-y-auto bg-gray-50">
        <header className="mb-8 flex justify-between items-center bg-white p-4 rounded-2xl shadow-sm border border-gray-100">
          <div>
            <h2 className="text-2xl font-bold text-gray-800">
              {activeTab === 'tasks' && 'Görev Yönetimi'}
              {activeTab === 'passwords' && 'Güvenli Kasa'}
              {activeTab === 'reminders' && 'Zamanlayıcı'}
            </h2>
            <p className="text-gray-500 text-sm mt-1">Bugün neler yapmak istersin?</p>
          </div>
          <div className="flex items-center gap-3 bg-gray-100 pl-4 pr-2 py-2 rounded-full">
             <span className="text-sm font-semibold text-gray-600 hidden md:block">Kullanıcı Paneli</span>
             <div className="w-10 h-10 bg-gray-800 rounded-full flex items-center justify-center text-white font-bold shadow-md">
              <User size={18} />
            </div>
          </div>
        </header>

        {/* Content Area */}
        <div className="max-w-6xl mx-auto">
          {activeTab === 'tasks' && <TaskPanel />}
          {activeTab === 'passwords' && <PasswordPanel />}
          {activeTab === 'reminders' && <ReminderPanel />}
        </div>
      </main>
    </div>
  );

  // --- SUB-COMPONENTS ---

  const NavButton = ({ active, onClick, icon, label, color }) => (
    <button
      onClick={onClick}
      className={`w-full flex items-center gap-3 px-4 py-3.5 rounded-xl transition-all duration-200 font-medium ${
        active 
          ? 'bg-gray-900 text-white shadow-lg shadow-gray-900/10' 
          : 'text-gray-600 hover:bg-gray-100 hover:pl-6'
      }`}
    >
      <span className={active ? 'text-white' : color}>{icon}</span>
      <span>{label}</span>
      {active && <ChevronRight className="ml-auto w-4 h-4 text-gray-400" />}
    </button>
  );

  const TaskPanel = () => (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-3xl shadow-sm border border-gray-100">
        <h3 className="font-bold text-gray-800 mb-4 flex items-center gap-2 text-lg">
          <div className="p-2 bg-blue-100 rounded-lg text-blue-600"><Plus size={20} /></div> 
          Yeni Görev Oluştur
        </h3>
        <div className="flex flex-col md:flex-row gap-3">
          <input 
            name="title"
            value={formData.title}
            onChange={handleInputChange}
            placeholder="Ne yapman gerekiyor?" 
            className="flex-1 px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:bg-white outline-none transition-all"
          />
          <input 
            name="description"
            value={formData.description}
            onChange={handleInputChange}
            placeholder="Detay (opsiyonel)" 
            className="flex-1 px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:bg-white outline-none transition-all"
          />
          <button 
            onClick={() => handleAddItem('task')}
            className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-xl font-bold transition-colors shadow-lg shadow-blue-500/30"
          >
            Ekle
          </button>
        </div>
      </div>

      <div className="grid gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
        {tasks.map(task => (
          <div key={task.id} className="bg-white p-6 rounded-3xl shadow-sm border border-gray-100 hover:shadow-xl hover:-translate-y-1 transition-all duration-300 group relative overflow-hidden">
            <div className="absolute top-0 right-0 w-16 h-16 bg-blue-50 rounded-bl-full -mr-8 -mt-8 transition-transform group-hover:scale-150"></div>
            <div className="relative">
              <div className="flex justify-between items-start mb-3">
                <span className="px-3 py-1 bg-blue-50 text-blue-600 text-xs font-bold rounded-full uppercase tracking-wide">Görev</span>
                <div className="w-6 h-6 rounded-full border-2 border-gray-200 group-hover:border-blue-500 transition-colors cursor-pointer"></div>
              </div>
              <h4 className="font-bold text-gray-800 text-lg mb-1 group-hover:text-blue-600 transition-colors">{task.title}</h4>
              <p className="text-gray-500 text-sm leading-relaxed">{task.description}</p>
            </div>
          </div>
        ))}
        {tasks.length === 0 && <EmptyState message="Hiç görevin yok, harika!" icon={<LayoutDashboard size={48} />} />}
      </div>
    </div>
  );

  const PasswordPanel = () => (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-3xl shadow-sm border border-gray-100">
        <h3 className="font-bold text-gray-800 mb-4 flex items-center gap-2 text-lg">
           <div className="p-2 bg-purple-100 rounded-lg text-purple-600"><Shield size={20} /></div> 
           Şifre Kaydet
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <input 
            name="account"
            value={formData.account}
            onChange={handleInputChange}
            placeholder="Platform (örn: Netflix)" 
            className="px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-200 transition-all"
          />
          <input 
            name="username"
            value={formData.username}
            onChange={handleInputChange}
            placeholder="Kullanıcı Adı" 
            className="px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-200 transition-all"
          />
          <div className="flex gap-2">
            <input 
              name="password"
              value={formData.password}
              onChange={handleInputChange}
              placeholder="Şifre" 
              className="flex-1 px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-200 transition-all"
            />
            <button 
              onClick={() => handleAddItem('password')}
              className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-3 rounded-xl font-bold transition-colors shadow-lg shadow-purple-500/30"
            >
              Kaydet
            </button>
          </div>
        </div>
      </div>

      <div className="space-y-3">
        {passwords.map(pwd => (
          <div key={pwd.id} className="bg-white p-4 rounded-2xl shadow-sm border border-gray-100 flex items-center justify-between hover:shadow-md transition-shadow">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-purple-50 rounded-xl flex items-center justify-center text-purple-600">
                <Lock size={24} />
              </div>
              <div>
                <h4 className="font-bold text-gray-800">{pwd.account}</h4>
                <p className="text-gray-500 text-sm font-medium bg-gray-100 px-2 py-0.5 rounded inline-block mt-1">{pwd.username}</p>
              </div>
            </div>
            <div className={`px-4 py-2 rounded-xl text-xs font-bold border ${
              pwd.strength === 'Güçlü' ? 'bg-green-100 text-green-700 border-green-200' :
              pwd.strength === 'Orta' ? 'bg-yellow-50 text-yellow-700 border-yellow-200' :
              'bg-red-50 text-red-700 border-red-200'
            }`}>
              {pwd.strength}
            </div>
          </div>
        ))}
        {passwords.length === 0 && <EmptyState message="Kasan boş." icon={<Lock size={48} />} />}
      </div>
    </div>
  );

  const ReminderPanel = () => (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-3xl shadow-sm border border-gray-100">
        <h3 className="font-bold text-gray-800 mb-4 flex items-center gap-2 text-lg">
           <div className="p-2 bg-orange-100 rounded-lg text-orange-600"><Calendar size={20} /></div> 
           Hatırlatıcı Ekle
        </h3>
        <div className="flex gap-3">
          <input 
            name="note"
            value={formData.note}
            onChange={handleInputChange}
            placeholder="Neyi hatırlatayım?" 
            className="flex-2 w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl outline-none focus:border-orange-500 focus:ring-2 focus:ring-orange-200 transition-all"
          />
          <input 
            name="time"
            value={formData.time}
            onChange={handleInputChange}
            placeholder="Zaman (örn: Yarın 14:00)" 
            className="flex-1 w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl outline-none focus:border-orange-500 focus:ring-2 focus:ring-orange-200 transition-all"
          />
          <button 
            onClick={() => handleAddItem('reminder')}
            className="bg-orange-500 hover:bg-orange-600 text-white px-6 py-3 rounded-xl font-bold transition-colors shadow-lg shadow-orange-500/30"
          >
            Ekle
          </button>
        </div>
      </div>

      <div className="grid gap-4 grid-cols-1 md:grid-cols-2">
        {reminders.map(rem => (
          <div key={rem.id} className="bg-white p-5 rounded-3xl shadow-sm border-l-[6px] border-orange-400 flex items-center gap-4 hover:bg-orange-50/30 transition-colors">
            <div className="bg-orange-100 p-3 rounded-full text-orange-600">
              <Bell size={22} />
            </div>
            <div>
              <p className="font-bold text-gray-800 text-lg">{rem.note}</p>
              <p className="text-orange-600 text-sm font-bold mt-1 bg-orange-50 inline-block px-2 py-0.5 rounded-md">{rem.time}</p>
            </div>
          </div>
        ))}
        {reminders.length === 0 && <EmptyState message="Hatırlatıcı yok." icon={<Bell size={48} />} />}
      </div>
    </div>
  );

  const EmptyState = ({ message, icon }) => (
    <div className="col-span-full py-16 flex flex-col items-center justify-center text-gray-300 border-2 border-dashed border-gray-200 rounded-3xl">
      <div className="mb-4 bg-gray-50 p-6 rounded-full">{icon}</div>
      <p className="text-lg font-medium text-gray-400">{message}</p>
    </div>
  );

  return view === 'dashboard' ? <Dashboard /> : <AuthScreen />;
}
