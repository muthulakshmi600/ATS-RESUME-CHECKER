/**
 * Dashboard Sidebar Component
 * ResumeAI ATS SaaS Theme
 */

window.Sidebar = ({ currentPage, onNavigate, currentUser, onLogout }) => {
  const {
    LayoutDashboard, FileText, History,
    User, Settings, LogOut, Briefcase
  } = window.Icons;

  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'check-resume', label: 'Check Resume', icon: FileText, highlight: true },
    { id: 'jobs', label: 'Job Search', icon: Briefcase },
    { id: 'history', label: 'Resume History', icon: History },
    { id: 'profile', label: 'Profile', icon: User },
  ];

  return (
    <aside className="w-64 bg-white border-r border-[#E2E8F0] flex flex-col justify-between h-screen sticky top-0 shadow-sm z-30">
      
      {/* Brand & Menu */}
      <div className="p-6">
        
        {/* Logo using standard window.Logo */}
        <div 
          onClick={() => onNavigate('landing')}
          className="cursor-pointer mb-8 transition-transform hover:scale-[1.02]"
        >
          <window.Logo isDark={false} size="md" />
        </div>

        {/* Navigation */}
        <nav className="space-y-1.5">
          <p className="text-[11px] font-bold text-[#64748B] uppercase tracking-wider px-3 mb-2">Main Navigation</p>
          {navItems.map(item => {
            const Icon = item.icon;
            const isActive = currentPage === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onNavigate(item.id)}
                className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-[#2563EB] text-white shadow-md shadow-blue-600/20 font-semibold'
                    : 'text-[#64748B] hover:text-[#1E293B] hover:bg-slate-100'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-[#64748B]'}`} />
                <span>{item.label}</span>
                {item.highlight && !isActive && (
                  <span className="ml-auto text-[10px] uppercase font-bold bg-teal-50 text-[#14B8A6] border border-teal-200 px-1.5 py-0.5 rounded">AI Match</span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* User profile & Settings & Logout */}
      <div className="p-4 border-t border-[#E2E8F0] bg-[#F8FAFC] space-y-2">
        <div 
          onClick={() => onNavigate('profile')}
          className={`flex items-center gap-3 mb-2 px-2.5 py-2 rounded-xl cursor-pointer transition ${
            currentPage === 'profile'
              ? 'bg-white ring-1 ring-[#2563EB] shadow-sm'
              : 'hover:bg-slate-200/60'
          }`}
          title="Open Profile & Account Hub"
        >
          <div className="w-9 h-9 rounded-full bg-[#14213D] flex items-center justify-center text-white text-xs font-bold uppercase shadow-sm">
            {currentUser && currentUser.name ? currentUser.name.charAt(0) : 'U'}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-semibold text-[#1E293B] truncate">
              {currentUser ? currentUser.name : 'Candidate'}
            </p>
            <p className="text-xs text-[#64748B] truncate">
              {currentUser ? currentUser.email : 'user@example.com'}
            </p>
          </div>
        </div>

        {/* Settings button */}
        <button
          onClick={() => onNavigate('settings')}
          className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs font-medium transition ${
            currentPage === 'settings'
              ? 'bg-[#2563EB] text-white shadow-sm'
              : 'text-[#64748B] hover:text-[#1E293B] hover:bg-white'
          }`}
        >
          <Settings className={`w-3.5 h-3.5 ${currentPage === 'settings' ? 'text-white' : 'text-[#64748B]'}`} />
          <span>Settings</span>
        </button>

        <button
          onClick={onLogout}
          className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-lg text-xs font-semibold text-rose-600 hover:bg-rose-50 border border-transparent hover:border-rose-200 transition"
        >
          <LogOut className="w-3.5 h-3.5" />
          <span>Logout</span>
        </button>
      </div>

    </aside>
  );
};
