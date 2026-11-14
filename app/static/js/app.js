// ============================================================================
// Translations & Localization Dictionary
// ============================================================================
const I18N = {
  en: {
    badge: "Microservices",
    subtitle: "ಕಾಯಕಸೇತು • श्रमसेतु — Connecting Workers & Employers with Smart Matching, Fair Wage & Regional Voice IVR",
    navJobs: "Job Feed",
    navWorkers: "Workers Feed",
    navMatching: "Smart Matcher",
    navWage: "Fair Wage Predictor",
    navPostJob: "Post Work (Employer)",
    navRegWorker: "Worker Registration",
    navPhone: "IVR Voice Simulator",
    statWorkers: "Registered Workers:",
    statJobs: "Open Jobs:",
    statContacts: "Active Inquiries:",
    statLocation: "Supported Hubs:",
    jobFeedTitle: "Live Job Opportunities for Workers",
    jobFeedSubtitle: "Browse verified work posted by households, shops, and contractors nearby.",
    workerFeedTitle: "Available Workers Feed for Employers",
    workerFeedSubtitle: "Hire skilled tradespeople with verified ratings, rates, and locations."
  },
  kn: {
    badge: "ಮೈಕ್ರೋಸರ್ವೀಸಸ್",
    subtitle: "ಕಾಯಕಸೇತು — ಕಾರ್ಮಿಕರು ಮತ್ತು ಉದ್ಯೋಗದಾತರನ್ನು ಬೆಸೆಯುವ ಸ್ಮಾರ್ಟ್ ಪ್ಲಾಟ್‌ಫಾರ್ಮ್ (ಕನ್ನಡ & ಹಿಂದಿ ಧ್ವನಿ IVR ಸೇರಿದಂತೆ)",
    navJobs: "ಕೆಲಸಗಳ ಫೀಡ್",
    navWorkers: "ಕಾರ್ಮಿಕರ ಪಟ್ಟಿ",
    navMatching: "ಸ್ಮಾರ್ಟ್ ಮ್ಯಾಚಿಂಗ್",
    navWage: "ನ್ಯಾಯಯುತ ದಿನಗೂಲಿ",
    navPostJob: "ಕೆಲಸ ಪ್ರಕಟಿಸಿ (ಉದ್ಯೋಗದಾತ)",
    navRegWorker: "ಕಾರ್ಮಿಕರ ನೋಂದಣಿ",
    navPhone: "ಧ್ವನಿ ಕರೆ ಸಿಮ್ಯುಲೇಟರ್ (IVR)",
    statWorkers: "ನೋಂದಾಯಿತ ಕಾರ್ಮಿಕರು:",
    statJobs: "ಲಭ್ಯವಿರುವ ಕೆಲಸಗಳು:",
    statContacts: "ಸಂಪರ್ಕಗಳು:",
    statLocation: "ಪ್ರಮುಖ ನಗರಗಳು:",
    jobFeedTitle: "ಕಾರ್ಮಿಕರಿಗಾಗಿ ಲಭ್ಯವಿರುವ ಪ್ರಸ್ತುತ ಕೆಲಸಗಳು",
    jobFeedSubtitle: "ನಿಮ್ಮ ಸಮೀಪದ ಉದ್ಯೋಗದಾತರು ಮತ್ತು ಗುತ್ತಿಗೆದಾರರು ಪ್ರಕಟಿಸಿದ ಕೆಲಸಗಳು.",
    workerFeedTitle: "ಉದ್ಯೋಗದಾತರಿಗಾಗಿ ಲಭ್ಯವಿರುವ ಕೌಶಲ್ಯಯುತ ಕಾರ್ಮಿಕರು",
    workerFeedSubtitle: "ಮೇಸ್ತ್ರಿ, ಎಲೆಕ್ಟ್ರಿಷಿಯನ್, ಪ್ಲಂಬರ್ ಮುಂತಾದ ಪರಿಣಿತರನ್ನು ನೇರವಾಗಿ ಸಂಪರ್ಕಿಸಿ."
  },
  hi: {
    badge: "माइक्रोसर्विसेज",
    subtitle: "श्रमसेतु — कामगारों और नियोक्ताओं को जोड़ने वाला स्मार्ट मंच (कन्नड़ और हिंदी वॉयस IVR सहित)",
    navJobs: "काम की सूची",
    navWorkers: "कामगारों की सूची",
    navMatching: "स्मार्ट मैचिंग",
    navWage: "उचित मजदूरी कैलकुलेटर",
    navPostJob: "काम पोस्ट करें (नियोक्ता)",
    navRegWorker: "श्रमिक पंजीकरण",
    navPhone: "वॉयस कॉल सिमुलेटर (IVR)",
    statWorkers: "पंजीकृत कामगार:",
    statJobs: "उपलब्ध काम:",
    statContacts: "संपर्क अनुरोध:",
    statLocation: "सक्रिय शहर:",
    jobFeedTitle: "कामगारों के लिए उपलब्ध काम",
    jobFeedSubtitle: "अपने आस-पास के ठेकेदारों और घरों द्वारा पोस्ट किए गए काम देखें।",
    workerFeedTitle: "नियोक्ताओं के लिए उपलब्ध कुशल श्रमिक",
    workerFeedSubtitle: "प्लंबर, इलेक्ट्रीशियन, राजमिस्त्री आदि को सीधे संपर्क करें।"
  }
};

let currentLang = "en";
let activeContactTarget = null;

// Authentication State
let currentUser = null;
let authToken = localStorage.getItem("kaayaka_auth_token") || null;

// IVR Telecom Call State
let telecomSessionId = "CALL_" + Math.floor(Math.random() * 100000);
let isIvrCallActive = false;
let lastIvrAudioText = "";

// ============================================================================
// Initialization
// ============================================================================
document.addEventListener("DOMContentLoaded", async () => {
  await initAuth();
  updatePhoneClock();
  setInterval(updatePhoneClock, 30000);
});

// ============================================================================
// Authentication & Role-Based UI Filtering
// ============================================================================
async function initAuth() {
  authToken = localStorage.getItem("kaayaka_auth_token") || null;
  if (!authToken) {
    showAuthScreen();
    return;
  }
  try {
    const res = await fetch("/api/v1/auth/me", {
      headers: { "Authorization": `Bearer ${authToken}` }
    });
    if (res.ok) {
      currentUser = await res.json();
      openMainDashboard();
    } else {
      authToken = null;
      currentUser = null;
      localStorage.removeItem("kaayaka_auth_token");
      showAuthScreen();
    }
  } catch (e) {
    console.warn("Auth check failed:", e);
    showAuthScreen();
  }
}

function showAuthScreen() {
  const authScreen = document.getElementById("auth-screen");
  const mainApp = document.getElementById("main-app-screen");
  if (authScreen) authScreen.style.display = "flex";
  if (mainApp) mainApp.style.display = "none";
  showAuthTab('signin');
}

function openMainDashboard() {
  if (!currentUser) {
    showAuthScreen();
    return;
  }

  const authScreen = document.getElementById("auth-screen");
  const mainApp = document.getElementById("main-app-screen");
  if (authScreen) authScreen.style.display = "none";
  if (mainApp) mainApp.style.display = "block";

  // Update User Profile Badge in top header
  const userBadge = document.getElementById("auth-user-badge");
  const isWorker = currentUser.role === "worker";
  const roleColor = isWorker ? "#15803d" : "#0284c7";
  const roleBg = isWorker ? "#dcfce7" : "#e0f2fe";
  const roleEmoji = isWorker ? "👷" : "🏢";
  const roleLabel = isWorker ? "WORKER" : "EMPLOYER";
  const displayName = isWorker 
    ? `${currentUser.full_name} (${currentUser.trade || 'Worker'})`
    : (currentUser.company_name || currentUser.full_name);

  if (userBadge) {
    userBadge.innerHTML = `
      <div style="display:flex; align-items:center; gap:0.45rem; background:${roleBg}; padding:0.25rem 0.75rem; border-radius:999px; border:1px solid ${roleColor}40;">
        <span style="font-size:0.75rem; font-weight:800; color:${roleColor};">${roleEmoji} ${roleLabel}</span>
        <span style="font-size:0.82rem; font-weight:700; color:#1e293b; max-width:200px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">
          ${displayName}
        </span>
      </div>
    `;
  }

  // Enforce Strict Role Separation
  const navBtnJobs = document.getElementById("nav-btn-jobs");
  const navBtnWorkers = document.getElementById("nav-btn-workers");
  const navBtnMatching = document.getElementById("nav-btn-matching");
  const navBtnWage = document.getElementById("nav-btn-wage");
  const navBtnPostJob = document.getElementById("nav-btn-post-job");
  const navBtnPhone = document.getElementById("nav-btn-phone-simulator");
  const navBtnChat = document.getElementById("nav-btn-chat");

  const tabJobs = document.getElementById("tab-jobs");
  const tabWorkers = document.getElementById("tab-workers");
  const tabMatching = document.getElementById("tab-matching");
  const tabWage = document.getElementById("tab-wage");
  const tabPostJob = document.getElementById("tab-post-job");
  const tabPhone = document.getElementById("tab-phone-simulator");
  const tabChat = document.getElementById("tab-chat");
  const matchScopeBadge = document.getElementById("match-scope-badge");

  // Common Messages Tab is visible to both Worker and Employer
  if (navBtnChat) navBtnChat.style.display = "inline-flex";

  if (isWorker) {
    // -----------------------------------------------------------------
    // WORKER PROFILE:
    // MUST NOT SEE: Workers Feed, Post Work Service
    // -----------------------------------------------------------------
    if (navBtnWorkers) navBtnWorkers.style.display = "none";
    if (tabWorkers) tabWorkers.style.display = "none";
    if (navBtnPostJob) navBtnPostJob.style.display = "none";
    if (tabPostJob) tabPostJob.style.display = "none";

    // MUST SEE: Job Feed, Smart Matcher, Fair Wage, IVR Simulator
    if (navBtnJobs) navBtnJobs.style.display = "inline-flex";
    if (tabJobs) tabJobs.style.display = "block";
    if (navBtnMatching) navBtnMatching.style.display = "inline-flex";
    if (navBtnWage) navBtnWage.style.display = "inline-flex";
    if (navBtnPhone) navBtnPhone.style.display = "inline-flex";

    if (matchScopeBadge) {
      matchScopeBadge.innerText = `🔒 Scoped to ${currentUser.full_name} (${currentUser.trade})`;
      matchScopeBadge.style.background = "#dcfce7";
      matchScopeBadge.style.color = "#15803d";
    }

    const callerIdInput = document.getElementById("phone-caller-id");
    if (callerIdInput && currentUser.phone) {
      callerIdInput.value = currentUser.phone;
    }

    // Default to Job Feed
    switchTab("tab-jobs", navBtnJobs);
    loadJobFeed();
  } else {
    // -----------------------------------------------------------------
    // EMPLOYER PROFILE:
    // MUST NOT SEE: Worker Registration, Job Feed, IVR Service
    // -----------------------------------------------------------------
    if (navBtnJobs) navBtnJobs.style.display = "none";
    if (tabJobs) tabJobs.style.display = "none";
    if (navBtnPhone) navBtnPhone.style.display = "none";
    if (tabPhone) tabPhone.style.display = "none";

    // MUST SEE: Workers Feed, Post Work, Smart Matcher, Fair Wage
    if (navBtnWorkers) navBtnWorkers.style.display = "inline-flex";
    if (tabWorkers) tabWorkers.style.display = "block";
    if (navBtnPostJob) navBtnPostJob.style.display = "inline-flex";
    if (navBtnMatching) navBtnMatching.style.display = "inline-flex";
    if (navBtnWage) navBtnWage.style.display = "inline-flex";

    if (matchScopeBadge) {
      matchScopeBadge.innerText = `🔒 Scoped to ${displayName}'s Open Jobs`;
      matchScopeBadge.style.background = "#e0f2fe";
      matchScopeBadge.style.color = "#0369a1";
    }

    // Pre-fill employer contact in Post Work form
    const phoneInput = document.getElementById("job-employer-phone");
    const nameInput = document.getElementById("job-employer-name");
    if (phoneInput && currentUser.phone) phoneInput.value = currentUser.phone;
    if (nameInput) nameInput.value = displayName;

    // Default to Workers Feed
    switchTab("tab-workers", navBtnWorkers);
    loadWorkerFeed();
  }

  loadInsights();
  populateMatchingDropdowns();
  loadConversations();
  initChatWebSocket();
}

function showAuthTab(tab) {
  const btnSignin = document.getElementById("tab-btn-signin");
  const btnWorker = document.getElementById("tab-btn-worker");
  const btnEmployer = document.getElementById("tab-btn-employer");

  const secSignin = document.getElementById("section-signin");
  const secWorker = document.getElementById("section-worker");
  const secEmployer = document.getElementById("section-employer");
  const title = document.getElementById("auth-box-title");
  const alertBox = document.getElementById("auth-screen-alert");

  if (alertBox) alertBox.style.display = "none";

  [btnSignin, btnWorker, btnEmployer].forEach(b => { if (b) b.classList.remove("active"); });
  [secSignin, secWorker, secEmployer].forEach(s => { if (s) s.style.display = "none"; });

  if (tab === "signin") {
    if (btnSignin) btnSignin.classList.add("active");
    if (secSignin) secSignin.style.display = "block";
    if (title) title.innerText = "Sign In to Your Workspace";
  } else if (tab === "worker") {
    if (btnWorker) btnWorker.classList.add("active");
    if (secWorker) secWorker.style.display = "block";
    if (title) title.innerText = "Register as Blue-Collar Worker";
  } else if (tab === "employer") {
    if (btnEmployer) btnEmployer.classList.add("active");
    if (secEmployer) secEmployer.style.display = "block";
    if (title) title.innerText = "Register as Employer / Contractor";
  }
}

function showAuthAlert(msg, isError = false) {
  const box = document.getElementById("auth-screen-alert");
  if (!box) return;
  box.style.display = "block";
  box.style.background = isError ? "#fee2e2" : "#dcfce7";
  box.style.color = isError ? "#991b1b" : "#166534";
  box.style.border = `1px solid ${isError ? '#f87171' : '#86efac'}`;
  box.innerText = msg;
}

async function handleSignIn(e) {
  e.preventDefault();
  const ident = document.getElementById("si-identifier").value.trim();
  const pass = document.getElementById("si-password").value;

  try {
    const res = await fetch("/api/v1/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username_or_phone: ident, password: pass })
    });
    const data = await res.json();
    if (!res.ok) {
      showAuthAlert(data.detail || "Invalid login credentials. Please check username and password.", true);
      return;
    }

    authToken = data.token;
    currentUser = data.user;
    localStorage.setItem("kaayaka_auth_token", authToken);
    showAuthAlert(`Signed in successfully as ${currentUser.full_name} (${currentUser.role.toUpperCase()})! Opening dashboard...`, false);
    setTimeout(() => {
      openMainDashboard();
    }, 350);
  } catch (err) {
    showAuthAlert("Network error while connecting to auth server.", true);
  }
}

async function directDemoLogin(username, password) {
  try {
    const res = await fetch("/api/v1/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username_or_phone: username, password: password })
    });
    const data = await res.json();
    if (res.ok) {
      authToken = data.token;
      currentUser = data.user;
      localStorage.setItem("kaayaka_auth_token", authToken);
      showAuthAlert(`Welcome ${currentUser.full_name}! Opening ${currentUser.role.toUpperCase()} workspace...`, false);
      setTimeout(() => {
        openMainDashboard();
      }, 300);
    } else {
      showAuthAlert(data.detail || "Demo login failed", true);
    }
  } catch (e) {
    showAuthAlert("Error signing in with demo account", true);
  }
}

async function handleRegister(e, role) {
  e.preventDefault();
  let payload = { role: role };

  if (role === "worker") {
    payload.full_name = document.getElementById("reg-w-name").value.trim();
    payload.phone = document.getElementById("reg-w-phone").value.trim();
    payload.username = document.getElementById("reg-w-user").value.trim();
    payload.password = document.getElementById("reg-w-pass").value;
    payload.trade = document.getElementById("reg-w-trade").value;
    payload.daily_rate = parseFloat(document.getElementById("reg-w-rate").value) || 850;
    payload.experience_years = parseInt(document.getElementById("reg-w-exp").value) || 3;
    payload.city = document.getElementById("reg-w-city").value;
  } else {
    payload.full_name = document.getElementById("reg-e-name").value.trim();
    payload.company_name = document.getElementById("reg-e-comp").value.trim() || payload.full_name;
    payload.phone = document.getElementById("reg-e-phone").value.trim();
    payload.username = document.getElementById("reg-e-user").value.trim();
    payload.password = document.getElementById("reg-e-pass").value;
    payload.city = document.getElementById("reg-e-city").value;
  }

  try {
    const res = await fetch("/api/v1/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (!res.ok) {
      showAuthAlert(data.detail || "Registration failed.", true);
      return;
    }

    authToken = data.token;
    currentUser = data.user;
    localStorage.setItem("kaayaka_auth_token", authToken);
    showAuthAlert(`Account created successfully as ${role.toUpperCase()}! Opening dashboard...`, false);
    setTimeout(() => {
      openMainDashboard();
    }, 350);
  } catch (e) {
    showAuthAlert("Network error while registering account.", true);
  }
}

function handleLogout() {
  if (chatSocket) {
    try { chatSocket.close(); } catch (e) {}
    chatSocket = null;
  }
  if (authToken) {
    fetch("/api/v1/auth/logout", {
      method: "POST",
      headers: { "Authorization": `Bearer ${authToken}` }
    });
  }
  authToken = null;
  currentUser = null;
  localStorage.removeItem("kaayaka_auth_token");
  showAuthScreen();
}

function changeLanguage(lang) {
  currentLang = lang;
  const t = I18N[lang] || I18N.en;

  const badgeEl = document.getElementById("lbl-badge"); if (badgeEl) badgeEl.innerText = t.badge;
  const subEl = document.getElementById("lbl-subtitle"); if (subEl) subEl.innerText = t.subtitle;
  const nj = document.getElementById("nav-jobs"); if (nj) nj.innerText = t.navJobs;
  const nw = document.getElementById("nav-workers"); if (nw) nw.innerText = t.navWorkers;
  const nm = document.getElementById("nav-matching"); if (nm) nm.innerText = t.navMatching;
  const nwg = document.getElementById("nav-wage"); if (nwg) nwg.innerText = t.navWage;
  const np = document.getElementById("nav-post-job"); if (np) np.innerText = t.navPostJob;
  const nph = document.getElementById("nav-phone"); if (nph) nph.innerText = t.navPhone;
  const sw = document.getElementById("lbl-stat-workers"); if (sw) sw.innerText = t.statWorkers;
  const sj = document.getElementById("lbl-stat-jobs"); if (sj) sj.innerText = t.statJobs;
  const sc = document.getElementById("lbl-stat-contacts"); if (sc) sc.innerText = t.statContacts;
  const sl = document.getElementById("lbl-stat-location"); if (sl) sl.innerText = t.statLocation;
  const jt = document.getElementById("job-feed-title"); if (jt) jt.innerText = t.jobFeedTitle;
  const js = document.getElementById("job-feed-subtitle"); if (js) js.innerText = t.jobFeedSubtitle;
  const wt = document.getElementById("worker-feed-title"); if (wt) wt.innerText = t.workerFeedTitle;
  const ws = document.getElementById("worker-feed-subtitle"); if (ws) ws.innerText = t.workerFeedSubtitle;
}

function switchTab(tabId, btn) {
  // Guard role permissions: prevent worker from switching to employer tabs and vice-versa
  if (currentUser) {
    if (currentUser.role === "worker") {
      if (tabId === "tab-workers" || tabId === "tab-post-job" || tabId === "tab-register-worker") return;
    } else if (currentUser.role === "employer") {
      if (tabId === "tab-jobs" || tabId === "tab-register-worker" || tabId === "tab-phone-simulator") return;
    }
  }

  document.querySelectorAll(".tab-pane").forEach(p => {
    p.classList.remove("active");
    p.style.display = "none";
  });
  document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));

  const targetPane = document.getElementById(tabId);
  if (targetPane) {
    targetPane.classList.add("active");
    targetPane.style.display = "block";
  }
  if (btn) btn.classList.add("active");

  if (tabId === "tab-matching") {
    populateMatchingDropdowns();
  } else if (tabId === "tab-jobs") {
    loadJobFeed();
  } else if (tabId === "tab-workers") {
    loadWorkerFeed();
  } else if (tabId === "tab-chat") {
    loadConversations();
  }
}

// ============================================================================
// Insights Helper
// ============================================================================
async function loadInsights() {
  try {
    const res = await fetch("/api/v1/feeds/insights");
    const data = await res.json();
    const sw = document.getElementById("stat-total-workers"); if (sw) sw.innerText = data.total_registered_workers;
    const sj = document.getElementById("stat-open-jobs"); if (sj) sj.innerText = data.open_job_vacancies;
    const sc = document.getElementById("stat-total-contacts"); if (sc) sc.innerText = data.active_inquiries;
  } catch (err) {
    // Ticker removed from UI
  }
}

// ============================================================================
// Job Feed Microservice
// ============================================================================
async function loadJobFeed() {
  const trade = document.getElementById("filter-job-trade").value;
  const city = document.getElementById("filter-job-city").value;
  const grid = document.getElementById("job-feed-grid");
  grid.innerHTML = "<p>Loading job postings...</p>";

  const params = new URLSearchParams();
  if (trade) params.append("trade", trade);
  if (city) params.append("city", city);

  try {
    const res = await fetch(`/api/v1/feeds/jobs?${params.toString()}`);
    const jobs = await res.json();
    grid.innerHTML = "";

    if (!jobs || jobs.length === 0) {
      grid.innerHTML = "<p>No active jobs found matching your criteria.</p>";
      return;
    }

    jobs.forEach(job => {
      const card = document.createElement("div");
      card.className = "card";
      card.innerHTML = `
        <div>
          <div class="card-header">
            <span class="badge badge-trade">${job.trade}</span>
            ${job.urgency === 'urgent' ? '<span class="badge badge-urgent">⚡ Urgent / ತುರ್ತು</span>' : ''}
          </div>
          <h3 class="card-title">${job.title}</h3>
          <p style="font-size:0.9rem; color:var(--text-muted); margin:0.4rem 0;">${job.description || 'No description provided.'}</p>
          <div class="card-meta">
            <span>📍 ${job.area || ''}, ${job.city}</span>
            <span>💰 Offered: <strong>₹${job.wage_offered}</strong> / ${job.payment_type}</span>
            <span>⏳ Duration: ${job.duration_days} Day(s) • Needed: ${job.workers_needed} Worker(s)</span>
            <span>🏢 Posted by: ${job.employer_name}</span>
          </div>
        </div>
        <button class="btn btn-primary" style="margin-top:1rem;" onclick="initiateChat('job', ${job.id}, '${job.title.replace(/'/g, "\\'")}')">
          💬 Message Employer
        </button>
      `;
      grid.appendChild(card);
    });
  } catch (err) {
    grid.innerHTML = "<p>Error loading jobs.</p>";
  }
}

// ============================================================================
// Worker Feed Microservice
// ============================================================================
async function loadWorkerFeed() {
  const trade = document.getElementById("filter-worker-trade").value;
  const city = document.getElementById("filter-worker-city").value;
  const grid = document.getElementById("worker-feed-grid");
  grid.innerHTML = "<p>Loading skilled workers...</p>";

  const params = new URLSearchParams();
  if (trade) params.append("trade", trade);
  if (city) params.append("city", city);

  try {
    const res = await fetch(`/api/v1/feeds/workers?${params.toString()}`);
    const workers = await res.json();
    grid.innerHTML = "";

    if (!workers || workers.length === 0) {
      grid.innerHTML = "<p>No workers currently registered matching these filters.</p>";
      return;
    }

    workers.forEach(w => {
      const card = document.createElement("div");
      card.className = "card";
      card.innerHTML = `
        <div>
          <div class="card-header">
            <span class="badge badge-trade">${w.trade}</span>
            <span class="badge badge-score">⭐ ${w.rating} / 5.0</span>
          </div>
          <h3 class="card-title">${w.name}</h3>
          <div class="card-meta">
            <span>📍 ${w.area || ''}, ${w.city}</span>
            <span>🛠️ Skills: ${w.secondary_skills || w.trade}</span>
            <span>📅 Experience: ${w.experience_years} Years (${w.jobs_completed} jobs done)</span>
            <span>💰 Rate: <strong>₹${w.daily_rate}</strong> / day</span>
            <span>🗣️ Language: ${w.language_pref.toUpperCase()}</span>
          </div>
        </div>
        <button class="btn btn-primary" style="margin-top:1rem;" onclick="initiateChat('worker', ${w.id}, '${w.name.replace(/'/g, "\\'")}')">
          💬 Message Worker
        </button>
      `;
      grid.appendChild(card);
    });
  } catch (err) {
    grid.innerHTML = "<p>Error loading workers.</p>";
  }
}

// ============================================================================
// Smart Job Matcher (Role-Scoped: Only User's Queries Shown)
// ============================================================================
async function populateMatchingDropdowns() {
  const select = document.getElementById("match-target-select");
  const label = document.getElementById("lbl-match-target");
  const note = document.getElementById("match-query-note");
  const modeGroup = document.getElementById("match-mode-group");
  const resultsContainer = document.getElementById("match-results-container");
  if (!select) return;

  if (resultsContainer) resultsContainer.innerHTML = "";

  if (!currentUser) {
    select.innerHTML = "<option>Please sign in to view your personalized matches</option>";
    return;
  }

  // User is Logged In: Strictly Scoped to their queries!
  if (modeGroup) modeGroup.style.display = "none";
  select.innerHTML = "<option>Fetching your queries...</option>";

  try {
    const res = await fetch(`/api/v1/match/my-queries?phone=${currentUser.phone}`, {
      headers: authToken ? { "Authorization": `Bearer ${authToken}` } : {}
    });
    const data = await res.json();

    if (currentUser.role === "worker") {
      if (label) label.innerText = "Your Worker Profile Query:";
      if (note) note.innerHTML = `🔒 <strong>Scoped Match:</strong> Computing jobs matched specifically to <strong>${currentUser.full_name}</strong> (${currentUser.trade} in ${currentUser.city}).`;
      select.innerHTML = "";
      if (data.queries && data.queries.length > 0) {
        data.queries.forEach(q => {
          select.innerHTML += `<option value="${q.id}" selected>${q.label}</option>`;
        });
        runMatching();
      } else {
        select.innerHTML = `<option value="">No linked worker profile found</option>`;
      }
    } else {
      // Employer
      if (label) label.innerText = "Select Your Job Opening (Your Postings Only):";
      if (note) note.innerHTML = `🔒 <strong>Scoped Match:</strong> Only job openings created by <strong>${currentUser.company_name || currentUser.full_name}</strong> are displayed. Other employers' data is hidden.`;
      select.innerHTML = "";
      if (data.queries && data.queries.length > 0) {
        data.queries.forEach(q => {
          select.innerHTML += `<option value="${q.id}">${q.label}</option>`;
        });
        runMatching();
      } else {
        select.innerHTML = `<option value="">No open jobs posted yet</option>`;
        if (resultsContainer) {
          resultsContainer.innerHTML = `
            <div style="text-align:center; padding:2rem; background:white; border-radius:12px; border:1px solid var(--border-color);">
              <h3 style="margin-bottom:0.5rem;">No Open Jobs Posted Yet</h3>
              <p style="color:var(--text-muted); font-size:0.9rem; margin-bottom:1rem;">Post a work requirement first to match skilled candidate workers.</p>
              <button class="btn btn-primary" onclick="switchTab('tab-post-job', document.getElementById('nav-btn-post-job'))">
                ➕ Post Work Now
              </button>
            </div>
          `;
        }
      }
    }
  } catch (err) {
    select.innerHTML = "<option>Error loading queries.</option>";
  }
}

function toggleMatchMode() {
  populateMatchingDropdowns();
}

async function runMatching() {
  const container = document.getElementById("match-results-container");
  const targetId = document.getElementById("match-target-select").value;

  if (!targetId) return;

  container.innerHTML = "<p style='text-align:center; padding:1.5rem;'>Computing multi-factor matching scores...</p>";

  let url;
  if (currentUser) {
    url = `/api/v1/match/my-matches?phone=${currentUser.phone}&target_id=${targetId}&max_radius_km=60`;
  } else {
    const mode = document.getElementById("match-mode").value;
    url = mode === "worker_to_jobs"
      ? `/api/v1/match/worker/${targetId}/jobs?max_radius_km=60`
      : `/api/v1/match/job/${targetId}/workers?max_radius_km=60`;
  }

  try {
    const res = await fetch(url, {
      headers: authToken ? { "Authorization": `Bearer ${authToken}` } : {}
    });
    const resultData = await res.json();
    container.innerHTML = "";

    const matches = Array.isArray(resultData) ? resultData : (resultData.matches || []);
    const isWorkerToJobs = currentUser
      ? (currentUser.role === "worker")
      : (document.getElementById("match-mode").value === "worker_to_jobs");

    if (!matches || matches.length === 0) {
      container.innerHTML = `<div style="text-align:center; padding:2rem; background:white; border-radius:12px; border:1px solid var(--border-color);">
        No high-confidence matches found within 60 km radius.
      </div>`;
      return;
    }

    const grid = document.createElement("div");
    grid.className = "card-grid";

    matches.forEach(m => {
      const card = document.createElement("div");
      card.className = "card";
      const b = m.breakdown;
      const score = m.match_score;

      if (isWorkerToJobs) {
        const j = m.job;
        card.innerHTML = `
          <div>
            <div class="card-header">
              <span class="badge badge-trade">${j.trade}</span>
              <span class="badge badge-score">Match: ${score}%</span>
            </div>
            <h3 class="card-title">${j.title}</h3>
            <div style="margin: 0.5rem 0;">
              <div style="font-size:0.8rem; color:var(--text-muted);">Match Compatibility:</div>
              <div style="background:#e2e8f0; height:8px; border-radius:4px; overflow:hidden; margin: 4px 0 8px 0;">
                <div style="background:#16a34a; width:${score}%; height:100%;"></div>
              </div>
            </div>
            <div class="card-meta">
              <span>📍 ${j.area || ''}, ${j.city} (${b.distance_km} km away)</span>
              <span>💰 Wage: ₹${j.wage_offered}/day (Fit score: ${b.wage_score}%)</span>
              <span>ℹ️ Why: ${b.explanation}</span>
            </div>
          </div>
          <button class="btn btn-primary" style="margin-top:1rem;" onclick="initiateChat('job', ${j.id}, '${j.title.replace(/'/g, "\\'")}')">
            💬 Message Employer
          </button>
        `;
      } else {
        const w = m.worker;
        card.innerHTML = `
          <div>
            <div class="card-header">
              <span class="badge badge-trade">${w.trade}</span>
              <span class="badge badge-score">Match: ${score}%</span>
            </div>
            <h3 class="card-title">${w.name}</h3>
            <div style="margin: 0.5rem 0;">
              <div style="font-size:0.8rem; color:var(--text-muted);">Candidate Compatibility:</div>
              <div style="background:#e2e8f0; height:8px; border-radius:4px; overflow:hidden; margin: 4px 0 8px 0;">
                <div style="background:#16a34a; width:${score}%; height:100%;"></div>
              </div>
            </div>
            <div class="card-meta">
              <span>📍 ${w.area || ''}, ${w.city} (${b.distance_km} km away)</span>
              <span>💰 Expected Rate: ₹${w.daily_rate}/day (Fit: ${b.wage_score}%)</span>
              <span>⭐ Rating: ${w.rating} • ${w.experience_years} yrs exp</span>
              <span>ℹ️ Why: ${b.explanation}</span>
            </div>
          </div>
          <button class="btn btn-primary" style="margin-top:1rem;" onclick="initiateChat('worker', ${w.id}, '${w.name.replace(/'/g, "\\'")}')">
            💬 Message Worker
          </button>
        `;
      }
      grid.appendChild(card);
    });

    container.appendChild(grid);
  } catch (err) {
    container.innerHTML = "<p>Error executing match.</p>";
  }
}

// ============================================================================
// Fair Wage Prediction Microservice
// ============================================================================
async function handleWagePrediction(e) {
  e.preventDefault();
  const trade = document.getElementById("wage-trade").value;
  const city = document.getElementById("wage-city").value;
  const exp = parseInt(document.getElementById("wage-exp").value) || 3;
  const hours = parseInt(document.getElementById("wage-hours").value) || 8;
  const tools = document.getElementById("wage-tools").checked;
  const urgent = document.getElementById("wage-urgent").checked;

  try {
    const res = await fetch("/api/v1/wage/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        trade: trade,
        city: city,
        experience_years: exp,
        hours_per_day: hours,
        has_own_tools: tools,
        is_urgent: urgent
      })
    });
    const data = await res.json();

    const resultCard = document.getElementById("wage-result-card");
    resultCard.style.display = "block";

    resultCard.innerHTML = `
      <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:1rem;">
        <div>
          <span class="badge" style="background:#dcfce7; color:#166534; font-size:0.9rem;">Fair Wage Recommendation</span>
          <h3 style="font-size:1.6rem; color:#14532d; margin-top:0.3rem;">
            ₹${data.recommended_daily_wage.toFixed(0)} <span style="font-size:1rem; font-weight:normal; color:#166534;">/ day (${hours} hrs)</span>
          </h3>
          <div style="font-size:0.9rem; color:#15803d;">
            Estimated Hourly Rate: <strong>₹${data.recommended_hourly_wage}/hr</strong> | Fair Range: <strong>₹${data.fair_wage_min} - ₹${data.fair_wage_max}/day</strong>
          </div>
        </div>
        <div style="text-align:right;">
          <span class="badge" style="background:#e0f2fe; color:#0369a1;">${data.city_tier} Market</span>
        </div>
      </div>

      <div style="margin-top:1rem; padding-top:1rem; border-top:1px dashed #86efac; font-size:0.9rem;">
        <div style="font-weight:600; color:#166534; margin-bottom:0.3rem;">Regional Multi-Lingual Explanations:</div>
        <div style="margin-bottom:0.4rem;"><strong>English:</strong> ${data.regional_explanations.english}</div>
        <div style="margin-bottom:0.4rem; color:#0f766e;"><strong>ಕನ್ನಡ (Kannada):</strong> ${data.regional_explanations.kannada}</div>
        <div style="color:#1d4ed8;"><strong>हिन्दी (Hindi):</strong> ${data.regional_explanations.hindi}</div>
      </div>
    `;
  } catch (err) {
    alert("Failed to compute wage prediction.");
  }
}

// ============================================================================
// Employer Post Work Form
// ============================================================================
async function handlePostJob(e) {
  e.preventDefault();
  const employerName = document.getElementById("job-employer-name").value || (currentUser ? currentUser.company_name || currentUser.full_name : "Employer");
  const employerPhone = document.getElementById("job-employer-phone").value || (currentUser ? currentUser.phone : "9900000000");

  const payload = {
    title: document.getElementById("job-title").value,
    trade: document.getElementById("job-trade").value,
    urgency: document.getElementById("job-urgency").value,
    city: document.getElementById("job-city").value,
    area: document.getElementById("job-area").value,
    wage_offered: parseFloat(document.getElementById("job-wage").value),
    duration_days: parseInt(document.getElementById("job-duration").value),
    employer_name: employerName,
    employer_phone: employerPhone,
    description: document.getElementById("job-desc").value
  };

  try {
    const res = await fetch("/api/v1/jobs/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    if (res.ok) {
      alert("Job posting published successfully!");
      document.getElementById("post-job-form").reset();
      loadJobFeed();
      loadInsights();

      // Switch employer straight to candidate matching for their newly posted job!
      if (currentUser && currentUser.role === "employer") {
        switchTab("tab-matching", document.getElementById("nav-btn-matching"));
      } else {
        switchTab("tab-workers", document.getElementById("nav-btn-workers"));
      }
    } else {
      const err = await res.json();
      alert("Error: " + JSON.stringify(err.detail));
    }
  } catch (err) {
    alert("Network error publishing job.");
  }
}

// ============================================================================
// Worker Registration Form
// ============================================================================
async function handleWorkerRegistration(e) {
  e.preventDefault();
  const payload = {
    name: document.getElementById("worker-name").value,
    phone: document.getElementById("worker-phone").value,
    trade: document.getElementById("worker-trade").value,
    experience_years: parseInt(document.getElementById("worker-exp").value),
    city: document.getElementById("worker-city").value,
    area: document.getElementById("worker-area").value,
    daily_rate: parseFloat(document.getElementById("worker-rate").value),
    language_pref: document.getElementById("worker-lang").value,
    secondary_skills: document.getElementById("worker-skills").value,
    source: "web"
  };

  try {
    const res = await fetch("/api/v1/workers/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    if (res.ok) {
      alert("Worker profile registered successfully!");
      document.getElementById("worker-register-form").reset();
      loadWorkerFeed();
      loadInsights();
      switchTab("tab-workers", document.getElementById("nav-btn-workers"));
    } else {
      const err = await res.json();
      alert("Error: " + JSON.stringify(err.detail));
    }
  } catch (err) {
    alert("Network error registering worker.");
  }
}

// ============================================================================
// Contact Modal & Notification Dispatch
// ============================================================================
function openContactModal(targetType, targetId, name, phone, titleOrTrade) {
  activeContactTarget = { targetType, targetId, name, phone, titleOrTrade };
  const modal = document.getElementById("contact-modal");
  const details = document.getElementById("modal-target-details");
  const modalTitle = document.getElementById("modal-title");

  if (targetType === "job") {
    modalTitle.innerText = "Apply for Work / Contact Employer";
    details.innerHTML = `<strong>Employer:</strong> ${name}<br><strong>Work:</strong> ${titleOrTrade}<br><strong>Contact:</strong> ${phone}`;
  } else {
    modalTitle.innerText = "Hire / Contact Worker";
    details.innerHTML = `<strong>Worker:</strong> ${name}<br><strong>Trade:</strong> ${titleOrTrade}<br><strong>Contact:</strong> ${phone}`;
  }

  modal.classList.add("active");
}

function closeContactModal() {
  document.getElementById("contact-modal").classList.remove("active");
}

async function submitContactRequest() {
  const msg = document.getElementById("modal-message").value.trim();
  if (!msg) {
    alert("Please enter a short message.");
    return;
  }

  const senderType = activeContactTarget.targetType === "job" ? "worker" : "employer";
  const receiverType = activeContactTarget.targetType === "job" ? "employer" : "worker";
  const senderId = currentUser ? currentUser.id : 1;

  try {
    const res = await fetch("/api/v1/contact/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        sender_type: senderType,
        sender_id: senderId,
        receiver_type: receiverType,
        receiver_id: activeContactTarget.targetId,
        message: msg
      })
    });
    const data = await res.json();

    // Auto-dispatch simulated SMS
    const smsRes = await fetch(`/api/v1/contact/${data.id}/dispatch-sms`, { method: "POST" });
    const smsData = await smsRes.json();

    alert(`Inquiry Dispatched Successfully!\n\nSMS Sent to: ${smsData.target_phone}\nMessage: "${smsData.notification_text}"`);
    closeContactModal();
    loadInsights();
  } catch (e) {
    alert("Error sending inquiry.");
  }
}

// ============================================================================
// Virtual IVR Voice Simulator
// ============================================================================
function updatePhoneClock() {
  const now = new Date();
  const hours = String(now.getHours()).padStart(2, '0');
  const minutes = String(now.getMinutes()).padStart(2, '0');
  const clockEl = document.getElementById("screen-clock");
  if (clockEl) clockEl.innerText = `${hours}:${minutes}`;
}

function updateCallStatusBadge(status, isLive) {
  const badge = document.getElementById("call-status-badge");
  if (!badge) return;
  badge.innerText = status;
  badge.style.background = isLive ? "#16a34a" : "#0284c7";
}

function pressKey(key) {
  const input = document.getElementById("phone-dial-input");
  input.value += key;

  if (isIvrCallActive) {
    sendIvrDigits(key);
    input.value = "";
  }
}

async function handlePhoneCallBtn() {
  const phone = document.getElementById("phone-caller-id").value.trim() || "9845099112";
  await startIvrCall(phone);
}

function handlePhoneEndBtn() {
  const screen = document.getElementById("screen-text");
  const input = document.getElementById("phone-dial-input");
  const xmlDisplay = document.getElementById("twiml-display");

  if (window.speechSynthesis) {
    window.speechSynthesis.cancel();
  }

  isIvrCallActive = false;
  updateCallStatusBadge("Ended", false);

  fetch(`/api/v1/telecom/ivr/reset?call_sid=${telecomSessionId}`, { method: "POST" });
  telecomSessionId = "CALL_" + Math.floor(Math.random() * 100000);

  screen.innerText = "Call Terminated.\n\nThank you for calling KaayakaSetu (1800-KAYAKA).\nPress CALL to start a new voice session.";
  if (input) input.value = "";
  if (xmlDisplay) {
    xmlDisplay.innerText = "<!-- Call ended. TwiML session closed. -->";
  }
}

async function startIvrCall(phone) {
  const screen = document.getElementById("screen-text");
  const xmlDisplay = document.getElementById("twiml-display");
  screen.innerText = "📞 Dialing 1800-KAYAKA...\nConnecting to Voice Gateway...";
  updateCallStatusBadge("Connecting...", false);

  try {
    const res = await fetch("/api/v1/telecom/ivr", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        call_sid: telecomSessionId,
        caller_phone: phone,
        digits: ""
      })
    });
    const data = await res.json();
    isIvrCallActive = true;
    updateCallStatusBadge("Live Call", true);

    screen.innerText = `📞 ACTIVE CALL (1800-KAYAKA)\n\n${data.prompt_text}\n\n[Press 1, 2, or 3 on keypad]`;
    if (xmlDisplay) {
      xmlDisplay.innerText = data.twiml_xml || "<!-- No TwiML -->";
    }

    lastIvrAudioText = data.prompt_audio_text;
    speakVoice(lastIvrAudioText);
  } catch (e) {
    screen.innerText = "Call failed to connect.\nPlease verify backend service is running.";
    updateCallStatusBadge("Failed", false);
  }
}

async function sendIvrDigits(digits) {
  const screen = document.getElementById("screen-text");
  const xmlDisplay = document.getElementById("twiml-display");
  const phone = document.getElementById("phone-caller-id").value.trim() || "9845099112";

  try {
    const res = await fetch("/api/v1/telecom/ivr", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        call_sid: telecomSessionId,
        caller_phone: phone,
        digits: digits
      })
    });
    const data = await res.json();
    screen.innerText = `📞 ACTIVE CALL (DTMF: ${digits})\n\n${data.prompt_text}`;
    if (xmlDisplay) {
      xmlDisplay.innerText = data.twiml_xml || "<!-- No TwiML -->";
    }

    lastIvrAudioText = data.prompt_audio_text;
    speakVoice(lastIvrAudioText);

    if (digits === "1") {
      loadWorkerFeed();
      loadInsights();
    }

    if (data.action === "hangup") {
      isIvrCallActive = false;
      updateCallStatusBadge("Completed", false);
      setTimeout(() => {
        screen.innerText += "\n\n[Call completed - Audio hung up]";
      }, 3500);
    }
  } catch (e) {
    screen.innerText = "Error transmitting DTMF tone.";
  }
}

function speakVoice(text) {
  if (!("speechSynthesis" in window)) return;
  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.rate = 0.95;
  utterance.pitch = 1.0;
  window.speechSynthesis.speak(utterance);
}

function speakCurrentPrompt() {
  if (lastIvrAudioText) {
    speakVoice(lastIvrAudioText);
  } else {
    speakVoice("ನಮಸ್ಕಾರ, ಕಾಯಕಸೇತುವಿಗೆ ಸ್ವಾಗತ. ಕಾರ್ಮಿಕ ಪ್ರೊಫೈಲ್ ನೋಂದಾಯಿಸಲು 1 ಒತ್ತಿ.");
  }
}

// ============================================================================
// Real-Time 1-to-1 Private Chat Microservice (WebSocket + HTTP Fallback)
// ============================================================================
let activeChatPartnerId = null;
let activeChatJobId = null;
let activeChatPartnerName = "";
let activeChatPartnerRole = "";
let activeChatPartnerPhone = "";
let activeChatJobTitle = "";
let chatPollTimer = null;
let chatSocket = null;
let chatReconnectTimer = null;
let typingIndicatorTimer = null;
let lastTypingSentAt = 0;

// Initialize Bidirectional WebSocket
function initChatWebSocket() {
  const token = authToken || localStorage.getItem("kaayaka_auth_token");
  if (!token) return;

  if (chatSocket && (chatSocket.readyState === WebSocket.OPEN || chatSocket.readyState === WebSocket.CONNECTING)) {
    return;
  }

  const proto = window.location.protocol === "https:" ? "wss:" : "ws:";
  const wsUrl = `${proto}//${window.location.host}/api/v1/chat/ws?token=${token}`;

  try {
    chatSocket = new WebSocket(wsUrl);

    chatSocket.onopen = () => {
      console.log("🟢 Real-Time Chat WebSocket connected.");
      updateWsStatusBadge(true);
      if (chatReconnectTimer) {
        clearTimeout(chatReconnectTimer);
        chatReconnectTimer = null;
      }
      loadConversations();
    };

    chatSocket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        handleRealTimeWsEvent(data);
      } catch (err) {
        console.error("Error parsing WebSocket message:", err);
      }
    };

    chatSocket.onclose = () => {
      console.warn("🔴 Chat WebSocket closed. Retrying in 2.5s...");
      updateWsStatusBadge(false);
      chatSocket = null;
      if (!chatReconnectTimer && (authToken || localStorage.getItem("kaayaka_auth_token"))) {
        chatReconnectTimer = setTimeout(initChatWebSocket, 2500);
      }
    };

    chatSocket.onerror = (err) => {
      console.error("Chat WebSocket error:", err);
      updateWsStatusBadge(false);
    };
  } catch (e) {
    console.warn("WebSocket initialization fallback:", e);
    updateWsStatusBadge(false);
  }
}

function updateWsStatusBadge(isConnected) {
  const badge = document.getElementById("ws-status-badge");
  if (!badge) return;
  if (isConnected) {
    badge.innerHTML = `<span style="display:inline-block; width:7px; height:7px; background:#22c55e; border-radius:50%;"></span> Real-Time Active`;
    badge.style.background = "#dcfce7";
    badge.style.color = "#15803d";
  } else {
    badge.innerHTML = `<span style="display:inline-block; width:7px; height:7px; background:#f59e0b; border-radius:50%;"></span> Connecting...`;
    badge.style.background = "#fef3c7";
    badge.style.color = "#b45309";
  }
}

function handleRealTimeWsEvent(data) {
  if (data.type === "new_message") {
    const msg = data.message;
    // If user is currently looking at this sender's thread:
    if (activeChatPartnerId && String(activeChatPartnerId) === String(msg.sender_id)) {
      appendChatMessage(msg);
      playChatChime();
      // Mark read via WebSocket
      if (chatSocket && chatSocket.readyState === WebSocket.OPEN) {
        chatSocket.send(JSON.stringify({ type: "mark_read", partner_id: activeChatPartnerId }));
      }
    } else {
      // In another tab or chat: chime and highlight unread badge
      playChatChime();
    }
    // Always refresh conversations list so latest preview and badge update
    loadConversations();
  } else if (data.type === "message_sent") {
    // Confirmation from server for sent message
    loadConversations();
  } else if (data.type === "typing") {
    if (activeChatPartnerId && String(activeChatPartnerId) === String(data.sender_id)) {
      showTypingIndicator(data.sender_name);
    }
  } else if (data.type === "messages_read") {
    if (activeChatPartnerId && String(activeChatPartnerId) === String(data.reader_id)) {
      // Update checkmarks to read
      document.querySelectorAll(".chat-bubble.mine .bubble-meta").forEach(el => {
        if (!el.innerText.includes("Read")) {
          el.innerText = el.innerText.replace("✓ Sent", "✓✓ Read");
        }
      });
    }
  }
}

function showTypingIndicator(name) {
  const indicator = document.getElementById("chat-typing-indicator");
  const userSpan = document.getElementById("chat-typing-user");
  if (!indicator) return;
  if (userSpan) userSpan.innerText = name || "Partner";
  indicator.style.display = "block";

  if (typingIndicatorTimer) clearTimeout(typingIndicatorTimer);
  typingIndicatorTimer = setTimeout(() => {
    indicator.style.display = "none";
  }, 2800);
}

function playChatChime() {
  try {
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    if (!AudioContext) return;
    const ctx = new AudioContext();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = "sine";
    osc.frequency.setValueAtTime(587.33, ctx.currentTime); // D5 tone
    osc.frequency.setValueAtTime(880, ctx.currentTime + 0.08); // A5 tone
    gain.gain.setValueAtTime(0.12, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.25);
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start();
    osc.stop(ctx.currentTime + 0.25);
  } catch (e) {
    // Ignore audio permission or blocked context
  }
}

async function loadConversations() {
  const token = authToken || localStorage.getItem("kaayaka_auth_token");
  if (!token) return;

  const listEl = document.getElementById("chat-conversation-list");
  const countEl = document.getElementById("chat-conv-count");
  const badgeEl = document.getElementById("chat-unread-badge");

  try {
    const res = await fetch("/api/v1/chat/conversations", {
      headers: { "Authorization": `Bearer ${token}` }
    });
    if (!res.ok) return;
    const conversations = await res.json();

    if (countEl) countEl.innerText = conversations.length;

    let totalUnread = 0;
    conversations.forEach(c => totalUnread += (c.unread_count || 0));

    if (badgeEl) {
      if (totalUnread > 0) {
        badgeEl.innerText = totalUnread;
        badgeEl.style.display = "inline-block";
      } else {
        badgeEl.style.display = "none";
      }
    }

    if (!listEl) return;

    if (!conversations || conversations.length === 0) {
      listEl.innerHTML = `
        <div style="padding:2rem 1rem; text-align:center; color:var(--text-muted); font-size:0.85rem;">
          <div style="font-size:1.8rem; margin-bottom:0.4rem;">💬</div>
          <div>No active conversations yet.</div>
          <div style="font-size:0.75rem; margin-top:0.3rem;">Click "💬 Message" on any job or worker card to start!</div>
        </div>
      `;
      return;
    }

    listEl.innerHTML = "";
    conversations.forEach(c => {
      const partnerId = c.partner_id || c.other_user_id;
      const partnerName = c.partner_name || c.other_user_name || "User";
      const partnerRole = c.partner_role || c.other_user_role || "user";
      const partnerPhone = c.partner_phone || c.other_user_phone || "";

      const item = document.createElement("div");
      item.className = `conversation-item ${String(activeChatPartnerId) === String(partnerId) ? 'active' : ''}`;
      
      const roleBadgeClass = partnerRole === "worker" ? "badge-trade" : "badge-score";
      const unreadBadge = c.unread_count > 0 
        ? `<span class="badge" style="background:#ef4444; color:white; font-size:0.7rem; border-radius:999px; padding:2px 7px;">${c.unread_count} new</span>` 
        : "";

      item.onclick = () => openChatThread(partnerId, partnerName, partnerRole, partnerPhone, c.job_title, c.job_id);
      
      item.innerHTML = `
        <div class="conv-avatar">${partnerName.charAt(0).toUpperCase()}</div>
        <div class="conv-info">
          <div class="conv-top">
            <span class="conv-name">${escapeHtml(partnerName)}</span>
            <span class="conv-time">${formatChatTime(c.last_message_at)}</span>
          </div>
          <div class="conv-preview">${escapeHtml(c.last_message || "")}</div>
          <div style="display:flex; justify-content:space-between; align-items:center; margin-top:4px;">
            <span class="badge ${roleBadgeClass}" style="font-size:0.68rem; padding:1px 6px;">${partnerRole === 'worker' ? '👷 Worker' : '🏢 Employer'}</span>
            ${unreadBadge}
          </div>
        </div>
      `;
      listEl.appendChild(item);
    });
  } catch (err) {
    console.error("Error loading chat conversations:", err);
  }
}

function openChatThread(partnerId, partnerName, partnerRole, partnerPhone, jobTitle, jobId) {
  activeChatPartnerId = partnerId;
  activeChatPartnerName = partnerName || "User";
  activeChatPartnerRole = partnerRole || "user";
  activeChatPartnerPhone = partnerPhone || "";
  activeChatJobTitle = jobTitle || "";
  activeChatJobId = jobId || null;

  // Highlight in conversation list
  document.querySelectorAll(".conversation-item").forEach(el => el.classList.remove("active"));
  
  // Update header
  const header = document.getElementById("chat-header");
  const partnerNameEl = document.getElementById("chat-partner-name");
  const roleBadgeEl = document.getElementById("chat-partner-role-badge");
  const phoneEl = document.getElementById("chat-partner-phone");
  const jobContextEl = document.getElementById("chat-job-context");
  const inputForm = document.getElementById("chat-input-form");

  if (header) header.style.display = "flex";
  if (partnerNameEl) partnerNameEl.innerText = activeChatPartnerName;
  if (roleBadgeEl) {
    roleBadgeEl.className = `badge ${activeChatPartnerRole === 'worker' ? 'badge-trade' : 'badge-score'}`;
    roleBadgeEl.innerText = activeChatPartnerRole === 'worker' ? '👷 Worker' : '🏢 Employer';
  }
  if (phoneEl) phoneEl.innerText = activeChatPartnerPhone ? `📞 ${activeChatPartnerPhone}` : "";
  if (jobContextEl) {
    jobContextEl.innerText = activeChatJobTitle ? `💼 Re: ${activeChatJobTitle}` : "";
  }
  if (inputForm) inputForm.style.display = "flex";

  // Hide placeholder if any
  const placeholder = document.getElementById("chat-placeholder");
  if (placeholder) placeholder.style.display = "none";

  // Hide typing indicator
  const indicator = document.getElementById("chat-typing-indicator");
  if (indicator) indicator.style.display = "none";

  fetchAndRenderMessages();

  // Focus input and attach typing listener
  const input = document.getElementById("chat-input-text");
  if (input) {
    input.focus();
    input.oninput = handleChatInputTyping;
  }

  // Notify server that messages are read via WebSocket
  if (chatSocket && chatSocket.readyState === WebSocket.OPEN) {
    chatSocket.send(JSON.stringify({ type: "mark_read", partner_id: activeChatPartnerId }));
  }

  // Backup fallback polling every 6 seconds in case socket disconnected
  if (chatPollTimer) clearInterval(chatPollTimer);
  chatPollTimer = setInterval(() => {
    const chatTab = document.getElementById("tab-chat");
    if (chatTab && chatTab.classList.contains("active") && activeChatPartnerId) {
      if (!chatSocket || chatSocket.readyState !== WebSocket.OPEN) {
        fetchAndRenderMessages(true);
      }
    }
  }, 6000);
}

function handleChatInputTyping() {
  if (!chatSocket || chatSocket.readyState !== WebSocket.OPEN || !activeChatPartnerId) return;
  const now = Date.now();
  if (now - lastTypingSentAt > 1800) {
    lastTypingSentAt = now;
    chatSocket.send(JSON.stringify({ type: "typing", receiver_id: activeChatPartnerId }));
  }
}

async function fetchAndRenderMessages(isBackground = false) {
  const token = authToken || localStorage.getItem("kaayaka_auth_token");
  if (!token || !activeChatPartnerId) return;

  const container = document.getElementById("chat-messages-container");
  if (!container) return;

  try {
    const res = await fetch(`/api/v1/chat/thread/${activeChatPartnerId}`, {
      headers: { "Authorization": `Bearer ${token}` }
    });
    if (!res.ok) return;
    const messages = await res.json();

    const isNearBottom = container.scrollHeight - container.scrollTop <= container.clientHeight + 100;

    container.innerHTML = "";

    if (!messages || messages.length === 0) {
      container.innerHTML = `
        <div style="text-align:center; color:var(--text-muted); padding:3rem 1rem; font-size:0.9rem;">
          👋 No messages yet with <strong>${escapeHtml(activeChatPartnerName)}</strong>.<br>
          <span style="font-size:0.8rem; opacity:0.8;">Say hello! Messages are delivered in real time with end-to-end privacy.</span>
        </div>
      `;
      return;
    }

    messages.forEach(msg => {
      appendChatMessage(msg, false);
    });

    if (!isBackground || isNearBottom) {
      container.scrollTop = container.scrollHeight;
    }

    if (!isBackground) {
      loadConversations();
    }
  } catch (err) {
    console.error("Error fetching messages:", err);
  }
}

function appendChatMessage(msg, autoScroll = true) {
  const container = document.getElementById("chat-messages-container");
  if (!container) return;

  // Clear "no messages yet" if present
  if (container.innerText.includes("No messages yet with")) {
    container.innerHTML = "";
  }

  const isMine = msg.is_mine || (currentUser && String(msg.sender_id) === String(currentUser.id));
  const bubble = document.createElement("div");
  bubble.className = `chat-bubble ${isMine ? 'mine' : 'theirs'}`;
  
  const timeStr = formatChatTime(msg.created_at || new Date().toISOString());
  const readIndicator = isMine ? (msg.is_read ? ' • ✓✓ Read' : ' • ✓ Sent') : '';

  bubble.innerHTML = `
    <div class="bubble-sender">${isMine ? 'You' : escapeHtml(msg.sender_name || activeChatPartnerName)}</div>
    <div class="bubble-text">${escapeHtml(msg.message_text)}</div>
    <div class="bubble-meta">${timeStr}${readIndicator}</div>
  `;
  container.appendChild(bubble);

  if (autoScroll) {
    container.scrollTop = container.scrollHeight;
  }
}

async function handleSendChatMessage(e) {
  e.preventDefault();
  const token = authToken || localStorage.getItem("kaayaka_auth_token");
  if (!token || !activeChatPartnerId) return;

  const input = document.getElementById("chat-input-text");
  const text = (input ? input.value : "").trim();
  if (!text) return;

  input.value = "";

  // 1. If WebSocket is connected, send instantly over WebSocket (0ms roundtrip)
  if (chatSocket && chatSocket.readyState === WebSocket.OPEN) {
    chatSocket.send(JSON.stringify({
      type: "chat_message",
      receiver_id: activeChatPartnerId,
      message_text: text,
      job_id: activeChatJobId || null
    }));

    // Optimistically render bubble immediately for instant UI response
    appendChatMessage({
      sender_id: currentUser ? currentUser.id : null,
      message_text: text,
      is_mine: true,
      is_read: false,
      created_at: new Date().toISOString()
    }, true);

    loadConversations();
    return;
  }

  // 2. HTTP Fallback if WebSocket is not open
  try {
    const res = await fetch("/api/v1/chat/send", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
      },
      body: JSON.stringify({
        receiver_id: activeChatPartnerId,
        message_text: text,
        job_id: activeChatJobId || null
      })
    });

    if (!res.ok) {
      const err = await res.json();
      alert(err.detail || "Failed to send message.");
      return;
    }

    const msg = await res.json();
    appendChatMessage(msg, true);
    await loadConversations();
  } catch (err) {
    console.error("Error sending message:", err);
  }
}

async function initiateChat(targetType, targetId, titleOrName) {
  const token = authToken || localStorage.getItem("kaayaka_auth_token");
  if (!token) {
    alert("Please sign in to message workers or employers.");
    return;
  }

  try {
    const res = await fetch("/api/v1/chat/initiate", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
      },
      body: JSON.stringify({
        target_type: targetType,
        target_id: targetId
      })
    });

    if (!res.ok) {
      const err = await res.json();
      alert(err.detail || "Unable to initiate chat.");
      return;
    }

    const data = await res.json();
    const partnerId = data.partner_id || (data.other_user && data.other_user.id);
    const partnerName = data.partner_name || (data.other_user && data.other_user.full_name) || titleOrName;
    const partnerRole = data.partner_role || (data.other_user && data.other_user.role) || (targetType === 'job' ? 'employer' : 'worker');
    const partnerPhone = data.partner_phone || (data.other_user && data.other_user.phone) || '';

    // Switch to Chat Tab
    switchTab("tab-chat", document.getElementById("nav-btn-chat"));

    // Load conversations list and select this conversation
    await loadConversations();
    openChatThread(
      partnerId,
      partnerName,
      partnerRole,
      partnerPhone,
      data.job_title,
      data.job_id
    );
  } catch (err) {
    console.error("Error initiating chat:", err);
    alert("Could not start chat thread.");
  }
}

function formatChatTime(dateStr) {
  if (!dateStr) return "";
  try {
    const d = new Date(dateStr);
    if (isNaN(d.getTime())) return dateStr;
    const now = new Date();
    const isToday = d.toDateString() === now.toDateString();
    if (isToday) {
      return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } else {
      return d.toLocaleDateString([], { month: 'short', day: 'numeric' }) + " " + d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
  } catch (e) {
    return dateStr;
  }
}

function escapeHtml(text) {
  if (!text) return "";
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
