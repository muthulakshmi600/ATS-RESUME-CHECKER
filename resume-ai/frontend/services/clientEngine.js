/**
 * Client-side ATS Scoring Engine for ResumeAI ATS.
 * Mirrors the Python backend analyzer:
 * - Zero dependency on Target Job Role.
 * - Computes Resume Quality Score (0-100) across 6 core factors:
 *   1. Structure & Sections (20 pts)
 *   2. Contact Info & Links (15 pts)
 *   3. Measurable Achievements & Action Verbs (20 pts)
 *   4. ATS Formatting, Layout & Length (15 pts)
 *   5. Readability, Tone & Style (15 pts)
 *   6. Technical Skills Breadth & Depth (15 pts)
 * - If Job Description is provided:
 *   Calculates separate Job Match Score (0-100) and extracts matched & missing JD skills.
 * - If no Job Description:
 *   Returns pure Resume Quality Score with a clear explanation of what it measures.
 */

window.ClientATSEngine = (() => {
  const ACTION_VERBS = [
    "accelerated", "accomplished", "achieved", "acquired", "adapted", "administered",
    "analyzed", "architected", "automated", "built", "centralized", "championed",
    "collaborated", "configured", "constructed", "converted", "coordinated", "created",
    "debugged", "decreased", "delivered", "deployed", "designed", "developed",
    "devised", "diagnosed", "directed", "documented", "doubled", "engineered",
    "enhanced", "established", "evaluated", "executed", "expanded", "expedited",
    "formulated", "generated", "guided", "implemented", "improved", "increased",
    "initiated", "inspected", "integrated", "invented", "launched", "led",
    "leveraged", "managed", "maximized", "mentored", "migrated", "minimized",
    "modernized", "monitored", "negotiated", "optimized", "orchestrated", "organized",
    "overhauled", "pioneered", "planned", "programmed", "reduced", "refactored",
    "resolved", "restructured", "revamped", "scaled", "secured", "simplified",
    "spearheaded", "standardized", "streamlined", "strengthened", "supervised",
    "trained", "transformed", "upgraded", "validated", "yielded"
  ];

  const BUZZWORD_CLICHES = [
    "team player", "go-getter", "hard worker", "results-driven", "detail-oriented",
    "self-starter", "think outside the box", "synergy", "proven track record",
    "dynamic individual", "strong work ethic", "fast learner"
  ];

  const UNIVERSAL_SKILLS = [
    "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "Go", "Rust", "Ruby", "PHP",
    "Swift", "Kotlin", "SQL", "HTML5", "CSS3", "Bash", "Shell Scripting", "PowerShell",
    "React", "Next.js", "Vue.js", "Angular", "Node.js", "Express.js", "Django", "Flask", "FastAPI",
    "Spring Boot", "Tailwind CSS", "Bootstrap", "Redux", "GraphQL", "REST APIs",
    "PyTorch", "TensorFlow", "Keras", "Scikit-Learn", "Pandas", "NumPy", "Scipy", "Matplotlib", "Seaborn",
    "PostgreSQL", "MySQL", "MongoDB", "Redis", "SQLite", "Oracle DB", "Cassandra", "DynamoDB",
    "AWS", "Microsoft Azure", "Google Cloud", "Docker", "Kubernetes", "CI/CD", "GitHub Actions",
    "Jenkins", "Terraform", "Linux", "Git", "GitHub", "GitLab",
    "Machine Learning", "Deep Learning", "NLP", "Computer Vision", "LLMs", "Generative AI",
    "Data Science", "Data Analysis", "Data Analytics", "Power BI", "Tableau", "Excel",
    "Agile", "Scrum", "Unit Testing", "TDD", "Code Review", "Microservices", "System Design", "OOP"
  ];

  function analyze(text, jobDesc = "") {
    if (!text || text.trim().length < 40) {
      throw new Error("Unable to extract sufficient text from resume. Please check file format.");
    }

    const lower = text.toLowerCase();
    const hasJd = Boolean(jobDesc && jobDesc.trim().length >= 30);

    // 1. Structure & Sections (20 pts)
    const sectionStatus = {
      "Contact Information": /@|contact|phone|email|linkedin|address/.test(lower),
      "Professional Summary": /summary|about me|profile|executive summary|career objective|objective/.test(lower),
      "Experience": /experience|employment|work history|career history|internship/.test(lower),
      "Education": /education|academic|qualifications|degree|university|college/.test(lower),
      "Skills": /skills|technologies|competencies|core competencies|tools|expertise/.test(lower),
      "Projects": /projects|portfolio|personal projects|featured projects/.test(lower),
      "Certifications": /certifications|certificates|licenses|accreditations|courses/.test(lower)
    };

    let structureScore = 0;
    if (sectionStatus["Contact Information"]) structureScore += 3;
    if (sectionStatus["Professional Summary"]) structureScore += 3;
    if (sectionStatus["Experience"]) structureScore += 5;
    if (sectionStatus["Education"]) structureScore += 3;
    if (sectionStatus["Skills"]) structureScore += 3;
    if (sectionStatus["Projects"] || sectionStatus["Certifications"]) structureScore += 3;
    structureScore = Math.min(20, structureScore);

    // 2. Contact Information & Links (15 pts)
    let contactScore = 0;
    const hasEmail = /[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+/.test(text);
    if (hasEmail) contactScore += 4;

    const hasPhone = /(\+?\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}/.test(text);
    if (hasPhone) contactScore += 4;

    const hasLinks = /(linkedin\.com|github\.com|gitlab\.com|portfolio|https?:\/\/)/.test(lower);
    if (hasLinks) contactScore += 4;

    const hasLocation = /(bangalore|chennai|hyderabad|mumbai|pune|delhi|new york|san francisco|seattle|austin|london|india|usa|canada)/.test(lower) ||
      /\b[A-Z][a-zA-Z]+,\s*[A-Z]{2}\b/.test(text);
    if (hasLocation) contactScore += 3;
    contactScore = Math.min(15, contactScore);

    // 3. Measurable Achievements & Action Verbs (20 pts)
    const metricMatches = lower.match(/(?:\b\d+(?:\.\d+)?%|\b\d+x\b|\$\d+[\d,]*(?:\.\d+)?|\b₹\d+[\d,]*(?:\.\d+)?|\b\d+[\d,]*\+?\s*(?:[a-z-]+\s+)?(?:users|clients|customers|projects|downloads|requests|tickets|students|team members|engineers|microservices|apis|records|stars|samples|queries|tests)\b|\b(?:reduced|increased|improved|saved|boosted|accelerated|scaled)\s+[a-z\s]{0,25}\b\d+)/g) || [];
    const metricsCount = metricMatches.length;
    let metricsPts = 0;
    if (metricsCount >= 6) metricsPts = 10;
    else if (metricsCount >= 4) metricsPts = 8;
    else if (metricsCount >= 2) metricsPts = 5;
    else if (metricsCount >= 1) metricsPts = 3;

    let actionVerbsFound = 0;
    const wordsSet = new Set(lower.match(/\b[a-z]+\b/g) || []);
    ACTION_VERBS.forEach(v => {
      if (wordsSet.has(v)) actionVerbsFound++;
    });

    let verbPts = 0;
    if (actionVerbsFound >= 10) verbPts = 10;
    else if (actionVerbsFound >= 7) verbPts = 8;
    else if (actionVerbsFound >= 4) verbPts = 5;
    else if (actionVerbsFound >= 2) verbPts = 3;

    const achievementsScore = Math.min(20, metricsPts + verbPts);

    // 4. ATS Formatting, Layout & Length (15 pts)
    let formattingScore = 0;
    const words = text.trim().split(/\s+/).length;
    let lengthStatus = "Optimal (1-2 pages)";
    if (words >= 300 && words <= 1100) {
      formattingScore += 5;
    } else if ((words >= 200 && words < 300) || (words > 1100 && words <= 1500)) {
      formattingScore += 3;
      lengthStatus = "Acceptable length";
    } else {
      formattingScore += 1;
      lengthStatus = words < 200 ? "Too brief" : "Too lengthy";
    }

    const lines = text.split('\n').filter(l => l.trim().length > 0);
    const bulletLines = lines.filter(l => /^[•\-\*–—]|\d+\./.test(l.trim()));
    const bulletCount = bulletLines.length;
    if (bulletCount >= 8) formattingScore += 5;
    else if (bulletCount >= 4) formattingScore += 3;
    else if (bulletCount >= 1) formattingScore += 2;

    formattingScore += 5; // Clean text encoding
    formattingScore = Math.min(15, formattingScore);

    // 5. Readability, Tone & Style (15 pts)
    let readabilityScore = 0;
    if (bulletCount > 0) {
      const avgBulletWords = bulletLines.reduce((acc, b) => acc + b.split(/\s+/).length, 0) / bulletCount;
      if (avgBulletWords >= 10 && avgBulletWords <= 26) readabilityScore += 5;
      else if (avgBulletWords >= 6 && avgBulletWords < 10) readabilityScore += 3;
      else readabilityScore += 2;
    } else {
      readabilityScore += 2;
    }

    const clichesFound = BUZZWORD_CLICHES.filter(c => lower.includes(c));
    readabilityScore += Math.max(1, 5 - clichesFound.length);

    const hasPassiveHeavy = /responsible for|duties included|assisted with/.test(lower);
    readabilityScore += hasPassiveHeavy ? 3 : 5;
    readabilityScore = Math.min(15, readabilityScore);

    // 6. Skills Breadth & Technical Depth (15 pts)
    const detectedSkills = [];
    UNIVERSAL_SKILLS.forEach(skill => {
      const reg = new RegExp(`(?:^|\\W)${skill.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}(?:$|\\W)`, "i");
      if (reg.test(lower)) {
        if (!detectedSkills.includes(skill)) detectedSkills.push(skill);
      }
    });

    const skillCount = detectedSkills.length;
    let skillsScore = 0;
    if (skillCount >= 15) skillsScore = 15;
    else if (skillCount >= 11) skillsScore = 12;
    else if (skillCount >= 7) skillsScore = 9;
    else if (skillCount >= 4) skillsScore = 6;
    else if (skillCount >= 1) skillsScore = 3;

    // Total Resume Quality Score (0 - 100)
    const resumeQualityScore = Math.min(100, Math.max(0,
      structureScore + contactScore + achievementsScore +
      formattingScore + readabilityScore + skillsScore
    ));

    // Optional Job Match
    let jobMatchScore = null;
    let matchedJdSkills = [];
    let missingJdSkills = [];
    let jobMatchDetails = null;
    let overallScore = resumeQualityScore;

    if (hasJd) {
      const jdLower = jobDesc.toLowerCase();
      const jdRequiredSkills = UNIVERSAL_SKILLS.filter(s => {
        const reg = new RegExp(`(?:^|\\W)${s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}(?:$|\\W)`, "i");
        return reg.test(jdLower);
      });

      const effectiveJdSkills = jdRequiredSkills.length > 0 ? jdRequiredSkills : ["Communication", "Problem Solving", "Git"];
      const resumeSkillSet = new Set(detectedSkills.map(s => s.toLowerCase()));

      effectiveJdSkills.forEach(s => {
        if (resumeSkillSet.has(s.toLowerCase())) matchedJdSkills.push(s);
        else missingJdSkills.push(s);
      });

      const skillMatchPct = Math.round((matchedJdSkills.length / Math.max(1, effectiveJdSkills.length)) * 100);

      // Overlap calculation
      const jdWords = jdLower.match(/\b[a-z]{4,}\b/g) || [];
      let overlap = 0;
      jdWords.forEach(w => { if (wordsSet.has(w)) overlap++; });
      const semanticPct = jdWords.length > 0 ? Math.min(100, Math.round((overlap / jdWords.length) * 150)) : skillMatchPct;

      jobMatchScore = Math.min(100, Math.max(10, Math.round(0.55 * skillMatchPct + 0.45 * semanticPct)));
      overallScore = Math.min(100, Math.max(0, Math.round(0.5 * resumeQualityScore + 0.5 * jobMatchScore)));

      jobMatchDetails = {
        job_match_score: jobMatchScore,
        skill_match_pct: skillMatchPct,
        semantic_similarity_pct: semanticPct,
        matched_skills: matchedJdSkills,
        missing_skills: missingJdSkills
      };
    }

    // Dynamic suggestions
    const suggestions = [];
    if (!sectionStatus["Professional Summary"]) {
      suggestions.push({
        category: "Structure",
        priority: "High",
        text: "Add a crisp 3-4 sentence 'Professional Summary' highlighting your primary value, years of experience, and signature strengths."
      });
    }
    if (!sectionStatus["Skills"]) {
      suggestions.push({
        category: "Structure",
        priority: "High",
        text: "Add a dedicated 'Technical Skills' section categorizing your programming languages, frameworks, databases, and developer tools."
      });
    }
    if (!hasLinks) {
      suggestions.push({
        category: "Contact Information",
        priority: "High",
        text: "Include your LinkedIn profile URL and GitHub or online portfolio link to showcase verified code."
      });
    }
    if (metricsCount < 3) {
      suggestions.push({
        category: "Measurable Impact",
        priority: "High",
        text: "Quantify your achievements using specific numbers or percentages (e.g., 'reduced query latency by 35%')."
      });
    }
    if (actionVerbsFound < 7) {
      suggestions.push({
        category: "Action Verbs",
        priority: "Medium",
        text: "Begin experience bullets with strong action verbs (e.g., 'Architected', 'Spearheaded', 'Optimized') instead of passive statements."
      });
    }
    if (clichesFound.length > 0) {
      suggestions.push({
        category: "Tone & Style",
        priority: "Medium",
        text: `Replace generic buzzwords (${clichesFound.slice(0, 3).map(c => `'${c}'`).join(', ')}) with concrete project results.`
      });
    }
    if (hasJd && missingJdSkills.length > 0) {
      suggestions.push({
        category: "Job Match",
        priority: "High",
        text: `Your target job specifically requires: ${missingJdSkills.slice(0, 4).join(', ')}. If you possess this experience, add it to your resume.`
      });
    } else if (!hasJd) {
      suggestions.push({
        category: "Job Matching",
        priority: "Low",
        text: "Paste an employer's Job Description to calculate targeted skill gap matching and alignment."
      });
    }

    const summary = hasJd
      ? (jobMatchScore >= 80
          ? `Outstanding Job Alignment (${jobMatchScore}%) with a Resume Quality Score of ${resumeQualityScore}/100. High alignment across key requirements.`
          : `Moderate Job Alignment (${jobMatchScore}%) with a Resume Quality Score of ${resumeQualityScore}/100. Key proficiencies detected, but specific JD skills are missing.`)
      : (resumeQualityScore >= 80
          ? `Exceptional Resume Quality (${resumeQualityScore}/100). Clean structure, strong technical skills, and quantified accomplishments ready for ATS parsing.`
          : `Resume Quality Score: ${resumeQualityScore}/100. Solid foundation; review the recommendations below to improve formatting, metrics, and technical depth.`);

    const grade = overallScore >= 90
      ? { label: "Excellent", color: "emerald", badge: "High ATS Compatibility" }
      : overallScore >= 75
      ? { label: "Good", color: "blue", badge: "Competitive Candidate" }
      : overallScore >= 60
      ? { label: "Fair", color: "amber", badge: "Moderate ATS Risk" }
      : { label: "Needs Improvement", color: "rose", badge: "High ATS Risk" };

    return {
      overall_score: overallScore,
      resume_quality_score: resumeQualityScore,
      job_match_score: jobMatchScore,
      has_job_description: hasJd,
      grade,
      breakdown: {
        structure: structureScore,
        contact: contactScore,
        achievements: achievementsScore,
        formatting: formattingScore,
        readability: readabilityScore,
        skills: skillsScore
      },
      max_breakdown: {
        structure: 20,
        contact: 15,
        achievements: 20,
        formatting: 15,
        readability: 15,
        skills: 15
      },
      section_status: sectionStatus,
      contact_details: { has_email: hasEmail, has_phone: hasPhone, has_links: hasLinks, has_location: hasLocation },
      achievements_details: { metrics_count: metricsCount, action_verbs_count: actionVerbsFound },
      formatting_details: { word_count: words, bullet_count: bulletCount, length_status: lengthStatus },
      readability_details: { cliches_found: clichesFound },
      detected_skills: detectedSkills,
      matched_skills: hasJd ? matchedJdSkills : detectedSkills.slice(0, 15),
      missing_skills: hasJd ? missingJdSkills : [],
      job_match_details: jobMatchDetails,
      action_verbs_found: actionVerbsFound,
      quantified_metrics_found: metricsCount,
      suggestions,
      summary
    };
  }

  return {
    analyze
  };
})();
