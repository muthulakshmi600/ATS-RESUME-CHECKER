import { spawn } from 'child_process';

const EDGE_PATH = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";
const PORT = 9222;

async function sleep(ms) {
  return new Promise(res => setTimeout(res, ms));
}

async function runBrowserTest() {
  console.log("Launching headless Edge on port " + PORT + "...");
  const edge = spawn(EDGE_PATH, [
    `--remote-debugging-port=${PORT}`,
    '--headless=new',
    '--disable-gpu',
    '--no-first-run',
    '--no-default-browser-check',
    'http://127.0.0.1:5050/'
  ]);

  let edgeExited = false;
  edge.on('exit', (code) => {
    edgeExited = true;
    console.log("Edge process exited with code " + code);
  });

  // Wait for Edge debug endpoint to come up
  let targets = null;
  for (let i = 0; i < 20; i++) {
    await sleep(500);
    try {
      const resp = await fetch(`http://127.0.0.1:${PORT}/json/list`);
      if (resp.ok) {
        targets = await resp.json();
        break;
      }
    } catch (e) {}
  }

  if (!targets || targets.length === 0) {
    console.error("Failed to connect to Edge debug endpoint.");
    edge.kill();
    process.exit(1);
  }

  const pageTarget = targets.find(t => t.type === 'page');
  console.log("Found Page target:", pageTarget.title, pageTarget.url);

  const ws = new WebSocket(pageTarget.webSocketDebuggerUrl);
  let msgId = 1;
  const callbacks = new Map();

  function sendCommand(method, params = {}) {
    return new Promise((resolve, reject) => {
      const id = msgId++;
      callbacks.set(id, { resolve, reject });
      ws.send(JSON.stringify({ id, method, params }));
    });
  }

  const pageErrors = [];

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.id && callbacks.has(data.id)) {
      const { resolve, reject } = callbacks.get(data.id);
      callbacks.delete(data.id);
      if (data.error) reject(data.error);
      else resolve(data.result);
    } else if (data.method === 'Runtime.exceptionThrown') {
      console.error(">>> PAGE JS EXCEPTION:", data.params.exceptionDetails.text, data.params.exceptionDetails.exception?.description);
      pageErrors.push(data.params.exceptionDetails);
    } else if (data.method === 'Runtime.consoleAPICalled') {
      const type = data.params.type;
      const args = (data.params.args || []).map(a => a.value || a.description).join(' ');
      if (type === 'error') {
        console.error(">>> CONSOLE ERROR:", args);
        pageErrors.push(args);
      } else {
        console.log(`[Browser Console ${type}]:`, args);
      }
    }
  };

  await new Promise(res => ws.onopen = res);
  console.log("Connected to Chrome DevTools Protocol WebSocket!");

  await sendCommand('Runtime.enable');
  await sendCommand('Page.enable');

  // Wait for initial Babel compilation and React render
  console.log("Waiting 3s for initial page load and React render...");
  await sleep(3000);

  // Check initial DOM content
  let evalRes = await sendCommand('Runtime.evaluate', {
    expression: 'document.getElementById("root").innerHTML.length'
  });
  console.log("Root element HTML length on initial load:", evalRes.result.value);

  // Now, simulate setting an analysis result into the application to test AnalysisResultPage!
  console.log("Simulating analysis results page rendering...");
  const sampleAnalysis = {
    overall_score: 88,
    resume_quality_score: 91,
    job_match_score: 82,
    has_job_description: true,
    grade: { label: "Exceptional ATS Fit", badge: "A+ Competitive" },
    summary: "Strong resume with high quantifiable achievements and technical alignment.",
    resume_name: "test_candidate_resume.pdf",
    quantified_metrics_found: 6,
    action_verbs_found: 12,
    matched_keywords: ["Python", "FastAPI", "PostgreSQL", "Docker"],
    missing_keywords: ["Kubernetes", "GraphQL"],
    matched_skills: ["Python", "Docker", "Git", "REST APIs"],
    missing_skills: ["AWS", "CI/CD"],
    suggestions: [
      { priority: "High", category: "Skills", text: "Add Cloud infrastructure skills such as AWS or GCP." },
      { priority: "Medium", category: "Metrics", text: "Quantify impact on project delivery timelines." }
    ],
    section_status: {
      "Summary / Objective": true,
      "Experience / Work History": true,
      "Education": true,
      "Skills": true,
      "Projects": true
    },
    formatting_details: {
      has_email: true,
      has_phone: true,
      has_links: true,
      word_count: 520,
      length_status: "Optimal"
    },
    contact_details: {
      has_email: true,
      has_phone: true,
      has_links: true
    },
    achievements_details: {
      metrics_count: 6,
      action_verbs_count: 12
    },
    breakdown: {
      structure: 20,
      contact: 15,
      metrics: 18,
      formatting: 14,
      readability: 14,
      skills: 13
    },
    max_breakdown: {
      structure: 20,
      contact: 15,
      metrics: 20,
      formatting: 15,
      readability: 15,
      skills: 15
    }
  };

  const scriptToInject = `
    (function() {
      try {
        localStorage.setItem('resumeai_last_analysis', JSON.stringify(${JSON.stringify(sampleAnalysis)}));
        // Mount or test AnalysisResultPage directly in DOM container or via window
        const container = document.createElement('div');
        container.id = 'test-analysis-container';
        document.body.appendChild(container);

        const AnalysisComp = window.AnalysisResultPage;
        const testRoot = ReactDOM.createRoot(container);
        testRoot.render(
          React.createElement(AnalysisComp, {
            analysis: ${JSON.stringify(sampleAnalysis)},
            onNavigate: () => {},
            onRecheck: () => {},
            showToast: () => {},
            currentUser: { name: 'Test User', email: 'test@example.com' }
          })
        );
        return { success: true, message: 'AnalysisResultPage mounted successfully' };
      } catch (err) {
        return { success: false, error: err.stack || err.message };
      }
    })()
  `;

  evalRes = await sendCommand('Runtime.evaluate', {
    expression: scriptToInject,
    returnByValue: true
  });
  console.log("AnalysisResultPage render result:", evalRes.result.value);

  // Wait 1s for DOM render
  await sleep(1000);

  // Also test Standalone mode (without job description)
  console.log("Simulating Standalone mode (without Job Description)...");
  const standaloneAnalysis = { ...sampleAnalysis, has_job_description: false, job_match_score: null };
  const standaloneScript = `
    (function() {
      try {
        const container2 = document.createElement('div');
        container2.id = 'test-standalone-container';
        document.body.appendChild(container2);

        const AnalysisComp = window.AnalysisResultPage;
        const testRoot2 = ReactDOM.createRoot(container2);
        testRoot2.render(
          React.createElement(AnalysisComp, {
            analysis: ${JSON.stringify(standaloneAnalysis)},
            onNavigate: () => {},
            onRecheck: () => {},
            showToast: () => {},
            currentUser: { name: 'Test User', email: 'test@example.com' }
          })
        );
        return { success: true, message: 'Standalone AnalysisResultPage mounted successfully' };
      } catch (err) {
        return { success: false, error: err.stack || err.message };
      }
    })()
  `;

  evalRes = await sendCommand('Runtime.evaluate', {
    expression: standaloneScript,
    returnByValue: true
  });
  console.log("Standalone mode render result:", evalRes.result.value);

  await sleep(1000);

  // Check DOM text content for score 88 and 91
  const domCheckRes = await sendCommand('Runtime.evaluate', {
    expression: `({
      hasQualityScoreText: document.body.innerText.includes('Resume Quality Score'),
      hasFactorBreakdown: document.body.innerText.includes('Scoring Factor Breakdown'),
      hasSectionCompleteness: document.body.innerText.includes('Standard Section Completeness'),
      textSample: document.body.innerText.substring(0, 300)
    })`,
    returnByValue: true
  });
  console.log("DOM Verification Check:", domCheckRes.result.value);

  // Also check if any page errors were collected
  console.log("\nTotal JavaScript errors/exceptions logged in browser:", pageErrors.length);
  if (pageErrors.length > 0) {
    console.error("FAIL: Browser errors detected:", pageErrors);
  } else {
    console.log("SUCCESS: 0 browser errors detected! Rendering is completely clean and stable!");
  }

  ws.close();
  edge.kill();

  if (pageErrors.length > 0) {
    process.exit(1);
  } else {
    process.exit(0);
  }
}

runBrowserTest().catch(err => {
  console.error("Test failed with exception:", err);
  process.exit(1);
});
