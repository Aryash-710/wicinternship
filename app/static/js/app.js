// ============================================================================
// Translations & Localization Dictionary
// ============================================================================
const I18N = {
  en: {
    badge: "Microservices",
    subtitle: "ಕಾಯಕಸೇತು • श्रमसेतु — Connecting Workers & Employers with Smart Matching, Fair Wage & Regional USSD/IVR",
    navJobs: "Job Feed",
    navWorkers: "Workers Feed",
    navMatching: "Smart Matcher",
    navWage: "Fair Wage Predictor",
    navPostJob: "Post Work (Employer)",
    navRegWorker: "Worker Registration",
    navPhone: "Feature Phone (USSD & IVR)",
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
    subtitle: "ಕಾಯಕಸೇತು — ಕಾರ್ಮಿಕರು ಮತ್ತು ಉದ್ಯೋಗದಾತರನ್ನು ಬೆಸೆಯುವ ಸ್ಮಾರ್ಟ್ ಪ್ಲಾಟ್‌ಫಾರ್ಮ್ (ಕನ್ನಡ & ಹಿಂದಿ USSD/IVR ಸೇರಿದಂತೆ)",
    navJobs: "ಕೆಲಸಗಳ ಫೀಡ್",
    navWorkers: "ಕಾರ್ಮಿಕರ ಪಟ್ಟಿ",
    navMatching: "ಸ್ಮಾರ್ಟ್ ಮ್ಯಾಚಿಂಗ್",
    navWage: "ನ್ಯಾಯಯುತ ದಿನಗೂಲಿ",
    navPostJob: "ಕೆಲಸ ಪ್ರಕಟಿಸಿ (ಉದ್ಯೋಗದಾತ)",
    navRegWorker: "ಕಾರ್ಮಿಕರ ನೋಂದಣಿ",
    navPhone: "ಫೋನ್ ಸಿಮ್ಯುಲೇಟರ್ (USSD/IVR)",
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
    subtitle: "श्रमसेतु — कामगारों और नियोक्ताओं को जोड़ने वाला स्मार्ट मंच (कन्नड़ और हिंदी USSD/IVR सहित)",
    navJobs: "काम की सूची",
    navWorkers: "कामगारों की सूची",
    navMatching: "स्मार्ट मैचिंग",
    navWage: "उचित मजदूरी कैलकुलेटर",
    navPostJob: "काम पोस्ट करें (नियोक्ता)",
    navRegWorker: "श्रमिक पंजीकरण",
    navPhone: "फोन सिमुलेटर (USSD/IVR)",
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

// USSD / IVR State
let telecomSessionId = "sess_" + Math.floor(Math.random() * 100000);
let currentTelecomMode = "ussd"; // 'ussd' or 'ivr'
let lastIvrAudioText = "";

// ============================================================================
// Initialization
// ============================================================================
document.addEventListener("DOMContentLoaded", () => {
  loadInsights();
  loadJobFeed();
  loadWorkerFeed();
  populateMatchingDropdowns();
  updatePhoneClock();
  setInterval(updatePhoneClock, 30000);
});

function changeLanguage(lang) {
  currentLang = lang;
  const t = I18N[lang] || I18N.en;

  document.getElementById("lbl-badge").innerText = t.badge;
  document.getElementById("lbl-subtitle").innerText = t.subtitle;
  document.getElementById("nav-jobs").innerText = t.navJobs;
  document.getElementById("nav-workers").innerText = t.navWorkers;
  document.getElementById("nav-matching").innerText = t.navMatching;
  document.getElementById("nav-wage").innerText = t.navWage;
  document.getElementById("nav-postJob") ? document.getElementById("nav-postJob").innerText = t.navPostJob : null;
  document.getElementById("nav-register-worker").innerText = t.navRegWorker;
  document.getElementById("nav-phone").innerText = t.navPhone;
  document.getElementById("lbl-stat-workers").innerText = t.statWorkers;
  document.getElementById("lbl-stat-jobs").innerText = t.statJobs;
  document.getElementById("lbl-stat-contacts").innerText = t.statContacts;
  document.getElementById("lbl-stat-location").innerText = t.statLocation;
  document.getElementById("job-feed-title").innerText = t.jobFeedTitle;
  document.getElementById("job-feed-subtitle").innerText = t.jobFeedSubtitle;
  document.getElementById("worker-feed-title").innerText = t.workerFeedTitle;
  document.getElementById("worker-feed-subtitle").innerText = t.workerFeedSubtitle;
}

function switchTab(tabId, btn) {
  document.querySelectorAll(".tab-pane").forEach(p => p.classList.remove("active"));
  document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
  document.getElementById(tabId).classList.add("active");
  if (btn) btn.classList.add("active");

  if (tabId === "tab-matching") {
    populateMatchingDropdowns();
  }
}

// ============================================================================
// Insights Ticker
// ============================================================================
async function loadInsights() {
  try {
    const res = await fetch("/api/v1/feeds/insights");
    const data = await res.json();
    document.getElementById("stat-total-workers").innerText = data.total_workers || 0;
    document.getElementById("stat-open-jobs").innerText = data.open_jobs || 0;
    document.getElementById("stat-total-contacts").innerText = data.total_contacts || 0;
  } catch (err) {
    console.error("Failed to load insights", err);
  }
}

// ============================================================================
// Job Feed Microservice
// ============================================================================
async function loadJobFeed() {
  const trade = document.getElementById("filter-job-trade").value;
  const city = document.getElementById("filter-job-city").value;
  const grid = document.getElementById("job-feed-grid");
  grid.innerHTML = "<p>Loading active job opportunities...</p>";

  let url = `/api/v1/feeds/jobs?limit=50`;
  if (trade) url += `&trade=${encodeURIComponent(trade)}`;
  if (city) url += `&city=${encodeURIComponent(city)}`;

  try {
    const res = await fetch(url);
    const jobs = await res.json();
    grid.innerHTML = "";

    if (!jobs || jobs.length === 0) {
      grid.innerHTML = `<div style="grid-column: 1/-1; text-align:center; padding: 2rem; color:var(--text-muted);">
        No jobs found matching your filters. Try selecting 'All Trades' or 'All Cities'.
      </div>`;
      return;
    }

    jobs.forEach(job => {
      const card = document.createElement("div");
      card.className = "card";
      const isUrgent = job.urgency === "urgent";

      card.innerHTML = `
        <div>
          <div class="card-header">
            <div>
              <span class="badge badge-trade">${job.trade}</span>
              ${isUrgent ? '<span class="badge badge-urgent">⚡ URGENT</span>' : ''}
            </div>
            <div class="wage-badge">₹${job.wage_offered} <span style="font-size:0.75rem; color:var(--text-muted); font-weight:normal;">/${job.payment_type}</span></div>
          </div>
          <h3 class="card-title">${job.title}</h3>
          <p style="font-size:0.85rem; color:#475569; margin: 0.5rem 0;">${job.description || 'General requirements'}</p>
          <div class="card-meta">
            <span>📍 ${job.area || ''}, ${job.city} ${job.distance_km ? `(${job.distance_km} km away)` : ''}</span>
            <span>👤 Employer: ${job.employer_name}</span>
            <span>⏱️ Duration: ${job.duration_days} day(s) • Needed: ${job.workers_needed} worker(s)</span>
          </div>
        </div>
        <div style="display:flex; gap:0.5rem; margin-top:1rem;">
          <button class="btn btn-primary" style="flex:1;" onclick="openContactModal('job', ${job.id}, '${job.employer_name}', '${job.employer_phone}', '${job.title}')">
            📞 Contact Employer
          </button>
          <a class="btn btn-secondary" style="padding:0.6rem;" href="https://wa.me/91${job.employer_phone}?text=Hello%20${encodeURIComponent(job.employer_name)},%20I%20am%20interested%20in%20your%20job%20posting%20for%20${encodeURIComponent(job.title)}" target="_blank" title="WhatsApp Message">
            💬
          </a>
        </div>
      `;
      grid.appendChild(card);
    });
  } catch (err) {
    grid.innerHTML = "<p>Error loading jobs. Please check if backend is running.</p>";
  }
}

// ============================================================================
// Workers Feed Microservice
// ============================================================================
async function loadWorkerFeed() {
  const trade = document.getElementById("filter-worker-trade").value;
  const city = document.getElementById("filter-worker-city").value;
  const grid = document.getElementById("worker-feed-grid");
  grid.innerHTML = "<p>Loading qualified workers...</p>";

  let url = `/api/v1/feeds/workers?limit=50`;
  if (trade) url += `&trade=${encodeURIComponent(trade)}`;
  if (city) url += `&city=${encodeURIComponent(city)}`;

  try {
    const res = await fetch(url);
    const workers = await res.json();
    grid.innerHTML = "";

    if (!workers || workers.length === 0) {
      grid.innerHTML = `<div style="grid-column: 1/-1; text-align:center; padding: 2rem; color:var(--text-muted);">
        No workers found matching your filters.
      </div>`;
      return;
    }

    workers.forEach(w => {
      const card = document.createElement("div");
      card.className = "card";

      card.innerHTML = `
        <div>
          <div class="card-header">
            <div>
              <span class="badge badge-trade">${w.trade}</span>
              <span class="badge" style="background:#e0f2fe; color:#0369a1;">⭐ ${w.rating || 4.5}</span>
            </div>
            <div class="wage-badge">₹${w.daily_rate} <span style="font-size:0.75rem; color:var(--text-muted); font-weight:normal;">/day</span></div>
          </div>
          <h3 class="card-title">${w.name}</h3>
          <p style="font-size:0.85rem; color:#475569; margin: 0.5rem 0;">Skills: ${w.secondary_skills || 'General skill set'}</p>
          <div class="card-meta">
            <span>📍 ${w.area || ''}, ${w.city}</span>
            <span>💼 ${w.experience_years} years experience • ${w.jobs_completed || 0} jobs done</span>
            <span>🗣️ Spoken: ${w.language_pref} • Registered via: ${w.source.toUpperCase()}</span>
          </div>
        </div>
        <div style="display:flex; gap:0.5rem; margin-top:1rem;">
          <button class="btn btn-primary" style="flex:1;" onclick="openContactModal('worker', ${w.id}, '${w.name}', '${w.phone}', '${w.trade}')">
            📞 Direct Hire Inquiry
          </button>
          <a class="btn btn-secondary" style="padding:0.6rem;" href="https://wa.me/91${w.phone}?text=Hello%20${encodeURIComponent(w.name)},%20I%20have%20a%20work%20opportunity%20for%20${encodeURIComponent(w.trade)}" target="_blank" title="WhatsApp Message">
            💬
          </a>
        </div>
      `;
      grid.appendChild(card);
    });
  } catch (err) {
    grid.innerHTML = "<p>Error loading workers.</p>";
  }
}

// ============================================================================
// Smart Job Matcher Microservice
// ============================================================================
async function populateMatchingDropdowns() {
  const mode = document.getElementById("match-mode").value;
  const select = document.getElementById("match-target-select");
  const label = document.getElementById("lbl-match-target");
  select.innerHTML = "<option>Loading options...</option>";

  if (mode === "worker_to_jobs") {
    label.innerText = "Select Worker Profile (ಕಾರ್ಮಿಕ):";
    try {
      const res = await fetch("/api/v1/workers/?limit=30");
      const workers = await res.json();
      select.innerHTML = "";
      workers.forEach(w => {
        select.innerHTML += `<option value="${w.id}">${w.name} - ${w.trade} (${w.city}, Rate: ₹${w.daily_rate}/day)</option>`;
      });
    } catch (e) {
      console.error(e);
    }
  } else {
    label.innerText = "Select Job Opening (ಉದ್ಯೋಗ):";
    try {
      const res = await fetch("/api/v1/jobs/?status=open&limit=30");
      const jobs = await res.json();
      select.innerHTML = "";
      jobs.forEach(j => {
        select.innerHTML += `<option value="${j.id}">${j.title} - ${j.trade} (${j.city}, Offer: ₹${j.wage_offered})</option>`;
      });
    } catch (e) {
      console.error(e);
    }
  }
}

function toggleMatchMode() {
  populateMatchingDropdowns();
  document.getElementById("match-results-container").innerHTML = "";
}

async function runMatching() {
  const mode = document.getElementById("match-mode").value;
  const targetId = document.getElementById("match-target-select").value;
  const container = document.getElementById("match-results-container");

  if (!targetId) {
    alert("Please select a target first.");
    return;
  }

  container.innerHTML = "<p style='text-align:center; padding:1.5rem;'>Computing multi-factor matching scores...</p>";

  const url = mode === "worker_to_jobs"
    ? `/api/v1/match/worker/${targetId}/jobs?max_radius_km=60`
    : `/api/v1/match/job/${targetId}/workers?max_radius_km=60`;

  try {
    const res = await fetch(url);
    const matches = await res.json();
    container.innerHTML = "";

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

      if (mode === "worker_to_jobs") {
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
          <button class="btn btn-primary" style="margin-top:1rem;" onclick="openContactModal('job', ${j.id}, '${j.employer_name}', '${j.employer_phone}', '${j.title}')">
            📞 Apply & Contact Employer
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
          <button class="btn btn-primary" style="margin-top:1rem;" onclick="openContactModal('worker', ${w.id}, '${w.name}', '${w.phone}', '${w.trade}')">
            📞 Hire Candidate
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
  const payload = {
    title: document.getElementById("job-title").value,
    trade: document.getElementById("job-trade").value,
    urgency: document.getElementById("job-urgency").value,
    city: document.getElementById("job-city").value,
    area: document.getElementById("job-area").value,
    wage_offered: parseFloat(document.getElementById("job-wage").value),
    duration_days: parseInt(document.getElementById("job-duration").value),
    employer_name: document.getElementById("job-employer-name").value,
    employer_phone: document.getElementById("job-employer-phone").value,
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
      switchTab("tab-jobs", document.querySelectorAll(".tab-btn")[0]);
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
      switchTab("tab-workers", document.querySelectorAll(".tab-btn")[1]);
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
  activeContactTarget = null;
}

async function submitContactRequest() {
  if (!activeContactTarget) return;
  const msg = document.getElementById("modal-message").value || "Interested in work collaboration.";

  const payload = {
    sender_type: activeContactTarget.targetType === "job" ? "worker" : "employer",
    sender_id: 1, // Simulated active logged in user
    receiver_type: activeContactTarget.targetType,
    receiver_id: activeContactTarget.targetId,
    job_id: activeContactTarget.targetType === "job" ? activeContactTarget.targetId : null,
    message: msg
  };

  try {
    const res = await fetch("/api/v1/contact/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const data = await res.json();

    // Trigger instant simulated SMS dispatch
    const smsRes = await fetch(`/api/v1/contact/${data.id}/dispatch-sms`, { method: "POST" });
    const smsData = await smsRes.json();

    alert(`Inquiry Sent!\nSimulated SMS Notification:\n"${smsData.notification_text}"`);
    closeContactModal();
    loadInsights();
  } catch (e) {
    alert("Failed to initiate contact.");
  }
}

// ============================================================================
// Virtual Feature Phone Simulator (USSD & IVR)
// ============================================================================
function updatePhoneClock() {
  const now = new Date();
  const hours = String(now.getHours()).padStart(2, '0');
  const minutes = String(now.getMinutes()).padStart(2, '0');
  const clockEl = document.getElementById("screen-clock");
  if (clockEl) clockEl.innerText = `${hours}:${minutes}`;
}

function switchTelecomMode() {
  const mode = document.getElementById("telecom-mode").value;
  currentTelecomMode = mode;
  const screen = document.getElementById("screen-text");
  const inputBar = document.getElementById("phone-dial-input");
  const audioControls = document.getElementById("ivr-audio-controls");

  if (mode === "ussd") {
    inputBar.value = "*345#";
    screen.innerText = "KaayakaSetu Gateway\nMode: USSD (*345#)\nDial *345# and press CALL to start in Kannada or Hindi.";
    audioControls.style.display = "none";
  } else {
    inputBar.value = "1800-KAYAKA";
    screen.innerText = "Voice IVR Gateway\nMode: Voice Call\nPress CALL to connect to Kannada/Hindi Voice Assistant.";
    audioControls.style.display = "block";
  }
}

function pressKey(key) {
  const input = document.getElementById("phone-dial-input");
  input.value += key;

  // In IVR mode, send DTMF immediately if call is active
  if (currentTelecomMode === "ivr" && input.value.length === 1 && !isNaN(key)) {
    sendIvrDigits(key);
    input.value = "";
  }
}

async function handlePhoneCallBtn() {
  const input = document.getElementById("phone-dial-input");
  const val = input.value.trim();
  const phone = document.getElementById("phone-caller-id").value.trim() || "9845099112";

  if (currentTelecomMode === "ussd") {
    await sendUssdInput(val, phone);
    input.value = "";
  } else {
    // Start or interact with IVR call
    await startIvrCall(phone);
  }
}

function handlePhoneEndBtn() {
  const screen = document.getElementById("screen-text");
  const input = document.getElementById("phone-dial-input");

  if (window.speechSynthesis) {
    window.speechSynthesis.cancel();
  }

  fetch(`/api/v1/telecom/ussd/reset?session_id=${telecomSessionId}`, { method: "POST" });
  telecomSessionId = "sess_" + Math.floor(Math.random() * 100000);

  if (currentTelecomMode === "ussd") {
    screen.innerText = "Call Ended.\nSession closed.\nDial *345# to start again.";
    input.value = "*345#";
  } else {
    screen.innerText = "Call Terminated.\nThank you for calling KaayakaSetu.";
    input.value = "1800-KAYAKA";
  }
}

async function sendUssdInput(val, phone) {
  const screen = document.getElementById("screen-text");
  screen.innerText = "Connecting to USSD Gateway...";

  try {
    const res = await fetch("/api/v1/telecom/ussd", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: telecomSessionId,
        phone_number: phone,
        user_input: val
      })
    });
    const data = await res.json();
    // Format message display
    const cleanMsg = data.message.replace(/^(CON|END)\s+/, "");
    screen.innerText = cleanMsg;

    if (data.action === "END") {
      telecomSessionId = "sess_" + Math.floor(Math.random() * 100000);
      loadWorkerFeed();
      loadInsights();
    }
  } catch (err) {
    screen.innerText = "USSD Connection Failed.\nPlease retry.";
  }
}

async function startIvrCall(phone) {
  const screen = document.getElementById("screen-text");
  screen.innerText = "📞 Calling 1800-KAYAKA...\nConnecting...";

  try {
    const res = await fetch("/api/v1/telecom/ivr", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        call_sid: "CALL_" + telecomSessionId,
        caller_phone: phone,
        digits: ""
      })
    });
    const data = await res.json();
    screen.innerText = `📞 ACTIVE CALL\n\n${data.prompt_text}\n\nPress 1 or 2 on keypad.`;
    lastIvrAudioText = data.prompt_audio_text;
    speakVoice(lastIvrAudioText);
  } catch (e) {
    screen.innerText = "Call failed to connect.";
  }
}

async function sendIvrDigits(digits) {
  const screen = document.getElementById("screen-text");
  const phone = document.getElementById("phone-caller-id").value.trim() || "9845099112";

  try {
    const res = await fetch("/api/v1/telecom/ivr", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        call_sid: "CALL_" + telecomSessionId,
        caller_phone: phone,
        digits: digits
      })
    });
    const data = await res.json();
    screen.innerText = `📞 ACTIVE CALL\n\n${data.prompt_text}`;
    lastIvrAudioText = data.prompt_audio_text;
    speakVoice(lastIvrAudioText);

    if (data.action === "hangup") {
      setTimeout(() => {
        screen.innerText += "\n\n[Call Finished - Hung up]";
      }, 4000);
    }
  } catch (e) {
    screen.innerText = "Error transmitting DTMF tone.";
  }
}

function speakVoice(text) {
  if (!("speechSynthesis" in window)) return;
  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.rate = 0.9;
  utterance.pitch = 1.0;
  window.speechSynthesis.speak(utterance);
}

function speakCurrentPrompt() {
  if (lastIvrAudioText) {
    speakVoice(lastIvrAudioText);
  } else {
    speakVoice("ನಮಸ್ಕಾರ, ಕಾಯಕಸೇತುವಿಗೆ ಸ್ವಾಗತ.");
  }
}
