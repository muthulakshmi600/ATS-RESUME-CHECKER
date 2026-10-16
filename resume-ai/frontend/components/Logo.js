/**
 * Reusable, sharp vector Logo component for ResumeAI ATS.
 * Combines Document/Resume, AI Intelligence nodes, and verifying Checkmark.
 * Supports 'sm', 'md', 'lg' sizes and 'full' vs 'icon-only' variants.
 */

window.Logo = ({
  size = 'md',
  variant = 'full',
  className = '',
  isDark = false,
  showSubtitle = true,
  onClick
}) => {
  const iconDimensions = {
    sm: { w: 30, h: 30, box: "w-8 h-8" },
    md: { w: 38, h: 38, box: "w-10 h-10" },
    lg: { w: 50, h: 50, box: "w-12 h-12" }
  }[size] || { w: 38, h: 38, box: "w-10 h-10" };

  const textSizes = {
    sm: "text-lg",
    md: "text-xl",
    lg: "text-2xl"
  }[size] || "text-xl";

  const badgeSizes = {
    sm: "text-[9px] px-1.5 py-0.5",
    md: "text-[10px] px-2 py-0.5",
    lg: "text-xs px-2.5 py-0.5"
  }[size] || "text-[10px] px-2 py-0.5";

  return (
    <div 
      onClick={onClick}
      className={`inline-flex items-center gap-3 select-none ${onClick ? 'cursor-pointer group' : ''} ${className}`}
    >
      {/* Crisp Vector Icon Container */}
      <div className={`relative flex-shrink-0 ${iconDimensions.box} flex items-center justify-center transition-transform duration-200 ${onClick ? 'group-hover:scale-105' : ''}`}>
        <svg
          width={iconDimensions.w}
          height={iconDimensions.h}
          viewBox="0 0 40 40"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className="drop-shadow-sm"
        >
          <defs>
            <linearGradient id="logoDocGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#14213D" />
              <stop offset="100%" stopColor="#2563EB" />
            </linearGradient>
            <linearGradient id="logoCheckGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#14B8A6" />
              <stop offset="100%" stopColor="#16A34A" />
            </linearGradient>
          </defs>

          {/* Document Sheet */}
          <rect x="4" y="3" width="26" height="32" rx="5" fill="url(#logoDocGrad)" />
          
          {/* Folded Corner */}
          <path d="M22 3 L30 11 L22 11 Z" fill="#93C5FD" opacity="0.75" />
          
          {/* Document Content Lines */}
          <line x1="9" y1="12" x2="18" y2="12" stroke="#FFFFFF" strokeWidth="2" strokeLinecap="round" />
          <line x1="9" y1="17" x2="22" y2="17" stroke="#DBEAFE" strokeWidth="1.8" strokeLinecap="round" />
          <line x1="9" y1="22" x2="16" y2="22" stroke="#DBEAFE" strokeWidth="1.8" strokeLinecap="round" />

          {/* AI Intelligence Nodes & Links */}
          <circle cx="21" cy="22" r="1.8" fill="#14B8A6" />
          <circle cx="26" cy="17" r="1.8" fill="#14B8A6" />
          <line x1="21" y1="22" x2="26" y2="17" stroke="#14B8A6" strokeWidth="1.2" strokeDasharray="1.5 1" />
          
          {/* Subtle Sparkle Star */}
          <path d="M10 27 L11 25.5 L12 27 L13.5 28 L12 29 L11 30.5 L10 29 L8.5 28 Z" fill="#38BDF8" />

          {/* Verifying Checkmark Badge */}
          <circle cx="27" cy="27" r="7.5" fill="#FFFFFF" />
          <circle cx="27" cy="27" r="6.2" fill="url(#logoCheckGrad)" />
          <path d="M24 27 L26 29 L30 25" stroke="#FFFFFF" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </div>

      {/* Typography: ResumeAI ATS */}
      {variant === 'full' && (
        <div className="flex flex-col">
          <div className="flex items-center gap-1.5 leading-none">
            <span className={`font-extrabold tracking-tight ${textSizes} ${isDark ? 'text-white' : 'text-[#14213D]'}`}>
              Resume<span className="text-[#2563EB]">AI</span>
            </span>
            <span className={`font-extrabold tracking-wider uppercase rounded-md bg-[#EFF6FF] text-[#2563EB] border border-[#BFDBFE] ${badgeSizes}`}>
              ATS
            </span>
          </div>
          {showSubtitle && (
            <p className={`text-[10px] font-medium tracking-wide mt-0.5 ${isDark ? 'text-slate-400' : 'text-[#64748B]'}`}>
              Intelligent Resume Score
            </p>
          )}
        </div>
      )}
    </div>
  );
};
