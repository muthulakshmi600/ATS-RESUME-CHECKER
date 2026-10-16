/**
 * LandingPage Component: Premium modern SaaS landing page
 * ResumeAI ATS SaaS Theme
 */

window.LandingPage = ({ onNavigate, currentUser }) => {
  const {
    Sparkles, ArrowRight, CheckCircle, BarChart, ShieldCheck,
    Zap, FileText, Upload, Target, Clock, Award, Briefcase, ChevronRight,
    Linkedin, Naukri, Github, ExternalLink
  } = window.Icons;

  const features = [
    {
      icon: BarChart,
      title: "ATS Quality Audit",
      description: "Get an objective 0–100 resume quality score based on structure, formatting, metrics, and readability."
    },
    {
      icon: Target,
      title: "Job Description Matching",
      description: "Paste any employer job posting for precision TF-IDF mathematical skill and keyword alignment."
    },
    {
      icon: ShieldCheck,
      title: "Formatting & Contact Audit",
      description: "Ensure email, phone numbers, GitHub/LinkedIn links, and length meet automated scanner requirements."
    },
    {
      icon: Zap,
      title: "Action Verbs & Metrics",
      description: "Identify high-impact action verbs and quantified achievements (% / $ / scale) in your bullet points."
    },
    {
      icon: Award,
      title: "Skills Gap Analysis",
      description: "Instantly detect matched competencies alongside missing high-demand technical and soft skills."
    },
    {
      icon: CheckCircle,
      title: "Actionable Recommendations",
      description: "Receive prioritized, step-by-step guidance to optimize bullet points and eliminate ATS blockers."
    },
    {
      icon: Clock,
      title: "Audit History",
      description: "Keep track of all analyzed resumes, compare improvements over time, and revisit previous reports."
    },
    {
      icon: Briefcase,
      title: "Frictionless Dashboard",
      description: "A clean, modern SaaS experience engineered for candidates to build job-winning resumes."
    }
  ];

  const steps = [
    {
      number: "01",
      title: "Upload Resume",
      description: "Upload your PDF or DOCX resume with one click or drag & drop."
    },
    {
      number: "02",
      title: "Add Job Description (Optional)",
      description: "Paste a target job posting to evaluate job alignment, or evaluate standalone quality."
    },
    {
      number: "03",
      title: "Deep AI Audit",
      description: "ResumeAI evaluates sections, contact info, quantifiable metrics, formatting, and keywords."
    },
    {
      number: "04",
      title: "Optimize & Succeed",
      description: "Receive clear, actionable suggestions to increase your ATS score and interview callbacks."
    }
  ];

  return (
    <div className="bg-[#F8FAFC] text-[#1E293B] min-h-screen selection:bg-[#2563EB] selection:text-white">
      
      {/* Hero Section */}
      <section className="relative overflow-hidden pt-12 pb-20 lg:pt-16 lg:pb-28">
        
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="text-center max-w-3xl mx-auto mb-14">
            
            {/* Small badge */}
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-blue-50 border border-blue-200 text-[#2563EB] text-xs font-semibold uppercase tracking-wider mb-6">
              <Sparkles className="w-4 h-4 text-[#2563EB]" />
              <span>Next-Generation ATS Diagnostic Engine</span>
            </div>

            {/* Main heading */}
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-[#14213D] leading-[1.15] mb-6">
              Audit Your Resume <span className="text-[#2563EB]">ATS Score</span> in Seconds
            </h1>

            {/* Subtitle */}
            <p className="text-lg sm:text-xl text-[#64748B] leading-relaxed mb-8 max-w-2xl mx-auto">
              Ensure your resume passes applicant tracking systems. Get a deterministic quality score, formatting verification, and optional job description matching.
            </p>

            {/* Tagline pill */}
            <p className="text-xs font-bold text-[#14B8A6] tracking-widest uppercase mb-10">
              "Build a Resume That Gets Noticed."
            </p>

            {/* Primary & Secondary Buttons */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <button
                onClick={() => onNavigate(currentUser ? 'check-resume' : 'login')}
                className="w-full sm:w-auto flex items-center justify-center gap-2.5 px-8 py-4 rounded-xl bg-[#2563EB] hover:bg-[#1D4ED8] text-white font-bold text-base shadow-lg shadow-blue-600/20 transition-all hover:scale-[1.02] active:scale-[0.98]"
              >
                <span>Audit My Resume Free</span>
                <ArrowRight className="w-5 h-5" />
              </button>

              <a
                href="#how-it-works"
                className="w-full sm:w-auto flex items-center justify-center gap-2 px-8 py-4 rounded-xl bg-white hover:bg-slate-50 text-[#1E293B] font-semibold text-base border border-[#CBD5E1] transition shadow-sm"
              >
                <span>See How It Works</span>
              </a>
            </div>

          </div>

          {/* Hero Dashboard Preview Visual */}
          <div className="max-w-4xl mx-auto mt-6">
            <div className="rounded-2xl p-1 bg-white border border-[#E2E8F0] shadow-xl">
              <div className="bg-[#F8FAFC] rounded-xl p-6 sm:p-8 border border-[#E2E8F0]">
                
                {/* Visual Header bar */}
                <div className="flex items-center justify-between border-b border-[#E2E8F0] pb-4 mb-6">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-rose-400"></div>
                    <div className="w-3 h-3 rounded-full bg-amber-400"></div>
                    <div className="w-3 h-3 rounded-full bg-emerald-400"></div>
                    <span className="text-xs text-[#64748B] font-mono ml-2">resumeai-ats-engine</span>
                  </div>
                  <span className="text-[11px] font-bold text-[#2563EB] bg-blue-50 border border-blue-200 px-2.5 py-0.5 rounded-full">
                    Live Diagnostic Preview
                  </span>
                </div>

                {/* Visual Stats Row */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mb-6">
                  
                  {/* Quality Score card */}
                  <div className="bg-white border border-[#E2E8F0] rounded-xl p-5 flex items-center justify-between shadow-sm">
                    <div>
                      <p className="text-xs font-bold text-[#64748B] uppercase tracking-wider">Quality Score</p>
                      <div className="flex items-baseline gap-1 mt-1">
                        <span className="text-4xl font-extrabold text-[#14213D]">84</span>
                        <span className="text-sm font-semibold text-[#64748B]">/100</span>
                      </div>
                      <span className="inline-block mt-2 text-[10px] font-bold uppercase px-2 py-0.5 rounded bg-emerald-50 text-[#16A34A] border border-emerald-200">
                        Strong Candidate
                      </span>
                    </div>
                    <div className="w-13 h-13 rounded-xl bg-blue-50 border border-blue-200 flex items-center justify-center text-[#2563EB] p-3">
                      <Award className="w-7 h-7" />
                    </div>
                  </div>

                  {/* Formatting & Structure */}
                  <div className="bg-white border border-[#E2E8F0] rounded-xl p-5 flex items-center justify-between shadow-sm">
                    <div>
                      <p className="text-xs font-bold text-[#64748B] uppercase tracking-wider">Structure & Contact</p>
                      <div className="flex items-baseline gap-1 mt-1">
                        <span className="text-4xl font-extrabold text-[#14213D]">35</span>
                        <span className="text-sm font-semibold text-[#64748B]">/35 pts</span>
                      </div>
                      <span className="inline-block mt-2 text-[10px] font-bold uppercase px-2 py-0.5 rounded bg-teal-50 text-[#0D9488] border border-teal-200">
                        All Sections Valid
                      </span>
                    </div>
                    <div className="w-13 h-13 rounded-xl bg-teal-50 border border-teal-200 flex items-center justify-center text-[#14B8A6] p-3">
                      <ShieldCheck className="w-7 h-7" />
                    </div>
                  </div>

                  {/* Measurable Metrics */}
                  <div className="bg-white border border-[#E2E8F0] rounded-xl p-5 flex items-center justify-between shadow-sm">
                    <div>
                      <p className="text-xs font-bold text-[#64748B] uppercase tracking-wider">Quantified Impact</p>
                      <div className="flex items-baseline gap-1 mt-1">
                        <span className="text-4xl font-extrabold text-[#14213D]">12</span>
                        <span className="text-sm font-semibold text-[#64748B]">metrics</span>
                      </div>
                      <span className="inline-block mt-2 text-[10px] font-bold uppercase px-2 py-0.5 rounded bg-blue-50 text-[#2563EB] border border-blue-200">
                        High Data Density
                      </span>
                    </div>
                    <div className="w-13 h-13 rounded-xl bg-blue-50 border border-blue-200 flex items-center justify-center text-[#2563EB] p-3">
                      <Zap className="w-7 h-7" />
                    </div>
                  </div>

                </div>

                {/* Sub-visual pills */}
                <div className="bg-white rounded-xl p-4 border border-[#E2E8F0] flex flex-wrap items-center justify-between gap-3 text-xs text-[#64748B] shadow-sm">
                  <div className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-[#16A34A]" />
                    <span>Objective 6-Factor Quality Analysis</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-[#16A34A]" />
                    <span>Contact Info & Profiles Verified</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-[#16A34A]" />
                    <span>Action Verbs & Impact Aligned</span>
                  </div>
                </div>

              </div>
            </div>
          </div>

        </div>
      </section>

      {/* HOW IT WORKS SECTION */}
      <section id="how-it-works" className="py-20 bg-white border-y border-[#E2E8F0]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          
          <div className="text-center max-w-2xl mx-auto mb-16">
            <span className="text-xs font-bold text-[#2563EB] uppercase tracking-wider bg-blue-50 border border-blue-200 px-3 py-1 rounded-full">
              4 Simple Steps
            </span>
            <h2 className="text-3xl sm:text-4xl font-extrabold text-[#14213D] mt-4 mb-3">
              How ResumeAI Works
            </h2>
            <p className="text-[#64748B] text-sm sm:text-base">
              From upload to optimization in four frictionless steps designed to get your resume past applicant filters.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {steps.map((st, idx) => (
              <div 
                key={idx}
                className="bg-[#F8FAFC] border border-[#E2E8F0] rounded-2xl p-6 relative hover:border-[#2563EB] transition group"
              >
                <div className="text-3xl font-extrabold text-[#2563EB]/40 group-hover:text-[#2563EB] transition mb-4">
                  {st.number}
                </div>
                <h3 className="text-base font-bold text-[#14213D] mb-2">
                  {st.title}
                </h3>
                <p className="text-xs text-[#64748B] leading-relaxed">
                  {st.description}
                </p>
              </div>
            ))}
          </div>

          <div className="mt-14 text-center">
            <button
              onClick={() => onNavigate(currentUser ? 'check-resume' : 'login')}
              className="inline-flex items-center gap-2 px-7 py-3.5 rounded-xl bg-[#2563EB] hover:bg-[#1D4ED8] text-white font-bold text-sm transition shadow-md shadow-blue-500/20"
            >
              <span>Audit Your Resume Now</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>

        </div>
      </section>

      {/* FEATURES SECTION */}
      <section id="features" className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          
          <div className="text-center max-w-2xl mx-auto mb-16">
            <span className="text-xs font-bold text-[#2563EB] uppercase tracking-wider bg-blue-50 border border-blue-200 px-3 py-1 rounded-full">
              Comprehensive Suite
            </span>
            <h2 className="text-3xl sm:text-4xl font-extrabold text-[#14213D] mt-4 mb-3">
              Everything You Need for ATS Readiness
            </h2>
            <p className="text-[#64748B] text-sm sm:text-base">
              A comprehensive toolkit engineered to identify gaps, fine-tune wording, and maximize recruiter interview rates.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feat, idx) => {
              const Icon = feat.icon;
              return (
                <div
                  key={idx}
                  className="bg-white border border-[#E2E8F0] rounded-2xl p-6 hover:border-[#2563EB] transition shadow-sm"
                >
                  <div className="w-12 h-12 rounded-xl bg-blue-50 border border-blue-200 flex items-center justify-center text-[#2563EB] mb-5">
                    <Icon className="w-6 h-6" />
                  </div>
                  <h4 className="text-base font-bold text-[#14213D] mb-2">
                    {feat.title}
                  </h4>
                  <p className="text-xs text-[#64748B] leading-relaxed">
                    {feat.description}
                  </p>
                </div>
              );
            })}
          </div>

        </div>
      </section>

      {/* ABOUT & RECRUITER PORTAL INTEGRATIONS */}
      <section id="about" className="py-20 bg-white border-t border-[#E2E8F0]">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          
          <div className="text-center max-w-3xl mx-auto mb-12">
            <div className="w-12 h-12 mx-auto rounded-2xl bg-blue-50 border border-blue-200 flex items-center justify-center text-[#2563EB] mb-5">
              <Sparkles className="w-6 h-6" />
            </div>
            <h2 className="text-3xl font-extrabold text-[#14213D] mb-3">
              About ResumeAI ATS
            </h2>
            <p className="text-[#1E293B] text-sm sm:text-base leading-relaxed mb-4">
              ResumeAI ATS is an enterprise-grade resume auditing platform demonstrating full-stack engineering, transparent natural language document parsing, and responsive UI design.
            </p>
            <p className="text-[#64748B] text-xs sm:text-sm leading-relaxed">
              Designed specifically to help candidates pass automated screening filters on top recruitment portals like <strong className="text-[#14213D]">LinkedIn</strong> and <strong className="text-[#14213D]">Naukri.com</strong>.
            </p>
          </div>

          {/* LinkedIn & Naukri Integration Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-10">
            
            {/* LinkedIn Card */}
            <div className="bg-[#F8FAFC] border border-[#E2E8F0] hover:border-blue-400 rounded-2xl p-6 transition shadow-sm">
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 rounded-xl bg-blue-50 border border-blue-200 flex items-center justify-center text-[#0A66C2]">
                  <Linkedin className="w-6 h-6" />
                </div>
                <span className="text-[10px] font-bold uppercase px-2.5 py-1 rounded-full bg-blue-100 text-[#0A66C2]">
                  Global Tech Hiring
                </span>
              </div>
              <h3 className="text-base font-bold text-[#14213D] mb-2">
                Optimized for LinkedIn Recruiter
              </h3>
              <p className="text-xs text-[#64748B] leading-relaxed mb-5">
                Align headline keywords, core competencies, and project deliverables with LinkedIn’s semantic talent search algorithms.
              </p>
              <a
                href="https://www.linkedin.com/jobs/"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 text-xs font-bold text-[#0A66C2] hover:underline"
              >
                <span>Browse LinkedIn Jobs</span>
                <ExternalLink className="w-3.5 h-3.5" />
              </a>
            </div>

            {/* Naukri Card */}
            <div className="bg-[#F8FAFC] border border-[#E2E8F0] hover:border-blue-400 rounded-2xl p-6 transition shadow-sm">
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 rounded-xl bg-blue-50 border border-blue-200 flex items-center justify-center text-[#2563EB]">
                  <Naukri className="w-7 h-7" />
                </div>
                <span className="text-[10px] font-bold uppercase px-2.5 py-1 rounded-full bg-blue-100 text-[#2563EB]">
                  Top Indian Job Portal
                </span>
              </div>
              <h3 className="text-base font-bold text-[#14213D] mb-2">
                Tuned for Naukri.com & Resdex
              </h3>
              <p className="text-xs text-[#64748B] leading-relaxed mb-5">
                Target high-volume hiring pipelines across MNCs and startups. Ensure technology stack recognition by automated ATS parsers.
              </p>
              <a
                href="https://www.naukri.com/"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 text-xs font-bold text-[#2563EB] hover:underline"
              >
                <span>Browse Naukri.com Openings</span>
                <ExternalLink className="w-3.5 h-3.5" />
              </a>
            </div>

          </div>

          {/* Quick social links row */}
          <div className="flex flex-wrap items-center justify-center gap-4 text-xs text-[#64748B]">
            <a
              href="https://www.linkedin.com/"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-white hover:bg-slate-50 text-[#1E293B] border border-[#CBD5E1] transition shadow-sm"
            >
              <Linkedin className="w-4 h-4 text-[#0A66C2]" />
              <span>LinkedIn</span>
            </a>
            <a
              href="https://www.naukri.com/"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-white hover:bg-slate-50 text-[#1E293B] border border-[#CBD5E1] transition shadow-sm"
            >
              <Naukri className="w-4 h-4" />
              <span>Naukri.com</span>
            </a>
            <a
              href="https://github.com/"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-white hover:bg-slate-50 text-[#1E293B] border border-[#CBD5E1] transition shadow-sm"
            >
              <Github className="w-4 h-4" />
              <span>GitHub</span>
            </a>
          </div>

        </div>
      </section>

      {/* FOOTER */}
      <footer className="border-t border-[#E2E8F0] py-10 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6 pb-6 border-b border-[#E2E8F0] text-xs text-[#64748B]">
            <div className="flex items-center gap-3">
              <window.Logo isDark={false} size="sm" />
              <span>•</span>
              <span className="font-medium">"Build a Resume That Gets Noticed."</span>
            </div>

            <div className="flex items-center gap-6">
              <a href="https://www.linkedin.com/jobs/" target="_blank" rel="noopener noreferrer" className="hover:text-[#0A66C2] transition flex items-center gap-1">
                <Linkedin className="w-3.5 h-3.5 text-[#0A66C2]" />
                <span>LinkedIn Jobs</span>
              </a>
              <a href="https://www.naukri.com/" target="_blank" rel="noopener noreferrer" className="hover:text-[#2563EB] transition flex items-center gap-1">
                <Naukri className="w-3.5 h-3.5" />
                <span>Naukri Portal</span>
              </a>
              <a href="https://github.com/" target="_blank" rel="noopener noreferrer" className="hover:text-black transition flex items-center gap-1">
                <Github className="w-3.5 h-3.5" />
                <span>GitHub</span>
              </a>
            </div>
          </div>

          <div className="pt-6 flex flex-col sm:flex-row items-center justify-between gap-3 text-[11px] text-[#64748B]">
            <p>ResumeAI ATS SaaS Engine & Portfolio Demonstration.</p>
            <p>Compatible with LinkedIn, Naukri, Workday, Greenhouse & Taleo ATS screening standards.</p>
          </div>
        </div>
      </footer>

    </div>
  );
};
