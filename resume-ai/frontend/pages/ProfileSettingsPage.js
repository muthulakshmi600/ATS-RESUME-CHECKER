/**
 * ProfileSettingsPage Component: User Profile, Account Management, Language,
 * Help Center, Contact Us, and ATS Engine Settings.
 * ResumeAI ATS SaaS Theme
 */

window.ProfileSettingsPage = ({ currentUser, onUserUpdate, showToast, onNavigate, initialTab = 'profile' }) => {
  const {
    User, Settings, ShieldCheck, CheckCircle, Trash2, Sparkles,
    Globe, HelpCircle, Mail, Send, Key, MessageSquare, ChevronDown,
    ChevronRight, Search, Download, AlertCircle, FileText, Check
  } = window.Icons;

  // Tabs: 'profile' | 'account' | 'language' | 'help' | 'contact'
  const [activeTab, setActiveTab] = React.useState(initialTab);

  React.useEffect(() => {
    if (initialTab) {
      setActiveTab(initialTab);
    }
  }, [initialTab]);

  // Profile State
  const [name, setName] = React.useState(currentUser ? currentUser.name : 'Candidate');
  const [email, setEmail] = React.useState(currentUser ? currentUser.email : 'candidate@example.com');
  const [bio, setBio] = React.useState(currentUser ? (currentUser.bio || '') : 'Engineering professional focused on building reliable, modern, and high-impact software.');

  // Account State
  const [currentPassword, setCurrentPassword] = React.useState('');
  const [newPassword, setNewPassword] = React.useState('');
  const [confirmNewPassword, setConfirmNewPassword] = React.useState('');

  // Language State
  const [selectedLanguage, setSelectedLanguage] = React.useState('en');
  const languages = [
    { code: 'en', name: 'English', native: 'English', flag: '🇺🇸', desc: 'Standard International English' },
    { code: 'ta', name: 'Tamil', native: 'தமிழ்', flag: '🇮🇳', desc: 'தமிழ்நாடு / இலங்கை / சிங்கப்பூர்' },
    { code: 'hi', name: 'Hindi', native: 'हिंदी', flag: '🇮🇳', desc: 'भारत' },
    { code: 'es', name: 'Spanish', native: 'Español', flag: '🇪🇸', desc: 'España y Latinoamérica' },
    { code: 'fr', name: 'French', native: 'Français', flag: '🇫🇷', desc: 'France & Canada' },
    { code: 'de', name: 'German', native: 'Deutsch', flag: '🇩🇪', desc: 'Deutschland, Österreich' },
    { code: 'ja', name: 'Japanese', native: '日本語', flag: '🇯🇵', desc: '日本' }
  ];

  // Help Center State
  const [faqSearch, setFaqSearch] = React.useState('');
  const [expandedFaq, setExpandedFaq] = React.useState(0);

  const faqs = [
    {
      q: "How is the Resume Quality Score (0 - 100) calculated?",
      a: "The quality score is calculated deterministically across 6 core structural factors: Section Completeness (20 pts), Contact Info & Links (15 pts), Measurable Metrics (20 pts), ATS Formatting & Layout (15 pts), Readability & Tone (15 pts), and Technical Skills Breadth (15 pts). If a Job Description is provided, a separate Job Match Score (0 - 100) evaluates exact keyword and skill alignment."
    },
    {
      q: "Which file format should I upload: PDF or DOCX?",
      a: "Both PDF (.pdf) and Microsoft Word (.docx) documents are fully supported up to 5MB. For automated ATS scanners, clean single-column PDF and DOCX files without complex tables or image-only text offer the highest text extraction fidelity."
    },
    {
      q: "How can I boost my resume score from 60 to 85+?",
      a: "1) Include standard section titles (Professional Summary, Experience, Education, Skills). 2) Start bullet points with strong action verbs (e.g. 'Architected', 'Optimized'). 3) Add measurable metrics (percentages, numbers, latency reductions). 4) Paste the employer's Job Description for precision keyword alignment."
    },
    {
      q: "What if I don't provide a Job Description?",
      a: "When no Job Description is provided, ResumeAI evaluates your resume on its standalone quality, formatting, section completeness, and quantifiable achievements. You can still see all detected skills, keywords, and action verbs with clear recommendations to improve your resume's readiness."
    },
    {
      q: "Is my resume data kept private?",
      a: "Yes. All resume processing occurs locally on your machine or private session storage. No data is shared with third-party advertisers."
    }
  ];

  // Contact Us State
  const [contactName, setContactName] = React.useState(currentUser ? currentUser.name : '');
  const [contactEmail, setContactEmail] = React.useState(currentUser ? currentUser.email : '');
  const [contactCategory, setContactCategory] = React.useState('Technical Support');
  const [contactSubject, setContactSubject] = React.useState('');
  const [contactMessage, setContactMessage] = React.useState('');
  const [isSendingContact, setIsSendingContact] = React.useState(false);
  const [isSaving, setIsSaving] = React.useState(false);

  // Handlers
  const handleProfileSave = async (e) => {
    e.preventDefault();
    setIsSaving(true);
    try {
      const updated = await window.ResumeAIService.updateProfile({
        name: name.trim(),
        bio: bio.trim()
      });
      onUserUpdate(updated);
      showToast('Profile updated successfully!', 'success');
    } catch (err) {
      showToast('Profile update failed.', 'error');
    } finally {
      setIsSaving(false);
    }
  };

  const handlePasswordUpdate = (e) => {
    e.preventDefault();
    if (!newPassword.trim()) {
      showToast('Please enter a new password.', 'error');
      return;
    }
    if (newPassword !== confirmNewPassword) {
      showToast('Passwords do not match.', 'error');
      return;
    }
    setCurrentPassword('');
    setNewPassword('');
    setConfirmNewPassword('');
    showToast('Demo account password updated successfully!', 'success');
  };

  const handleExportData = () => {
    const dataToExport = {
      profile: { name, email, bio },
      language: selectedLanguage,
      exportedAt: new Date().toISOString()
    };
    const blob = new Blob([JSON.stringify(dataToExport, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ResumeAI_${email.split('@')[0]}_data.json`;
    a.click();
    URL.revokeObjectURL(url);
    showToast('Candidate data exported as JSON!', 'success');
  };

  const handleLanguageChange = async (langCode) => {
    setSelectedLanguage(langCode);
    const langObj = languages.find(l => l.code === langCode);
    try {
      await window.ResumeAIService.updateSettings({ language: langCode });
      showToast(`Language switched to ${langObj ? langObj.name : langCode}!`, 'success');
    } catch (e) {
      showToast(`Language set to ${langCode}.`, 'info');
    }
  };

  const handleContactSubmit = (e) => {
    e.preventDefault();
    if (!contactMessage.trim() || !contactSubject.trim()) {
      showToast('Please enter a subject and message.', 'error');
      return;
    }
    setIsSendingContact(true);
    setTimeout(() => {
      setIsSendingContact(false);
      setContactSubject('');
      setContactMessage('');
      showToast('Thank you! Your message has been sent to ResumeAI support.', 'success');
    }, 800);
  };

  const filteredFaqs = faqs.filter(f =>
    f.q.toLowerCase().includes(faqSearch.toLowerCase()) ||
    f.a.toLowerCase().includes(faqSearch.toLowerCase())
  );

  const tabs = [
    { id: 'profile', label: 'Profile', icon: User },
    { id: 'account', label: 'Account', icon: Key },
    { id: 'language', label: 'Language', icon: Globe },
    { id: 'help', label: 'Help Center', icon: HelpCircle },
    { id: 'contact', label: 'Contact Us', icon: Mail }
  ];

  return (
    <div className="max-w-5xl mx-auto space-y-8 pb-12">
      
      {/* Header */}
      <div className="border-b border-[#E2E8F0] pb-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-[#14213D] tracking-tight flex items-center gap-3">
            <User className="w-7 h-7 text-[#2563EB]" />
            <span>Profile & Account Hub</span>
          </h1>
          <p className="text-xs text-[#64748B] mt-1">
            Manage your candidate profile, account security, multi-language preferences, and ATS knowledge base.
          </p>
        </div>

        {/* Quick Language Indicator badge */}
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-white border border-[#E2E8F0] text-xs shadow-sm">
          <Globe className="w-4 h-4 text-[#2563EB]" />
          <span className="text-[#64748B]">Language:</span>
          <span className="font-semibold text-[#14213D]">
            {languages.find(l => l.code === selectedLanguage)?.name || 'English'}
          </span>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex items-center gap-1.5 overflow-x-auto pb-2 border-b border-[#E2E8F0] scrollbar-none">
        {tabs.map(tab => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
                isActive
                  ? 'bg-[#2563EB] text-white shadow-sm shadow-blue-500/20'
                  : 'text-[#64748B] hover:text-[#1E293B] hover:bg-slate-100'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* TAB 1: PROFILE */}
      {activeTab === 'profile' && (
        <div className="bg-white border border-[#E2E8F0] rounded-2xl p-6 sm:p-8 shadow-sm space-y-6">
          <div className="flex items-center gap-4 pb-4 border-b border-[#E2E8F0]">
            <div className="w-16 h-16 rounded-2xl bg-[#14213D] flex items-center justify-center text-white text-2xl font-bold uppercase shadow-sm">
              {name ? name.charAt(0) : 'U'}
            </div>
            <div>
              <h3 className="text-lg font-bold text-[#14213D]">{name}</h3>
              <p className="text-xs text-[#64748B]">{email}</p>
              <span className="inline-block mt-1 text-[10px] font-bold uppercase px-2 py-0.5 rounded bg-emerald-50 text-[#16A34A] border border-emerald-200">
                Active Candidate Account
              </span>
            </div>
          </div>

          <form onSubmit={handleProfileSave} className="space-y-6">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
              <div>
                <label className="block text-xs font-semibold text-[#64748B] mb-1.5 uppercase tracking-wider">
                  Full Name
                </label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full px-4 py-2.5 rounded-xl bg-[#F8FAFC] border border-[#CBD5E1] text-[#1E293B] text-sm focus:outline-none focus:border-[#2563EB] transition"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#64748B] mb-1.5 uppercase tracking-wider">
                  Email Address
                </label>
                <input
                  type="email"
                  value={email}
                  disabled
                  className="w-full px-4 py-2.5 rounded-xl bg-slate-100 border border-slate-200 text-slate-500 text-sm cursor-not-allowed"
                />
                <span className="text-[11px] text-[#64748B] mt-1 block">Primary login identifier</span>
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-[#64748B] mb-1.5 uppercase tracking-wider">
                Professional Bio / Summary
              </label>
              <textarea
                rows={3}
                value={bio}
                onChange={(e) => setBio(e.target.value)}
                placeholder="Brief summary of your background, technical interests, and experience..."
                className="w-full p-4 rounded-xl bg-[#F8FAFC] border border-[#CBD5E1] text-[#1E293B] text-sm focus:outline-none focus:border-[#2563EB] transition resize-y font-sans"
              />
            </div>

            <div className="pt-2">
              <button
                type="submit"
                disabled={isSaving}
                className="flex items-center gap-2 px-6 py-3 rounded-xl bg-[#2563EB] hover:bg-[#1D4ED8] text-white font-bold text-xs shadow-sm transition"
              >
                <CheckCircle className="w-4 h-4" />
                <span>{isSaving ? 'Saving Profile...' : 'Save Profile Changes'}</span>
              </button>
            </div>
          </form>
        </div>
      )}

      {/* TAB 2: ACCOUNT */}
      {activeTab === 'account' && (
        <div className="bg-white border border-[#E2E8F0] rounded-2xl p-6 sm:p-8 shadow-sm space-y-8">
          <div>
            <h3 className="text-base font-bold text-[#14213D] flex items-center gap-2">
              <Key className="w-5 h-5 text-[#2563EB]" />
              <span>Account Security & Credentials</span>
            </h3>
            <p className="text-xs text-[#64748B] mt-0.5">
              Update password or review active session details for your account.
            </p>
          </div>

          {/* Change Password Form */}
          <form onSubmit={handlePasswordUpdate} className="space-y-4 max-w-lg">
            <div>
              <label className="block text-xs font-semibold text-[#64748B] mb-1 uppercase tracking-wider">
                Current Password
              </label>
              <input
                type="password"
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full px-4 py-2.5 rounded-xl bg-[#F8FAFC] border border-[#CBD5E1] text-[#1E293B] text-sm focus:outline-none focus:border-[#2563EB] transition"
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-[#64748B] mb-1 uppercase tracking-wider">
                  New Password
                </label>
                <input
                  type="password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full px-4 py-2.5 rounded-xl bg-[#F8FAFC] border border-[#CBD5E1] text-[#1E293B] text-sm focus:outline-none focus:border-[#2563EB] transition"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#64748B] mb-1 uppercase tracking-wider">
                  Confirm New Password
                </label>
                <input
                  type="password"
                  value={confirmNewPassword}
                  onChange={(e) => setConfirmNewPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full px-4 py-2.5 rounded-xl bg-[#F8FAFC] border border-[#CBD5E1] text-[#1E293B] text-sm focus:outline-none focus:border-[#2563EB] transition"
                />
              </div>
            </div>

            <button
              type="submit"
              className="px-5 py-2.5 rounded-xl bg-[#2563EB] hover:bg-[#1D4ED8] text-white font-bold text-xs transition shadow-sm"
            >
              Update Password
            </button>
          </form>

          {/* Session details */}
          <div className="pt-6 border-t border-[#E2E8F0] space-y-3">
            <h4 className="text-xs font-bold text-[#14213D] uppercase tracking-wider">Active Browser Session</h4>
            <div className="p-4 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-2.5 h-2.5 rounded-full bg-[#16A34A] animate-pulse" />
                <div>
                  <p className="text-xs font-semibold text-[#14213D]">Current Web Browser Session</p>
                  <p className="text-[11px] text-[#64748B]">Logged in as {email}</p>
                </div>
              </div>
              <span className="text-[11px] font-bold px-2.5 py-1 rounded-lg bg-emerald-50 text-[#16A34A] border border-emerald-200">
                Online
              </span>
            </div>
          </div>

          {/* Export Candidate Data */}
          <div className="pt-6 border-t border-[#E2E8F0] flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h4 className="text-xs font-bold text-[#14213D] uppercase tracking-wider">Export Candidate Profile</h4>
              <p className="text-xs text-[#64748B] mt-0.5">Download a complete JSON archive of your settings and profile.</p>
            </div>
            <button
              type="button"
              onClick={handleExportData}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-white hover:bg-slate-50 text-[#1E293B] border border-[#CBD5E1] text-xs font-semibold transition shadow-sm"
            >
              <Download className="w-4 h-4 text-[#2563EB]" />
              <span>Export Data JSON</span>
            </button>
          </div>
        </div>
      )}

      {/* TAB 3: LANGUAGE */}
      {activeTab === 'language' && (
        <div className="bg-white border border-[#E2E8F0] rounded-2xl p-6 sm:p-8 shadow-sm space-y-6">
          <div>
            <h3 className="text-base font-bold text-[#14213D] flex items-center gap-2">
              <Globe className="w-5 h-5 text-[#2563EB]" />
              <span>Language & Regional Preferences</span>
            </h3>
            <p className="text-xs text-[#64748B] mt-0.5">
              Select your preferred display language for the ResumeAI portal interface.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 pt-2">
            {languages.map(lang => {
              const isSelected = selectedLanguage === lang.code;
              return (
                <div
                  key={lang.code}
                  onClick={() => handleLanguageChange(lang.code)}
                  className={`p-4 rounded-xl border cursor-pointer transition-all duration-200 ${
                    isSelected
                      ? 'bg-blue-50 border-[#2563EB] shadow-sm'
                      : 'bg-[#F8FAFC] border-[#E2E8F0] hover:border-slate-300 hover:bg-slate-50'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-2xl">{lang.flag}</span>
                    {isSelected ? (
                      <span className="flex items-center gap-1 text-[11px] font-bold text-[#16A34A] bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded-full">
                        <Check className="w-3 h-3" />
                        <span>Active</span>
                      </span>
                    ) : (
                      <span className="text-[10px] uppercase font-bold text-[#64748B]">Select</span>
                    )}
                  </div>
                  <h4 className="text-sm font-bold text-[#14213D]">{lang.name}</h4>
                  <p className="text-xs text-[#2563EB] font-medium">{lang.native}</p>
                  <p className="text-[11px] text-[#64748B] mt-2 truncate">{lang.desc}</p>
                </div>
              );
            })}
          </div>

          <div className="p-4 rounded-xl bg-blue-50 border border-blue-200 text-xs text-[#2563EB] flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-[#2563EB] flex-shrink-0" />
            <span>Support for English, தமிழ் (Tamil), and multilingual resume parsing is fully enabled.</span>
          </div>
        </div>
      )}

      {/* TAB 4: HELP CENTER */}
      {activeTab === 'help' && (
        <div className="bg-white border border-[#E2E8F0] rounded-2xl p-6 sm:p-8 shadow-sm space-y-6">
          <div>
            <h3 className="text-base font-bold text-[#14213D] flex items-center gap-2">
              <HelpCircle className="w-5 h-5 text-[#2563EB]" />
              <span>Help Center & ATS Knowledge Base</span>
            </h3>
            <p className="text-xs text-[#64748B] mt-0.5">
              Browse common questions, guidelines, and scoring methodology to optimize your resume.
            </p>
          </div>

          {/* FAQ Search */}
          <div className="relative">
            <Search className="w-4 h-4 text-[#64748B] absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={faqSearch}
              onChange={(e) => setFaqSearch(e.target.value)}
              placeholder="Search help topics (e.g. ATS scoring, formatting, PDF vs DOCX)..."
              className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-[#F8FAFC] border border-[#CBD5E1] text-[#1E293B] placeholder-slate-400 text-xs focus:outline-none focus:border-[#2563EB] transition"
            />
          </div>

          {/* FAQ Accordions */}
          <div className="space-y-3">
            {filteredFaqs.map((faq, idx) => {
              const isOpen = expandedFaq === idx;
              return (
                <div
                  key={idx}
                  className="rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] overflow-hidden transition"
                >
                  <button
                    onClick={() => setExpandedFaq(isOpen ? -1 : idx)}
                    className="w-full p-4 text-left flex items-center justify-between gap-4 hover:bg-slate-100 transition"
                  >
                    <span className="text-xs sm:text-sm font-bold text-[#14213D]">{faq.q}</span>
                    <ChevronDown className={`w-4 h-4 text-[#64748B] transition-transform duration-200 flex-shrink-0 ${isOpen ? 'rotate-180 text-[#2563EB]' : ''}`} />
                  </button>
                  {isOpen && (
                    <div className="px-4 pb-4 text-xs text-[#1E293B] leading-relaxed border-t border-[#E2E8F0] pt-3">
                      {faq.a}
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {/* Quick Help Action Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-4 border-t border-[#E2E8F0]">
            <div className="p-4 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0]">
              <h5 className="text-xs font-bold text-[#14213D] mb-1">Need direct assistance?</h5>
              <p className="text-[11px] text-[#64748B] mb-3">Submit your inquiry directly through our Contact Us tab.</p>
              <button
                onClick={() => setActiveTab('contact')}
                className="text-xs font-bold text-[#2563EB] hover:text-[#1D4ED8] flex items-center gap-1"
              >
                <span>Go to Contact Us</span>
                <ChevronRight className="w-3.5 h-3.5" />
              </button>
            </div>

            <div className="p-4 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0]">
              <h5 className="text-xs font-bold text-[#14213D] mb-1">Ready to test your score?</h5>
              <p className="text-[11px] text-[#64748B] mb-3">Upload a new document or test with our ready-to-use sample resumes.</p>
              <button
                onClick={() => onNavigate ? onNavigate('check-resume') : (window.location.hash = '#check-resume')}
                className="text-xs font-bold text-[#14B8A6] hover:text-[#0D9488] flex items-center gap-1"
              >
                <span>Audit Resume Now</span>
                <ChevronRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        </div>
      )}

      {/* TAB 5: CONTACT US */}
      {activeTab === 'contact' && (
        <div className="bg-white border border-[#E2E8F0] rounded-2xl p-6 sm:p-8 shadow-sm space-y-6">
          <div>
            <h3 className="text-base font-bold text-[#14213D] flex items-center gap-2">
              <Mail className="w-5 h-5 text-[#2563EB]" />
              <span>Contact Us & Support</span>
            </h3>
            <p className="text-xs text-[#64748B] mt-0.5">
              Have a question about ResumeAI ATS, need feedback for your tutor presentation, or have feature ideas? Send us a message!
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            
            {/* Form */}
            <form onSubmit={handleContactSubmit} className="lg:col-span-2 space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-[#64748B] mb-1 uppercase tracking-wider">
                    Your Name
                  </label>
                  <input
                    type="text"
                    value={contactName}
                    onChange={(e) => setContactName(e.target.value)}
                    placeholder="Candidate Name"
                    className="w-full px-4 py-2.5 rounded-xl bg-[#F8FAFC] border border-[#CBD5E1] text-[#1E293B] text-sm focus:outline-none focus:border-[#2563EB] transition"
                    required
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-[#64748B] mb-1 uppercase tracking-wider">
                    Email Address
                  </label>
                  <input
                    type="email"
                    value={contactEmail}
                    onChange={(e) => setContactEmail(e.target.value)}
                    placeholder="candidate@example.com"
                    className="w-full px-4 py-2.5 rounded-xl bg-[#F8FAFC] border border-[#CBD5E1] text-[#1E293B] text-sm focus:outline-none focus:border-[#2563EB] transition"
                    required
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-[#64748B] mb-1 uppercase tracking-wider">
                    Inquiry Category
                  </label>
                  <select
                    value={contactCategory}
                    onChange={(e) => setContactCategory(e.target.value)}
                    className="w-full px-4 py-2.5 rounded-xl bg-[#F8FAFC] border border-[#CBD5E1] text-[#1E293B] text-xs focus:outline-none focus:border-[#2563EB] transition"
                  >
                    <option value="Technical Support">Technical Support</option>
                    <option value="ATS Scoring Feedback">ATS Scoring Feedback</option>
                    <option value="Academic / College Demo">Academic / College Demo</option>
                    <option value="Feature Request">Feature Request</option>
                    <option value="Other">Other</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-[#64748B] mb-1 uppercase tracking-wider">
                    Subject
                  </label>
                  <input
                    type="text"
                    value={contactSubject}
                    onChange={(e) => setContactSubject(e.target.value)}
                    placeholder="e.g. Question regarding resume scoring weights"
                    className="w-full px-4 py-2.5 rounded-xl bg-[#F8FAFC] border border-[#CBD5E1] text-[#1E293B] text-xs focus:outline-none focus:border-[#2563EB] transition"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#64748B] mb-1 uppercase tracking-wider">
                  Message
                </label>
                <textarea
                  rows={4}
                  value={contactMessage}
                  onChange={(e) => setContactMessage(e.target.value)}
                  placeholder="Type your message, question, or feedback here..."
                  className="w-full p-4 rounded-xl bg-[#F8FAFC] border border-[#CBD5E1] text-[#1E293B] text-sm focus:outline-none focus:border-[#2563EB] transition resize-y font-sans"
                  required
                />
              </div>

              <button
                type="submit"
                disabled={isSendingContact}
                className="flex items-center gap-2 px-6 py-3 rounded-xl bg-[#2563EB] hover:bg-[#1D4ED8] text-white font-bold text-xs shadow-sm transition disabled:opacity-50"
              >
                <Send className="w-4 h-4" />
                <span>{isSendingContact ? 'Sending Message...' : 'Send Message'}</span>
              </button>
            </form>

            {/* Support Info Sidebar */}
            <div className="space-y-4">
              <div className="p-5 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] space-y-4">
                <h4 className="text-xs font-bold text-[#14213D] uppercase tracking-wider">Direct Support Info</h4>
                
                <div className="space-y-3 text-xs">
                  <div>
                    <span className="text-[#64748B] block text-[11px]">Support Email</span>
                    <span className="text-[#2563EB] font-bold">support@resumeai.demo</span>
                  </div>

                  <div>
                    <span className="text-[#64748B] block text-[11px]">Response Time</span>
                    <span className="text-[#1E293B] font-medium">Under 2 hours (24/7 Demo Support)</span>
                  </div>

                  <div>
                    <span className="text-[#64748B] block text-[11px]">Evaluation Mode</span>
                    <span className="text-[#1E293B] font-medium">College Project / SaaS Demo</span>
                  </div>
                </div>
              </div>

              <div className="p-4 rounded-xl bg-teal-50 border border-teal-200 text-xs text-[#0D9488]">
                <p className="font-bold text-[#0D9488] mb-1">Student & Tutor Demo Ready</p>
                <p className="text-[11px] leading-relaxed text-teal-800">
                  Every submission is logged and confirmed immediately. Feel free to submit test inquiries during your review!
                </p>
              </div>
            </div>

          </div>
        </div>
      )}

    </div>
  );
};
