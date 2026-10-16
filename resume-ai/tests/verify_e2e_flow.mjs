import { spawn } from 'child_process';

const EDGE_PATH = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";
const PORT = 9223;

async function sleep(ms) {
  return new Promise(res => setTimeout(res, ms));
}

async function runFullInteractiveFlowTest() {
  console.log("Launching headless Edge on port " + PORT + " for interactive flow test...");
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
      console.error(">>> PAGE JS EXCEPTION:", data.params.exceptionDetails.text, data.params.exceptionDetails.exception?.description);
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

  // Trigger real backend analysis through window.ResumeAIService using real PDF sample from backend!
  console.log("Executing end-to-end API call and UI transition in the browser context...");
  const e2eTestScript = `
    (async function() {
      try {
        // 1. Fetch sample PDF resume from backend
        const sampleResp = await fetch('/api/sample-resume?type=pdf');
        if (!sampleResp.ok) throw new Error('Sample resume fetch failed: ' + sampleResp.status);
        const blob = await sampleResp.blob();
        const file = new File([blob], 'real_test_resume.pdf', { type: 'application/pdf' });

        // 2. Call analyzeResume with JD
        const jd = "Looking for an AI / ML Engineer proficient in Python, PyTorch, Docker, REST APIs, and Machine Learning algorithms.";
        const analysisResult = await window.ResumeAIService.analyzeResume(file, jd, true);

        // 3. Mount AnalysisResultPage using the real result
        const container = document.createElement('div');
        container.id = 'live-e2e-result-view';
        document.getElementById('root').appendChild(container);

        const AnalysisComp = window.AnalysisResultPage;
        const root = ReactDOM.createRoot(container);
        root.render(
          React.createElement(AnalysisComp, {
            analysis: analysisResult,
            onNavigate: () => {},
            onRecheck: () => {},
            showToast: () => {},
            currentUser: { name: 'Live Candidate', email: 'candidate@test.com' }
          })
        );

        return {
          success: true,
          overallScore: analysisResult.overall_score,
          qualityScore: analysisResult.resume_quality_score,
          jobMatchScore: analysisResult.job_match_score,
          skillsCount: (analysisResult.matched_skills || []).length,
          suggestionsCount: (analysisResult.suggestions || []).length
        };
      } catch (err) {
        return { success: false, error: err.stack || err.message };
      }
    })()
  `;

  const evalRes = await sendCommand('Runtime.evaluate', {
    expression: e2eTestScript,
    awaitPromise: true,
    returnByValue: true
  });
  console.log("E2E Live Backend + Frontend Execution Result:", evalRes.result.value);

  await sleep(1500);

  const domCheck = await sendCommand('Runtime.evaluate', {
    expression: `({
      hasDualScoreGauge: document.body.innerText.includes('Resume Quality Score') && document.body.innerText.includes('Job Match Score'),
      hasBreakdown: document.body.innerText.includes('Scoring Factor Breakdown'),
      hasSectionAudit: document.body.innerText.includes('Standard Section Completeness'),
      totalTextLength: document.body.innerText.length
    })`,
    returnByValue: true
  });
  console.log("Live E2E DOM Content Check:", domCheck.result.value);

  console.log("Total errors captured during full live flow:", pageErrors.length);

  ws.close();
  edge.kill();

  if (pageErrors.length > 0 || !evalRes.result.value.success) {
    console.error("FAIL: E2E interactive test failed!");
    process.exit(1);
  } else {
    console.log("SUCCESS: End-to-end interactive flow passed with 0 errors!");
    process.exit(0);
  }
}

runFullInteractiveFlowTest().catch(err => {
  console.error("Test error:", err);
  process.exit(1);
});
