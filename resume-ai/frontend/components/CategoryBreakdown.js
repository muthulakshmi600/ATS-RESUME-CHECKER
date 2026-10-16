/**
 * CategoryBreakdown Component: Visual breakdown of the 6 scoring dimensions
 * ResumeAI ATS SaaS Theme
 */

window.CategoryBreakdown = ({ breakdown = {}, maxBreakdown = {} }) => {
  const safeBreakdown = (breakdown && typeof breakdown === 'object') ? breakdown : {};
  const safeMaxBreakdown = (maxBreakdown && typeof maxBreakdown === 'object') ? maxBreakdown : {};

  const getVal = (primaryKey, altKey, defaultVal = 0) => {
    if (safeBreakdown[primaryKey] !== undefined) return safeBreakdown[primaryKey];
    if (altKey && safeBreakdown[altKey] !== undefined) return safeBreakdown[altKey];
    return defaultVal;
  };

  const getMax = (primaryKey, altKey, defaultMax = 15) => {
    if (safeMaxBreakdown[primaryKey] !== undefined) return safeMaxBreakdown[primaryKey];
    if (altKey && safeMaxBreakdown[altKey] !== undefined) return safeMaxBreakdown[altKey];
    return defaultMax;
  };

  const categories = [
    {
      key: 'structure',
      label: 'Section Completeness',
      max: getMax('structure', null, 20),
      value: getVal('structure', null, 0),
      description: 'Presence of standard ATS sections: Summary, Experience, Education, Skills, and Projects',
      color: 'royal'
    },
    {
      key: 'contact',
      label: 'Contact Info & Profiles',
      max: getMax('contact', null, 15),
      value: getVal('contact', null, 0),
      description: 'Clean email address, validated phone number, LinkedIn, and GitHub/Portfolio URLs',
      color: 'teal'
    },
    {
      key: 'metrics',
      label: 'Measurable Achievements',
      max: getMax('metrics', 'achievements', 20),
      value: getVal('metrics', 'achievements', 0),
      description: 'Quantifiable achievements (% growth, dollar savings, latency cuts, numbers in bullets)',
      color: 'royal'
    },
    {
      key: 'formatting',
      label: 'ATS Formatting & Length',
      max: getMax('formatting', null, 15),
      value: getVal('formatting', null, 0),
      description: 'Optimal 400–1000 word length, bullet point density, and readable text hierarchy',
      color: 'teal'
    },
    {
      key: 'readability',
      label: 'Readability & Action Verbs',
      max: getMax('readability', null, 15),
      value: getVal('readability', null, 0),
      description: 'Dynamic power verbs (Architected, Spearheaded, Built) and clean professional tone',
      color: 'navy'
    },
    {
      key: 'skills',
      label: 'Technical Skills Breadth',
      max: getMax('skills', null, 15),
      value: getVal('skills', null, 0),
      description: 'Recognized technical libraries, developer frameworks, programming languages, and tools',
      color: 'royal'
    }
  ];

  const barColors = {
    royal: 'bg-[#2563EB]',
    teal: 'bg-[#14B8A6]',
    navy: 'bg-[#14213D]'
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {categories.map(cat => {
        const percentage = Math.round((cat.value / cat.max) * 100);
        return (
          <div key={cat.key} className="bg-white border border-[#E2E8F0] rounded-2xl p-4.5 hover:border-slate-300 transition shadow-sm">
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-sm font-bold text-[#14213D]">{cat.label}</span>
              <span className="text-xs font-semibold text-[#64748B]">
                <span className="text-[#14213D] font-extrabold text-sm">{cat.value}</span> / {cat.max} pts
              </span>
            </div>
            
            <p className="text-xs text-[#64748B] mb-3 h-8 line-clamp-2 leading-relaxed">
              {cat.description}
            </p>

            <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
              <div
                className={`h-2 rounded-full transition-all duration-800 ease-out ${barColors[cat.color] || 'bg-[#2563EB]'}`}
                style={{ width: `${Math.min(100, percentage)}%` }}
              />
            </div>

            <div className="flex justify-between items-center mt-2 text-[11px] text-[#64748B]">
              <span>Score Weight</span>
              <span className="font-bold text-[#14213D]">{percentage}%</span>
            </div>
          </div>
        );
      })}
    </div>
  );
};
