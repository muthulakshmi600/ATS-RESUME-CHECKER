/**
 * SignUpPage Component: Registration with validation & seamless demo redirect
 * ResumeAI ATS SaaS Theme
 */

window.SignUpPage = ({ onNavigate, showToast }) => {
  const { ArrowRight, AlertCircle, ShieldCheck } = window.Icons;
  const [name, setName] = React.useState('');
  const [email, setEmail] = React.useState('');
  const [password, setPassword] = React.useState('');
  const [confirmPassword, setConfirmPassword] = React.useState('');
  const [error, setError] = React.useState('');
  const [isLoading, setIsLoading] = React.useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!name.trim() || !email.trim() || !password.trim() || !confirmPassword.trim()) {
      setError('Please fill in all fields.');
      return;
    }

    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim())) {
      setError('Please enter a valid email address.');
      return;
    }

    if (password !== confirmPassword) {
      setError('Password and Confirm Password must match.');
      return;
    }

    if (password.length < 4) {
      setError('Password should be at least 4 characters long.');
      return;
    }

    setIsLoading(true);
    try {
      await window.ResumeAIService.signup(name.trim(), email.trim(), password.trim(), confirmPassword.trim());
      showToast('Account created successfully! Please sign in.', 'success');
      onNavigate('login');
    } catch (err) {
      setError(err.message || 'Registration failed.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#F8FAFC] flex flex-col justify-center py-12 sm:px-6 lg:px-8 relative overflow-hidden">
      
      <div className="sm:mx-auto sm:w-full sm:max-w-md relative z-10">
        
        {/* Brand Logo */}
        <div 
          onClick={() => onNavigate('landing')}
          className="flex justify-center cursor-pointer mb-6 transition-transform hover:scale-105"
        >
          <window.Logo isDark={false} size="lg" />
        </div>

        <h2 className="text-center text-2xl font-extrabold text-[#14213D]">
          Create your candidate account
        </h2>
        <p className="mt-1.5 text-center text-xs text-[#64748B]">
          Already have an account?{' '}
          <button 
            onClick={() => onNavigate('login')}
            className="font-bold text-[#2563EB] hover:text-[#1D4ED8] hover:underline"
          >
            Login
          </button>
        </p>

        {/* Demo Notice */}
        <div className="mt-4 mx-4 sm:mx-0 p-3 rounded-xl bg-blue-50 border border-blue-200 text-xs text-[#2563EB] flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-[#2563EB] flex-shrink-0" />
          <span className="text-slate-700">Demo environment: Instant activation without email verification delays.</span>
        </div>
      </div>

      <div className="mt-5 sm:mx-auto sm:w-full sm:max-w-md relative z-10 px-4 sm:px-0">
        <div className="bg-white border border-[#E2E8F0] py-8 px-6 sm:px-8 shadow-sm rounded-2xl">
          
          <form className="space-y-4" onSubmit={handleSubmit}>
            
            {error && (
              <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-xs text-rose-600 flex items-center gap-2">
                <AlertCircle className="w-4 h-4 flex-shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <div>
              <label className="block text-xs font-semibold text-[#64748B] uppercase tracking-wider mb-1.5">
                Full Name
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Candidate Name"
                className="w-full px-4 py-2.5 rounded-xl bg-[#F8FAFC] border border-[#CBD5E1] text-[#1E293B] placeholder-slate-400 text-sm focus:outline-none focus:border-[#2563EB] focus:ring-1 focus:ring-[#2563EB] transition"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-[#64748B] uppercase tracking-wider mb-1.5">
                Email address
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="candidate@example.com"
                className="w-full px-4 py-2.5 rounded-xl bg-[#F8FAFC] border border-[#CBD5E1] text-[#1E293B] placeholder-slate-400 text-sm focus:outline-none focus:border-[#2563EB] focus:ring-1 focus:ring-[#2563EB] transition"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-[#64748B] uppercase tracking-wider mb-1.5">
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full px-4 py-2.5 rounded-xl bg-[#F8FAFC] border border-[#CBD5E1] text-[#1E293B] placeholder-slate-400 text-sm focus:outline-none focus:border-[#2563EB] focus:ring-1 focus:ring-[#2563EB] transition"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-[#64748B] uppercase tracking-wider mb-1.5">
                Confirm Password
              </label>
              <input
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full px-4 py-2.5 rounded-xl bg-[#F8FAFC] border border-[#CBD5E1] text-[#1E293B] placeholder-slate-400 text-sm focus:outline-none focus:border-[#2563EB] focus:ring-1 focus:ring-[#2563EB] transition"
              />
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full flex items-center justify-center gap-2 py-3 px-4 rounded-xl bg-[#2563EB] hover:bg-[#1D4ED8] text-white text-sm font-bold shadow-sm transition-all hover:scale-[1.01] active:scale-[0.99] disabled:opacity-50 mt-2"
            >
              {isLoading ? (
                <span>Creating Account...</span>
              ) : (
                <>
                  <span>Create Account</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          <div className="mt-6 border-t border-[#E2E8F0] pt-5 text-center">
            <p className="text-xs text-[#64748B]">
              Already registered?{' '}
              <button
                onClick={() => onNavigate('login')}
                className="font-bold text-[#2563EB] hover:text-[#1D4ED8] hover:underline"
              >
                Sign In
              </button>
            </p>
          </div>

        </div>
      </div>

    </div>
  );
};
