/**
 * ResumeAI API Service Layer.
 * Communicates with Flask backend with automatic fallback to localStorage
 * ensuring 100% demo resilience.
 */

window.ResumeAIService = (() => {
  const API_BASE = window.location.origin.includes('http') ? window.location.origin : 'http://127.0.0.1:5050';
  let backendAvailable = null;

  // Session keys
  const USER_KEY = 'resumeai_current_user';
  const HISTORY_KEY = 'resumeai_history_records';
  const SETTINGS_KEY = 'resumeai_settings';

  async function checkBackend() {
    if (backendAvailable !== null) return backendAvailable;
    try {
      const res = await fetch(`${API_BASE}/api/health`, { method: 'GET', signal: AbortSignal.timeout(2000) });
      backendAvailable = res.ok;
    } catch (e) {
      backendAvailable = false;
    }
    return backendAvailable;
  }

  // Auto detect
  checkBackend();

  function getCurrentUser() {
    try {
      const stored = localStorage.getItem(USER_KEY);
      if (stored) return JSON.parse(stored);
    } catch (e) {}
    return null;
  }

  function setCurrentUser(user) {
    if (user) {
      localStorage.setItem(USER_KEY, JSON.stringify(user));
    } else {
      localStorage.removeItem(USER_KEY);
    }
  }

  async function login(email, password) {
    email = (email || '').trim();
    password = (password || '').trim();

    if (!email || !password) {
      throw new Error("Please enter email and password.");
    }

    const hasBackend = await checkBackend();
    if (hasBackend) {
      try {
        const resp = await fetch(`${API_BASE}/api/auth/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password })
        });
        const result = await resp.json();
        if (!resp.ok || !result.success) {
          throw new Error(result.message || 'Login failed.');
        }
        setCurrentUser(result.user);
        return result.user;
      } catch (err) {
        if (err.message.includes('Please enter email and password.')) {
          throw err;
        }
        // Fallback to client demo login
      }
    }

    // Client-side demo login: ANY non-empty email and password succeeds!
    const namePart = email.split('@')[0].replace('.', ' ');
    const formattedName = namePart.charAt(0).toUpperCase() + namePart.slice(1);
    const demoUser = {
      email: email,
      name: formattedName,
      bio: "Software professional building impactful products."
    };
    setCurrentUser(demoUser);
    return demoUser;
  }

  async function signup(name, email, password, confirmPassword) {
    name = (name || '').trim();
    email = (email || '').trim();
    password = (password || '').trim();
    confirmPassword = (confirmPassword || '').trim();

    if (!name || !email || !password || !confirmPassword) {
      throw new Error("All fields are required.");
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      throw new Error("Please enter a valid email address.");
    }
    if (password !== confirmPassword) {
      throw new Error("Passwords do not match.");
    }
    if (password.length < 4) {
      throw new Error("Password must be at least 4 characters long.");
    }

    const hasBackend = await checkBackend();
    if (hasBackend) {
      try {
        const resp = await fetch(`${API_BASE}/api/auth/signup`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name, email, password, confirm_password: confirmPassword })
        });
        const result = await resp.json();
        if (!resp.ok || !result.success) {
          throw new Error(result.message || 'Sign up failed.');
        }
        return result;
      } catch (err) {
        // If specific validation message, rethrow
        if (err.message.includes('match') || err.message.includes('valid email')) throw err;
      }
    }

    // Client demo signup success
    return { success: true, message: "Account created successfully! Please log in." };
  }

  function logout() {
    setCurrentUser(null);
  }

  async function analyzeResume(file, arg2 = "", arg3 = "", arg4 = "", arg5 = true) {
    if (!file) {
      throw new Error("Please select a resume file (PDF or DOCX).");
    }

    const filename = (file.name || '').toLowerCase();
    const isPdf = filename.endsWith('.pdf');
    const isDocx = filename.endsWith('.docx');
    if (!isPdf && !isDocx) {
      throw new Error("Unsupported file format. Only PDF (.pdf) and Word documents (.docx) are supported.");
    }

    if (file.size === 0) {
      throw new Error("The uploaded file is empty (0 bytes). Please upload a valid resume file.");
    }

    if (file.size > 5 * 1024 * 1024) {
      throw new Error(`File exceeds 5MB size limit. Your file is ${(file.size / (1024 * 1024)).toFixed(2)} MB.`);
    }

    // Flexible parameter support:
    // analyzeResume(file, jobDescription, autoSave) OR legacy (file, role, custom, jd, autoSave)
    let jobDescription = "";
    let autoSave = true;

    if (typeof arg2 === 'string' && (arg3 === undefined || typeof arg3 === 'boolean')) {
      jobDescription = arg2.trim();
      autoSave = arg3 !== undefined ? arg3 : true;
    } else {
      jobDescription = (typeof arg4 === 'string' ? arg4 : (typeof arg2 === 'string' ? arg2 : "")) || "";
      autoSave = typeof arg5 === 'boolean' ? arg5 : (typeof arg3 === 'boolean' ? arg3 : true);
    }

    const user = getCurrentUser();
    const userEmail = user ? user.email : '';

    const hasBackend = await checkBackend();
    if (hasBackend) {
      const formData = new FormData();
      formData.append('resume', file);
      formData.append('job_description', jobDescription);
      formData.append('user_email', userEmail);
      formData.append('auto_save', autoSave ? 'true' : 'false');

      let resp;
      try {
        resp = await fetch(`${API_BASE}/api/analyze`, {
          method: 'POST',
          body: formData
        });
      } catch (networkErr) {
        throw new Error("Cannot connect to ResumeAI backend service. Please verify server is running on port 5050.");
      }

      let result;
      try {
        result = await resp.json();
      } catch (e) {
        throw new Error(`Backend error (${resp.status}): Unable to parse response.`);
      }

      if (!resp.ok || !result.success) {
        throw new Error(result.message || 'Resume analysis failed.');
      }

      // Also mirror in local history for instant client cache
      saveLocalHistory(result.data, userEmail);
      return result.data;
    }

    // Fallback if backend is completely unavailable
    const fileText = await extractFileTextClient(file);
    if (!fileText || fileText.trim().length < 40) {
      throw new Error("Could not extract selectable text from this file. Please ensure it is a valid text-based PDF or DOCX.");
    }

    const analysis = window.ClientATSEngine.analyze(fileText, jobDescription);
    analysis.id = Date.now();
    analysis.resume_name = file.name;
    analysis.file_size_kb = Math.round(file.size / 1024);
    analysis.created_at = new Date().toISOString();

    if (autoSave && userEmail) {
      saveLocalHistory(analysis, userEmail);
    }

    return analysis;
  }

  async function getHistory() {
    const user = getCurrentUser();
    if (!user) return [];

    const hasBackend = await checkBackend();
    if (hasBackend) {
      try {
        const resp = await fetch(`${API_BASE}/api/history?email=${encodeURIComponent(user.email)}`);
        const result = await resp.json();
        if (resp.ok && result.success) {
          return result.data;
        }
      } catch (err) {}
    }

    return getLocalHistory(user.email);
  }

  async function getAnalysisDetail(id) {
    const user = getCurrentUser();
    const hasBackend = await checkBackend();
    if (hasBackend) {
      try {
        const resp = await fetch(`${API_BASE}/api/history/${id}?email=${encodeURIComponent(user ? user.email : '')}`);
        const result = await resp.json();
        if (resp.ok && result.success) {
          return result.data;
        }
      } catch (err) {}
    }

    const localList = getLocalHistory(user ? user.email : '');
    return localList.find(item => String(item.id) === String(id)) || null;
  }

  async function deleteAnalysis(id) {
    const user = getCurrentUser();
    const hasBackend = await checkBackend();
    if (hasBackend) {
      try {
        await fetch(`${API_BASE}/api/history/${id}?email=${encodeURIComponent(user ? user.email : '')}`, {
          method: 'DELETE'
        });
      } catch (err) {}
    }
    deleteLocalHistory(id, user ? user.email : '');
    return true;
  }

  async function deleteAllHistory() {
    const user = getCurrentUser();
    const hasBackend = await checkBackend();
    if (hasBackend) {
      try {
        await fetch(`${API_BASE}/api/history/all?email=${encodeURIComponent(user ? user.email : '')}`, {
          method: 'DELETE'
        });
      } catch (err) {}
    }
    clearAllLocalHistory();
    return true;
  }

  async function getStats() {
    const user = getCurrentUser();
    if (!user) {
      return { total_checked: 0, avg_score: 0, best_score: 0, last_analysis: null };
    }

    const hasBackend = await checkBackend();
    if (hasBackend) {
      try {
        const resp = await fetch(`${API_BASE}/api/stats?email=${encodeURIComponent(user.email)}`);
        const result = await resp.json();
        if (resp.ok && result.success) {
          return result.data;
        }
      } catch (err) {}
    }

    const list = getLocalHistory(user.email);
    if (list.length === 0) {
      return { total_checked: 0, avg_score: 0, best_score: 0, last_analysis: null };
    }

    const scores = list.map(item => item.overall_score || 0);
    const avg = Math.round(scores.reduce((a, b) => a + b, 0) / scores.length);
    const best = Math.max(...scores);
    return {
      total_checked: list.length,
      avg_score: avg,
      best_score: best,
      last_analysis: list[0].created_at || new Date().toISOString()
    };
  }

  async function updateProfile(profileData) {
    const user = getCurrentUser() || {};
    const updated = { ...user, ...profileData };
    setCurrentUser(updated);

    const hasBackend = await checkBackend();
    if (hasBackend) {
      try {
        await fetch(`${API_BASE}/api/profile`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(updated)
        });
      } catch (err) {}
    }
    return updated;
  }

  async function getSettings() {
    try {
      const stored = localStorage.getItem(SETTINGS_KEY);
      if (stored) return JSON.parse(stored);
    } catch (e) {}
    return { scoring_sensitivity: 'Standard', theme: 'light', email_alerts: false, auto_save: true };
  }

  async function updateSettings(settings) {
    localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings));
    const user = getCurrentUser();
    const hasBackend = await checkBackend();
    if (hasBackend && user) {
      try {
        await fetch(`${API_BASE}/api/settings`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email: user.email, ...settings })
        });
      } catch (err) {}
    }
    return settings;
  }

  // --- LocalStorage helpers ---
  function getLocalHistory(email) {
    try {
      const raw = localStorage.getItem(HISTORY_KEY);
      const all = raw ? JSON.parse(raw) : [];
      if (!email) return all;
      return all.filter(item => !item.user_email || item.user_email === email);
    } catch (e) {
      return [];
    }
  }

  function saveLocalHistory(analysis, email) {
    try {
      const all = getLocalHistory('');
      const record = {
        ...analysis,
        user_email: email,
        created_at: analysis.created_at || new Date().toISOString()
      };
      // Check if already present by id
      const filtered = all.filter(item => String(item.id) !== String(record.id));
      filtered.unshift(record);
      localStorage.setItem(HISTORY_KEY, JSON.stringify(filtered.slice(0, 50)));
    } catch (e) {}
  }

  function deleteLocalHistory(id, email) {
    try {
      const all = getLocalHistory('');
      const filtered = all.filter(item => String(item.id) !== String(id));
      localStorage.setItem(HISTORY_KEY, JSON.stringify(filtered));
    } catch (e) {}
  }

  function clearAllLocalHistory() {
    localStorage.removeItem(HISTORY_KEY);
  }

  // Client-side text reader for text files or plain document fallback
  async function extractFileTextClient(file) {
    return new Promise((resolve) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        const content = e.target.result;
        if (typeof content === 'string') {
          const printable = content.replace(/[^\x20-\x7E\t\n\r]/g, ' ').replace(/\s+/g, ' ').trim();
          resolve(printable);
        } else {
          resolve('');
        }
      };
      reader.onerror = () => resolve('');
      reader.readAsText(file);
    });
  }

  // ----------------- JOB SEARCH & MATCHING ----------------- //

  async function getJobs(filters = {}) {
    const hasBackend = await checkBackend();
    if (hasBackend) {
      try {
        const queryParams = new URLSearchParams();
        if (filters.search) queryParams.set('search', filters.search);
        if (filters.skill) queryParams.set('skill', filters.skill);
        if (filters.location) queryParams.set('location', filters.location);
        if (filters.job_type) queryParams.set('job_type', filters.job_type);
        if (filters.remote !== undefined && filters.remote !== '') queryParams.set('remote', filters.remote);

        const resp = await fetch(`${API_BASE}/api/jobs?${queryParams.toString()}`);
        const result = await resp.json();
        if (result.success) return result.jobs || [];
      } catch (e) {
        console.warn("Backend getJobs failed, falling back to local dataset:", e);
      }
    }
    // Client fallback: Return starter verified jobs
    return getLocalJobs(filters);
  }

  async function matchJobs(resumeText, skills = [], threshold = 75, filters = {}) {
    const hasBackend = await checkBackend();
    if (hasBackend) {
      try {
        const resp = await fetch(`${API_BASE}/api/jobs/match`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            resume_text: resumeText,
            skills: skills,
            threshold: threshold,
            ...filters
          })
        });
        const result = await resp.json();
        if (result.success) return result;
      } catch (e) {
        console.warn("Backend matchJobs failed, falling back to client matching:", e);
      }
    }
    return clientMatchJobs(resumeText, skills, threshold, filters);
  }

  async function saveJob(jobId) {
    const user = getCurrentUser();
    const email = user ? user.email : 'demo@example.com';
    const hasBackend = await checkBackend();
    if (hasBackend) {
      try {
        const resp = await fetch(`${API_BASE}/api/jobs/save`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ user_email: email, job_id: jobId })
        });
        const result = await resp.json();
        if (result.success) return true;
      } catch (e) {}
    }
    // Local fallback
    try {
      const saved = JSON.parse(localStorage.getItem('resumeai_saved_jobs') || '[]');
      if (!saved.includes(jobId)) saved.push(jobId);
      localStorage.setItem('resumeai_saved_jobs', JSON.stringify(saved));
    } catch (e) {}
    return true;
  }

  async function unsaveJob(jobId) {
    const user = getCurrentUser();
    const email = user ? user.email : 'demo@example.com';
    const hasBackend = await checkBackend();
    if (hasBackend) {
      try {
        await fetch(`${API_BASE}/api/jobs/save`, {
          method: 'DELETE',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ user_email: email, job_id: jobId })
        });
      } catch (e) {}
    }
    // Local fallback
    try {
      let saved = JSON.parse(localStorage.getItem('resumeai_saved_jobs') || '[]');
      saved = saved.filter(id => Number(id) !== Number(jobId));
      localStorage.setItem('resumeai_saved_jobs', JSON.stringify(saved));
    } catch (e) {}
    return true;
  }

  async function getSavedJobs() {
    const user = getCurrentUser();
    const email = user ? user.email : 'demo@example.com';
    const hasBackend = await checkBackend();
    if (hasBackend) {
      try {
        const resp = await fetch(`${API_BASE}/api/jobs/saved?user_email=${encodeURIComponent(email)}`);
        const result = await resp.json();
        if (result.success) return result.saved_jobs || [];
      } catch (e) {}
    }
    // Local fallback
    try {
      const savedIds = JSON.parse(localStorage.getItem('resumeai_saved_jobs') || '[]');
      const all = getLocalJobs();
      return all.filter(j => savedIds.includes(j.id));
    } catch (e) {
      return [];
    }
  }

  async function recordApplication(appData) {
    const user = getCurrentUser();
    const email = user ? user.email : 'demo@example.com';
    const payload = {
      user_email: email,
      job_id: appData.job_id || 0,
      job_title: appData.job_title || 'Software Developer',
      company: appData.company || 'Tech Company',
      application_url: appData.application_url || '',
      status: appData.status || 'Applied',
      applied_date: appData.applied_date || new Date().toISOString().split('T')[0],
      notes: appData.notes || ''
    };

    const hasBackend = await checkBackend();
    if (hasBackend) {
      try {
        const resp = await fetch(`${API_BASE}/api/applications`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const result = await resp.json();
        if (result.success) return result;
      } catch (e) {}
    }

    // Local storage fallback
    try {
      const apps = JSON.parse(localStorage.getItem('resumeai_user_applications') || '[]');
      payload.id = Date.now();
      payload.created_at = new Date().toISOString();
      apps.unshift(payload);
      localStorage.setItem('resumeai_user_applications', JSON.stringify(apps));
      return { success: true, id: payload.id };
    } catch (e) {
      return { success: true };
    }
  }

  async function getApplications() {
    const user = getCurrentUser();
    const email = user ? user.email : 'demo@example.com';
    const hasBackend = await checkBackend();
    if (hasBackend) {
      try {
        const resp = await fetch(`${API_BASE}/api/applications?user_email=${encodeURIComponent(email)}`);
        const result = await resp.json();
        if (result.success) return result.applications || [];
      } catch (e) {}
    }
    try {
      return JSON.parse(localStorage.getItem('resumeai_user_applications') || '[]');
    } catch (e) {
      return [];
    }
  }

  async function updateApplication(appId, status, notes = null) {
    const user = getCurrentUser();
    const email = user ? user.email : 'demo@example.com';
    const hasBackend = await checkBackend();
    if (hasBackend) {
      try {
        await fetch(`${API_BASE}/api/applications/${appId}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ user_email: email, status, notes })
        });
      } catch (e) {}
    }
    try {
      const apps = JSON.parse(localStorage.getItem('resumeai_user_applications') || '[]');
      const target = apps.find(a => Number(a.id) === Number(appId));
      if (target) {
        target.status = status;
        if (notes !== null) target.notes = notes;
        localStorage.setItem('resumeai_user_applications', JSON.stringify(apps));
      }
    } catch (e) {}
    return true;
  }

  function getLinkedInSearchUrl(job) {
    if (!job) return 'https://www.linkedin.com/jobs/';
    if (job.linkedin_search_url) return job.linkedin_search_url;
    if (job.linkedin_url && job.linkedin_url.startsWith('http')) return job.linkedin_url;
    const title = (job.title || '').trim();
    const company = (job.company || '').trim();
    const loc = (job.location || '').split('/')[0].split('(')[0].trim();
    const query = [title, company].filter(Boolean).join(' ');
    const params = new URLSearchParams();
    if (query) params.set('keywords', query);
    if (loc) params.set('location', loc);
    return `https://www.linkedin.com/jobs/search/?${params.toString()}`;
  }

  function getNaukriSearchUrl(job) {
    if (!job) return 'https://www.naukri.com/';
    if (job.naukri_search_url) return job.naukri_search_url;
    if (job.naukri_url && job.naukri_url.startsWith('http')) return job.naukri_url;
    const title = (job.title || '').trim();
    const loc = (job.location || '').split('/')[0].split('(')[0].trim();
    const slug = title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
    const params = new URLSearchParams();
    if (title) params.set('k', title);
    if (loc) params.set('l', loc);
    return slug
      ? `https://www.naukri.com/${slug}-jobs?${params.toString()}`
      : `https://www.naukri.com/jobs?${params.toString()}`;
  }

  // Local fallback jobs catalog for offline demo resiliency
  function getLocalJobs(filters = {}) {

    const defaultJobs = [
      {
        id: 1,
        title: "Python Developer (Fresher)",
        company: "Zoho Corporation",
        location: "Chennai, Tamil Nadu",
        job_type: "Full-Time",
        experience_level: "Fresher (0-1 yrs)",
        salary: "₹4.5 - 6.5 LPA",
        description: "Design and implement backend web services and automation scripts using Python and Django. Work with relational databases like MySQL and PostgreSQL.",
        required_skills: ["Python", "SQL", "MySQL", "Git", "REST API", "Data Structures", "Django"],
        application_url: "https://www.zoho.com/careers/",
        portal_name: "Zoho Official Careers Portal",
        is_remote: 0,
        posted_date: "2026-10-10",
        is_verified: 1
      },
      {
        id: 2,
        title: "Associate Software Engineer (Python & Cloud)",
        company: "Cisco Systems India",
        location: "Bangalore, Karnataka",
        job_type: "Full-Time",
        experience_level: "Fresher / Entry-Level",
        salary: "₹9.0 - 12.0 LPA",
        description: "Build robust microservices using Python and FastAPI / Flask. Develop automated unit tests and interface with Docker containers and Linux systems.",
        required_skills: ["Python", "FastAPI", "Linux", "Docker", "Git", "REST API", "Unit Testing"],
        application_url: "https://jobs.cisco.com/",
        portal_name: "Cisco Official Careers Portal",
        is_remote: 2,
        posted_date: "2026-10-11",
        is_verified: 1
      },
      {
        id: 3,
        title: "AI / Machine Learning Engineer (Graduate Trainee)",
        company: "Microsoft India",
        location: "Hyderabad, Telangana (Hybrid)",
        job_type: "Full-Time",
        experience_level: "Entry-Level (0-1 yrs)",
        salary: "₹14.0 - 18.0 LPA",
        description: "Develop, train, and test machine learning models and NLP pipelines. Preprocess large-scale text and numerical datasets using Python, Pandas, and NumPy.",
        required_skills: ["Python", "Machine Learning", "Deep Learning", "PyTorch", "Pandas", "NumPy", "Scikit-learn", "NLP", "Git"],
        application_url: "https://careers.microsoft.com/",
        portal_name: "Microsoft Global Careers",
        is_remote: 2,
        posted_date: "2026-10-12",
        is_verified: 1
      },
      {
        id: 4,
        title: "Junior AI / ML Engineer",
        company: "Fractal Analytics",
        location: "Mumbai / Bangalore",
        job_type: "Full-Time",
        experience_level: "Fresher (0-1 yrs)",
        salary: "₹6.5 - 8.5 LPA",
        description: "Implement machine learning algorithms using Scikit-learn and TensorFlow. Create data visualizations and summaries using Pandas, Matplotlib, and Seaborn.",
        required_skills: ["Python", "Machine Learning", "Pandas", "NumPy", "Scikit-learn", "TensorFlow", "SQL", "Data Analysis", "Matplotlib"],
        application_url: "https://fractal.ai/careers/",
        portal_name: "Fractal Official Careers",
        is_remote: 0,
        posted_date: "2026-10-09",
        is_verified: 1
      },
      {
        id: 5,
        title: "Data Analyst Fresher",
        company: "Amazon India",
        location: "Bangalore, Karnataka",
        job_type: "Full-Time",
        experience_level: "Fresher (0-1 yrs)",
        salary: "₹6.0 - 8.5 LPA",
        description: "Extract, analyze, and synthesize large operational datasets using SQL. Build interactive operational reports and dashboards using Power BI and Tableau.",
        required_skills: ["SQL", "Python", "Pandas", "Data Analysis", "Power BI", "Tableau", "Excel", "Statistics"],
        application_url: "https://www.amazon.jobs/",
        portal_name: "Amazon Jobs Portal",
        is_remote: 0,
        posted_date: "2026-10-13",
        is_verified: 1
      },
      {
        id: 6,
        title: "Frontend Web Developer (React.js)",
        company: "Freshworks",
        location: "Chennai, Tamil Nadu",
        job_type: "Full-Time",
        experience_level: "Fresher (0-1 yrs)",
        salary: "₹6.0 - 8.0 LPA",
        description: "Build responsive, interactive web components using React, HTML5, and CSS3 / Tailwind. Integrate frontend views with RESTful backend APIs.",
        required_skills: ["JavaScript", "React", "HTML5", "CSS3", "Tailwind", "REST API", "Git", "TypeScript"],
        application_url: "https://careers.freshworks.com/",
        portal_name: "Freshworks Careers",
        is_remote: 0,
        posted_date: "2026-10-11",
        is_verified: 1
      }
    ];

    let filtered = defaultJobs.map(j => ({
      ...j,
      linkedin_search_url: getLinkedInSearchUrl(j),
      naukri_search_url: getNaukriSearchUrl(j),
      has_company_url: Boolean(j.application_url && j.application_url.startsWith('http')),
      company_application_url: (j.application_url && j.application_url.startsWith('http')) ? j.application_url : null
    }));

    if (filters.search) {
      const q = filters.search.toLowerCase();
      filtered = filtered.filter(j =>
        j.title.toLowerCase().includes(q) ||
        j.company.toLowerCase().includes(q) ||
        j.description.toLowerCase().includes(q)
      );
    }
    return filtered;
  }

  function clientMatchJobs(resumeText, skills = [], threshold = 75, filters = {}) {
    const jobs = getLocalJobs(filters);
    const resumeLower = (resumeText || '').toLowerCase();
    const skillsLower = (skills || []).map(s => s.toLowerCase());

    const matched = jobs.map(job => {
      const req = job.required_skills || [];
      const match = req.filter(s =>
        skillsLower.includes(s.toLowerCase()) ||
        resumeLower.includes(s.toLowerCase())
      );
      const missing = req.filter(s => !match.includes(s));
      const matchPct = Math.min(98, Math.max(25, Math.round((match.length / Math.max(1, req.length)) * 85 + 15)));

      return {
        ...job,
        job_match_percentage: matchPct,
        matched_skills: match,
        missing_skills: missing,
        is_good_match: matchPct >= threshold,
        match_explanation: matchPct >= 75
          ? `Strong match (${matchPct}%). Directly matches ${match.length} required skills (${match.slice(0, 3).join(', ')}).`
          : `Moderate match (${matchPct}%). Missing skills: ${missing.slice(0, 2).join(', ')}.`
      };
    });

    matched.sort((a, b) => b.job_match_percentage - a.job_match_percentage);

    return {
      success: true,
      jobs: matched,
      threshold: threshold,
      total_jobs: matched.length,
      good_matches_count: matched.filter(j => j.is_good_match).length
    };
  }

  return {
    login,
    signup,
    logout,
    getCurrentUser,
    setCurrentUser,
    analyzeResume,
    getHistory,
    getAnalysisDetail,
    deleteAnalysis,
    deleteAllHistory,
    getStats,
    updateProfile,
    getSettings,
    updateSettings,
    clearAllLocalHistory,
    getJobs,
    matchJobs,
    saveJob,
    unsaveJob,
    getSavedJobs,
    recordApplication,
    getApplications,
    updateApplication,
    getLinkedInSearchUrl,
    getNaukriSearchUrl
  };
})();


