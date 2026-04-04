'use strict';

// ── State ──────────────────────────────────────────────────────────────────
let config = {};            // grades, stars, tags, theme_colour
let boardData = null;       // { holds, image_url, img_width, img_height }
let currentProblem = null;  // full detail object
let currentUser = null;     // logged-in username or null
let problems = [];          // current filtered list
let selectedTags = new Set();

// ── Init ───────────────────────────────────────────────────────────────────
async function init() {
  await Promise.all([loadConfig(), loadBoard(), checkLogin()]);
  loadUsers();
  buildGradeSliders();
  buildTagChips();
  loadProblems();

  // Apply theme colour from server config
  if (config.theme_colour) {
    document.getElementById('app-header').style.background = config.theme_colour;
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
  if (currentUser) {
    usernameEl.textContent = currentUser;
    usernameEl.classList.remove('hidden');
    logoutBtn.classList.remove('hidden');
    loginBtn.classList.add('hidden');
  } else {
    usernameEl.classList.add('hidden');
    logoutBtn.classList.add('hidden');
    loginBtn.classList.remove('hidden');
  }
  // Show/hide auth-dependent buttons on detail panel
  if (currentProblem) {
    updateDetailAuthButtons();
  }
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
  if (!username) {
    showError(errorEl, 'Please select a username');
    return;
  }
  try {
    await api('/api/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });
    currentUser = username;
    updateAuthBar();
    document.getElementById('login-overlay').classList.add('hidden');
  } catch (e) {
    showError(errorEl, e.message || 'Login failed');
  }
}

document.getElementById('btn-logout').addEventListener('click', async () => {
  await api('/api/logout', { method: 'POST' });
  currentUser = null;
  updateAuthBar();
});

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
      if (cb.checked) {
        selectedTags.add(tag);
        chip.classList.add('active');
      } else {
        selectedTags.delete(tag);
        chip.classList.remove('active');
      }
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
    li.innerHTML = `
      <span class="prob-list-name">${escHtml(prob.name)}</span>
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
    showDetailPanel();
  } catch (e) {
    console.error('Failed to load problem', e);
  }
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
}

function updateDetailAuthButtons() {
  const projectBtn = document.getElementById('btn-project');
  const logBtn = document.getElementById('btn-log');
  if (currentUser) {
    projectBtn.classList.remove('hidden');
    logBtn.classList.remove('hidden');
    // Update project button state
    if (currentProblem) {
      projectBtn.textContent = currentProblem.is_project ? '★ Remove project' : '☆ Add project';
    }
  } else {
    projectBtn.classList.add('hidden');
    logBtn.classList.add('hidden');
  }
}

// ── Board overlay ──────────────────────────────────────────────────────────
function renderOverlay(prob) {
  // Remove existing markers
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
    } else if (hold.x_px != null && boardData.img_width) {
      // Fallback: raw pixels when Pillow unavailable
      marker.style.left = (hold.x_px / boardData.img_width * 100) + '%';
      marker.style.top  = (hold.y_px / boardData.img_height * 100) + '%';
    }

    container.appendChild(marker);
  });
}

// ── LED controls ───────────────────────────────────────────────────────────
document.getElementById('btn-light').addEventListener('click', async () => {
  if (!currentProblem) return;
  const btn = document.getElementById('btn-light');
  btn.disabled = true;
  try {
    await api(`/api/light/${currentProblem.row}`, { method: 'POST' });
    hideLedStatus();
  } catch (e) {
    if (e.status === 409) {
      showLedStatus(e.message);
    } else {
      showLedStatus('LED control failed: ' + e.message);
    }
  } finally {
    btn.disabled = false;
  }
});

document.getElementById('btn-off').addEventListener('click', async () => {
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

  // Populate grade select with problem's grade pre-selected
  const gradeSelect = document.getElementById('log-grade');
  gradeSelect.innerHTML = '';
  (config.grades || []).forEach((g, i) => {
    const opt = new Option(g, g);
    if (i === prob.grade) opt.selected = true;
    gradeSelect.appendChild(opt);
  });

  // Populate stars select
  const starsSelect = document.getElementById('log-stars');
  starsSelect.innerHTML = '';
  (config.stars || []).forEach(s => {
    starsSelect.appendChild(new Option(s, s));
  });

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
      body: JSON.stringify({
        problem_name: prob.name,
        grade,
        stars,
        style,
        comments,
      }),
    });
    document.getElementById('log-overlay').classList.add('hidden');
    // Refresh problem detail to update ascent count
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
  currentProblem = null;
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
