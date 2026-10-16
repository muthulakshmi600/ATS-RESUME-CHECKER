/**
 * NexusAI - Modern Intelligent Assistant Client Application
 * Handles authentication, streaming chat, file uploads, library, projects,
 * settings, speech-to-text, and keyboard shortcuts.
 */

// Application State
const state = {
  currentUser: null,
  activeChatId: null,
  activeProjectId: null,
  activePersona: 'all',
  currentView: 'chat', // 'chat', 'library', 'projects', 'settings'
  chats: [],
  pinnedChats: [],
  historyChats: [],
  projects: [],
  libraryFiles: [],
  pendingAttachments: [], // [{ id, name, size, type, preview }]
  isStreaming: false,
  abortController: null,
  speechRecognition: null,
  isRecordingVoice: false,
  libraryCategory: 'all',
  activeColor: '#6366f1',
  activeAvatar: 'avatar-1'
};

// =====================================================================
// Initialization
// =====================================================================
document.addEventListener('DOMContentLoaded', async () => {
  setupMarkdownRenderer();
  setupKeyboardShortcuts();
  setupSpeechRecognition();
  await checkAuthStatus();
});

function setupMarkdownRenderer() {
  if (window.marked) {
    marked.setOptions({
      breaks: true,
      gfm: true,
      highlight: function (code, lang) {
        if (window.hljs) {
          const language = hljs.getLanguage(lang) ? lang : 'plaintext';
          return hljs.highlight(code, { language }).value;
        }
        return code;
      }
    });
  }
}

function setupKeyboardShortcuts() {
  document.addEventListener('keydown', (e) => {
    // Ctrl + K or Cmd + K: Global Search
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
      e.preventDefault();
      openSearchModal();
    }
    // Ctrl + N or Cmd + N: New Chat (when logged in)
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'n' && state.currentUser) {
      e.preventDefault();
      createNewChat();
    }
    // Escape: Close any open modal
    if (e.key === 'Escape') {
      closeAllModals();
    }
  });
}

// =====================================================================
// Authentication Logic
// =====================================================================

async function checkAuthStatus() {
  try {
    const res = await fetch('/api/auth/status');
    const data = await res.json();
    if (data.authenticated && data.user) {
      state.currentUser = data.user;
      renderAuthenticatedApp();
    } else {
      const path = window.location.pathname;
      if (path === '/signup') {
        showAuthScreen('signup');
      } else {
        showAuthScreen('login');
      }
    }
  } catch (err) {
    console.error('Auth status check error:', err);
    showAuthScreen('login');
  }
}

function showAuthScreen(mode = 'login') {
  document.getElementById('auth-container').classList.remove('hidden');
  document.getElementById('app-container').classList.add('hidden');
  switchAuthMode(mode);
}

function switchAuthMode(mode) {
  const isSignup = mode === 'signup';
  document.getElementById('login-form').classList.toggle('hidden', isSignup);
  document.getElementById('signup-form').classList.toggle('hidden', !isSignup);
  document.getElementById('auth-title').innerText = isSignup ? 'Create NexusAI Account' : 'Welcome to NexusAI';
  document.getElementById('auth-subtitle').innerText = isSignup
    ? 'Start exploring intelligent coding and file analysis'
    : 'Sign in to access your intelligent workspace';
  clearAuthAlert();
}

function showAuthAlert(message, isSuccess = false) {
  const box = document.getElementById('auth-alert');
  box.className = `alert-box ${isSuccess ? 'alert-success' : 'alert-danger'}`;
  box.innerText = message;
  box.classList.remove('hidden');
}

function clearAuthAlert() {
  const box = document.getElementById('auth-alert');
  box.classList.add('hidden');
  box.innerText = '';
}

async function handleLogin(e) {
  e.preventDefault();
  clearAuthAlert();

  const email = document.getElementById('login-email').value.trim();
  const password = document.getElementById('login-password').value;
  const remember_me = document.getElementById('login-remember').checked;
  const btn = document.getElementById('login-btn');

  if (!email || !password) {
    showAuthAlert('Please enter both email and password.');
    return;
  }

  btn.disabled = true;
  btn.querySelector('.btn-text').innerText = 'Signing In...';

  try {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, remember_me })
    });
    const data = await res.json();

    if (!res.ok) {
      showAuthAlert(data.error || 'Invalid email or password.');
      return;
    }

    state.currentUser = data.user;
    showToast(data.message || 'Signed in successfully!', 'success');
    renderAuthenticatedApp();
    if (window.location.pathname !== '/dashboard') {
      window.history.pushState({}, '', '/dashboard');
    }
  } catch (err) {
    showAuthAlert('Network error occurred. Please try again.');
  } finally {
    btn.disabled = false;
    btn.querySelector('.btn-text').innerText = 'Sign In';
  }
}

async function handleSignup(e) {
  e.preventDefault();
  clearAuthAlert();

  const name = document.getElementById('signup-name').value.trim();
  const email = document.getElementById('signup-email').value.trim();
  const password = document.getElementById('signup-password').value;
  const confirm_password = document.getElementById('signup-confirm-password').value;
  const btn = document.getElementById('signup-btn');

  if (!name || !email || !password || !confirm_password) {
    showAuthAlert('Please fill in all fields.');
    return;
  }

  if (password.length < 4) {
    showAuthAlert('Password must be at least 4 characters long.');
    return;
  }

  if (password !== confirm_password) {
    showAuthAlert('Passwords do not match. Please verify.');
    return;
  }

  btn.disabled = true;
  btn.querySelector('.btn-text').innerText = 'Creating Account...';

  try {
    const res = await fetch('/api/auth/signup', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, password, confirm_password })
    });
    const data = await res.json();

    if (!res.ok) {
      showAuthAlert(data.error || 'Registration failed.');
      return;
    }

    // Success -> switch to login page and display message
    switchAuthMode('login');
    showAuthAlert(data.message || 'Account created successfully! Please sign in.', true);
    document.getElementById('login-email').value = email;
    document.getElementById('login-password').value = '';
    document.getElementById('login-password').focus();
    showToast('Registration complete! Please sign in.', 'success');
  } catch (err) {
    showAuthAlert('Network error occurred during sign up.');
  } finally {
    btn.disabled = false;
    btn.querySelector('.btn-text').innerText = 'Create Account';
  }
}

async function handleLogout() {
  try {
    await fetch('/api/auth/logout', { method: 'POST' });
    state.currentUser = null;
    state.activeChatId = null;
    state.chats = [];
    showToast('Logged out successfully.', 'info');
    window.location.href = '/login';
  } catch (err) {
    showToast('Error during logout.', 'error');
    window.location.href = '/login';
  }
}

function showForgotPasswordModal() {
  openModal('forgot-pw-modal');
  document.getElementById('forgot-email').value = document.getElementById('login-email').value || '';
  document.getElementById('forgot-new-pw').value = '';
}

async function handleForgotPasswordSubmit() {
  const email = document.getElementById('forgot-email').value.trim();
  const new_password = document.getElementById('forgot-new-pw').value;

  if (!email || !new_password) {
    showToast('Please provide both email and a new password.', 'error');
    return;
  }

  if (new_password.length < 4) {
    showToast('New password must be at least 4 characters long.', 'error');
    return;
  }

  try {
    const res = await fetch('/api/auth/forgot-password', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, new_password })
    });
    const data = await res.json();

    if (!res.ok) {
      showToast(data.error || 'Failed to reset password.', 'error');
      return;
    }

    closeModal('forgot-pw-modal');
    showToast(data.message, 'success');
    switchAuthMode('login');
    showAuthAlert(data.message, true);
    document.getElementById('login-email').value = email;
    document.getElementById('login-password').value = '';
  } catch (err) {
    showToast('Network error during password reset.', 'error');
  }
}

// Password Visibility Toggle
function togglePasswordVisibility(inputId, btn) {
  const input = document.getElementById(inputId);
  const icon = btn.querySelector('i');
  if (input.type === 'password') {
    input.type = 'text';
    icon.className = 'fa-regular fa-eye-slash';
  } else {
    input.type = 'password';
    icon.className = 'fa-regular fa-eye';
  }
}

// Real-time Password Strength Meter
function evaluatePasswordStrength(password, meterId, textId) {
  const meter = document.getElementById(meterId);
  const label = document.getElementById(textId);
  if (!meter || !label) return;

  if (!password || password.length === 0) {
    meter.style.width = '0%';
    meter.style.background = 'transparent';
    label.innerText = 'Strength: Empty';
    label.style.color = 'var(--text-muted)';
    return;
  }

  let score = 0;
  if (password.length >= 4) score += 1;
  if (password.length >= 8) score += 1;
  if (/[a-z]/.test(password) || /[A-Z]/.test(password)) score += 1;
  if (/\d/.test(password)) score += 1;
  if (/[^A-Za-z0-9]/.test(password)) score += 1;

  if (score <= 2) {
    meter.style.width = '33%';
    meter.style.background = 'var(--danger)';
    label.innerText = 'Strength: Fair';
    label.style.color = 'var(--danger)';
  } else if (score <= 3) {
    meter.style.width = '66%';
    meter.style.background = 'var(--warning)';
    label.innerText = 'Strength: Good';
    label.style.color = 'var(--warning)';
  } else {
    meter.style.width = '100%';
    meter.style.background = 'var(--success)';
    label.innerText = 'Strength: Strong';
    label.style.color = 'var(--success)';
  }
}

// =====================================================================
// Authenticated App Shell & View Navigation
// =====================================================================

function renderAuthenticatedApp() {
  document.getElementById('auth-container').classList.add('hidden');
  document.getElementById('app-container').classList.remove('hidden');

  // Populate User Info in Sidebar
  const u = state.currentUser;
  const initials = u.name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
  const avatarEl = document.getElementById('user-avatar-display');
  avatarEl.innerText = initials;
  document.getElementById('user-name-display').innerText = u.name;
  document.getElementById('user-email-display').innerText = u.email;

  // Populate Settings fields
  document.getElementById('settings-name').value = u.name;
  document.getElementById('settings-email').value = u.email;
  if (u.settings) {
    document.getElementById('settings-gemini-key').value = u.settings.gemini_api_key || '';
    document.getElementById('settings-model').value = u.settings.ai_model || 'gemini-3.8-flash';
    document.getElementById('settings-temperature').value = u.settings.temperature || 0.7;
    document.getElementById('temp-val').innerText = u.settings.temperature || 0.7;
    document.getElementById('settings-system-instruction').value = u.settings.system_instruction || '';
  }

  // Load Chats, Projects, and Library Counts
  loadChats();
  loadProjects();
  fetchLibraryFiles();

  // Open default New Chat view
  switchView('chat');
  if (!state.activeChatId) {
    showHeroWelcome();
  }
}

function switchView(viewName) {
  state.currentView = viewName;

  // Update Nav highlighting
  document.querySelectorAll('.sidebar-nav .nav-item').forEach(el => el.classList.remove('active'));
  const activeNav = document.getElementById(`nav-${viewName}`);
  if (activeNav) activeNav.classList.add('active');

  // Switch View Panes
  document.querySelectorAll('.app-view').forEach(el => el.classList.add('hidden'));
  const target = document.getElementById(`view-${viewName}`);
  if (target) {
    target.classList.remove('hidden');
    target.classList.add('active-view');
  }

  if (viewName === 'library') {
    fetchLibraryFiles();
  } else if (viewName === 'projects') {
    loadProjects();
  }
}

function toggleSidebar() {
  const sidebar = document.getElementById('app-sidebar');
  sidebar.classList.toggle('open');
}

// =====================================================================
// Chat & Conversation Management
// =====================================================================

async function loadChats() {
  try {
    const res = await fetch('/api/chats');
    const data = await res.json();
    state.chats = data.all || [];
    state.pinnedChats = data.pinned || [];
    state.historyChats = data.history || [];
    renderSidebarChats();
  } catch (err) {
    console.error('Error loading chats:', err);
  }
}

function renderSidebarChats() {
  const pinnedContainer = document.getElementById('pinned-chats-list');
  const historyContainer = document.getElementById('history-chats-list');
  const pinnedSection = document.getElementById('pinned-section');

  // Pinned Chats
  pinnedContainer.innerHTML = '';
  if (state.pinnedChats.length === 0) {
    pinnedSection.classList.add('hidden');
  } else {
    pinnedSection.classList.remove('hidden');
    const pinnedTitleSpan = pinnedSection.querySelector('.section-title span');
    if (pinnedTitleSpan) {
      pinnedTitleSpan.innerHTML = `<i class="fa-solid fa-thumbtack text-warning"></i> Pinned Chats <span style="background:rgba(234,179,8,0.22);color:#facc15;padding:1px 7px;border-radius:10px;font-size:10px;margin-left:6px;font-weight:700;">${state.pinnedChats.length}</span>`;
    }
    state.pinnedChats.forEach(chat => {
      pinnedContainer.appendChild(createChatSidebarItem(chat, true));
    });
  }

  // History Chats
  historyContainer.innerHTML = '';
  if (state.historyChats.length === 0) {
    historyContainer.innerHTML = '<div style="padding:10px 8px; font-size:12px; color:var(--text-muted);">No saved chats yet.</div>';
  } else {
    state.historyChats.forEach(chat => {
      historyContainer.appendChild(createChatSidebarItem(chat, false));
    });
  }
}

function createChatSidebarItem(chat, isPinned) {
  const div = document.createElement('div');
  div.className = `chat-item ${isPinned ? 'is-pinned-item' : ''} ${state.activeChatId === chat.id ? 'active' : ''}`;
  div.id = `sidebar-chat-${chat.id}`;
  div.onclick = (e) => {
    // Avoid triggering if action button clicked
    if (e.target.closest('.chat-item-actions')) return;
    openChat(chat.id);
  };

  div.innerHTML = `
    <span class="chat-item-title" title="${escapeHtml(chat.title)}">
      ${isPinned ? '<i class="fa-solid fa-thumbtack text-warning" style="font-size:10px; margin-right:4px;"></i>' : ''}
      ${escapeHtml(chat.title)}
    </span>
    <div class="chat-item-actions">
      <button title="${isPinned ? 'Unpin' : 'Pin'}" onclick="togglePinChat('${chat.id}', ${!isPinned})">
        <i class="fa-${isPinned ? 'solid' : 'regular'} fa-thumbtack"></i>
      </button>
      <button title="Rename" onclick="promptRenameChat('${chat.id}', '${escapeHtml(chat.title)}')">
        <i class="fa-solid fa-pen"></i>
      </button>
      <button title="Delete" onclick="deleteChatById('${chat.id}')">
        <i class="fa-regular fa-trash-can text-danger"></i>
      </button>
    </div>
  `;
  return div;
}

async function createNewChat(projectId = null) {
  try {
    const res = await fetch('/api/chats', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title: 'New Conversation', project_id: projectId })
    });
    const chat = await res.json();
    state.activeChatId = chat.id;
    await loadChats();
    openChat(chat.id);
    switchView('chat');
  } catch (err) {
    showToast('Failed to create new chat.', 'error');
  }
}

async function openChat(chatId) {
  state.activeChatId = chatId;
  switchView('chat');

  // Highlight active item in sidebar
  document.querySelectorAll('.chat-item').forEach(el => el.classList.remove('active'));
  const activeEl = document.getElementById(`sidebar-chat-${chatId}`);
  if (activeEl) activeEl.classList.add('active');

  // Fetch full chat messages
  try {
    const res = await fetch(`/api/chats/${chatId}`);
    if (!res.ok) throw new Error('Chat not found');
    const chat = await res.json();

    // Update Header
    document.getElementById('current-chat-title').innerText = chat.title;
    updatePinHeaderButton(chat.is_pinned);

    const projBadge = document.getElementById('current-chat-project-badge');
    if (chat.project) {
      projBadge.innerText = chat.project.name;
      projBadge.style.borderColor = chat.project.color;
      projBadge.style.color = chat.project.color;
      projBadge.classList.remove('hidden');
    } else {
      projBadge.classList.add('hidden');
    }

    // Render Messages
    const container = document.getElementById('messages-list');
    container.innerHTML = '';

    if (chat.messages.length === 0) {
      showHeroWelcome();
    } else {
      hideHeroWelcome();
      chat.messages.forEach(msg => {
        container.appendChild(renderMessageBubble(msg));
      });
      scrollToBottom();
    }
  } catch (err) {
    showToast('Failed to open chat.', 'error');
  }
}

function updatePinHeaderButton(isPinned) {
  const pinBtn = document.getElementById('btn-pin-active-chat');
  if (!pinBtn) return;
  if (isPinned) {
    pinBtn.classList.add('is-pinned');
    pinBtn.innerHTML = `<i class="fa-solid fa-thumbtack"></i> <span id="pin-btn-text">Pinned</span>`;
    pinBtn.title = 'Unpin this conversation';
  } else {
    pinBtn.classList.remove('is-pinned');
    pinBtn.innerHTML = `<i class="fa-regular fa-thumbtack"></i> <span id="pin-btn-text">Pin Chat</span>`;
    pinBtn.title = 'Pin this conversation to top of sidebar';
  }
}

function showHeroWelcome() {
  document.getElementById('hero-welcome-screen').classList.remove('hidden');
  document.getElementById('messages-list').innerHTML = '';
  document.getElementById('current-chat-title').innerText = 'New Conversation';
  updatePinHeaderButton(false);
}

function hideHeroWelcome() {
  document.getElementById('hero-welcome-screen').classList.add('hidden');
}

async function togglePinChat(chatId, newPinStatus) {
  try {
    const res = await fetch(`/api/chats/${chatId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ is_pinned: newPinStatus ? 1 : 0 })
    });
    if (res.ok) {
      showToast(newPinStatus ? 'Conversation pinned to top! 📌' : 'Conversation unpinned.', 'success');
      await loadChats();
      if (state.activeChatId === chatId) {
        updatePinHeaderButton(newPinStatus);
      }
    }
  } catch (err) {
    showToast('Failed to update pin state.', 'error');
  }
}

function togglePinCurrentChat() {
  if (!state.activeChatId) return;
  const currentChat = state.chats.find(c => c.id === state.activeChatId);
  const isPinned = currentChat ? currentChat.is_pinned : false;
  togglePinChat(state.activeChatId, !isPinned);
}

function promptRenameChat(chatId = null, currentTitle = '') {
  const targetId = chatId || state.activeChatId;
  if (!targetId) return;

  const title = currentTitle || document.getElementById('current-chat-title').innerText;
  openModal('rename-modal');
  document.getElementById('rename-modal-title').innerHTML = '<i class="fa-solid fa-pen text-primary"></i> Rename Conversation';
  document.getElementById('rename-input-label').innerText = 'Conversation Title';
  const input = document.getElementById('rename-input');
  input.value = title;
  input.focus();

  document.getElementById('btn-save-rename').onclick = async () => {
    const newTitle = input.value.trim();
    if (!newTitle) return;

    try {
      const res = await fetch(`/api/chats/${targetId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: newTitle })
      });
      if (res.ok) {
        closeModal('rename-modal');
        showToast('Conversation renamed.', 'success');
        await loadChats();
        if (state.activeChatId === targetId) {
          document.getElementById('current-chat-title').innerText = newTitle;
        }
      }
    } catch (err) {
      showToast('Failed to rename conversation.', 'error');
    }
  };
}

async function deleteChatById(chatId) {
  if (!confirm('Are you sure you want to permanently delete this conversation?')) return;

  try {
    const res = await fetch(`/api/chats/${chatId}`, { method: 'DELETE' });
    if (res.ok) {
      showToast('Conversation deleted.', 'info');
      await loadChats();
      if (state.activeChatId === chatId) {
        if (state.chats.length > 0) {
          openChat(state.chats[0].id);
        } else {
          state.activeChatId = null;
          showHeroWelcome();
        }
      }
    }
  } catch (err) {
    showToast('Failed to delete conversation.', 'error');
  }
}

function deleteCurrentChat() {
  if (state.activeChatId) {
    deleteChatById(state.activeChatId);
  }
}

// =====================================================================
// Sending Messages & Streaming AI Responses (SSE)
// =====================================================================

function usePromptSuggestion(promptText) {
  hideHeroWelcome();
  const input = document.getElementById('chat-input');
  input.value = promptText;
  autoResizeInput(input);
  sendActiveMessage();
}

function handleInputKeydown(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendActiveMessage();
  }
}

function autoResizeInput(el) {
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 180) + 'px';
}

async function sendActiveMessage() {
  const input = document.getElementById('chat-input');
  const content = input.value.trim();
  const attachments = [...state.pendingAttachments];

  if (!content && attachments.length === 0) return;
  if (state.isStreaming) return;

  // If no chat is active, create one first
  if (!state.activeChatId) {
    await createNewChat();
  }

  hideHeroWelcome();

  // Reset input and attachments
  input.value = '';
  input.style.height = 'auto';
  handleInputStats(input);
  state.pendingAttachments = [];
  renderAttachmentChips();

  // Append user message bubble immediately to DOM
  const userMsgObj = {
    id: 'temp_' + Date.now(),
    role: 'user',
    content: content,
    attachments: attachments,
    created_at: new Date().toISOString()
  };
  const list = document.getElementById('messages-list');
  list.appendChild(renderMessageBubble(userMsgObj));
  scrollToBottom();

  // Show Typing Indicator
  showTypingIndicator();

  // Set streaming state
  state.isStreaming = true;
  document.getElementById('btn-send').disabled = true;
  document.getElementById('btn-stop-generate').classList.remove('hidden');

  state.abortController = new AbortController();

  // Prepare Assistant Placeholder Bubble
  let assistantBubble = null;
  let assistantTextBuffer = '';

  try {
    const response = await fetch(`/api/chats/${state.activeChatId}/message`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content, attachments, persona: state.activePersona || 'all' }),
      signal: state.abortController.signal
    });

    if (!response.ok) {
      throw new Error(`Server returned status: ${response.status}`);
    }

    hideTypingIndicator();

    // Create assistant message element in DOM
    const assistantMsgObj = {
      id: 'ai_' + Date.now(),
      role: 'assistant',
      content: '',
      created_at: new Date().toISOString()
    };
    assistantBubble = renderMessageBubble(assistantMsgObj);
    list.appendChild(assistantBubble);
    const bubbleContentEl = assistantBubble.querySelector('.msg-content-body');

    // Consume Server-Sent Events (SSE) Stream
    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n\n');
      buffer = lines.pop(); // Keep partial line in buffer

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.substring(6));
            if (data.chunk) {
              assistantTextBuffer += data.chunk;
              bubbleContentEl.innerHTML = parseMarkdownSafely(assistantTextBuffer);
              highlightCodeBlocks(bubbleContentEl);
              scrollToBottom();
            }
            if (data.done) {
              if (data.chat_title) {
                document.getElementById('current-chat-title').innerText = data.chat_title;
                loadChats(); // refresh sidebar title
              }
            }
          } catch (pe) {
            console.error('Error parsing SSE data:', pe);
          }
        }
      }
    }
  } catch (err) {
    hideTypingIndicator();
    if (err.name === 'AbortError') {
      showToast('Generation stopped by user.', 'info');
    } else {
      showToast('Error streaming AI response. Fallback error handled.', 'error');
      if (assistantBubble) {
        const bubbleContentEl = assistantBubble.querySelector('.msg-content-body');
        bubbleContentEl.innerHTML += `<p class="text-danger"><i class="fa-solid fa-triangle-exclamation"></i> Communication error. Please check your network or Gemini API Key.</p>`;
      }
    }
  } finally {
    state.isStreaming = false;
    document.getElementById('btn-send').disabled = false;
    document.getElementById('btn-stop-generate').classList.add('hidden');
    scrollToBottom();
  }
}

function stopGenerating() {
  if (state.abortController) {
    state.abortController.abort();
    state.isStreaming = false;
    hideTypingIndicator();
    document.getElementById('btn-stop-generate').classList.add('hidden');
    document.getElementById('btn-send').disabled = false;
  }
}

async function regenerateResponse() {
  if (!state.activeChatId || state.isStreaming) return;

  try {
    const res = await fetch(`/api/chats/${state.activeChatId}/regenerate`, { method: 'POST' });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error);

    // Replay prompt
    const input = document.getElementById('chat-input');
    input.value = data.prompt;
    state.pendingAttachments = data.attachments || [];
    renderAttachmentChips();

    // Reload chat and send
    await openChat(state.activeChatId);
    sendActiveMessage();
  } catch (err) {
    showToast('Failed to regenerate response.', 'error');
  }
}

async function deleteMessage(messageId, msgRowEl) {
  if (!confirm('Delete this message?')) return;

  try {
    const res = await fetch(`/api/chats/${state.activeChatId}/messages/${messageId}`, { method: 'DELETE' });
    if (res.ok) {
      msgRowEl.remove();
      showToast('Message deleted.', 'info');
      // If list is empty, show hero
      if (document.getElementById('messages-list').children.length === 0) {
        showHeroWelcome();
      }
    }
  } catch (err) {
    showToast('Failed to delete message.', 'error');
  }
}

// Render message DOM element
function renderMessageBubble(msg) {
  const isAi = msg.role === 'assistant';
  const row = document.createElement('div');
  row.className = `message-row ${isAi ? 'message-ai' : 'message-user'}`;
  row.id = `msg-${msg.id}`;

  const timeStr = msg.created_at ? formatTimestamp(msg.created_at) : '';

  // Attachments HTML
  let attachmentsHtml = '';
  if (msg.attachments && msg.attachments.length > 0) {
    attachmentsHtml = `<div class="msg-attachments-row">` + msg.attachments.map(att => `
      <div class="file-chip">
        <i class="fa-solid fa-file file-chip-icon"></i>
        <span class="file-chip-name">${escapeHtml(att.name || att.original_filename || 'Attachment')}</span>
      </div>
    `).join('') + `</div>`;
  }

  // Action Buttons Toolbar
  const actionsHtml = isAi ? `
    <button class="msg-action-btn" title="Copy response" onclick="copyMessageText(this)">
      <i class="fa-regular fa-copy"></i> Copy
    </button>
    <button class="msg-action-btn msg-speak-btn" title="Read Aloud (Listen)" onclick="speakMessage(this)">
      <i class="fa-solid fa-volume-high"></i> Read
    </button>
    <button class="msg-action-btn vote-btn" title="Helpful" onclick="voteMessage(this, 'up')">
      <i class="fa-regular fa-thumbs-up"></i>
    </button>
    <button class="msg-action-btn vote-btn" title="Needs improvement" onclick="voteMessage(this, 'down')">
      <i class="fa-regular fa-thumbs-down"></i>
    </button>
    <button class="msg-action-btn" title="Regenerate response" onclick="regenerateResponse()">
      <i class="fa-solid fa-rotate-right"></i> Regenerate
    </button>
    <button class="msg-action-btn" title="Delete message" onclick="deleteMessage('${msg.id}', this.closest('.message-row'))">
      <i class="fa-regular fa-trash-can"></i>
    </button>
  ` : `
    <button class="msg-action-btn" title="Copy text" onclick="copyMessageText(this)">
      <i class="fa-regular fa-copy"></i> Copy
    </button>
    <button class="msg-action-btn" title="Edit message" onclick="editUserMessage(this)">
      <i class="fa-solid fa-pen"></i> Edit
    </button>
    <button class="msg-action-btn" title="Delete message" onclick="deleteMessage('${msg.id}', this.closest('.message-row'))">
      <i class="fa-regular fa-trash-can"></i>
    </button>
  `;

  row.innerHTML = `
    <div class="msg-avatar ${isAi ? 'msg-avatar-ai' : 'msg-avatar-user'}">
      <i class="fa-${isAi ? 'solid fa-sparkles' : 'regular fa-user'}"></i>
    </div>
    <div class="msg-bubble-wrapper">
      <div class="msg-meta">
        <span class="msg-author">${isAi ? 'NexusAI' : (state.currentUser ? state.currentUser.name : 'You')}</span>
        <span class="msg-timestamp">${timeStr}</span>
      </div>
      <div class="msg-bubble ${isAi ? 'msg-bubble-ai' : 'msg-bubble-user'}">
        ${attachmentsHtml}
        <div class="msg-content-body">${parseMarkdownSafely(msg.content)}</div>
      </div>
      <div class="msg-actions-toolbar">
        ${actionsHtml}
      </div>
    </div>
  `;

  highlightCodeBlocks(row);
  return row;
}

function parseMarkdownSafely(text) {
  if (!text) return '';
  if (window.marked) {
    return marked.parse(text);
  }
  return escapeHtml(text).replace(/\n/g, '<br>');
}

function highlightCodeBlocks(container) {
  if (!container) return;
  const preElements = container.querySelectorAll('pre code');
  preElements.forEach((block) => {
    if (window.hljs) {
      hljs.highlightElement(block);
    }
    // Wrap in modern code block header if not already wrapped
    if (!block.closest('.code-block-container')) {
      const pre = block.parentElement;
      const lang = block.className.replace('language-', '').replace('hljs', '').trim() || 'code';
      const wrapper = document.createElement('div');
      wrapper.className = 'code-block-container';

      wrapper.innerHTML = `
        <div class="code-header">
          <span>${lang.toUpperCase()}</span>
          <button class="btn-copy-code" onclick="copyCodeFromBlock(this)">
            <i class="fa-regular fa-copy"></i> Copy
          </button>
        </div>
      `;

      pre.parentNode.insertBefore(wrapper, pre);
      wrapper.appendChild(pre);
    }
  });
}

function copyCodeFromBlock(btn) {
  const pre = btn.closest('.code-block-container').querySelector('pre');
  if (pre) {
    navigator.clipboard.writeText(pre.innerText).then(() => {
      btn.innerHTML = '<i class="fa-solid fa-check"></i> Copied!';
      setTimeout(() => {
        btn.innerHTML = '<i class="fa-regular fa-copy"></i> Copy';
      }, 2000);
      showToast('Code copied to clipboard.', 'success');
    });
  }
}

function copyMessageText(btn, fallbackText) {
  const row = btn.closest('.message-row');
  const body = row ? row.querySelector('.msg-content-body') : null;
  const text = (body ? (body.innerText || body.textContent) : '') || fallbackText || '';
  if (!text.trim()) return;

  navigator.clipboard.writeText(text.trim()).then(() => {
    const origHtml = btn.innerHTML;
    btn.innerHTML = '<i class="fa-solid fa-check text-success"></i> Copied!';
    setTimeout(() => {
      btn.innerHTML = origHtml;
    }, 2000);
    showToast('Message copied to clipboard.', 'success');
  });
}

function speakMessage(btn, fallbackText) {
  if (!window.speechSynthesis) {
    showToast('Text-to-speech is not supported in this browser.', 'warning');
    return;
  }

  // If already speaking on this button, stop
  if (btn.classList.contains('speaking')) {
    window.speechSynthesis.cancel();
    btn.classList.remove('speaking');
    btn.innerHTML = '<i class="fa-solid fa-volume-high"></i> Read';
    return;
  }

  // Cancel any ongoing speech
  window.speechSynthesis.cancel();
  document.querySelectorAll('.msg-speak-btn').forEach(b => {
    b.classList.remove('speaking');
    b.innerHTML = '<i class="fa-solid fa-volume-high"></i> Read';
  });

  const row = btn.closest('.message-row');
  const body = row ? row.querySelector('.msg-content-body') : null;
  const rawText = (body ? (body.innerText || body.textContent) : '') || fallbackText || '';

  const cleanText = rawText
    .replace(/```[\s\S]*?```/g, 'Code block omitted.')
    .replace(/`([^`]+)`/g, '$1')
    .replace(/\[([^\]]+)\]\([^\)]+\)/g, '$1')
    .replace(/[*_~#>]/g, '')
    .replace(/\n+/g, ' ')
    .trim();

  if (!cleanText) return;

  const utterance = new SpeechSynthesisUtterance(cleanText);
  utterance.rate = 1.0;
  utterance.pitch = 1.0;

  btn.classList.add('speaking');
  btn.innerHTML = '<i class="fa-solid fa-stop"></i> Stop';

  utterance.onend = () => {
    btn.classList.remove('speaking');
    btn.innerHTML = '<i class="fa-solid fa-volume-high"></i> Read';
  };

  utterance.onerror = () => {
    btn.classList.remove('speaking');
    btn.innerHTML = '<i class="fa-solid fa-volume-high"></i> Read';
  };

  window.speechSynthesis.speak(utterance);
}

function voteMessage(btn, type) {
  const toolbar = btn.parentElement;
  toolbar.querySelectorAll('.vote-btn').forEach(b => b.classList.remove('voted'));
  btn.classList.add('voted');
  if (type === 'up') {
    showToast('Thank you for the positive feedback! 👍', 'success');
  } else {
    showToast('Feedback noted! We are continuously improving. 👎', 'info');
  }
}

function editUserMessage(btn, fallbackText) {
  const row = btn.closest('.message-row');
  const body = row ? row.querySelector('.msg-content-body') : null;
  const text = (body ? (body.innerText || body.textContent) : '') || fallbackText || '';
  const input = document.getElementById('chat-input');
  input.value = text.trim();
  handleInputStats(input);
  input.focus();
  input.scrollIntoView({ behavior: 'smooth', block: 'center' });
  showToast('Message loaded into input for editing ✏️', 'info');
}

async function exportCurrentChat() {
  if (!state.activeChatId) {
    showToast('No active conversation to export.', 'warning');
    return;
  }

  try {
    const res = await fetch(`/api/chats/${state.activeChatId}`);
    if (!res.ok) throw new Error('Failed to fetch conversation');
    const chat = await res.json();

    let md = `# ${chat.title || 'NexusAI Conversation'}\n\n`;
    md += `_Exported from NexusAI on ${new Date().toLocaleString()}_\n\n`;
    md += `---\n\n`;

    if (chat.messages && chat.messages.length > 0) {
      chat.messages.forEach(m => {
        const sender = m.role === 'assistant' ? '🤖 **NexusAI**' : '👤 **You**';
        const time = m.created_at ? ` _(${formatTimestamp(m.created_at)})_` : '';
        md += `### ${sender}${time}\n\n`;
        if (m.attachments && m.attachments.length > 0) {
          md += `📎 **Attachments:** ` + m.attachments.map(a => a.name || a.original_filename).join(', ') + `\n\n`;
        }
        md += `${m.content}\n\n---\n\n`;
      });
    } else {
      md += `_No messages in this conversation._\n`;
    }

    const blob = new Blob([md], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    const safeTitle = (chat.title || 'chat').replace(/[^a-z0-9_-]/gi, '_').toLowerCase();
    a.href = url;
    a.download = `${safeTitle}_${Date.now()}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    showToast('Conversation exported to Markdown! 📄', 'success');
  } catch (err) {
    showToast('Failed to export conversation.', 'error');
  }
}

async function clearCurrentChatMessages() {
  if (!state.activeChatId) {
    showToast('No active conversation to clear.', 'warning');
    return;
  }

  if (!confirm('Clear all messages in this conversation? The conversation topic will be kept.')) {
    return;
  }

  try {
    const res = await fetch(`/api/chats/${state.activeChatId}/clear`, { method: 'POST' });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Failed to clear chat');

    showToast('Conversation messages cleared.', 'info');
    showHeroWelcome();
    await loadChats();
  } catch (err) {
    showToast('Failed to clear messages.', 'error');
  }
}

function selectPersona(personaType, btnElement) {
  state.activePersona = personaType;
  document.querySelectorAll('.persona-chip').forEach(chip => {
    chip.classList.toggle('active', chip.getAttribute('data-persona') === personaType);
  });
  const personaLabels = {
    all: 'All-Round AI',
    coder: 'Code Expert 💻',
    resume: 'Resume & ATS Coach 📄',
    tamil: 'தமிழ் / Tanglish Assistant 🇮🇳',
    math: 'Math & Logic Solver 🧮',
    writer: 'Writing & Email Assistant ✍️'
  };
  showToast(`Active Mode: ${personaLabels[personaType] || personaType}`, 'info');
}

function handleInputStats(textarea) {
  autoResizeInput(textarea);
  const text = textarea.value || '';
  const trimmed = text.trim();
  const chars = text.length;
  const words = trimmed ? trimmed.split(/\s+/).length : 0;
  const wordEl = document.getElementById('input-word-count');
  const charEl = document.getElementById('input-char-count');
  if (wordEl) wordEl.innerText = `${words} word${words === 1 ? '' : 's'}`;
  if (charEl) charEl.innerText = `${chars} char${chars === 1 ? '' : 's'}`;
}

function showTypingIndicator() {
  document.getElementById('typing-indicator').classList.remove('hidden');
  scrollToBottom();
}

function hideTypingIndicator() {
  document.getElementById('typing-indicator').classList.add('hidden');
}

function scrollToBottom() {
  const container = document.getElementById('chat-messages-container');
  container.scrollTop = container.scrollHeight;
}

// =====================================================================
// File Upload & Attachment Logic
// =====================================================================

function triggerFilePicker(type = 'any') {
  const input = document.getElementById('chat-file-input');
  if (type === 'image') {
    input.accept = '.jpg,.jpeg,.png,.webp,.gif';
  } else {
    input.accept = '.pdf,.docx,.doc,.txt,.csv,.xlsx,.xls,.pptx,.ppt,.jpg,.jpeg,.png,.webp,.json,.py';
  }
  input.click();
}

function triggerFileUploadForPrompt() {
  triggerFilePicker('any');
  showToast('Select a document or spreadsheet to analyze with NexusAI.', 'info');
}

async function handleFileSelected(e) {
  const file = e.target.files[0];
  if (!file) return;

  // Max 25 MB validation
  if (file.size > 25 * 1024 * 1024) {
    showToast('File size exceeds 25 MB limit.', 'error');
    e.target.value = '';
    return;
  }

  showToast(`Uploading and extracting: ${file.name}...`, 'info');

  const formData = new FormData();
  formData.append('file', file);
  if (state.activeProjectId) {
    formData.append('project_id', state.activeProjectId);
  }

  try {
    const res = await fetch('/api/upload', {
      method: 'POST',
      body: formData
    });
    const data = await res.json();

    if (!res.ok) {
      showToast(data.error || 'Upload failed.', 'error');
      return;
    }

    showToast(`File uploaded successfully: ${data.file.name}`, 'success');

    // Add to pending attachments
    state.pendingAttachments.push(data.file);
    renderAttachmentChips();

    // Refresh Library and Projects count
    fetchLibraryFiles();
  } catch (err) {
    showToast('Network error during file upload.', 'error');
  } finally {
    e.target.value = '';
  }
}

function renderAttachmentChips() {
  const container = document.getElementById('attachment-chips-container');
  container.innerHTML = '';

  if (state.pendingAttachments.length === 0) {
    container.classList.add('hidden');
    return;
  }

  container.classList.remove('hidden');
  state.pendingAttachments.forEach((file, index) => {
    const chip = document.createElement('div');
    chip.className = 'file-chip';
    chip.innerHTML = `
      <i class="fa-solid fa-file-lines file-chip-icon"></i>
      <span class="file-chip-name">${escapeHtml(file.name)}</span>
      <span class="file-chip-size">(${formatFileSize(file.size)})</span>
      <button class="file-chip-remove" onclick="removePendingAttachment(${index})">
        <i class="fa-solid fa-xmark"></i>
      </button>
    `;
    container.appendChild(chip);
  });
}

function removePendingAttachment(index) {
  state.pendingAttachments.splice(index, 1);
  renderAttachmentChips();
}

// =====================================================================
// Library Management
// =====================================================================

async function fetchLibraryFiles() {
  const search = document.getElementById('library-search') ? document.getElementById('library-search').value.trim() : '';
  const sort = document.getElementById('library-sort') ? document.getElementById('library-sort').value : 'date_desc';
  const category = state.libraryCategory;

  try {
    const res = await fetch(`/api/library?search=${encodeURIComponent(search)}&category=${category}&sort=${sort}`);
    const data = await res.json();
    state.libraryFiles = data.files || [];

    // Update Badge
    const badge = document.getElementById('library-count-badge');
    if (badge) badge.innerText = data.count || 0;

    renderLibraryGrid();
  } catch (err) {
    console.error('Error fetching library:', err);
  }
}

function setLibraryCategory(category, btn) {
  state.libraryCategory = category;
  document.querySelectorAll('.filter-group .filter-pill').forEach(el => el.classList.remove('active'));
  if (btn) btn.classList.add('active');
  fetchLibraryFiles();
}

function renderLibraryGrid() {
  const container = document.getElementById('library-files-container');
  if (!container) return;

  container.innerHTML = '';
  if (state.libraryFiles.length === 0) {
    container.innerHTML = `
      <div style="grid-column: 1 / -1; text-align: center; padding: 60px 20px; color: var(--text-muted);">
        <i class="fa-regular fa-folder-open" style="font-size: 40px; margin-bottom: 12px;"></i>
        <h4>No files in your library yet</h4>
        <p>Attach documents or spreadsheets in chat, or upload them directly to build your collection.</p>
      </div>
    `;
    return;
  }

  state.libraryFiles.forEach(file => {
    const card = document.createElement('div');
    card.className = 'library-file-card';
    const iconClass = getFileIcon(file.type);

    card.innerHTML = `
      <div class="file-card-top">
        <div class="file-card-icon"><i class="${iconClass}"></i></div>
        <div class="file-card-meta">
          <h4 class="file-card-name" title="${escapeHtml(file.name)}">${escapeHtml(file.name)}</h4>
          <span class="file-card-info">${file.type} • ${formatFileSize(file.size)} • ${formatDate(file.created_at)}</span>
        </div>
      </div>
      <div class="file-card-preview" title="Summary preview">${escapeHtml(file.summary || 'Parsed file content ready for AI reasoning.')}</div>
      <div class="file-card-actions">
        <button class="btn btn-secondary btn-sm" onclick="previewLibraryFile('${file.id}')">
          <i class="fa-regular fa-eye"></i> Preview
        </button>
        <button class="btn btn-primary btn-sm" onclick="attachFileToNewChat('${file.id}', '${escapeForAttribute(file.name)}')">
          <i class="fa-solid fa-message-plus"></i> Chat with file
        </button>
        <div style="display:flex; gap:4px;">
          <a href="/api/files/${file.id}/download" class="btn-icon" title="Download">
            <i class="fa-solid fa-download"></i>
          </a>
          <button class="btn-icon" title="Rename" onclick="promptRenameFile('${file.id}', '${escapeForAttribute(file.name)}')">
            <i class="fa-solid fa-pen"></i>
          </button>
          <button class="btn-icon text-danger" title="Delete" onclick="deleteLibraryFile('${file.id}')">
            <i class="fa-regular fa-trash-can"></i>
          </button>
        </div>
      </div>
    `;
    container.appendChild(card);
  });
}

async function previewLibraryFile(fileId) {
  try {
    const res = await fetch(`/api/files/${fileId}/preview`);
    if (!res.ok) throw new Error('Preview error');
    const data = await res.json();

    openModal('file-preview-modal');
    document.getElementById('preview-modal-title').innerHTML = `<i class="fa-solid fa-file-lines text-primary"></i> ${escapeHtml(data.name)}`;
    document.getElementById('preview-download-btn').onclick = () => {
      window.location.href = `/api/files/${fileId}/download`;
    };

    const body = document.getElementById('preview-modal-body');
    if (data.category === 'image') {
      body.innerHTML = `<img src="${data.preview}" style="max-width:100%; border-radius:var(--radius-md);" alt="Preview">`;
    } else {
      body.innerHTML = `
        <div style="font-size:12px; color:var(--text-muted); margin-bottom:12px;">
          File Type: <strong>${data.type}</strong> | Size: <strong>${formatFileSize(data.size)}</strong>
        </div>
        <pre style="background:var(--bg-tertiary); padding:16px; border-radius:var(--radius-md); max-height:450px; overflow:auto; font-family:var(--font-mono); font-size:12.5px; white-space:pre-wrap;">${escapeHtml(data.full_text || data.preview)}</pre>
      `;
    }
  } catch (err) {
    showToast('Failed to load file preview.', 'error');
  }
}

function attachFileToNewChat(fileId, fileName) {
  state.pendingAttachments = [{ id: fileId, name: fileName, size: 0, type: 'FILE' }];
  createNewChat().then(() => {
    renderAttachmentChips();
    const input = document.getElementById('chat-input');
    input.value = `Please analyze and summarize the attached file: "${fileName}".`;
    autoResizeInput(input);
  });
}

function promptRenameFile(fileId, currentName) {
  openModal('rename-modal');
  document.getElementById('rename-modal-title').innerHTML = '<i class="fa-solid fa-pen text-primary"></i> Rename File';
  document.getElementById('rename-input-label').innerText = 'Filename';
  const input = document.getElementById('rename-input');
  input.value = currentName;
  input.focus();

  document.getElementById('btn-save-rename').onclick = async () => {
    const newName = input.value.trim();
    if (!newName) return;

    try {
      const res = await fetch(`/api/files/${fileId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: newName })
      });
      if (res.ok) {
        closeModal('rename-modal');
        showToast('File renamed.', 'success');
        fetchLibraryFiles();
      }
    } catch (err) {
      showToast('Failed to rename file.', 'error');
    }
  };
}

async function deleteLibraryFile(fileId) {
  if (!confirm('Are you sure you want to delete this file from your library?')) return;

  try {
    const res = await fetch(`/api/files/${fileId}`, { method: 'DELETE' });
    if (res.ok) {
      showToast('File deleted.', 'info');
      fetchLibraryFiles();
    }
  } catch (err) {
    showToast('Failed to delete file.', 'error');
  }
}

// =====================================================================
// Projects Workspace Management
// =====================================================================

async function loadProjects() {
  try {
    const res = await fetch('/api/projects');
    const data = await res.json();
    state.projects = data.projects || [];

    const badge = document.getElementById('project-count-badge');
    if (badge) badge.innerText = state.projects.length;

    renderProjectsGrid();
  } catch (err) {
    console.error('Error loading projects:', err);
  }
}

function renderProjectsGrid() {
  const grid = document.getElementById('projects-grid');
  if (!grid) return;

  grid.innerHTML = '';
  if (state.projects.length === 0) {
    grid.innerHTML = `
      <div style="grid-column: 1 / -1; text-align: center; padding: 60px 20px; color: var(--text-muted);">
        <i class="fa-solid fa-diagram-project" style="font-size: 40px; margin-bottom: 12px;"></i>
        <h4>No projects created yet</h4>
        <p>Create a dedicated workspace to organize chats, files, and project guidelines.</p>
        <button class="btn btn-primary" style="margin-top: 14px;" onclick="openCreateProjectModal()">
          <i class="fa-solid fa-plus"></i> Create First Project
        </button>
      </div>
    `;
    return;
  }

  state.projects.forEach(proj => {
    const card = document.createElement('div');
    card.className = 'project-card';
    card.onclick = () => openProjectWorkspace(proj.id);

    card.innerHTML = `
      <div class="project-card-header">
        <span class="color-dot" style="background:${proj.color}"></span>
        <h4 class="project-card-name">${escapeHtml(proj.name)}</h4>
      </div>
      <p class="project-card-desc">${escapeHtml(proj.description || 'No description provided.')}</p>
      <div class="project-card-stats">
        <span><i class="fa-solid fa-comments"></i> ${proj.chat_count} chats</span>
        <span><i class="fa-solid fa-file-lines"></i> ${proj.file_count} files</span>
      </div>
    `;
    grid.appendChild(card);
  });
}

async function openProjectWorkspace(projectId) {
  state.activeProjectId = projectId;
  try {
    const res = await fetch(`/api/projects/${projectId}`);
    if (!res.ok) throw new Error('Project not found');
    const proj = await res.json();

    document.getElementById('projects-grid').classList.add('hidden');
    const panel = document.getElementById('project-detail-panel');
    panel.classList.remove('hidden');

    document.getElementById('proj-detail-name').innerText = proj.name;
    document.getElementById('proj-detail-desc').innerText = proj.description || 'Dedicated AI Project Workspace';
    document.getElementById('proj-color-pill').style.background = proj.color;

    // Associated Chats
    const chatsList = document.getElementById('project-chats-list');
    chatsList.innerHTML = '';
    if (proj.chats.length === 0) {
      chatsList.innerHTML = '<p class="text-muted" style="font-size:12px;">No chats in this project yet.</p>';
    } else {
      proj.chats.forEach(c => {
        const item = document.createElement('div');
        item.className = 'chat-item';
        item.style.background = 'var(--bg-tertiary)';
        item.innerHTML = `<span class="chat-item-title"><i class="fa-solid fa-comment" style="color:${proj.color}; margin-right:6px;"></i> ${escapeHtml(c.title)}</span>`;
        item.onclick = () => openChat(c.id);
        chatsList.appendChild(item);
      });
    }

    // Associated Files
    const filesList = document.getElementById('project-files-list');
    filesList.innerHTML = '';
    if (proj.files.length === 0) {
      filesList.innerHTML = '<p class="text-muted" style="font-size:12px;">No files assigned to this project yet.</p>';
    } else {
      proj.files.forEach(f => {
        const item = document.createElement('div');
        item.className = 'chat-item';
        item.style.background = 'var(--bg-tertiary)';
        item.innerHTML = `<span class="chat-item-title"><i class="fa-solid fa-file" style="margin-right:6px;"></i> ${escapeHtml(f.name)}</span>`;
        item.onclick = () => previewLibraryFile(f.id);
        filesList.appendChild(item);
      });
    }
  } catch (err) {
    showToast('Failed to load project details.', 'error');
  }
}

function startChatInProject() {
  if (!state.activeProjectId) return;
  createNewChat(state.activeProjectId);
}

function openCreateProjectModal() {
  openModal('project-modal');
  document.getElementById('project-modal-title').innerHTML = '<i class="fa-solid fa-diagram-project text-primary"></i> Create Project';
  document.getElementById('modal-proj-name').value = '';
  document.getElementById('modal-proj-desc').value = '';
  document.getElementById('modal-proj-instructions').value = '';
  state.editingProjectId = null;
}

function selectProjectColor(color, swatch) {
  state.activeColor = color;
  document.querySelectorAll('.color-swatch').forEach(s => s.classList.remove('active'));
  swatch.classList.add('active');
}

async function saveProjectModal() {
  const name = document.getElementById('modal-proj-name').value.trim();
  const description = document.getElementById('modal-proj-desc').value.trim();
  const color = state.activeColor;
  const system_instructions = document.getElementById('modal-proj-instructions').value.trim();

  if (!name) {
    showToast('Project name is required.', 'error');
    return;
  }

  const isEdit = Boolean(state.editingProjectId);
  const url = isEdit ? `/api/projects/${state.editingProjectId}` : '/api/projects';
  const method = isEdit ? 'PATCH' : 'POST';

  try {
    const res = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, description, color, system_instructions })
    });
    if (res.ok) {
      closeModal('project-modal');
      showToast(isEdit ? 'Project updated.' : 'Project created!', 'success');
      await loadProjects();
      if (isEdit && state.activeProjectId === state.editingProjectId) {
        openProjectWorkspace(state.editingProjectId);
      }
    }
  } catch (err) {
    showToast('Failed to save project.', 'error');
  }
}

function editCurrentProject() {
  const proj = state.projects.find(p => p.id === state.activeProjectId);
  if (!proj) return;

  openModal('project-modal');
  document.getElementById('project-modal-title').innerHTML = '<i class="fa-solid fa-pen text-primary"></i> Edit Project';
  document.getElementById('modal-proj-name').value = proj.name;
  document.getElementById('modal-proj-desc').value = proj.description || '';
  document.getElementById('modal-proj-instructions').value = proj.system_instructions || '';
  state.editingProjectId = proj.id;
}

async function deleteCurrentProject() {
  if (!confirm('Are you sure you want to delete this project? Associated chats will be unlinked.')) return;

  try {
    const res = await fetch(`/api/projects/${state.activeProjectId}`, { method: 'DELETE' });
    if (res.ok) {
      showToast('Project deleted.', 'info');
      state.activeProjectId = null;
      document.getElementById('project-detail-panel').classList.add('hidden');
      document.getElementById('projects-grid').classList.remove('hidden');
      loadProjects();
    }
  } catch (err) {
    showToast('Failed to delete project.', 'error');
  }
}

// =====================================================================
// Global Search (Ctrl + K)
// =====================================================================

function openSearchModal() {
  openModal('search-modal');
  const input = document.getElementById('global-search-input');
  input.value = '';
  input.focus();
  document.getElementById('search-results-list').innerHTML = `
    <div class="search-empty-state">
      <i class="fa-regular fa-compass"></i>
      <p>Type to search across conversation titles, user questions, AI answers, and uploaded files.</p>
    </div>
  `;
}

let searchDebounce = null;
function handleGlobalSearch(query) {
  clearTimeout(searchDebounce);
  if (query.trim().length < 2) {
    document.getElementById('search-results-list').innerHTML = `
      <div class="search-empty-state">
        <i class="fa-regular fa-compass"></i>
        <p>Type at least 2 characters to search...</p>
      </div>
    `;
    return;
  }

  searchDebounce = setTimeout(async () => {
    try {
      const res = await fetch(`/api/search?q=${encodeURIComponent(query.trim())}`);
      const data = await res.json();
      renderSearchResults(data.results || [], query.trim());
    } catch (err) {
      console.error('Search error:', err);
    }
  }, 250);
}

function renderSearchResults(results, query) {
  const list = document.getElementById('search-results-list');
  list.innerHTML = '';

  if (results.length === 0) {
    list.innerHTML = `
      <div class="search-empty-state">
        <i class="fa-solid fa-magnifying-glass"></i>
        <p>No results found for "<strong>${escapeHtml(query)}</strong>"</p>
      </div>
    `;
    return;
  }

  results.forEach(item => {
    const div = document.createElement('div');
    div.className = 'search-result-item';

    let icon = 'fa-comment';
    if (item.type === 'message') icon = item.role === 'user' ? 'fa-user' : 'fa-sparkles';
    if (item.type === 'file') icon = 'fa-file-lines';

    div.innerHTML = `
      <i class="fa-solid ${icon} search-result-icon"></i>
      <div class="search-result-text">
        <h5>${escapeHtml(item.title)}</h5>
        <p>${escapeHtml(item.snippet)}</p>
      </div>
    `;

    div.onclick = () => {
      closeModal('search-modal');
      if (item.chat_id) {
        openChat(item.chat_id);
      } else if (item.file_id) {
        previewLibraryFile(item.file_id);
      }
    };

    list.appendChild(div);
  });
}

// =====================================================================
// Settings & Profile Management
// =====================================================================

function switchSettingsTab(tabName, btn) {
  document.querySelectorAll('.settings-tab').forEach(el => el.classList.remove('active'));
  if (btn) btn.classList.add('active');

  document.querySelectorAll('.settings-tab-pane').forEach(el => {
    el.classList.add('hidden');
    el.classList.remove('active');
  });

  const pane = document.getElementById(`tab-settings-${tabName}`);
  if (pane) {
    pane.classList.remove('hidden');
    pane.classList.add('active');
  }
}

function selectAvatar(avatarKey, el) {
  state.activeAvatar = avatarKey;
  document.querySelectorAll('.avatar-option').forEach(a => a.classList.remove('active'));
  el.classList.add('active');
}

async function saveProfileSettings() {
  const name = document.getElementById('settings-name').value.trim();
  const email = document.getElementById('settings-email').value.trim();
  const avatar = state.activeAvatar;

  try {
    const res = await fetch('/api/settings/profile', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, avatar })
    });
    const data = await res.json();
    if (res.ok) {
      showToast('Profile updated successfully.', 'success');
      state.currentUser.name = name;
      state.currentUser.email = email;
      document.getElementById('user-name-display').innerText = name;
      document.getElementById('user-email-display').innerText = email;
    } else {
      showToast(data.error || 'Failed to update profile.', 'error');
    }
  } catch (err) {
    showToast('Network error updating profile.', 'error');
  }
}

async function handlePasswordChange() {
  const current_password = document.getElementById('current-password').value;
  const new_password = document.getElementById('new-password').value;
  const confirm_new_password = document.getElementById('confirm-new-password').value;

  if (new_password !== confirm_new_password) {
    showToast('New passwords do not match.', 'error');
    return;
  }

  try {
    const res = await fetch('/api/settings/password', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ current_password, new_password, confirm_new_password })
    });
    const data = await res.json();
    if (res.ok) {
      showToast(data.message, 'success');
      document.getElementById('current-password').value = '';
      document.getElementById('new-password').value = '';
      document.getElementById('confirm-new-password').value = '';
    } else {
      showToast(data.error || 'Password update failed.', 'error');
    }
  } catch (err) {
    showToast('Network error updating password.', 'error');
  }
}

async function saveAISettings() {
  const gemini_api_key = document.getElementById('settings-gemini-key').value.trim();
  const ai_model = document.getElementById('settings-model').value;
  const temperature = parseFloat(document.getElementById('settings-temperature').value);
  const system_instruction = document.getElementById('settings-system-instruction').value.trim();

  try {
    const res = await fetch('/api/settings/ai', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ gemini_api_key, ai_model, temperature, system_instruction })
    });
    const data = await res.json();
    if (res.ok) {
      showToast('AI preferences saved.', 'success');
    } else {
      showToast('Failed to save AI preferences.', 'error');
    }
  } catch (err) {
    showToast('Network error saving AI settings.', 'error');
  }
}

async function testGeminiConnection() {
  const apiKey = document.getElementById('settings-gemini-key').value.trim();
  const statusPill = document.getElementById('gemini-test-status');

  statusPill.className = 'test-status-pill';
  statusPill.style.background = 'var(--bg-tertiary)';
  statusPill.style.color = 'var(--text-muted)';
  statusPill.innerText = 'Testing connection...';
  statusPill.classList.remove('hidden');

  try {
    const res = await fetch('/api/settings/test-gemini', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ api_key: apiKey })
    });
    const data = await res.json();

    if (data.success) {
      statusPill.style.background = 'rgba(16, 185, 129, 0.2)';
      statusPill.style.color = '#6ee7b7';
      statusPill.innerText = '✓ Connection Verified!';
      showToast('Google Gemini API connected successfully!', 'success');
    } else {
      statusPill.style.background = 'rgba(239, 68, 68, 0.2)';
      statusPill.style.color = '#fca5a5';
      statusPill.innerText = '✗ Test Failed';
      showToast(data.error || 'Connection test failed.', 'error');
    }
  } catch (err) {
    statusPill.innerText = '✗ Connection Error';
    showToast('Network error testing key.', 'error');
  }
}

function exportUserData() {
  window.location.href = '/api/settings/export';
}

async function clearAllChatHistory() {
  if (!confirm('Are you sure you want to delete ALL your conversations? This cannot be undone.')) return;

  try {
    const res = await fetch('/api/settings/clear-history', { method: 'POST' });
    if (res.ok) {
      showToast('All chat history cleared.', 'info');
      state.chats = [];
      state.pinnedChats = [];
      state.historyChats = [];
      state.activeChatId = null;
      renderSidebarChats();
      showHeroWelcome();
    }
  } catch (err) {
    showToast('Failed to clear history.', 'error');
  }
}

// =====================================================================
// Speech-to-Text Integration (Microphone Button)
// =====================================================================

function setupSpeechRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    console.warn('Speech recognition not supported in this browser.');
    return;
  }

  state.speechRecognition = new SpeechRecognition();
  state.speechRecognition.continuous = false;
  state.speechRecognition.interimResults = false;
  state.speechRecognition.lang = 'en-US';

  state.speechRecognition.onstart = () => {
    state.isRecordingVoice = true;
    document.getElementById('btn-mic').classList.add('recording');
    showToast('Listening... Speak into your microphone.', 'info');
  };

  state.speechRecognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    const input = document.getElementById('chat-input');
    input.value = (input.value ? input.value + ' ' : '') + transcript;
    autoResizeInput(input);
  };

  state.speechRecognition.onerror = (event) => {
    console.error('Speech recognition error:', event.error);
    showToast('Voice input error: ' + event.error, 'error');
  };

  state.speechRecognition.onend = () => {
    state.isRecordingVoice = false;
    document.getElementById('btn-mic').classList.remove('recording');
  };
}

function toggleSpeechRecognition() {
  if (!state.speechRecognition) {
    showToast('Speech-to-text is not supported in this browser. Please use Chrome or Edge.', 'warning');
    return;
  }

  if (state.isRecordingVoice) {
    state.speechRecognition.stop();
  } else {
    state.speechRecognition.start();
  }
}

// =====================================================================
// Modal & Toast Helpers
// =====================================================================

function openModal(modalId) {
  document.getElementById('modal-backdrop').classList.remove('hidden');
  document.getElementById(modalId).classList.remove('hidden');
}

function closeModal(modalId) {
  document.getElementById(modalId).classList.add('hidden');
  // If no other modal open, hide backdrop
  const anyOpen = Array.from(document.querySelectorAll('.modal-dialog')).some(m => !m.classList.contains('hidden'));
  if (!anyOpen) {
    document.getElementById('modal-backdrop').classList.add('hidden');
  }
}

function closeAllModals() {
  document.querySelectorAll('.modal-dialog').forEach(m => m.classList.add('hidden'));
  document.getElementById('modal-backdrop').classList.add('hidden');
}

function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;

  let icon = 'fa-info-circle';
  if (type === 'success') icon = 'fa-check-circle';
  if (type === 'error') icon = 'fa-circle-exclamation';
  if (type === 'warning') icon = 'fa-triangle-exclamation';

  toast.innerHTML = `<i class="fa-solid ${icon}"></i> <span>${escapeHtml(message)}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(100%)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

// Format Utilities
function formatFileSize(bytes) {
  if (!bytes || bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

function formatDate(isoStr) {
  if (!isoStr) return '';
  const d = new Date(isoStr);
  return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
}

function formatTimestamp(isoStr) {
  if (!isoStr) return '';
  const d = new Date(isoStr);
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function getFileIcon(type) {
  const t = (type || '').toUpperCase();
  if (t === 'PDF') return 'fa-solid fa-file-pdf text-danger';
  if (['DOCX', 'DOC'].includes(t)) return 'fa-solid fa-file-word text-primary';
  if (['CSV', 'XLSX', 'XLS'].includes(t)) return 'fa-solid fa-file-excel text-success';
  if (['PPTX', 'PPT'].includes(t)) return 'fa-solid fa-file-powerpoint text-warning';
  if (['JPG', 'JPEG', 'PNG', 'WEBP', 'GIF'].includes(t)) return 'fa-solid fa-file-image text-info';
  return 'fa-solid fa-file-lines';
}

function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/[&<>'"]/g, tag => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    "'": '&#39;',
    '"': '&quot;'
  }[tag] || tag));
}

function escapeForAttribute(str) {
  if (!str) return '';
  return str.replace(/'/g, "\\'").replace(/"/g, '&quot;');
}
