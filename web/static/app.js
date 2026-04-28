'use strict';

// ── State ──────────────────────────────────────────────────────────────────
let config = {};
let boardData = null;
let currentProblem = null;
let currentUser = null;
let problems = [];
let selectedTags = new Set();
let projectsFilterActive = false;
let currentSection = 'problems';

// LED mode state
let ledMode = null;          // 'mirror' | 'heatmap' | 'sequence' | null
let sequenceTimer = null;
let sequenceStep = 0;
let timerInterval = null;
let timerSecondsLeft = 0;

// Admin state
let adminProblems = [];      // full list for admin problem edit dropdown
let currentAdminTab = 'users';
let loggedProblems = new Set();

// ── Init ───────────────────────────────────────────────────────────────────
async function init() {
  await Promise.all([loadConfig(), loadBoard(), checkLogin()]);
  await loadLoggedProblems();
  loadUsers();
  buildGradeSliders();
  buildTagChips();
  loadProblems();

  if (config.theme_colour) {
    document.getElementById('app-header').style.background = config.theme_colour;
    document.getElementById('app-nav').style.borderBottomColor = config.theme_colour;
  }
}

// ── API helpers ────────────────────────────────────────────────────────────
async function api(path, opts = {}) {
  const resp = await fetch(path, {
    headers: { 'Content-Type': 'application/json' },
    ...opts,
  });
  if (resp.status === 204) return {};
  const data = await resp.json();
  if (!resp.ok) {
    throw Object.assign(new Error(data.error || 'Request failed'), { status: resp.status });
  }
  return data;
}

// ── Config & board ─────────────────────────────────────────────────────────
async function loadConfig() {
  try {
    config = await api('/api/config');
  } catch (e) {
    console.error('Failed to load config', e);
  }
}

async function loadBoard() {
  try {
    boardData = await api('/api/board');
  } catch (e) {
    console.error('Failed to load board', e);
  }
}

// ── Auth ───────────────────────────────────────────────────────────────────
async function loadLoggedProblems() {
  if (!currentUser) { loggedProblems = new Set(); return; }
  try {
    const names = await api('/api/logbook/names');
    loggedProblems = new Set(names);
  } catch (e) {
    loggedProblems = new Set();
  }
}

async function checkLogin() {
  try {
    const data = await api('/api/me');
    currentUser = data.username;
    updateAuthBar();
  } catch (e) {
    currentUser = null;
    updateAuthBar();
  }
}

function updateAuthBar() {
  const usernameEl = document.getElementById('auth-username');
  const logoutBtn = document.getElementById('btn-logout');
  const loginBtn = document.getElementById('btn-show-login');
  const registerBtn = document.getElementById('btn-show-register');
  const projectsBtn = document.getElementById('btn-projects-filter');
  const adminTab = document.getElementById('nav-admin');

  if (currentUser) {
    usernameEl.textContent = currentUser;
    usernameEl.classList.remove('hidden');
    logoutBtn.classList.remove('hidden');
    loginBtn.classList.add('hidden');
    registerBtn.classList.add('hidden');
    projectsBtn.classList.remove('hidden');
    if (config.admin_user && currentUser === config.admin_user) {
      adminTab.classList.remove('hidden');
    } else {
      adminTab.classList.add('hidden');
    }
  } else {
    usernameEl.classList.add('hidden');
    logoutBtn.classList.add('hidden');
    loginBtn.classList.remove('hidden');
    registerBtn.classList.remove('hidden');
    projectsBtn.classList.add('hidden');
    adminTab.classList.add('hidden');
    // If currently on admin or logbook, go back to problems
    if (currentSection === 'admin') showSection('problems');
  }

  if (currentProblem) updateDetailAuthButtons();
}

// Login overlay
document.getElementById('btn-show-login').addEventListener('click', () => {
  document.getElementById('login-overlay').classList.remove('hidden');
  document.getElementById('login-password').value = '';
  document.getElementById('login-error').classList.add('hidden');
});

document.getElementById('btn-login-cancel').addEventListener('click', () => {
  document.getElementById('login-overlay').classList.add('hidden');
});

document.getElementById('btn-login-submit').addEventListener('click', submitLogin);
document.getElementById('login-password').addEventListener('keydown', e => {
  if (e.key === 'Enter') submitLogin();
});

async function submitLogin() {
  const username = document.getElementById('login-username').value;
  const password = document.getElementById('login-password').value;
  const errorEl = document.getElementById('login-error');
  if (!username) { showError(errorEl, 'Please select a username'); return; }
  try {
    await api('/api/login', { method: 'POST', body: JSON.stringify({ username, password }) });
    currentUser = username;
    await loadLoggedProblems();
    renderProblemList(problems);
    updateAuthBar();
    document.getElementById('login-overlay').classList.add('hidden');
  } catch (e) {
    showError(errorEl, e.message || 'Login failed');
  }
}

document.getElementById('btn-logout').addEventListener('click', async () => {
  await api('/api/logout', { method: 'POST' });
  currentUser = null;
  projectsFilterActive = false;
  document.getElementById('btn-projects-filter').classList.remove('active-filter');
  updateAuthBar();
  loggedProblems = new Set();
  loadProblems();
});

// Register overlay
document.getElementById('btn-show-register').addEventListener('click', () => {
  document.getElementById('register-overlay').classList.remove('hidden');
  document.getElementById('reg-username').value = '';
  document.getElementById('reg-password').value = '';
  document.getElementById('reg-name').value = '';
  document.getElementById('reg-email').value = '';
  document.getElementById('register-error').classList.add('hidden');
});

document.getElementById('btn-register-cancel').addEventListener('click', () => {
  document.getElementById('register-overlay').classList.add('hidden');
});

document.getElementById('btn-register-submit').addEventListener('click', submitRegister);

async function submitRegister() {
  const username = document.getElementById('reg-username').value.trim();
  const password = document.getElementById('reg-password').value;
  const name = document.getElementById('reg-name').value.trim();
  const email = document.getElementById('reg-email').value.trim();
  const errorEl = document.getElementById('register-error');
  if (!username || !password) { showError(errorEl, 'Username and password are required'); return; }
  try {
    await api('/api/register', { method: 'POST', body: JSON.stringify({ username, password, name, email }) });
    document.getElementById('register-overlay').classList.add('hidden');
    // Auto-login after registration
    try {
      await api('/api/login', { method: 'POST', body: JSON.stringify({ username, password }) });
      currentUser = username;
      // Refresh user list in login dropdown
      const select = document.getElementById('login-username');
      if (![...select.options].some(o => o.value === username)) {
        select.appendChild(new Option(username, username));
      }
      const filterSelect = document.getElementById('filter-user');
      if (![...filterSelect.options].some(o => o.value === username)) {
        filterSelect.appendChild(new Option(username, username));
      }
      updateAuthBar();
      await loadLoggedProblems();
      renderProblemList(problems);
    } catch (_) {}
  } catch (e) {
    showError(errorEl, e.message || 'Registration failed');
  }
}

async function loadUsers() {
  try {
    const users = await api('/api/users');
    const select = document.getElementById('login-username');
    const filterSelect = document.getElementById('filter-user');
    users.forEach(u => {
      select.appendChild(new Option(u, u));
      filterSelect.appendChild(new Option(u, u));
    });
  } catch (e) {
    console.error('Failed to load users', e);
  }
}

// ── Navigation ─────────────────────────────────────────────────────────────
function showSection(name) {
  currentSection = name;
  ['problems', 'logbook', 'admin'].forEach(s => {
    document.getElementById(`section-${s}`).classList.toggle('hidden', s !== name);
    document.getElementById(`nav-${s}`).classList.toggle('active', s === name);
  });

  if (name === 'logbook') loadLogbook();
  if (name === 'admin') loadAdminTab(currentAdminTab);
}

document.getElementById('nav-problems').addEventListener('click', () => showSection('problems'));
document.getElementById('nav-logbook').addEventListener('click', () => showSection('logbook'));
document.getElementById('nav-admin').addEventListener('click', () => showSection('admin'));

// ── Grade sliders ──────────────────────────────────────────────────────────
function buildGradeSliders() {
  const grades = config.grades || [];
  if (!grades.length) return;

  const minSlider = document.getElementById('grade-min');
  const maxSlider = document.getElementById('grade-max');
  const minLabel = document.getElementById('grade-min-label');
  const maxLabel = document.getElementById('grade-max-label');

  minSlider.max = grades.length - 1;
  minSlider.value = 0;
  maxSlider.max = grades.length - 1;
  maxSlider.value = grades.length - 1;

  function update() {
    let lo = parseInt(minSlider.value);
    let hi = parseInt(maxSlider.value);
    if (lo > hi) { lo = hi; minSlider.value = lo; }
    minLabel.textContent = grades[lo];
    maxLabel.textContent = grades[hi];
  }

  minSlider.addEventListener('input', () => { update(); debounceLoadProblems(); });
  maxSlider.addEventListener('input', () => { update(); debounceLoadProblems(); });
  update();
}

// ── Tag filter ─────────────────────────────────────────────────────────────
function buildTagChips() {
  const tags = config.tags || [];
  const container = document.getElementById('tag-checkboxes');
  container.innerHTML = '';
  tags.forEach(tag => {
    if (!tag) return;
    const chip = document.createElement('label');
    chip.className = 'tag-chip';
    chip.dataset.tag = tag;
    const cb = document.createElement('input');
    cb.type = 'checkbox';
    cb.value = tag;
    cb.addEventListener('change', () => {
      if (cb.checked) { selectedTags.add(tag); chip.classList.add('active'); }
      else { selectedTags.delete(tag); chip.classList.remove('active'); }
      debounceLoadProblems();
    });
    chip.appendChild(cb);
    chip.appendChild(document.createTextNode(tag));
    container.appendChild(chip);
  });
}

document.getElementById('btn-filter-tags').addEventListener('click', () => {
  document.getElementById('tag-filter-panel').classList.toggle('hidden');
});

document.getElementById('btn-clear-tags').addEventListener('click', () => {
  selectedTags.clear();
  document.querySelectorAll('#tag-checkboxes input[type="checkbox"]').forEach(cb => {
    cb.checked = false;
    cb.closest('.tag-chip').classList.remove('active');
  });
  debounceLoadProblems();
});

// Projects filter toggle
document.getElementById('btn-projects-filter').addEventListener('click', () => {
  if (!currentUser) return;
  projectsFilterActive = !projectsFilterActive;
  const btn = document.getElementById('btn-projects-filter');
  btn.classList.toggle('active-filter', projectsFilterActive);
  btn.textContent = projectsFilterActive ? '★ My Projects' : '☆ My Projects';
  loadProblems();
});

// Random problem button
document.getElementById('btn-random').addEventListener('click', async () => {
  const grades = config.grades || [];
  const gradeMin = parseInt(document.getElementById('grade-min').value || 0);
  const gradeMax = parseInt(document.getElementById('grade-max').value || grades.length - 1);
  const name = document.getElementById('filter-name').value.trim();
  const user = document.getElementById('filter-user').value;
  const tags = [...selectedTags].join(',');

  const params = new URLSearchParams({ grade_min: gradeMin, grade_max: gradeMax });
  if (name) params.set('name', name);
  if (user) params.set('user', user);
  if (tags) params.set('tags', tags);

  try {
    const prob = await api(`/api/problems/random?${params}`);
    openProblem(prob.row);
  } catch (e) {
    if (e.status === 404) alert('No matching problems found.');
    else console.error('Random problem failed', e);
  }
});

// ── Problem list ───────────────────────────────────────────────────────────
let filterTimer = null;
function debounceLoadProblems() {
  clearTimeout(filterTimer);
  filterTimer = setTimeout(loadProblems, 350);
}

document.getElementById('filter-name').addEventListener('input', debounceLoadProblems);
document.getElementById('filter-user').addEventListener('change', loadProblems);

async function loadProblems() {
  const grades = config.grades || [];
  const gradeMin = parseInt(document.getElementById('grade-min').value || 0);
  const gradeMax = parseInt(document.getElementById('grade-max').value || grades.length - 1);
  const name = document.getElementById('filter-name').value.trim();
  const user = document.getElementById('filter-user').value;
  const tags = [...selectedTags].join(',');

  const params = new URLSearchParams({ grade_min: gradeMin, grade_max: gradeMax });
  if (name) params.set('name', name);
  if (user) params.set('user', user);
  if (tags) params.set('tags', tags);
  if (projectsFilterActive && currentUser) params.set('projects', '1');

  try {
    problems = await api(`/api/problems?${params}`);
    renderProblemList(problems);
  } catch (e) {
    console.error('Failed to load problems', e);
  }
}

function renderProblemList(list) {
  const ul = document.getElementById('problem-list');
  const countEl = document.getElementById('problem-count');
  ul.innerHTML = '';
  countEl.textContent = `${list.length} problem${list.length !== 1 ? 's' : ''}`;

  if (!list.length) {
    const empty = document.createElement('li');
    empty.id = 'list-empty';
    empty.textContent = 'No problems match the filters.';
    ul.appendChild(empty);
    return;
  }

  list.forEach(prob => {
    const li = document.createElement('li');
    const tick = loggedProblems.has(prob.name)
      ? '<span class="prob-logged-tick">✓</span>' : '';
    li.innerHTML = `
      <span class="prob-list-name">${tick}${escHtml(prob.name)}</span>
      <span class="prob-list-meta">
        <span class="grade-badge">${escHtml(prob.grade_label)}</span><br>
        <span>${escHtml(prob.user)}</span>
      </span>
    `;
    li.addEventListener('click', () => openProblem(prob.row));
    ul.appendChild(li);
  });
}

// ── Problem detail ─────────────────────────────────────────────────────────
async function openProblem(row) {
  try {
    const prob = await api(`/api/problems/${row}`);
    currentProblem = prob;
    renderDetail(prob);
    updatePrevNextButtons();
    showDetailPanel();
    loadVotes(prob);
  } catch (e) {
    console.error('Failed to load problem', e);
  }
}

function updatePrevNextButtons() {
  const prevBtn = document.getElementById('btn-prev');
  const nextBtn = document.getElementById('btn-next');
  if (!currentProblem) {
    prevBtn.disabled = true;
    nextBtn.disabled = true;
    return;
  }
  const idx = problems.findIndex(p => p.row === currentProblem.row);
  prevBtn.disabled = idx <= 0;
  nextBtn.disabled = idx === -1 || idx >= problems.length - 1;
}

function renderDetail(prob) {
  document.getElementById('prob-name').textContent = prob.name;
  document.getElementById('prob-grade').textContent = prob.grade_label;
  document.getElementById('prob-grade').className = 'grade-badge';
  document.getElementById('prob-stars').textContent = prob.stars_label !== '-' ? prob.stars_label : '';
  document.getElementById('prob-user').textContent = 'Set by ' + prob.user;
  document.getElementById('prob-date').textContent = prob.date;
  document.getElementById('prob-ascents').textContent =
    prob.ascent_count != null ? `${prob.ascent_count} ascent${prob.ascent_count !== 1 ? 's' : ''}` : '';
  document.getElementById('prob-notes').textContent = prob.notes || '';

  const fsEl = document.getElementById('prob-footholdset');
  if (prob.footholdset) {
    fsEl.textContent = prob.footholdset;
    fsEl.classList.remove('hidden');
  } else {
    fsEl.textContent = '';
    fsEl.classList.add('hidden');
  }

  const tagsEl = document.getElementById('prob-tags');
  tagsEl.innerHTML = '';
  (prob.tags || []).forEach(tag => {
    const span = document.createElement('span');
    span.className = 'prob-tag';
    span.textContent = tag;
    tagsEl.appendChild(span);
  });

  renderOverlay(prob);
  updateDetailAuthButtons();
  hideLedStatus();
  stopAllModes();
  stopTimer();

  // Reset vote histograms
  document.getElementById('vote-histograms').classList.add('hidden');
  document.getElementById('star-bars').innerHTML = '';
  document.getElementById('grade-bars').innerHTML = '';
}

function updateDetailAuthButtons() {
  const projectBtn = document.getElementById('btn-project');
  const logBtn = document.getElementById('btn-log');
  if (currentUser) {
    projectBtn.classList.remove('hidden');
    logBtn.classList.remove('hidden');
    if (currentProblem) {
      projectBtn.textContent = currentProblem.is_project ? '★ Remove project' : '☆ Add project';
    }
  } else {
    projectBtn.classList.add('hidden');
    logBtn.classList.add('hidden');
  }
}

// Vote histograms
async function loadVotes(prob) {
  try {
    const votes = await api(`/api/problems/${prob.row}/votes`);
    renderStarBars(votes.star_votes);
    renderGradeBars(votes.grade_votes);
    const total = Object.values(votes.star_votes).reduce((a, b) => a + b, 0);
    if (total > 0) document.getElementById('vote-histograms').classList.remove('hidden');
  } catch (e) {
    console.error('Failed to load votes', e);
  }
}

function renderBarChart(containerId, data) {
  const container = document.getElementById(containerId);
  container.innerHTML = '';
  const max = Math.max(...Object.values(data), 1);
  Object.entries(data).forEach(([label, count]) => {
    const row = document.createElement('div');
    row.className = 'bar-row';
    row.innerHTML = `
      <span class="bar-label">${escHtml(label)}</span>
      <div class="bar-track">
        <div class="bar-fill" style="width:${Math.round(count / max * 100)}%"></div>
      </div>
      <span class="bar-count">${count}</span>
    `;
    container.appendChild(row);
  });
}

function renderStarBars(starVotes) {
  // Reverse so highest stars first
  const ordered = {};
  [...(config.stars || [])].reverse().forEach(s => { ordered[s] = starVotes[s] || 0; });
  renderBarChart('star-bars', ordered);
}

function renderGradeBars(gradeVotes) {
  // Only show grades that appear in config, in order
  const ordered = {};
  (config.grades || []).forEach(g => { if (gradeVotes[g] > 0) ordered[g] = gradeVotes[g]; });
  if (Object.keys(ordered).length) renderBarChart('grade-bars', ordered);
}

// ── Board overlay ──────────────────────────────────────────────────────────
function renderOverlay(prob) {
  document.querySelectorAll('.hold-marker').forEach(el => el.remove());
  if (!boardData || !boardData.holds) return;

  const container = document.getElementById('board-container');
  const { startHolds = [], probHolds = [], finHolds = [] } = prob;

  boardData.holds.forEach(hold => {
    const isStart = startHolds.includes(hold.id);
    const isFin   = finHolds.includes(hold.id);
    const isProb  = probHolds.includes(hold.id);
    if (!isStart && !isFin && !isProb) return;

    const type = isStart ? 'start' : isFin ? 'finish' : 'problem';
    const marker = document.createElement('div');
    marker.className = `hold-marker ${type}`;

    if (hold.x_pct != null && hold.y_pct != null) {
      marker.style.left = hold.x_pct + '%';
      marker.style.top  = hold.y_pct + '%';
    }

    container.appendChild(marker);
  });
}

// Mirror helper
function getMirrorHolds(holdIds) {
  if (!boardData || !boardData.mirror_table) return holdIds;
  return holdIds.map(id => {
    for (const pair of boardData.mirror_table) {
      if (pair[0] === id) return pair[1];
      if (pair[1] === id) return pair[0];
    }
    return id;
  });
}

// ── LED controls ───────────────────────────────────────────────────────────
document.getElementById('btn-light').addEventListener('click', async () => {
  if (!currentProblem) return;
  stopAllModes();
  const btn = document.getElementById('btn-light');
  btn.disabled = true;
  try {
    await api(`/api/light/${currentProblem.row}`, { method: 'POST' });
    hideLedStatus();
  } catch (e) {
    showLedStatus('LED control failed: ' + e.message);
  } finally {
    btn.disabled = false;
  }
});

document.getElementById('btn-off').addEventListener('click', async () => {
  stopAllModes();
  const btn = document.getElementById('btn-off');
  btn.disabled = true;
  try {
    await api('/api/light/off', { method: 'POST' });
    hideLedStatus();
  } catch (e) {
    showLedStatus(e.message);
  } finally {
    btn.disabled = false;
  }
});

function showLedStatus(msg) {
  const bar = document.getElementById('led-status-bar');
  document.getElementById('led-status-msg').textContent = msg;
  bar.classList.remove('hidden');
}

function hideLedStatus() {
  document.getElementById('led-status-bar').classList.add('hidden');
}

// ── LED modes ──────────────────────────────────────────────────────────────

function stopAllModes() {
  if (sequenceTimer) { clearInterval(sequenceTimer); sequenceTimer = null; }
  ledMode = null;
  updateModeButtons();
}

function updateModeButtons() {
  ['btn-mirror', 'btn-heatmap', 'btn-sequence'].forEach(id => {
    document.getElementById(id).classList.remove('mode-active');
  });
  if (ledMode === 'mirror')   document.getElementById('btn-mirror').classList.add('mode-active');
  if (ledMode === 'heatmap')  document.getElementById('btn-heatmap').classList.add('mode-active');
  if (ledMode === 'sequence') document.getElementById('btn-sequence').classList.add('mode-active');
}

// Mirror
document.getElementById('btn-mirror').addEventListener('click', async () => {
  if (!currentProblem) return;
  if (ledMode === 'mirror') {
    stopAllModes();
    await api('/api/light/off', { method: 'POST' }).catch(() => {});
    return;
  }
  stopAllModes();
  ledMode = 'mirror';
  updateModeButtons();
  const start = getMirrorHolds(currentProblem.startHolds || []);
  const prob  = getMirrorHolds(currentProblem.probHolds || []);
  const fin   = getMirrorHolds(currentProblem.finHolds || []);
  api('/api/light/custom', { method: 'POST', body: JSON.stringify({ start, prob, fin }) })
    .catch(() => {});
});

// Heatmap
document.getElementById('btn-heatmap').addEventListener('click', async () => {
  if (ledMode === 'heatmap') {
    stopAllModes();
    await api('/api/light/off', { method: 'POST' }).catch(() => {});
    return;
  }
  stopAllModes();
  ledMode = 'heatmap';
  updateModeButtons();
  api('/api/light/heatmap', { method: 'POST' }).catch(() => {});
});

// Sequence
document.getElementById('btn-sequence').addEventListener('click', () => {
  if (!currentProblem) return;
  if (ledMode === 'sequence') {
    stopAllModes();
    api('/api/light/off', { method: 'POST' }).catch(() => {});
    return;
  }
  stopAllModes();
  ledMode = 'sequence';
  sequenceStep = 0;
  updateModeButtons();
  sequenceTimer = setInterval(() => {
    const step = sequenceStep % 3;
    const start = step === 0 ? (currentProblem.startHolds || []) : [];
    const prob  = step === 1 ? (currentProblem.probHolds  || []) : [];
    const fin   = step === 2 ? (currentProblem.finHolds   || []) : [];
    api('/api/light/custom', { method: 'POST', body: JSON.stringify({ start, prob, fin }) })
      .catch(() => {});
    sequenceStep++;
  }, 250);
});


// ── Countdown timer ────────────────────────────────────────────────────────
document.getElementById('btn-timer-start').addEventListener('click', startTimer);
document.getElementById('btn-timer-stop').addEventListener('click', stopTimer);

function startTimer() {
  const minutes = parseInt(document.getElementById('timer-minutes').value) || 3;
  timerSecondsLeft = minutes * 60;
  document.getElementById('btn-timer-start').classList.add('hidden');
  document.getElementById('btn-timer-stop').classList.remove('hidden');
  updateTimerDisplay();
  if (timerInterval) clearInterval(timerInterval);
  timerInterval = setInterval(async () => {
    timerSecondsLeft--;
    updateTimerDisplay();
    if (timerSecondsLeft <= 0) {
      clearInterval(timerInterval);
      timerInterval = null;
      document.getElementById('btn-timer-start').classList.remove('hidden');
      document.getElementById('btn-timer-stop').classList.add('hidden');
      document.getElementById('timer-display').textContent = 'Time!';
      await flashCurrentProblem();
    }
  }, 1000);
}

function stopTimer() {
  if (timerInterval) { clearInterval(timerInterval); timerInterval = null; }
  document.getElementById('btn-timer-start').classList.remove('hidden');
  document.getElementById('btn-timer-stop').classList.add('hidden');
  document.getElementById('timer-display').textContent = '';
}

function updateTimerDisplay() {
  const m = Math.floor(timerSecondsLeft / 60);
  const s = timerSecondsLeft % 60;
  document.getElementById('timer-display').textContent =
    `${m}:${String(s).padStart(2, '0')}`;
}

async function flashCurrentProblem() {
  const holds = currentProblem
    ? { start: currentProblem.startHolds || [], prob: currentProblem.probHolds || [], fin: currentProblem.finHolds || [] }
    : { start: [], prob: [], fin: [] };

  for (let i = 0; i < 3; i++) {
    await api('/api/light/custom', { method: 'POST', body: JSON.stringify(holds) }).catch(() => {});
    await new Promise(r => setTimeout(r, 400));
    await api('/api/light/off', { method: 'POST' }).catch(() => {});
    await new Promise(r => setTimeout(r, 400));
  }
}

// ── Projects ───────────────────────────────────────────────────────────────
document.getElementById('btn-project').addEventListener('click', async () => {
  if (!currentProblem || !currentUser) return;
  try {
    const data = await api(
      `/api/projects/${encodeURIComponent(currentProblem.name)}`,
      { method: 'POST' }
    );
    currentProblem.is_project = data.is_project;
    updateDetailAuthButtons();
  } catch (e) {
    console.error('Project toggle failed', e);
  }
});

// ── Log climb ──────────────────────────────────────────────────────────────
document.getElementById('btn-log').addEventListener('click', () => {
  if (!currentUser || !currentProblem) return;
  openLogOverlay(currentProblem);
});

function openLogOverlay(prob) {
  document.getElementById('log-prob-name').textContent = prob.name;

  const gradeSelect = document.getElementById('log-grade');
  gradeSelect.innerHTML = '';
  (config.grades || []).forEach((g, i) => {
    const opt = new Option(g, g);
    if (i === prob.grade) opt.selected = true;
    gradeSelect.appendChild(opt);
  });

  const starsSelect = document.getElementById('log-stars');
  starsSelect.innerHTML = '';
  (config.stars || []).forEach(s => starsSelect.appendChild(new Option(s, s)));

  document.getElementById('log-comments').value = '';
  document.getElementById('log-error').classList.add('hidden');
  document.getElementById('log-overlay').classList.remove('hidden');
}

document.getElementById('btn-log-cancel').addEventListener('click', () => {
  document.getElementById('log-overlay').classList.add('hidden');
});

document.getElementById('btn-log-submit').addEventListener('click', submitLog);

async function submitLog() {
  const prob = currentProblem;
  const grade = document.getElementById('log-grade').value;
  const stars = document.getElementById('log-stars').value;
  const style = document.getElementById('log-style').value;
  const comments = document.getElementById('log-comments').value.trim();
  const errorEl = document.getElementById('log-error');
  try {
    await api('/api/log', {
      method: 'POST',
      body: JSON.stringify({ problem_name: prob.name, grade, stars, style, comments }),
    });
    document.getElementById('log-overlay').classList.add('hidden');
    loggedProblems.add(prob.name);
    renderProblemList(problems);
    openProblem(prob.row);
  } catch (e) {
    showError(errorEl, e.message || 'Failed to save log');
  }
}

// ── Panel navigation ───────────────────────────────────────────────────────
function showDetailPanel() {
  if (window.innerWidth < 768) {
    document.getElementById('list-panel').classList.add('hidden');
    document.getElementById('detail-panel').classList.remove('hidden');
  } else {
    document.getElementById('detail-panel').classList.remove('hidden');
  }
}

document.getElementById('btn-back').addEventListener('click', () => {
  document.getElementById('detail-panel').classList.add('hidden');
  document.getElementById('list-panel').classList.remove('hidden');
  stopAllModes();
  stopTimer();
  currentProblem = null;
});

document.getElementById('btn-prev').addEventListener('click', () => {
  if (!currentProblem) return;
  const idx = problems.findIndex(p => p.row === currentProblem.row);
  if (idx > 0) openProblem(problems[idx - 1].row);
});

document.getElementById('btn-next').addEventListener('click', () => {
  if (!currentProblem) return;
  const idx = problems.findIndex(p => p.row === currentProblem.row);
  if (idx !== -1 && idx < problems.length - 1) openProblem(problems[idx + 1].row);
});

// ── Logbook ────────────────────────────────────────────────────────────────
async function loadLogbook() {
  const content = document.getElementById('logbook-content');
  if (!currentUser) {
    content.innerHTML = '<p class="muted-msg">Log in to view your logbook.</p>';
    return;
  }
  content.innerHTML = '<p class="muted-msg">Loading…</p>';
  try {
    const entries = await api('/api/logbook');
    if (!entries.length) {
      content.innerHTML = '<p class="muted-msg">No climbs logged yet.</p>';
      return;
    }
    const table = document.createElement('table');
    table.className = 'data-table';
    table.innerHTML = `
      <thead><tr>
        <th>Problem</th><th>Grade</th><th>Stars</th><th>Style</th><th>Date</th><th>Comments</th>
      </tr></thead>
    `;
    const tbody = document.createElement('tbody');
    entries.forEach(e => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${escHtml(e.problem)}</td>
        <td>${escHtml(e.grade)}</td>
        <td>${escHtml(e.stars)}</td>
        <td>${escHtml(e.style)}</td>
        <td>${escHtml(e.date)}</td>
        <td>${escHtml(e.comments)}</td>
      `;
      tbody.appendChild(tr);
    });
    table.appendChild(tbody);
    content.innerHTML = '';
    content.appendChild(table);
  } catch (e) {
    content.innerHTML = `<p class="error-inline">${escHtml(e.message)}</p>`;
  }
}

// ── Admin ──────────────────────────────────────────────────────────────────
document.getElementById('admin-tab-users').addEventListener('click', () => switchAdminTab('users'));
document.getElementById('admin-tab-logs').addEventListener('click', () => switchAdminTab('logs'));
document.getElementById('admin-tab-problems').addEventListener('click', () => switchAdminTab('problems'));
document.getElementById('admin-tab-config').addEventListener('click', () => switchAdminTab('config'));

function switchAdminTab(name) {
  currentAdminTab = name;
  ['users', 'logs', 'problems', 'config'].forEach(t => {
    document.getElementById(`admin-tab-${t}`).classList.toggle('active', t === name);
    document.getElementById(`admin-panel-${t}`).classList.toggle('hidden', t !== name);
  });
  loadAdminTab(name);
}

function loadAdminTab(name) {
  if (name === 'users') loadAdminUsers();
  else if (name === 'logs') loadAdminLogs();
  else if (name === 'problems') loadAdminProblems();
  else if (name === 'config') loadAdminConfig();
}

async function loadAdminUsers() {
  const content = document.getElementById('admin-users-content');
  content.innerHTML = '<p class="muted-msg">Loading…</p>';
  try {
    const users = await api('/api/admin/users');
    if (!users.length) { content.innerHTML = '<p class="muted-msg">No users found.</p>'; return; }
    const table = document.createElement('table');
    table.className = 'data-table';
    table.innerHTML = `<thead><tr>
      <th>Username</th><th>Name</th><th>Email</th><th>Joined</th><th></th>
    </tr></thead>`;
    const tbody = document.createElement('tbody');
    users.forEach(u => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${escHtml(u.username)}</td>
        <td>${escHtml(u.name)}</td>
        <td>${escHtml(u.email)}</td>
        <td>${escHtml(u.date)}</td>
        <td><button class="btn-danger btn-small" data-user="${escHtml(u.username)}">Delete</button></td>
      `;
      tbody.appendChild(tr);
    });
    table.appendChild(tbody);
    content.innerHTML = '';
    content.appendChild(table);
    content.querySelectorAll('.btn-danger[data-user]').forEach(btn => {
      btn.addEventListener('click', async () => {
        const uname = btn.dataset.user;
        if (!confirm(`Delete user "${uname}"?`)) return;
        try {
          await api(`/api/admin/users/${encodeURIComponent(uname)}`, { method: 'DELETE' });
          loadAdminUsers();
        } catch (e) { alert('Delete failed: ' + e.message); }
      });
    });
  } catch (e) {
    content.innerHTML = `<p class="error-inline">${escHtml(e.message)}</p>`;
  }
}

async function loadAdminLogs() {
  const content = document.getElementById('admin-logs-content');
  content.innerHTML = '<p class="muted-msg">Loading…</p>';
  try {
    const logs = await api('/api/admin/logs');
    if (!logs.length) { content.innerHTML = '<p class="muted-msg">No log entries.</p>'; return; }
    const table = document.createElement('table');
    table.className = 'data-table';
    table.innerHTML = `<thead><tr>
      <th>User</th><th>Problem</th><th>Grade</th><th>Stars</th><th>Style</th><th>Date</th><th>Comments</th><th></th>
    </tr></thead>`;
    const tbody = document.createElement('tbody');
    logs.forEach(entry => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${escHtml(entry.username)}</td>
        <td>${escHtml(entry.problem)}</td>
        <td>${escHtml(entry.grade)}</td>
        <td>${escHtml(entry.stars)}</td>
        <td>${escHtml(entry.style)}</td>
        <td>${escHtml(entry.date)}</td>
        <td>${escHtml(entry.comments)}</td>
        <td><button class="btn-danger btn-small" data-idx="${entry.idx}">Delete</button></td>
      `;
      tbody.appendChild(tr);
    });
    table.appendChild(tbody);
    content.innerHTML = '';
    content.appendChild(table);
    content.querySelectorAll('.btn-danger[data-idx]').forEach(btn => {
      btn.addEventListener('click', async () => {
        if (!confirm('Delete this log entry?')) return;
        try {
          await api(`/api/admin/logs/${btn.dataset.idx}`, { method: 'DELETE' });
          loadAdminLogs();
        } catch (e) { alert('Delete failed: ' + e.message); }
      });
    });
  } catch (e) {
    content.innerHTML = `<p class="error-inline">${escHtml(e.message)}</p>`;
  }
}

async function loadAdminProblems() {
  // Populate grade/stars/footholdset dropdowns
  const gradeSelect = document.getElementById('admin-prob-grade');
  gradeSelect.innerHTML = '';
  (config.grades || []).forEach(g => gradeSelect.appendChild(new Option(g, g)));

  const starsSelect = document.getElementById('admin-prob-stars');
  starsSelect.innerHTML = '';
  (config.stars || []).forEach(s => starsSelect.appendChild(new Option(s, s)));

  const fsSelect = document.getElementById('admin-prob-footholdset');
  fsSelect.innerHTML = '';
  (config.footholdsets || ['Standard']).forEach(f => fsSelect.appendChild(new Option(f, f)));

  // Load problems into dropdown
  const probSelect = document.getElementById('admin-prob-select');
  probSelect.innerHTML = '<option value="">Select problem to edit…</option>';
  try {
    adminProblems = await api('/api/problems');
    adminProblems.forEach(p => {
      probSelect.appendChild(new Option(`${p.name} (${p.grade_label})`, p.row));
    });
  } catch (e) {
    console.error('Failed to load problems for admin', e);
  }

  document.getElementById('admin-prob-fields').classList.add('hidden');
}

document.getElementById('admin-prob-select').addEventListener('change', async function () {
  const row = parseInt(this.value);
  if (isNaN(row)) { document.getElementById('admin-prob-fields').classList.add('hidden'); return; }
  try {
    const prob = await api(`/api/problems/${row}`);
    document.getElementById('admin-prob-name').value = prob.name;
    document.getElementById('admin-prob-grade').value = prob.grade_label;
    document.getElementById('admin-prob-stars').value = prob.stars_label !== '-' ? prob.stars_label : '-';
    document.getElementById('admin-prob-footholdset').value = prob.footholdset || (config.footholdsets || ['Standard'])[0];
    document.getElementById('admin-prob-notes').value = prob.notes || '';
    document.getElementById('admin-prob-error').classList.add('hidden');
    document.getElementById('admin-prob-fields').classList.remove('hidden');
  } catch (e) {
    console.error('Failed to load problem for edit', e);
  }
});

document.getElementById('btn-admin-prob-save').addEventListener('click', async () => {
  const row = parseInt(document.getElementById('admin-prob-select').value);
  if (isNaN(row)) return;
  const errorEl = document.getElementById('admin-prob-error');
  const body = {
    name: document.getElementById('admin-prob-name').value.trim(),
    grade: document.getElementById('admin-prob-grade').value,
    stars: document.getElementById('admin-prob-stars').value,
    footholdset: document.getElementById('admin-prob-footholdset').value,
    notes: document.getElementById('admin-prob-notes').value.trim(),
  };
  try {
    await api(`/api/admin/problems/${row}`, { method: 'PATCH', body: JSON.stringify(body) });
    errorEl.classList.add('hidden');
    // Refresh dropdown label
    loadAdminProblems();
    loadProblems();
  } catch (e) {
    showError(errorEl, e.message || 'Save failed');
  }
});

async function loadAdminConfig() {
  try {
    const cfg = await api('/api/admin/config');
    document.getElementById('cfg-ADMIN').value = cfg.ADMIN || '';
    document.getElementById('cfg-THEMECOLOUR').value = cfg.THEMECOLOUR || '';
    document.getElementById('cfg-DEFAULTMSG').value = cfg.DEFAULTMSG || '';
    document.getElementById('cfg-LEDBRIGHTNESS').value = cfg.LEDBRIGHTNESS ?? '';
    document.getElementById('cfg-TOTALLEDCOUNT').value = cfg.TOTALLEDCOUNT ?? '';
    document.getElementById('cfg-LOGOUTTIMEOUT').value = cfg.LOGOUTTIMEOUT ?? '';
    document.getElementById('cfg-LINUX').value = cfg.LINUX ?? '';
    document.getElementById('cfg-GRADES').value = (cfg.GRADES || []).join('\n');
    document.getElementById('cfg-STARS').value = (cfg.STARS || []).join('\n');
    document.getElementById('cfg-TAGS').value = (cfg.TAGS || []).join('\n');
    document.getElementById('cfg-FOOTHOLDSETS').value = (cfg.FOOTHOLDSETS || []).join('\n');
    document.getElementById('cfg-USERSPATH').value = cfg.USERSPATH || '';
    document.getElementById('cfg-LOGPATH').value = cfg.LOGPATH || '';
    document.getElementById('cfg-PROBPATH').value = cfg.PROBPATH || '';
    document.getElementById('cfg-PROJECTSPATH').value = cfg.PROJECTSPATH || '';
    document.getElementById('cfg-BOARDNAME').value = cfg.BOARDNAME || '';
    document.getElementById('cfg-IMAGEPATH').value = cfg.IMAGEPATH || '';
  } catch (e) {
    document.getElementById('admin-config-error').textContent = e.message;
    document.getElementById('admin-config-error').classList.remove('hidden');
  }
}

document.getElementById('btn-admin-config-save').addEventListener('click', async () => {
  const errorEl = document.getElementById('admin-config-error');
  const okEl = document.getElementById('admin-config-ok');
  errorEl.classList.add('hidden');
  okEl.classList.add('hidden');

  const parseList = txt => txt.split('\n').map(s => s.trim()).filter(s => s.length > 0);

  const body = {
    ADMIN: document.getElementById('cfg-ADMIN').value.trim(),
    THEMECOLOUR: document.getElementById('cfg-THEMECOLOUR').value.trim(),
    DEFAULTMSG: document.getElementById('cfg-DEFAULTMSG').value.trim(),
    LEDBRIGHTNESS: parseInt(document.getElementById('cfg-LEDBRIGHTNESS').value) || 50,
    TOTALLEDCOUNT: parseInt(document.getElementById('cfg-TOTALLEDCOUNT').value) || 0,
    LOGOUTTIMEOUT: parseInt(document.getElementById('cfg-LOGOUTTIMEOUT').value) || 1800,
    LINUX: parseInt(document.getElementById('cfg-LINUX').value) || 0,
    GRADES: parseList(document.getElementById('cfg-GRADES').value),
    STARS: parseList(document.getElementById('cfg-STARS').value),
    TAGS: parseList(document.getElementById('cfg-TAGS').value),
    FOOTHOLDSETS: parseList(document.getElementById('cfg-FOOTHOLDSETS').value),
    USERSPATH: document.getElementById('cfg-USERSPATH').value.trim(),
    LOGPATH: document.getElementById('cfg-LOGPATH').value.trim(),
    PROBPATH: document.getElementById('cfg-PROBPATH').value.trim(),
    PROJECTSPATH: document.getElementById('cfg-PROJECTSPATH').value.trim(),
    BOARDNAME: document.getElementById('cfg-BOARDNAME').value.trim(),
    IMAGEPATH: document.getElementById('cfg-IMAGEPATH').value.trim(),
  };

  try {
    await api('/api/admin/config', { method: 'POST', body: JSON.stringify(body) });
    okEl.classList.remove('hidden');
    setTimeout(() => okEl.classList.add('hidden'), 3000);
  } catch (e) {
    showError(errorEl, e.message || 'Save failed');
  }
});

// ── Utilities ──────────────────────────────────────────────────────────────
function escHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function showError(el, msg) {
  el.textContent = msg;
  el.classList.remove('hidden');
}

// ── Start ──────────────────────────────────────────────────────────────────
init();
