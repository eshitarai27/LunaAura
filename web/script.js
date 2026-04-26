const API_BASE = 'http://localhost:5001';

let currentUser = null;
let currentPage = 'dashboard';
let charts = {};
let dataHistory = [];
let cohortAnalytics = null;
let cohortRecords = [];

let formData = { age: 26, gender: 'Female', sleep_duration: 7, stress_level: 2, physical_activity: 30, cycle_day: 14, base_cycle: 28, anxiety_level: 5, water_intake: 4 };
let lastPrediction = null;

function isSessionStorageAvailable() { try { sessionStorage.setItem('X', 'X'); sessionStorage.removeItem('X'); return true; } catch(e) { return false; } }

function checkAuth() {
    const authC = document.getElementById('landing-container');
    const appC = document.getElementById('app-container');

    if (!isSessionStorageAvailable()) { initializeAuth(); return; }

    const user = sessionStorage.getItem('luna_user');
    const toggleBtn = document.getElementById('auth-toggle-btn');

    const stBtn = document.getElementById('nav-settings-btn');
    if (user) {
        currentUser = JSON.parse(user);
        toggleBtn.innerText = 'Logout';
        toggleBtn.onclick = logout;
        if(stBtn) stBtn.style.display = 'block';
        const p = currentUser.profile;
        if(p) {
            formData.gender = p.gender;
            formData.base_cycle = p.cycle_length;
            formData.age = p.age;
            
            document.getElementById('header-welcome-msg').innerHTML = `Welcome, ${p.username} <span class="text-sm font-medium text-gray-400">| Age: ${p.age} | Base Loaded</span>`;
            document.getElementById('header-subtitle-msg').innerText = "Personalized Context Authenticated";
        }
        if (currentUser.history && currentUser.history.length > 0) {
            dataHistory = currentUser.history;
            lastPrediction = currentUser; 
        }
    } else {
        currentUser = null;
        appC.style.display = 'none';
        authC.style.display = 'flex'; 
        document.getElementById('auth-signup-fields').classList.add('hidden');
        
        toggleBtn.innerText = 'Login';
        toggleBtn.onclick = () => { 
            appC.style.display = 'none';
            authC.style.display = 'flex';
        };
        if(stBtn) stBtn.style.display = 'none';
        document.getElementById('header-welcome-msg').innerText = `Welcome to Luna Aura`;
        document.getElementById('header-subtitle-msg').innerText = "Cycle-Aware AI Mental Wellbeing Intelligence";
    }
    initializeAuth();
    initializeApp();
}

let isSignupMode = false;
function initializeAuth() {
    const signupToggle = document.getElementById('auth-toggle-signup-btn');
    const loginBtn = document.getElementById('auth-login-btn');
    const authTitle = document.getElementById('auth-title');
    
    document.getElementById('demo-btn').addEventListener('click', () => {
        document.getElementById('landing-container').style.display = 'none';
        document.getElementById('app-container').style.display = 'flex';
        navigateTo('analytics');
    });
    if(signupToggle) {
        signupToggle.addEventListener('click', () => {
            isSignupMode = !isSignupMode;
            const sf = document.getElementById('auth-signup-fields');
            if (isSignupMode) {
                sf.classList.remove('hidden');
                signupToggle.innerText = 'Switch to Login';
                loginBtn.innerText = 'Create Profile';
                authTitle.innerText = 'Initialization';
            } else {
                sf.classList.add('hidden');
                signupToggle.innerText = 'Create an Account';
                loginBtn.innerText = 'Login';
                authTitle.innerText = 'Welcome Back';
            }
        });
    }
    if(loginBtn) {
        loginBtn.addEventListener('click', () => {
            if(isSignupMode) signup(); else login();
        });
    }
}

async function login() {
    const u = document.getElementById('auth-username').value.trim();
    const p = document.getElementById('auth-password').value.trim();
    if (!u || !p) return;
    
    document.getElementById('auth-error').classList.add('hidden');
    
    try {
        const response = await fetch(`${API_BASE}/login`, {
            method: 'POST', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username: u, password: p})
        });
        if(response.ok) {
            const payload = await response.json();
            sessionStorage.setItem('luna_user', JSON.stringify(payload));
            currentUser = payload;
            lastPrediction = payload;
            document.getElementById('landing-container').style.display = 'none';
            document.getElementById('app-container').style.display = 'flex';
            checkAuth();
            navigateTo('dashboard');
        } else {
            document.getElementById('auth-error').innerText = "Invalid credentials or User not found.";
            document.getElementById('auth-error').classList.remove('hidden');
        }
    } catch(e) {
        document.getElementById('auth-error').innerText = "Server Error. Ensure Python backend is running.";
        document.getElementById('auth-error').classList.remove('hidden');
    }
}

async function signup() {
    const u = document.getElementById('auth-username').value.trim();
    const p = document.getElementById('auth-password').value.trim();
    if (!u || !p) return;
    
    document.getElementById('auth-error').classList.add('hidden');
    
    const payloadReq = {
        username: u, password: p,
        age: document.getElementById('auth-age').value,
        gender: document.getElementById('auth-gender').value,
        height_cm: document.getElementById('auth-height').value,
        weight_kg: document.getElementById('auth-weight').value,
        cycle_length: document.getElementById('auth-cycle').value,
        sleep_target: document.getElementById('auth-sleep').value
    };
    
    try {
        const response = await fetch(`${API_BASE}/signup`, {
            method: 'POST', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payloadReq)
        });
        if(response.ok) {
            const payload = await response.json();
            sessionStorage.setItem('luna_user', JSON.stringify(payload));
            currentUser = payload;
            lastPrediction = payload;
            document.getElementById('landing-container').style.display = 'none';
            document.getElementById('app-container').style.display = 'flex';
            checkAuth();
            navigateTo('dashboard');
        } else {
            document.getElementById('auth-error').innerText = "Username already exists.";
            document.getElementById('auth-error').classList.remove('hidden');
        }
    } catch(e) {
        document.getElementById('auth-error').innerText = "Server Error. Ensure Python backend is running.";
        document.getElementById('auth-error').classList.remove('hidden');
    }
}

function logout() { 
    sessionStorage.removeItem('luna_user'); 
    dataHistory = [];
    lastPrediction = null;
    checkAuth();
    navigateTo('dashboard');
}

function initializeApp() {
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.addEventListener('click', () => { navigateTo(btn.dataset.page); });
    });
    // Chart Default Configurations
    Chart.defaults.color = '#9ca3af';
    Chart.defaults.font.family = 'Inter, sans-serif';
    Chart.defaults.elements.bar.borderRadius = 4;
    Chart.defaults.elements.line.tension = 0.4;
    
    // Boot Status Checks
    startHeartbeat();
    
    // Pre-fetch Cohort Data silently
    fetchCohortData();
    
    navigateTo('dashboard');
}

function startHeartbeat() {
    const checkServer = async () => {
        const dot = document.getElementById('server-dot');
        const st = document.getElementById('server-status');
        try {
            const res = await fetch(`${API_BASE}/health`);
            if (res.ok) {
                dot.className = 'w-2.5 h-2.5 rounded-full bg-green-500 transition-colors duration-500 shadow-[0_0_10px_rgba(34,197,94,0.5)]';
                st.innerText = 'API Connected';
                st.className = 'text-xs font-medium text-green-400 transition-colors';
            } else throw new Error();
        } catch (e) {
            dot.className = 'w-2.5 h-2.5 rounded-full bg-red-500 transition-colors duration-500 shadow-[0_0_10px_rgba(239,68,68,0.5)]';
            st.innerText = 'Server Offline [5001]';
            st.className = 'text-xs font-medium text-red-400 transition-colors';
        }
    };
    checkServer();
    setInterval(checkServer, 5000);
}

async function fetchCohortData() {
    try {
        const resA = await fetch(`${API_BASE}/analytics`);
        if (resA.ok) cohortAnalytics = await resA.json();
        const resR = await fetch(`${API_BASE}/records`);
        if (resR.ok) cohortRecords = await resR.json();
    } catch(e) { console.warn("Failed to prefetch cohort:", e); }
}

function navigateTo(page) {
    if (page === 'daily-log' && (!currentUser || !currentUser.profile || currentUser.profile.username === 'Guest')) {
        document.getElementById('page-content').innerHTML = `
            <div class="flex flex-col items-center justify-center p-12 mt-12 text-center bg-gray-900 border border-gray-800 rounded-2xl max-w-2xl mx-auto shadow-2xl">
                <div class="text-6xl mb-6">🔒</div>
                <h3 class="text-2xl font-bold text-white mb-4">Authentication Required</h3>
                <p class="text-gray-400 mb-8">Signal injections map directly to your personal physiological baseline. Please login or create a persistent account to access the Daily Log.</p>
                <button onclick="document.getElementById('app-container').style.display = 'none'; document.getElementById('landing-container').style.display = 'flex'; document.getElementById('auth-signup-fields').classList.add('hidden');" class="bg-purple-600 px-6 py-3 rounded-lg text-white font-medium hover:bg-purple-500 transition shadow-lg shadow-purple-900/40">Switch to Login Module</button>
            </div>
        `;
        return;
    }

    currentPage = page;
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.remove('bg-purple-600', 'text-white');
        btn.classList.add('text-gray-300');
    });
    const activeBtn = document.querySelector(`[data-page="${page}"]`);
    if (activeBtn) {
        activeBtn.classList.add('bg-purple-600', 'text-white');
        activeBtn.classList.remove('text-gray-300');
    }
    destroyAllCharts();
    renderPage();
}

function destroyAllCharts() {
    Object.values(charts).forEach(chart => { if (chart) chart.destroy(); });
    charts = {};
}

function renderPage() {
    const content = document.getElementById('page-content');
    switch(currentPage) {
        case 'dashboard': renderDashboard(content); break;
        case 'daily-log': renderDailyLog(content); break;
        case 'analytics': renderAnalytics(content); break;
        case 'model-insights': renderModelInsights(content); break;
        case 'research-mode': renderResearchMode(content); break;
        case 'profile-settings': renderProfileSettings(content); break;
    }
}

// ============================================
// DASHBOARD
// ============================================
function renderDashboard(content) {
    if (currentUser && (!dataHistory || dataHistory.length === 0)) {
        content.innerHTML = `
            <div class="space-y-6 animate-fade-in pb-12">
                <div class="flex flex-col items-center justify-center bg-gray-900 border border-gray-800 p-12 rounded-2xl shadow-xl text-center mt-8">
                    <div class="text-6xl mb-6">🌱</div>
                    <h3 class="text-3xl font-bold bg-gradient-to-r from-purple-400 to-indigo-400 bg-clip-text text-transparent mb-4">Welcome to Luna Aura</h3>
                    <p class="text-gray-400 max-w-2xl text-lg mb-8 leading-relaxed">
                        Your personalized behavioral baseline profile has been initialized securely. 
                        Currently, you have <span class="text-white font-bold">0 records</span> in your tracking history.
                    </p>
                    <div class="w-full max-w-md bg-gray-800/50 border border-gray-700 rounded-xl p-6 mb-8 text-left space-y-4 shadow-inner">
                        <h4 class="text-sm tracking-widest text-gray-500 font-bold uppercase mb-2">Maturity Path:</h4>
                        <div class="flex justify-between items-center text-sm"><span class="text-gray-300">Phase 1: First Entry</span><span class="text-purple-400 font-mono">1 Log</span></div>
                        <div class="w-full bg-gray-700 h-1.5 rounded-full overflow-hidden"><div class="bg-gray-600 h-full w-[0%]"></div></div>
                        
                        <div class="flex justify-between items-center text-sm"><span class="text-gray-400">Phase 2: Weekly Trend</span><span class="text-gray-500 font-mono">7 Logs</span></div>
                        <div class="w-full bg-gray-700 h-1.5 rounded-full overflow-hidden"><div class="bg-gray-600 h-full w-[0%]"></div></div>
                        
                        <div class="flex justify-between items-center text-sm"><span class="text-gray-400">Phase 3: Rolling Analytics</span><span class="text-gray-500 font-mono">30 Logs</span></div>
                        <div class="w-full bg-gray-700 h-1.5 rounded-full overflow-hidden"><div class="bg-gray-600 h-full w-[0%]"></div></div>
                    </div>
                    
                    <button onclick="navigateTo('daily-log')" class="bg-purple-600 px-8 py-4 rounded-xl text-white font-bold text-lg hover:bg-purple-500 transition shadow-lg shadow-purple-900/40 transform hover:-translate-y-1">
                        Inject First Signal
                    </button>
                </div>
            </div>
        `;
        return;
    }

    content.innerHTML = `
        <div class="space-y-6 animate-fade-in pb-12">
            <div class="flex justify-between items-center bg-gray-900 border border-gray-800 p-4 rounded-xl shadow-lg">
                <h3 class="text-xl font-bold bg-gradient-to-r from-purple-400 to-indigo-400 bg-clip-text text-transparent">Telemetry Dashboard</h3>
                <button onclick="navigateTo('daily-log')" class="text-sm bg-purple-600 px-6 py-2 rounded-lg text-white font-medium hover:bg-purple-500 transition shadow-lg shadow-purple-900/40">Inject Signal</button>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
                <!-- Fallback Summary if < 14 logs -->
                <div class="md:col-span-3 bg-gradient-to-r from-gray-900 to-gray-800 border-l-4 border-purple-500 rounded-2xl p-8 relative overflow-hidden shadow-2xl">
                    <div class="absolute -right-10 -top-10 w-40 h-40 bg-purple-500/10 rounded-full blur-3xl"></div>
                    <h4 class="text-xs font-semibold uppercase tracking-widest text-purple-400 mb-2" id="insight-badge">Automated Insight</h4>
                    <div id="summary-sentence" class="text-3xl font-bold text-white leading-tight">Waiting for dataset.</div>
                    <div id="what-changed" class="text-sm mt-4 text-gray-400 bg-gray-900/50 inline-block px-4 py-2 rounded-lg border border-gray-700 font-mono">Navigate to 'Inject Signal' to populate.</div>
                </div>
                
                <div class="bg-gray-900 border border-gray-800 rounded-2xl p-6 flex flex-col items-center justify-center shadow-xl relative">
                    <h4 class="text-sm font-semibold text-gray-400 absolute top-6 left-6">Behavioral Wellness Estimate</h4>
                    <div class="relative w-32 h-32 mt-6">
                        <svg class="w-full h-full transform -rotate-90">
                            <circle cx="64" cy="64" r="56" stroke="currentColor" stroke-width="8" fill="transparent" class="text-gray-800"/>
                            <circle id="score-ring" cx="64" cy="64" r="56" stroke="currentColor" stroke-width="8" fill="transparent" stroke-dasharray="351" stroke-dashoffset="351" class="text-purple-500 transition-all duration-1000 ease-out"/>
                        </svg>
                        <div class="absolute inset-0 flex items-center justify-center text-3xl font-bold text-white" id="score-val">0</div>
                    </div>
                </div>
            </div>

            <div id="dashboard-heatmap-block" class="bg-gray-900 border border-gray-800 rounded-2xl p-6 shadow-xl hidden">
                <h4 class="text-sm font-semibold text-gray-400 mb-2">7-Day Risk Momentum Heatmap</h4>
                <div id="heatmap-container" class="flex justify-between gap-2 h-12 mb-2">
                    <div class="flex-1 bg-gray-800 rounded-md"></div><div class="flex-1 bg-gray-800 rounded-md"></div><div class="flex-1 bg-gray-800 rounded-md"></div><div class="flex-1 bg-gray-800 rounded-md"></div><div class="flex-1 bg-gray-800 rounded-md"></div><div class="flex-1 bg-gray-800 rounded-md"></div><div class="flex-1 bg-gray-800 rounded-md"></div>
                </div>
                <div class="mt-3 mb-2">
                    <div class="flex items-center gap-2">
                        <span class="text-xs text-gray-500">Low Risk</span>
                        <div class="flex-1 h-3 rounded-full" style="background: linear-gradient(to right, #10b981, #84cc16, #eab308, #f97316, #ef4444);"></div>
                        <span class="text-xs text-gray-500">High Risk</span>
                    </div>
                    <div class="flex justify-between mt-1 px-1">
                        <span class="text-[10px] text-emerald-400">Stable</span>
                        <span class="text-[10px] text-yellow-400">Elevated</span>
                        <span class="text-[10px] text-red-400">Critical</span>
                    </div>
                </div>
                <p class="text-xs text-gray-500 mt-2">Each cell represents one day's composite risk probability. <span class="text-emerald-400">Green</span> = Low behavioral risk (R&lt;35). <span class="text-yellow-400">Yellow/Orange</span> = Moderate concern (35≤R&lt;65). <span class="text-red-400">Red</span> = Elevated multi-factor adversity (R≥65). Colors are driven by model risk probability combined with recent volatility variance.</p>
            </div>

            <div id="dashboard-charts-block" class="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6 hidden">
                <div class="bg-gray-900 border border-gray-800 rounded-2xl p-6 shadow-lg"><h4 class="font-semibold text-white mb-2">30-Day Trend Projection</h4><div style="height:200px;"><canvas id="chart-mood-forecast"></canvas></div><p class="text-xs text-gray-500 mt-3 pt-3 border-t border-gray-800">Driven by: historic wellness scores. <span class="text-purple-400">↑ Upward</span> = improving behavioral patterns. <span class="text-red-400">↓ Downward</span> = declining wellness requiring attention.</p></div>
                <div class="bg-gray-900 border border-gray-800 rounded-2xl p-6 shadow-lg"><h4 class="font-semibold text-white mb-2">30-Day Stress Trajectory</h4><div style="height:200px;"><canvas id="chart-stress-trend"></canvas></div><p class="text-xs text-gray-500 mt-3 pt-3 border-t border-gray-800">Driven by: physiological stress records. Scale 1–10 ordinal. Sustained readings above <span class="text-yellow-400">5.5</span> correlate with Moderate risk tier transition.</p></div>
                <div class="bg-gray-900 border border-gray-800 rounded-2xl p-6 shadow-lg"><h4 class="font-semibold text-white mb-2">30-Day Sleep/Activity</h4><div style="height:200px;"><canvas id="chart-sleep-proj"></canvas></div><p class="text-xs text-gray-500 mt-3 pt-3 border-t border-gray-800">Driven by: recovery and physical activity vectors. Sleep below <span class="text-blue-400">7h</span> = deficit penalty. Activity below <span class="text-blue-400">60 min</span> = reduced wellness contribution.</p></div>
            </div>
            
            <div id="dashboard-prob-block" class="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6 hidden">
                <div class="bg-gray-900 border border-gray-800 rounded-2xl p-6 shadow-lg">
                    <h4 class="font-semibold text-white mb-4">Risk Indicator</h4>
                    <div class="relative mx-auto" style="height:220px; width:220px;"><canvas id="chart-risk-dist"></canvas></div>
                    <div class="flex justify-center gap-4 mt-3 text-[10px]">
                        <span class="flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-emerald-500"></span><span class="text-gray-400">Low (R&lt;35) — Stable</span></span>
                        <span class="flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-amber-500"></span><span class="text-gray-400">Moderate (35–64)</span></span>
                        <span class="flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-red-500"></span><span class="text-gray-400">High (≥65) — Alert</span></span>
                    </div>
                    <p class="text-xs text-center text-gray-500 mt-2">Based on composite deterministic formula R = Σf(xᵢ) + τ + φ(d,g). Not a clinical diagnosis — behavioral wellness estimate only.</p>
                </div>
                <div id="phase-influence-container" class="bg-gray-900 border border-gray-800 rounded-2xl p-6 shadow-lg ${currentUser && currentUser.profile && currentUser.profile.gender !== 'Female' ? 'hidden' : ''}">
                    <h4 class="font-semibold text-white mb-4">Phase Influence</h4>
                    <div id="phase-bars" class="space-y-4 text-gray-500 text-sm italic">Awaiting rendering...</div>
                    <div class="mt-4 pt-3 border-t border-gray-800">
                        <p class="text-xs text-gray-500">Phase modifier range: <span class="text-emerald-400">Ovulatory −8</span> · <span class="text-green-400">Follicular −5</span> · <span class="text-orange-400">Menstrual +5</span> · <span class="text-red-400">Luteal +8</span></p>
                        <p class="text-xs text-gray-500 mt-1">Based on Baker & Driver (2007) and Kiesner (2012). Hormonal context modulates — does not dominate — the composite score.</p>
                    </div>
                </div>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
                <div class="bg-gray-900 border border-gray-800 rounded-2xl p-6 shadow-xl">
                    <h4 class="font-semibold text-white mb-4">Factor Breakdown</h4>
                    <p class="text-xs text-gray-400 mb-4">Behavioral parameters tracking active metrics driving today's variance:</p>
                    <div class="w-full px-2">
                        <ul id="factor-list" class="space-y-3 text-sm">
                            <li class="flex justify-between text-gray-500"><span>Awaiting breakdown...</span></li>
                        </ul>
                    </div>
                    <div class="mt-4 pt-3 border-t border-gray-800">
                        <p class="text-xs text-gray-500"><span class="text-emerald-400">+ positive</span> = factor is improving wellness. <span class="text-red-400">− negative</span> = factor is elevating risk.</p>
                        <p class="text-xs text-gray-500 mt-1">Weights: Stress 35% · Sleep 25% · Anxiety 20% · Activity 10% · Hydration 5%</p>
                    </div>
                </div>
                <div class="bg-gray-900 border border-gray-800 rounded-2xl p-6 shadow-xl relative overflow-hidden">
                    <div class="absolute -right-10 -bottom-10 w-32 h-32 bg-indigo-500/10 rounded-full blur-2xl"></div>
                    <h4 class="font-semibold text-white mb-4">Personalized Insights</h4>
                    <ul id="rec-list" class="space-y-4 text-gray-300 text-sm">
                        <li class="p-4 bg-gray-800/50 rounded-lg border border-gray-700">Awaiting inference...</li>
                    </ul>
                </div>
            </div>
        </div>
    `;

    requestAnimationFrame(() => {
        let runPayload = lastPrediction;
        
        // Generic Fallback Context
        if (!currentUser && cohortAnalytics) {
            runPayload = {
                charts: {
                    wellness_trend: cohortAnalytics.mood_trend || [3.5, 3.6, 3.4, 3.5, 3.7, 3.6, 3.5],
                    stress_trend: [4, 4.5, 4.2, 4.1, 4.4, 4.6, parseFloat(cohortAnalytics.avg_stress || 4.5)],
                    sleep_trend: [7.1, 7.0, 7.3, 7.2, 6.9, 7.1, 7.0],
                    risk_heatmap: [0.1, 0.12, 0.15, 0.11, 0.14, 0.13, 0.1],
                    risk_distribution: { Low: 65, Moderate: 25, High: 10 },
                    phase_influence: { Menstrual: 10, Follicular: 10, Ovulatory: 10, Luteal: 10 },
                    factor_breakdown: {
                        "Sleep": {score: 7, impact: "+10"}, "Stress": {score: 5, impact: "-5"}, "Activity": {score: 30, impact: "+2"}
                    }
                },
                summary: {
                    summary_sentence: "Population baseline actively monitored.",
                    what_changed_most: "Aggregate Cohort Telemetry",
                    wellness_score: Math.round(parseFloat(cohortAnalytics.avg_wellness || 72))
                },
                recommendation: {
                    action: [{type: "System Ready", priority: "LOW", message: "Login to activate personalized localized trace parameters."}]
                }
            };
        }

        if (runPayload && runPayload.charts) {
            bindDashboardData(runPayload);
        }
    });
}

function bindDashboardData(payload) {
    try {
        const c = payload.charts;
        const p = payload.premium || payload.summary;

        // Apply Logic Thresholds
        const L = (currentUser && currentUser.history) ? currentUser.history.length : 100;
        
        if(L >= 1) {
            document.getElementById('summary-sentence').innerText = p.summary_sentence;
            document.getElementById('what-changed').innerText = "💡 Insight: " + p.what_changed_most;
    
            const ring = document.getElementById('score-ring');
            document.getElementById('score-val').innerText = p.wellness_score;
            const offset = 351 - (351 * (p.wellness_score / 100));
            requestAnimationFrame(() => { ring.style.strokeDashoffset = offset; });
            if(p.wellness_score < 40) ring.classList.replace('text-purple-500', 'text-red-500');
            if(p.wellness_score > 75) ring.classList.replace('text-purple-500', 'text-green-500');
            
            // Factor Breakdown
            const factorList = document.getElementById('factor-list');
            if (c.factor_breakdown) {
                factorList.innerHTML = '';
                for (const [key, val] of Object.entries(c.factor_breakdown)) {
                    let color = val.impact.startsWith('-') ? 'text-red-400' : 'text-green-400';
                    factorList.innerHTML += `
                        <li class="flex justify-between items-center bg-gray-800/50 px-3 py-2 rounded-lg border border-gray-700/50">
                            <span class="text-gray-300 font-medium">${key}</span>
                            <span class="flex gap-3">
                                <span class="text-gray-500 font-mono">w·${val.score}</span>
                                <span class="${color} font-bold w-10 text-right">${val.impact}</span>
                            </span>
                        </li>`;
                }
            }
            
            // Recommendations
            const recList = document.getElementById('rec-list');
            if (payload.recommendation && payload.recommendation.action) {
                recList.innerHTML = '';
                payload.recommendation.action.forEach(rec => {
                    let rCol = 'border-blue-500 text-blue-400';
                    if (rec.priority === "HIGH") rCol = 'border-red-500 text-red-400';
                    else if (rec.priority === "MEDIUM") rCol = 'border-yellow-500 text-yellow-400';
                    recList.innerHTML += `
                        <li class="p-4 bg-gray-800/50 rounded-lg border-l-4 ${rCol}">
                            <div class="font-bold text-xs mb-1">${rec.type.toUpperCase()}</div>
                            <div class="text-gray-300">${rec.message}</div>
                        </li>`;
                });
            }
        }
        
        if (L >= 1) {
            document.getElementById('insight-badge').innerText = "Automated Analytics Active";
            document.getElementById('dashboard-heatmap-block').classList.remove('hidden');
            const heatC = document.getElementById('heatmap-container');
            heatC.innerHTML = '';
            if(c.risk_heatmap) {
                c.risk_heatmap.forEach((val, i) => {
                    const div = document.createElement('div');
                    div.className = 'flex-1 rounded-md transition duration-1000';
                    const g = Math.max(0, 255 - (val * 255));
                    const r = Math.min(255, val * 255 + 50);
                    div.style.backgroundColor = `rgba(${r}, ${g}, 50, 0.8)`;
                    div.style.opacity = 0;
                    heatC.appendChild(div);
                    setTimeout(() => div.style.opacity = 1, i * 100);
                });
            }

            document.getElementById('dashboard-charts-block').classList.remove('hidden');
            let traceMood = c.wellness_trend || c.mood_forecast || [0,0,0,0];
            let traceStress = c.stress_trend || [0,0,0,0];
            let traceSleep = c.sleep_trend || c.sleep_projection || [0,0,0,0];
            buildLineChart('chart-mood-forecast', traceMood, '#a855f7', 'Wellness Trend');
            buildLineChart('chart-stress-trend', traceStress, '#ef4444', 'Stress Trend');
            buildLineChart('chart-sleep-proj', traceSleep, '#3b82f6', 'Sleep Trend');

            document.getElementById('dashboard-prob-block').classList.remove('hidden');
            
            const phaseBars = document.getElementById('phase-bars');
            phaseBars.innerHTML = '';
            if (currentUser && currentUser.profile && currentUser.profile.gender !== 'Female') {
                phaseBars.innerHTML = '<div class="text-center mt-8 text-gray-400 font-mono text-xs">Phase modeling disabled for non-female biology.<br>Telemetry defaults to neutral baseline.</div>';
            } else if(c.phase_influence) {
                Object.entries(c.phase_influence).forEach(([name, val]) => {
                const color = val > 50 ? 'bg-purple-500' : 'bg-gray-700';
                phaseBars.innerHTML += `
                    <div>
                        <div class="flex justify-between text-xs mb-1"><span class="text-gray-300">${name} Phase</span><span class="text-white font-mono">${val}%</span></div>
                        <div class="w-full bg-gray-800 rounded-full h-2"><div class="${color} h-2 rounded-full transition-all duration-1000" style="width: 0%" data-w="${val}%"></div></div>
                    </div>`;
                });
                setTimeout(() => {
                    document.querySelectorAll('#phase-bars > div > div > div.transition-all').forEach(bar => bar.style.width = bar.getAttribute('data-w'));
                }, 50);
            }
            
            const ctxRisk = document.getElementById('chart-risk-dist').getContext('2d');
            if(charts.risk) charts.risk.destroy();
            
            const liveRiskVal = parseInt(payload.summary.latest_risk.replace('%', '')) || 0;
            const currentDist = { Low: liveRiskVal < 35 ? 100 : 0, Moderate: (liveRiskVal >= 35 && liveRiskVal < 65) ? 100 : 0, High: liveRiskVal >= 65 ? 100 : 0 };

            charts.risk = new Chart(ctxRisk, {
                type: 'doughnut',
                data: {
                    labels: ['Low', 'Moderate', 'High Risk'],
                    datasets: [{ data: [currentDist.Low, currentDist.Moderate, currentDist.High], backgroundColor: ['#10b981', '#f59e0b', '#ef4444'], borderWidth: 0 }]
                },
                options: { cutout: '75%', plugins: { legend: { position: 'bottom', labels: {color:'#fff'} } } }
            });
        }
    } catch(e) { console.error("Binding Error:", e); }
}

function buildLineChart(id, dataArr, color, label) {
    const ctx = document.getElementById(id).getContext('2d');
    const grad = ctx.createLinearGradient(0, 0, 0, 200);
    grad.addColorStop(0, color + '66'); grad.addColorStop(1, color + '00');

    if(charts[id]) charts[id].destroy();
    charts[id] = new Chart(ctx, {
        type: 'line',
        data: {
            labels: dataArr.map((_, i) => 'D'+(i+1)),
            datasets: [{ label: label, data: dataArr, borderColor: color, backgroundColor: grad, borderWidth: 3, pointBackgroundColor: '#fff', pointBorderColor: color, fill: true }]
        },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } },
            scales: { y: { display: false, min: 0, max: Math.max(...dataArr)*1.2 }, x: { grid: { display: false } } },
            animation: { y: { duration: 1000, easing: 'easeOutBounce'} }
        }
    });
}

// ============================================
// DAILY LOG
// ============================================
function renderDailyLog(content) {
    content.innerHTML = `
        <div class="max-w-3xl mx-auto animate-fade-in pb-12">
            <div class="text-center mb-8">
                <h3 class="text-3xl font-bold text-white tracking-tight">Signal Injection</h3>
                <p class="text-gray-400 mt-2">Adjust values to trigger generating realtime analytics arrays.</p>
            </div>
            
            <div class="bg-gray-900 border border-gray-800 rounded-2xl p-8 space-y-10 shadow-2xl">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                    <div>
                        <div class="flex justify-between items-center mb-3">
                            <label class="text-sm font-semibold text-white">Sleep Duration</label>
                            <span class="text-sm font-bold text-blue-400 font-mono" id="sleep-display">${formData.sleep_duration} h</span>
                        </div>
                        <input type="range" id="input-sleep" min="0" max="12" step="0.5" value="${formData.sleep_duration}" class="w-full h-2 bg-gray-800 rounded-lg appearance-none cursor-pointer">
                    </div>
                    <div>
                        <div class="flex justify-between items-center mb-3">
                            <label class="text-sm font-semibold text-white">Stress Load</label>
                            <span class="text-sm font-bold text-red-400 font-mono" id="stress-display">${formData.stress_level} / 10</span>
                        </div>
                        <input type="range" id="input-stress" min="1" max="10" value="${formData.stress_level}" class="w-full h-2 bg-gray-800 rounded-lg appearance-none cursor-pointer">
                    </div>
                    <div>
                        <div class="flex justify-between items-center mb-3">
                            <label class="text-sm font-semibold text-white">Physical Activity</label>
                            <span class="text-sm font-bold text-green-400 font-mono" id="activity-display">${formData.physical_activity} m</span>
                        </div>
                        <input type="range" id="input-activity" min="0" max="120" step="5" value="${formData.physical_activity}" class="w-full h-2 bg-gray-800 rounded-lg appearance-none cursor-pointer">
                    </div>
                    <div>
                        <div class="flex justify-between items-center mb-3">
                            <label class="text-sm font-semibold text-white">Anxiety Descriptor</label>
                            <span class="text-sm font-bold text-red-500 font-mono" id="anxiety-display">${formData.anxiety_level} / 10</span>
                        </div>
                        <input type="range" id="input-anxiety" min="1" max="10" value="${formData.anxiety_level}" class="w-full h-2 bg-gray-800 rounded-lg appearance-none cursor-pointer">
                    </div>
                    <div>
                        <div class="flex justify-between items-center mb-3">
                            <label class="text-sm font-semibold text-white">Water Intake (Litres)</label>
                            <span class="text-sm font-bold text-cyan-400 font-mono" id="water-display">${formData.water_intake} L</span>
                        </div>
                        <input type="range" id="input-water" min="0" max="5" step="0.5" value="${formData.water_intake}" class="w-full h-2 bg-gray-800 rounded-lg appearance-none cursor-pointer">
                    </div>
                    <div id="cycle-wrapper" class="${formData.gender !== 'Female' ? 'hidden' : ''}">
                        <div class="flex justify-between items-center mb-3">
                            <label class="text-sm font-semibold text-white">Cycle Day</label>
                            <span class="text-sm font-bold text-pink-400 font-mono" id="cycle-display">Day ${formData.cycle_day}</span>
                        </div>
                        <input type="range" id="input-cycle" min="0" max="35" value="${formData.cycle_day}" class="w-full h-2 bg-gray-800 rounded-lg appearance-none cursor-pointer">
                    </div>
                </div>

                <div class="bg-gray-800/40 border border-gray-700/50 rounded-xl p-4 text-center">
                    <p class="text-xs text-gray-400 tracking-wide font-mono">Behavioral Inference Inputs: Sleep, Stress, Activity, Anxiety, Hydration, Cycle Context</p>
                </div>

                <div class="flex items-center gap-4 pt-6 border-t border-gray-800">
                    <button id="predict-btn" class="w-full bg-gradient-to-r from-purple-600 to-indigo-600 text-white font-bold text-lg px-6 py-4 rounded-xl shadow-lg transition-transform hover:-translate-y-1">
                        Evaluate Tensors
                    </button>
                </div>
                
                <div class="text-center h-8">
                    <div id="loading" class="hidden flex items-center justify-center gap-3">
                        <div class="spinner border-t-white"></div>
                        <span class="text-sm font-medium text-white tracking-widest uppercase">Processing...</span>
                    </div>
                </div>
            </div>
        </div>
    `;

    document.getElementById('input-sleep').addEventListener('input', e => { formData.sleep_duration = parseFloat(e.target.value); document.getElementById('sleep-display').textContent = e.target.value + ' h'; });
    document.getElementById('input-stress').addEventListener('input', e => { formData.stress_level = parseInt(e.target.value); document.getElementById('stress-display').textContent = e.target.value + ' / 10'; });
    document.getElementById('input-activity').addEventListener('input', e => { formData.physical_activity = parseInt(e.target.value); document.getElementById('activity-display').textContent = e.target.value + ' m'; });
    document.getElementById('input-cycle').addEventListener('input', e => { formData.cycle_day = parseInt(e.target.value); document.getElementById('cycle-display').textContent = 'Day ' + e.target.value; });
    document.getElementById('input-anxiety').addEventListener('input', e => { formData.anxiety_level = parseInt(e.target.value); document.getElementById('anxiety-display').textContent = e.target.value + ' / 10'; });
    document.getElementById('input-water').addEventListener('input', e => { formData.water_intake = parseFloat(e.target.value); document.getElementById('water-display').textContent = e.target.value + ' L'; });

    document.getElementById('predict-btn').addEventListener('click', runPrediction);
}

async function runPrediction() {
    const loading = document.getElementById('loading');
    const predictBtn = document.getElementById('predict-btn');
    loading.classList.remove('hidden'); predictBtn.disabled = true;

    const payload = { 
        "Sleep Duration": formData.sleep_duration, 
        "Stress Level": formData.stress_level, 
        "Physical Activity Level": formData.physical_activity, 
        "Cycle_Day": formData.cycle_day, 
        "Base_Cycle_Length": formData.base_cycle, 
        "anxiety_level": formData.anxiety_level,
        "water_intake": formData.water_intake
    };

        if (currentUser) payload["username"] = currentUser.user || "Guest";

    try {
        const response = await fetch(`${API_BASE}/predict`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
        if (response.ok) {
            lastPrediction = await response.json();
            if(currentUser) currentUser = lastPrediction;
            sessionStorage.setItem('luna_user', JSON.stringify(lastPrediction));
            setTimeout(() => navigateTo('dashboard'), 400);
        } else { alert("API Error. Ensure API is running."); }
    } catch (e) {
        alert("Fetch failed. Is the Python server running?");
    } finally {
        loading.classList.add('hidden'); predictBtn.disabled = false;
    }
}

// ============================================
// ANALYTICS (Cohort Averages)
// ============================================
async function renderAnalytics(content) {
    content.innerHTML = `<div class="flex justify-center mt-20"><div class="spinner w-8 h-8"></div></div>`;
    
    // Fetch if missing
    if(!cohortAnalytics) await fetchCohortData();
    
    if(!cohortAnalytics) {
        content.innerHTML = `<div class="text-center text-red-400 mt-20">Backend Offline. Cohort missing.</div>`;
        return;
    }
    
    const cd = cohortAnalytics;

    content.innerHTML = `
        <div class="animate-fade-in pb-12">
            <h3 class="text-2xl font-bold bg-gradient-to-r from-purple-400 to-indigo-400 bg-clip-text text-transparent mb-2">Population Analytics</h3>
            <p class="text-gray-400 mb-8">Aggregating ${cd.total_population} pseudo-users across statistical baselines.</p>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                <div class="bg-gray-900 border border-gray-800 shadow-xl rounded-2xl p-6 relative">
                    <h4 class="text-sm font-semibold text-gray-400">Mean Population Wellness</h4>
                    <div class="text-4xl font-bold text-white mt-2">${cd.avg_wellness} <span class="text-sm font-normal text-purple-500">/ 100</span></div>
                </div>
                <div class="bg-gray-900 border border-gray-800 shadow-xl rounded-2xl p-6">
                    <h4 class="text-sm font-semibold text-gray-400">Average Stress Vector</h4>
                    <div class="text-4xl font-bold text-white mt-2">${cd.avg_stress} <span class="text-sm font-normal text-red-500">/ 10</span></div>
                </div>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div class="bg-gray-900 border border-gray-800 rounded-2xl p-6 shadow-xl">
                    <h4 class="font-semibold text-white mb-4">Mood Trajectory (7-day Average)</h4>
                    <div style="height:250px;"><canvas id="chart-pop-mood"></canvas></div>
                </div>
                <div class="bg-gray-900 border border-gray-800 rounded-2xl p-6 shadow-xl">
                    <h4 class="font-semibold text-white mb-4">Stress Segmentation</h4>
                    <div style="height:250px;"><canvas id="chart-pop-stress"></canvas></div>
                </div>
            </div>
        </div>
    `;

    requestAnimationFrame(() => {
        buildLineChart('chart-pop-mood', cd.mood_trend, '#a855f7', 'Population Mood');
        
        charts.popStress = new Chart(document.getElementById('chart-pop-stress').getContext('2d'), {
            type: 'bar',
            data: {
                labels: Object.keys(cd.stress_distribution),
                datasets: [{ label: 'Users', data: Object.values(cd.stress_distribution), backgroundColor: '#ef4444' }]
            },
            options: { responsive: true, maintainAspectRatio: false, plugins: {legend:{display:false}} }
        });
    });
}

// ============================================
// MODEL INSIGHTS
// ============================================
async function renderModelInsights(content) {
    content.innerHTML = `<div class="flex justify-center mt-20"><div class="spinner w-8 h-8"></div></div>`;
    
    try {
        const res = await fetch(`${API_BASE}/insights`);
        if(!res.ok) throw new Error("API Exception");
        const data = await res.json();
        
        content.innerHTML = `
            <div class="animate-fade-in pb-12">
                <h3 class="text-2xl font-bold text-white mb-4">Model Diagnostics</h3>
                <div class="grid grid-cols-2 gap-6 mb-8">
                    <div class="bg-gray-900 border border-gray-800 rounded-2xl p-6 border-l-4 border-l-green-500">
                        <h4 class="text-sm text-gray-400">Classification AUC</h4>
                        <div class="text-3xl font-bold text-green-400 mt-2">${data.metrics.classification_auc}</div>
                    </div>
                    <div class="bg-gray-900 border border-gray-800 rounded-2xl p-6 border-l-4 border-l-purple-500">
                        <h4 class="text-sm text-gray-400">Regression RMSE</h4>
                        <div class="text-3xl font-bold text-purple-400 mt-2">${data.metrics.regression_rmse}</div>
                    </div>
                </div>
                
                <div class="bg-gray-900 border border-gray-800 rounded-2xl p-6 shadow-xl">
                    <h4 class="font-semibold text-white mb-4">Relative Feature Importance</h4>
                    <div style="height:250px;"><canvas id="chart-importance"></canvas></div>
                </div>
            </div>
        `;

        requestAnimationFrame(() => {
            charts.importance = new Chart(document.getElementById('chart-importance').getContext('2d'), {
                type: 'bar',
                data: {
                    labels: Object.keys(data.feature_importance),
                    datasets: [{ label: 'Impact %', data: Object.values(data.feature_importance), backgroundColor: '#8b5cf6' }]
                },
                options: { indexAxis: 'y', responsive: true, maintainAspectRatio: false, plugins: {legend:{display:false}} }
            });
        });
    } catch(e) {
        content.innerHTML = `<div class="text-center text-red-500 mt-20">Backend Offline. Deploy Flask Server.</div>`;
    }
}

// ============================================
// RESEARCH MODE
// ============================================
function renderResearchMode(content) {
    const userCount = cohortRecords.length ? cohortRecords.length : 100;
    
    content.innerHTML = `
        <div class="animate-fade-in pb-12 max-w-5xl mx-auto">
            <div class="mb-10 text-center">
                <h3 class="text-4xl font-bold bg-gradient-to-r from-purple-400 to-indigo-400 bg-clip-text text-transparent mb-4">Luna Aura: Academic Framework & Methodology</h3>
                <p class="text-gray-400 text-lg max-w-3xl mx-auto leading-relaxed">
                    This document explicitly details the mathematical, inferential, and infrastructural topology driving the Luna Aura platform.
                </p>
            </div>
            
            <div class="space-y-8">
                <!-- Data Strategy & Privacy -->
                <div class="bg-gray-900 border border-gray-800 rounded-2xl p-8 overflow-hidden relative shadow-lg">
                    <div class="absolute -right-6 -top-6 w-32 h-32 bg-indigo-500/10 rounded-full blur-2xl"></div>
                    <h4 class="text-xl font-bold text-white mb-4 flex items-center gap-3"><span class="text-indigo-400">01.</span> Data Infrastructure & SQL Schema</h4>
                    <p class="text-gray-400 leading-relaxed text-sm mb-6">
                        The platform operates defensively using localized SQLite mapping. Demographic arrays (Age, Gender) explicitly bound to the primary <code>users</code> table to prevent temporal degradation, while behavioral telemetry maps strictly to <code>user_history</code>. Active tracking covers <strong class="text-white">${userCount} synchronized profiles</strong>.
                    </p>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div class="bg-gray-800/80 p-4 rounded-lg border border-gray-700">
                            <div class="text-xs font-bold uppercase tracking-widest text-indigo-400 mb-2">Table: users (Static Identity)</div>
                            <ul class="text-sm font-mono text-gray-300 space-y-1">
                                <li>id (int, Primary Key)</li>
                                <li>username, password_hash (text)</li>
                                <li>age (int), gender (text)</li>
                                <li>height_cm, weight_kg (float)</li>
                                <li>cycle_length, sleep_target (float)</li>
                            </ul>
                        </div>
                        <div class="bg-gray-800/80 p-4 rounded-lg border border-gray-700">
                            <div class="text-xs font-bold uppercase tracking-widest text-purple-400 mb-2">Table: user_history (Temporal)</div>
                            <ul class="text-sm font-mono text-gray-300 space-y-1">
                                <li>id (int, Primary Key)</li>
                                <li>user_id (int, Foreign Key)</li>
                                <li>date (datetime)</li>
                                <li>sleep_duration, stress_level (float/int)</li>
                                <li>activity, anxiety_level (int)</li>
                                <li>wellness_score, predicted_risk (derived)</li>
                            </ul>
                        </div>
                    </div>
                </div>

                <!-- Equations & Factor Modeling -->
                <div class="bg-gray-900 border border-gray-800 rounded-2xl p-8 shadow-lg">
                    <h4 class="text-xl font-bold text-white mb-4 flex items-center gap-3"><span class="text-emerald-400">02.</span> Ground-Truth Weightages & Exact Formulas</h4>
                    <p class="text-gray-400 leading-relaxed text-sm mb-6">
                        Before passing vectors to the ML engine, the system utilizes an explicit foundational heuristic equation generating a baseline <code>Wellness Score [0-100]</code>. This ensures mathematical stability regardless of model latency.
                    </p>
                    
                    <div class="bg-gray-800 rounded-xl p-5 mb-6 text-sm overflow-x-auto text-gray-300 border border-gray-700">
                        <span class="block text-emerald-400 font-bold mb-2">Final Weighting Framework:</span>
                        <code>Wellness = (Sleep 25%) + (Stress 20%) + (Activity 15%) + (Anxiety 15%) + (Water 5%) + (Age Context 5%) + (Cycle Context 10%) + (Stability Adjustment 5%)</code>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mt-4 opacity-90">
                        <div>
                            <h5 class="text-sm font-bold text-gray-300 mb-2">Core Penalty Deductions:</h5>
                            <ul class="text-sm text-gray-400 space-y-2 list-disc list-inside">
                                <li><strong>Sleep Context:</strong> (7 - hours) × 5 points deducted if hours &lt; 7. Optimal bounds: 7-9 hours.</li>
                                <li><strong>Stress Penalty:</strong> (level - 2) × 6 deducted if level &gt; 2.</li>
                                <li><strong>Activity Deficit:</strong> (30 - activity_mins) × 0.5 deducted if mins &lt; 30.</li>
                                <li><strong>Anxiety Penalty:</strong> higher anxiety dynamically limits upper bound wellness tracking.</li>
                            </ul>
                        </div>
                        <div>
                            <h5 class="text-sm font-bold text-gray-300 mb-2">Phase Mapping (Non-Diagnostic):</h5>
                            <ul class="text-sm text-gray-400 space-y-2 list-disc list-inside">
                                <li><strong>Hormonal Context Proxy:</strong> Derived mathematically via <code class="bg-gray-800 px-1 py-0.5 rounded text-xs">sin(current_day / base_length * 2pi)</code></li>
                                <li><strong>Cycle Sensitivity:</strong> Modulates final score softly (±2 points). It serves as context, not a deterministic outcome generator.</li>
                            </ul>
                        </div>
                    </div>
                </div>

                <!-- Machine Learning -->
                <div class="bg-gray-900 border border-gray-800 rounded-2xl p-8 shadow-lg">
                    <h4 class="text-xl font-bold text-white mb-4 flex items-center gap-3"><span class="text-blue-400">03.</span> Machine Learning Pipeline (Random Forest)</h4>
                    <p class="text-gray-400 leading-relaxed text-sm mb-4">
                        A proprietary ensemble <code>RandomForestRegressor</code> is trained dynamically bridging the gap between localized physiological signals and broader cohort variance.
                    </p>
                    <ul class="text-sm text-gray-400 space-y-3 list-disc list-inside mb-6 bg-gray-800/50 p-6 rounded-lg border border-gray-700/50">
                        <li><strong>Inference Generation:</strong> Transforms discrete (Stress Level: 5) inputs into a probabilistic <code>Risk Probability Estimate</code>.</li>
                        <li><strong>Feature Representation:</strong> The model maps inputs like [Age, Factor(Gender), Sleep, Stress, HormoneProxy] through dense trees to isolate non-linear thresholds (e.g. at what sleep deficit does stress compound exponentially?).</li>
                        <li><strong>Visualizations:</strong> The <em>30-Day Projective Trend</em> charts and <em>Heatmaps</em> process exact array extractions pushed gracefully via Chart.js canvas elements. Missing indices default into sequence constraints blocking visualization rendering until baseline lengths are hit.</li>
                    </ul>
                </div>

                <!-- Assumptions and Ethics -->
                <div class="bg-gray-900 border border-l-4 border-l-yellow-500 border-gray-800 rounded-2xl p-8 shadow-2xl relative">
                    <h4 class="text-xl font-bold text-white mb-4">Limitations, Disclaimers & Assumptions</h4>
                    <div class="text-sm text-gray-400 space-y-4">
                        <p>
                            <strong class="text-yellow-400">Estimation, Not Diagnosis:</strong> Luna Aura estimates Behavioral Wellness based exclusively on explicitly reported lifestyle variables. The AI output acts strictly as a "Behavioral Wellness Estimate" or "Risk Probability Estimate". It makes no claims to diagnose, prescribe, or clinically evaluate psychiatric conditions.
                        </p>
                        <p>
                            <strong class="text-yellow-400">Age Context Non-Discrimination:</strong> Age modifications exist purely to smooth baseline mathematical variance parameters, preventing false-flag volatility mapping. It applies universally as non-discriminatory stabilization noise.
                        </p>
                        <p>
                            <strong class="text-yellow-400">Cycle Dynamics Assumptions:</strong> Cycle variance maps to established biological rhythms, assuming a normal harmonic sequence. Actual patient biology may drastically differ; the model interprets timeline context as a general behavioral modifier layer, entirely constrained within a strict 10% maximum factor weight penalty limit.
                        </p>
                    </div>
                </div>

                <!-- Transparency: Real vs Simulated -->
                <div class="bg-gray-900 border border-gray-800 rounded-2xl p-8 shadow-lg">
                    <h4 class="text-xl font-bold text-white mb-4 flex items-center gap-3"><span class="text-teal-400">04.</span> Transparency: Real vs Simulated Data</h4>
                    <p class="text-gray-400 leading-relaxed text-sm mb-4">
                        To protect privacy and ensure a robust testing environment, Luna Aura uses a hybrid data pipeline bridging real user activity with synthetic distributions:
                    </p>
                    <ul class="text-sm text-gray-400 space-y-3 list-disc list-inside bg-gray-800/50 p-6 rounded-lg border border-gray-700/50">
                        <li><strong>Real Data (Your Inputs):</strong> When you use "Inject Signal", the platform securely stores your exact inputs directly onto your local database. These inputs actively shape your baseline logic instantly.</li>
                        <li><strong>Simulated Data (Cohort Generation):</strong> To allow immediate exploration without waiting 30 days for data maturity, the platform initializes with a mathematically constrained 100-user pseudo-cohort. These synthetic users feature logical bounding (e.g. stress negatively impacts sleep uniformly) mimicking true PHQ metrics strictly for demonstration purposes.</li>
                    </ul>
                </div>

                <!-- Academic References & Citations -->
                <div class="bg-gray-900 border border-gray-800 rounded-2xl p-8 shadow-lg">
                    <h4 class="text-xl font-bold text-white mb-4 flex items-center gap-3"><span class="text-gray-400">05.</span> Academic References & Citations</h4>
                    <p class="text-gray-500 leading-relaxed text-sm mb-6">
                        The heuristic thresholds and algorithmic structure driving Luna Aura's risk mapping are informed by established clinical and academic research standards.
                    </p>
                    <div class="text-sm text-gray-400 space-y-4">
                        <div>
                            <strong class="text-white">Sleep Science:</strong> 
                            <p class="mt-1 italic">Hirshkowitz, M., et al. (2015). "National Sleep Foundation's updated sleep duration recommendations". Sleep Health. Validates the 7-9 hour optimal boundary.</p>
                        </div>
                        <div>
                            <strong class="text-white">Physical Activity & Stress:</strong> 
                            <p class="mt-1 italic">Schuch, F. B., et al. (2018). "Physical Activity and Incident Depression: A Meta-Analysis of Prospective Cohort Studies". American Journal of Psychiatry. Informs the activity deficit penalty floor.</p>
                        </div>
                        <div>
                            <strong class="text-white">PHQ Background:</strong> 
                            <p class="mt-1 italic">Kroenke, K., et al. (2001). "The PHQ-9: validity of a brief depression severity measure". Journal of General Internal Medicine. Frames the severity distributions without directly diagnosing.</p>
                        </div>
                        <div>
                            <strong class="text-white">Explainable AI (XAI):</strong> 
                            <p class="mt-1 italic">Lundberg, S. M., & Lee, S. I. (2017). "A unified approach to interpreting model predictions". Advances in Neural Information Processing Systems. Drives the feature attribution breakdown model.</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// Initial Boot Call Wait
document.addEventListener('DOMContentLoaded', checkAuth);
// ============================================
// PROFILE SETTINGS
// ============================================
function renderProfileSettings(content) {
    if (!currentUser || !currentUser.profile) {
        content.innerHTML = `<div class="text-center text-red-500 mt-20 font-bold">Unauthenticated.</div>`;
        return;
    }
    const p = currentUser.profile;
    content.innerHTML = `
        <div class="max-w-3xl mx-auto animate-fade-in pb-12">
            <div class="text-center mb-8">
                <h3 class="text-3xl font-bold text-white tracking-tight">Static Profile Config</h3>
                <p class="text-gray-400 mt-2">Adjusting these parameters radically shifts your behavioral projection baseline.</p>
            </div>
            
            <div class="bg-gray-900 border border-gray-800 rounded-2xl p-8 shadow-2xl">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div><label class="block text-sm font-medium text-gray-300 mb-1">Age</label>
                    <input type="number" id="set-age" class="w-full bg-gray-800 border border-gray-700 rounded px-4 py-2 text-white" value="${p.age}"></div>
                    
                    <div><label class="block text-sm font-medium text-gray-300 mb-1">Gender</label>
                    <select id="set-gender" class="w-full bg-gray-800 border border-gray-700 rounded px-4 py-2 text-white">
                        <option value="Female" ${p.gender === 'Female' ? 'selected':''}>Female</option>
                        <option value="Male" ${p.gender === 'Male' ? 'selected':''}>Male</option>
                        <option value="Other" ${p.gender === 'Other' ? 'selected':''}>Other</option>
                    </select></div>
                    
                    <div><label class="block text-sm font-medium text-gray-300 mb-1">Height (cm)</label>
                    <input type="number" id="set-height" class="w-full bg-gray-800 border border-gray-700 rounded px-4 py-2 text-white" value="${p.height_cm}"></div>
                    
                    <div><label class="block text-sm font-medium text-gray-300 mb-1">Weight (kg)</label>
                    <input type="number" id="set-weight" class="w-full bg-gray-800 border border-gray-700 rounded px-4 py-2 text-white" value="${p.weight_kg}"></div>
                    
                    <div><label class="block text-sm font-medium text-gray-300 mb-1">Sleep Target (Hours)</label>
                    <input type="number" step="0.5" id="set-sleep" class="w-full bg-gray-800 border border-gray-700 rounded px-4 py-2 text-white" value="${p.sleep_target}"></div>
                    
                    <div id="set-cycle-wrapper" class="${p.gender !== 'Female' ? 'hidden' : ''}"><label class="block text-sm font-medium text-gray-300 mb-1">Cycle Length (Days)</label>
                    <input type="number" id="set-cycle" class="w-full bg-gray-800 border border-gray-700 rounded px-4 py-2 text-white" value="${p.cycle_length}"></div>
                </div>
                
                <div id="set-msg" class="hidden text-green-400 text-sm text-center font-medium mt-6"></div>
                <div class="mt-8 flex justify-end">
                    <button id="save-profile-btn" class="bg-purple-600 hover:bg-purple-500 text-white font-bold py-2 px-8 rounded-lg shadow-lg transition">Save Baseline</button>
                </div>
            </div>
        </div>
    `;

    document.getElementById('set-gender').addEventListener('change', (e) => {
        document.getElementById('set-cycle-wrapper').classList.toggle('hidden', e.target.value !== 'Female');
    });

    document.getElementById('save-profile-btn').addEventListener('click', async () => {
        const payload = {
            username: p.username,
            age: document.getElementById('set-age').value,
            gender: document.getElementById('set-gender').value,
            height_cm: document.getElementById('set-height').value,
            weight_kg: document.getElementById('set-weight').value,
            sleep_target: document.getElementById('set-sleep').value,
            cycle_length: document.getElementById('set-cycle').value
        };
        const msg = document.getElementById('set-msg');
        msg.classList.add('hidden');
        try {
            const res = await fetch(`${API_BASE}/profile`, { method: 'PUT', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload) });
            if (res.ok) {
                const refreshed = await res.json();
                currentUser = refreshed;
                lastPrediction = refreshed;
                sessionStorage.setItem('luna_user', JSON.stringify(refreshed));
                msg.innerText = "Profile updated securely.";
                msg.classList.replace('text-red-400', 'text-green-400');
                msg.classList.remove('hidden');
                checkAuth(); // Updates the header
            } else { throw new Error('API failure'); }
        } catch(e) {
            msg.innerText = "Error saving profile.";
            msg.classList.replace('text-green-400', 'text-red-400');
            msg.classList.remove('hidden');
        }
    });
}
