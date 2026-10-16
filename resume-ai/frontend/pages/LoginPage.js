/**
 * LoginPage Component: Professional demo login page
 * ResumeAI ATS SaaS Theme
 */

window.LoginPage = ({ onNavigate, onLoginSuccess, showToast }) => {
  const { ArrowRight, AlertCircle, ShieldCheck } = window.Icons;
  const [email, setEmail] = React.useState('test@gmail.com');
  const [password, setPassword] = React.useState('12345');
  const [error, setError] = React.useState('');
  const [isLoading, setIsLoading] = React.useState(false);
  const [showForgotModal, setShowForgotModal] = React.useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!email.trim() || !password.trim()) {
      setError('Please enter email and password.');
      return;
    }

    setIsLoading(true);
    try {
      const user = await window.ResumeAIService.login(email.trim(), password.trim());
      showToast(`Logged in successfully as ${user.name}!`, 'success');
      onLoginSuccess(user);
      onNavigate('dashboard');
    } catch (err) {
      setError(err.message || 'Login failed. Please try again.');
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
          Sign in to your account
        </h2>
        <p className="mt-1.5 text-center text-xs text-[#64748B]">
          Or{' '}
          <button 
            onClick={() => onNavigate('signup')}
            className="font-bold text-[#2563EB] hover:text-[#1D4ED8] hover:underline"
          >
            create a new account
          </button>
        </p>

        {/* Demo Mode Notice Banner */}
        <div className="mt-4 mx-4 sm:mx-0 p-3 rounded-xl bg-blue-50 border border-blue-200 text-xs text-[#2563EB] flex items-start gap-2.5">
          <ShieldCheck className="w-4 h-4 text-[#2563EB] mt-0.5 flex-shrink-0" />
          <div className="text-slate-700">
            <span className="font-bold text-[#14213D]">Quick Demo:</span> Enter any non-empty credentials (e.g. <span className="font-mono text-[#2563EB]">test@gmail.com</span> / <span className="font-mono text-[#2563EB]">12345</span>).
          </div>
        </div>
      </div>

      <div className="mt-6 sm:mx-auto sm:w-full sm:max-w-md relative z-10 px-4 sm:px-0">
        <div className="bg-white border border-[#E2E8F0] py-8 px-6 sm:px-8 shadow-sm rounded-2xl">
          
          <form className="space-y-5" onSubmit={handleSubmit}>
            
            {error && (
              <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-xs text-rose-600 flex items-center gap-2">
                <AlertCircle className="w-4 h-4 flex-shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <div>
              <label className="block text-xs font-semibold text-[#64748B] uppercase tracking-wider mb-1.5">
                Email address
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                className="w-full px-4 py-2.5 rounded-xl bg-[#F8FAFC] border border-[#CBD5E1] text-[#1E293B] placeholder-slate-400 text-sm focus:outline-none focus:border-[#2563EB] focus:ring-1 focus:ring-[#2563EB] transition"
              />
            </div>

            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="block text-xs font-semibold text-[#64748B] uppercase tracking-wider">
                  Password
                </label>
                <button
                  type="button"
                  onClick={() => setShowForgotModal(true)}
                  className="text-xs text-[#2563EB] hover:text-[#1D4ED8] hover:underline"
                >
                  Forgot Password?
                </button>
              </div>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full px-4 py-2.5 rounded-xl bg-[#F8FAFC] border border-[#CBD5E1] text-[#1E293B] placeholder-slate-400 text-sm focus:outline-none focus:border-[#2563EB] focus:ring-1 focus:ring-[#2563EB] transition"
              />
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full flex items-center justify-center gap-2 py-3 px-4 rounded-xl bg-[#2563EB] hover:bg-[#1D4ED8] text-white text-sm font-bold shadow-sm transition-all hover:scale-[1.01] active:scale-[0.99] disabled:opacity-50"
            >
              {isLoading ? (
                <span>Signing in...</span>
              ) : (
                <>
                  <span>Sign In</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          <div className="mt-6 border-t border-[#E2E8F0] pt-5 space-y-3 text-center">
            <p className="text-xs text-[#64748B]">
              Don't have an account?{' '}
              <button
                onClick={() => onNavigate('signup')}
                className="font-bold text-[#2563EB] hover:text-[#1D4ED8] hover:underline"
              >
                Sign Up
              </button>
            </p>
          </div>

        </div>
      </div>

      {/* Forgot Password Modal */}
      {showForgotModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white border border-[#E2E8F0] rounded-2xl p-6 max-w-sm w-full shadow-2xl">
            <h3 className="text-base font-bold text-[#14213D] mb-2">Reset Password</h3>
            <p className="text-xs text-[#64748B] mb-4">
              Demo environment: Any password will allow authentication. Simply sign in with your email.
            </p>
            <button
              onClick={() => setShowForgotModal(false)}
              className="w-full py-2.5 rounded-xl bg-[#2563EB] text-white text-xs font-bold"
            >
              Back to Login
            </button>
          </div>
        </div>
      )}

    </div>
  );
};
