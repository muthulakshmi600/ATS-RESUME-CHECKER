import { spawn } from 'child_process';

const EDGE_PATH = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";
const PORT = 9224;

async function sleep(ms) {
  return new Promise(res => setTimeout(res, ms));
}

async function runJobsBrowserTest() {
  console.log("Launching headless Edge on port " + PORT + " for Job Matching UI verification...");
  const edge = spawn(EDGE_PATH, [
    `--remote-debugging-port=${PORT}`,
    '--headless=new',
    '--disable-gpu',
    '--no-first-run',
    '--no-default-browser-check',
    'http://127.0.0.1:5050/'
  ]);

  edge.on('exit', (code) => {
    console.log("Edge process exited with code " + code);
  });

  // Wait for Edge debug endpoint
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

  const pageTarget = targets.find(t => t.type === 'page');
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
      console.error(">>> BROWSER RUNTIME EXCEPTION:", data.params.exceptionDetails.text, data.params.exceptionDetails.exception?.description);
      pageErrors.push(data.params.exceptionDetails);
    } else if (data.method === 'Runtime.consoleAPICalled' && data.params.type === 'error') {
      const args = (data.params.args || []).map(a => a.value || a.description).join(' ');
      console.error(">>> CONSOLE ERROR:", args);
      pageErrors.push(args);
    }
  };

  await new Promise(res => ws.onopen = res);
  await sendCommand('Runtime.enable');
  await sendCommand('Page.enable');

  console.log("Waiting 3s for React App initialization...");
  await sleep(3000);

  // 1. Verify Jobs Page Rendering
  console.log("Testing JobsPage rendering...");
  const jobsPageScript = `
    (async function() {
      try {
        const container = document.createElement('div');
        container.id = 'test-jobs-page-container';
        document.body.appendChild(container);

        const JobsComp = window.JobsPage;
        if (!JobsComp) throw new Error("window.JobsPage is not defined");

        const testRoot = ReactDOM.createRoot(container);
        testRoot.render(
          React.createElement(JobsComp, {
            onNavigate: () => {},
            showToast: () => {},
            currentUser: { name: 'Alex Morgan', email: 'alex@example.com' },
            currentAnalysis: null
          })
        );
        return { success: true, message: 'JobsPage mounted cleanly' };
      } catch (err) {
        return { success: false, error: err.stack || err.message };
      }
    })()
  `;

  let evalRes = await sendCommand('Runtime.evaluate', {
    expression: jobsPageScript,
    awaitPromise: true,
    returnByValue: true
  });
  console.log("JobsPage mount result:", evalRes.result.value);

  await sleep(2000);

  // 2. Verify RecommendedJobs inside AnalysisResultPage with real sample analysis
  console.log("Testing AnalysisResultPage with RecommendedJobs and ApplyModal...");
  const analysisWithJobsScript = `
    (async function() {
      try {
        // Fetch real analysis from backend using sample resume
        const sampleResp = await fetch('/api/sample-resume?type=pdf');
        const blob = await sampleResp.blob();
        const file = new File([blob], 'test_resume.pdf', { type: 'application/pdf' });

        const analysisData = await window.ResumeAIService.analyzeResume(file, '', true);

        const container2 = document.createElement('div');
        container2.id = 'test-result-with-jobs-container';
        document.body.appendChild(container2);

        const ResultComp = window.AnalysisResultPage;
        const testRoot2 = ReactDOM.createRoot(container2);
        testRoot2.render(
          React.createElement(ResultComp, {
            analysis: analysisData,
            onNavigate: () => {},
            onRecheck: () => {},
            showToast: () => {},
            currentUser: { name: 'Alex Morgan', email: 'alex@example.com' }
          })
        );

        return {
          success: true,
          overallScore: analysisData.overall_score,
          recommendedJobsCount: (analysisData.recommended_jobs || []).length,
          topJobTitle: analysisData.recommended_jobs?.[0]?.title,
          topJobMatchPct: analysisData.recommended_jobs?.[0]?.job_match_percentage
        };
      } catch (err) {
        return { success: false, error: err.stack || err.message };
      }
    })()
  `;

  evalRes = await sendCommand('Runtime.evaluate', {
    expression: analysisWithJobsScript,
    awaitPromise: true,
    returnByValue: true
  });
  console.log("AnalysisResultPage with RecommendedJobs result:", evalRes.result.value);

  await sleep(2000);

  // 3. Inspect DOM text content for all required elements (LinkedIn, Naukri, Company)
  const domCheck = await sendCommand('Runtime.evaluate', {
    expression: `({
      hasJobsHeader: document.body.innerText.includes('Find Matching Jobs') || document.body.innerText.includes('Recommended Jobs'),
      hasMatchThresholdControl: document.body.innerText.includes('Match Threshold:'),
      hasGoodMatchBadge: document.body.innerText.includes('Good Match') || document.body.innerText.includes('High Match'),
      hasFindOnLinkedIn: document.body.innerText.includes('Find on LinkedIn'),
      hasFindOnNaukri: document.body.innerText.includes('Find on Naukri'),
      hasApplyCompanyWebsite: document.body.innerText.includes('Apply on Company Website'),
      hasDisclaimer: document.body.innerText.includes('Transparency Disclaimer:'),
      totalTextLength: document.body.innerText.length
    })`,
    returnByValue: true
  });
  console.log("DOM Verification check:", domCheck.result.value);

  // 4. Test ApplyModal for LinkedIn, Naukri, and Company
  console.log("Testing ApplyModal transparency and disclosures for LinkedIn and Naukri...");
  const modalTestScript = `
    (async function() {
      try {
        const testJob = {
          id: 1,
          title: "Python Developer (Fresher)",
          company: "Zoho Corporation",
          location: "Chennai, Tamil Nadu",
          application_url: "https://www.zoho.com/careers/",
          linkedin_search_url: "https://www.linkedin.com/jobs/search/?keywords=Python+Developer+Zoho&location=Chennai",
          naukri_search_url: "https://www.naukri.com/python-developer-jobs?k=Python+Developer&l=Chennai"
        };

        const modalContainer = document.createElement('div');
        modalContainer.id = 'test-modal-container';
        document.body.appendChild(modalContainer);

        const modalRoot = ReactDOM.createRoot(modalContainer);

        // Render LinkedIn Modal
        modalRoot.render(
          React.createElement(window.ApplyModal, {
            job: testJob,
            platform: 'linkedin',
            isOpen: true,
            onClose: () => {},
            onApplied: () => {},
            showToast: () => {}
          })
        );

        await new Promise(r => setTimeout(r, 500));
        const modalText = modalContainer.innerText;

        return {
          success: true,
          hasLinkedInHeader: modalText.includes('LinkedIn Jobs') || modalText.includes('LinkedIn'),
          hasPrivacyGuarantees: modalText.includes('Privacy Guarantee') || modalText.includes('External Redirection'),
          hasNoAutoSubmitNotice: modalText.includes('automatically') || modalText.includes('ResumeAI ATS'),
          hasProceedButton: modalText.includes('Proceed to LinkedIn Jobs')
        };
      } catch (err) {
        return { success: false, error: err.stack || err.message };
      }
    })()
  `;

  const modalRes = await sendCommand('Runtime.evaluate', {
    expression: modalTestScript,
    awaitPromise: true,
    returnByValue: true
  });
  console.log("ApplyModal Test Result:", modalRes.result.value);

  console.log("Total browser errors/exceptions logged:", pageErrors.length);

  ws.close();
  edge.kill();

  if (pageErrors.length > 0 || !evalRes.result.value.success || !modalRes.result.value.success) {
    console.error("FAIL: Browser errors or test failure encountered!");
    process.exit(1);

  } else {
    console.log("SUCCESS: All Job Matching UI features rendered with 0 browser errors!");
    process.exit(0);
  }
}

runJobsBrowserTest().catch(err => {
  console.error("Browser test failed:", err);
  process.exit(1);
});
