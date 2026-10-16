/**
 * Public Navigation Header Component for ResumeAI ATS
 * Styled with modern AI SaaS theme (Deep Navy #14213D, Royal Blue #2563EB, Teal #14B8A6)
 */

window.Navbar = ({ currentPage, onNavigate, currentUser, onLogout }) => {
  const { ArrowRight, User, Settings } = window.Icons;

  return (
    <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-[#E2E8F0] shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
        
        {/* Brand Logo */}
        <window.Logo 
          onClick={() => onNavigate('landing')} 
          size="md"
        />

        {/* Navigation Links */}
        <nav className="hidden md:flex items-center gap-8 text-sm font-semibold text-[#64748B]">
          <button 
            onClick={() => onNavigate('landing')} 
            className="hover:text-[#14213D] transition-colors"
          >
            Home
          </button>
          <button 
            onClick={() => onNavigate('jobs')} 
            className="hover:text-[#14213D] transition-colors flex items-center gap-1.5"
          >
            <span>Jobs</span>
            <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-teal-50 text-[#14B8A6] border border-teal-200">Fresher</span>
          </button>
          <a 
            href="#how-it-works" 
            onClick={(e) => {
              if (currentPage !== 'landing') {
                e.preventDefault();
                onNavigate('landing');
                setTimeout(() => {
                  const el = document.getElementById('how-it-works');
                  if (el) el.scrollIntoView({ behavior: 'smooth' });
                }, 100);
              }
            }}
            className="hover:text-[#14213D] transition-colors"
          >
            How It Works
          </a>
          <a 
            href="#features" 
            onClick={(e) => {
              if (currentPage !== 'landing') {
                e.preventDefault();
                onNavigate('landing');
                setTimeout(() => {
                  const el = document.getElementById('features');
                  if (el) el.scrollIntoView({ behavior: 'smooth' });
                }, 100);
              }
            }}
            className="hover:text-[#14213D] transition-colors"
          >
            Features
          </a>
          <a 
            href="#about" 
            onClick={(e) => {
              if (currentPage !== 'landing') {
                e.preventDefault();
                onNavigate('landing');
                setTimeout(() => {
                  const el = document.getElementById('about');
                  if (el) el.scrollIntoView({ behavior: 'smooth' });
                }, 100);
              }
            }}
            className="hover:text-[#14213D] transition-colors"
          >
            About
          </a>
        </nav>

        {/* Action Buttons */}
        <div className="flex items-center gap-3">
          {currentUser ? (
            <div className="flex items-center gap-2 sm:gap-3">
              <button 
                onClick={() => onNavigate('profile')}
                className="flex items-center gap-1.5 px-3 py-2 text-sm font-semibold text-[#64748B] hover:text-[#14213D] transition rounded-lg hover:bg-[#F1F5F9]"
                title="Profile & Account Hub"
              >
                <User className="w-4 h-4 text-[#2563EB]" />
                <span className="hidden sm:inline">Profile</span>
              </button>
              <button 
                onClick={() => onNavigate('settings')}
                className="flex items-center gap-1.5 px-3 py-2 text-sm font-semibold text-[#64748B] hover:text-[#14213D] transition rounded-lg hover:bg-[#F1F5F9]"
                title="Settings & Preferences"
              >
                <Settings className="w-4 h-4 text-[#64748B]" />
                <span className="hidden sm:inline">Settings</span>
              </button>
              <button 
                onClick={() => onNavigate('dashboard')}
                className="flex items-center gap-2 px-4 py-2 rounded-xl bg-[#2563EB] hover:bg-[#1D4ED8] text-white text-sm font-semibold transition shadow-md shadow-blue-500/20"
              >
                <span>Dashboard</span>
                <ArrowRight className="w-4 h-4" />
              </button>
              <button
                onClick={onLogout}
                className="px-3 py-2 text-xs font-semibold text-[#64748B] hover:text-[#14213D] transition"
              >
                Logout
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-2 sm:gap-3">
              <button 
                onClick={() => onNavigate('settings')}
                className="flex items-center gap-1.5 px-3 py-2 text-sm font-semibold text-[#64748B] hover:text-[#14213D] transition rounded-lg hover:bg-[#F1F5F9]"
                title="Application Settings"
              >
                <Settings className="w-4 h-4 text-[#64748B]" />
                <span>Settings</span>
              </button>
              <button 
                onClick={() => onNavigate('login')}
                className="px-4 py-2 text-sm font-semibold text-[#1E293B] hover:text-[#2563EB] transition"
              >
                Sign In
              </button>
              <button 
                onClick={() => onNavigate('signup')}
                className="flex items-center gap-1.5 px-4 py-2 text-sm font-semibold text-white bg-[#2563EB] hover:bg-[#1D4ED8] rounded-xl shadow-md shadow-blue-500/20 transition-all hover:scale-102"
              >
                <span>Get Started</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          )}
        </div>

      </div>
    </header>
  );
};
