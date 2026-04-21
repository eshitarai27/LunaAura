const API_BASE = 'http://localhost:5001';

let currentUser = null;
let currentPage = 'dashboard';
let charts = {};
let dataHistory = [];
let cohortAnalytics = null;
let cohortRecords = [];

let formData = { age: 26, gender: 'Female', sleep_duration: 7, stress_level: 2, physical_activity: 30, cycle_day: 14, base_cycle: 28, anxiety_level: 5, water_intake: 4 };
let lastPrediction = null;

function isLocalStorageAvailable() { try { localStorage.setItem('X', 'X'); localStorage.removeItem('X'); return true; } catch(e) { return false; } }

function checkAuth() {
    const authC = document.getElementById('auth-container');
    const appC = document.getElementById('app-container');
    appC.style.display = 'flex'; // ALWAYS visible
    authC.style.display = 'none';

    if (!isLocalStorageAvailable()) { initializeAuth(); return; }

    const user = localStorage.getItem('luna_user');
    const toggleBtn = document.getElementById('auth-toggle-btn');

    if (user) {
        currentUser = JSON.parse(user);
        toggleBtn.innerText = 'Logout';
        toggleBtn.onclick = logout;
        if (currentUser.history && currentUser.history.length > 0) {
            dataHistory = currentUser.history;
            lastPrediction = currentUser; // Explicitly map uniform API Payload object natively
        }
    } else {
        currentUser = null;
        toggleBtn.innerText = 'Login';
        toggleBtn.onclick = () => { authC.style.display = 'flex'; };
    }
    initializeAuth();
    initializeApp();
}

function initializeAuth() {
    document.getElementById('auth-login-btn').addEventListener('click', login);
    const signupBtn = document.getElementById('auth-signup-btn');
    if(signupBtn) signupBtn.addEventListener('click', () => { 
        document.getElementById('auth-container').style.display = 'none'; 
    }); // Close overlay
}

async function login() {
    const u = document.getElementById('auth-username').value.trim();
    if (!u) return;
    
    document.getElementById('auth-error').classList.add('hidden');
    
    try {
        const response = await fetch(`${API_BASE}/user/${u}`);
        if(response.ok) {
            const payload = await response.json();
            localStorage.setItem('luna_user', JSON.stringify(payload));
            currentUser = payload;
            lastPrediction = payload;
            document.getElementById('auth-container').style.display = 'none';
            checkAuth(); // Re-verify auth locally!
            navigateTo('dashboard'); // Render cleanly natively without refresh bugs!
        } else {
            document.getElementById('auth-error').classList.remove('hidden');
        }
    } catch(e) {
        document.getElementById('auth-error').innerText = "Server Error. Ensure Python backend is running.";
        document.getElementById('auth-error').classList.remove('hidden');
    }
}

function logout() { 
    localStorage.removeItem('luna_user'); 
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
    }
}

// ============================================
// DASHBOARD
// ============================================
function renderDashboard(content) {
    content.innerHTML = `
        <div class="space-y-6 animate-fade-in pb-12">
            <div class="flex justify-between items-center bg-gray-900 border border-gray-800 p-4 rounded-xl shadow-lg">
                <h3 class="text-xl font-bold bg-gradient-to-r from-purple-400 to-indigo-400 bg-clip-text text-transparent">Telemetry Dashboard</h3>
                <button onclick="navigateTo('daily-log')" class="text-sm bg-purple-600 px-6 py-2 rounded-lg text-white font-medium hover:bg-purple-500 transition shadow-lg shadow-purple-900/40">Inject Signal</button>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div class="md:col-span-3 bg-gradient-to-r from-gray-900 to-gray-800 border-l-4 border-purple-500 rounded-2xl p-8 relative overflow-hidden shadow-2xl">
                    <div class="absolute -right-10 -top-10 w-40 h-40 bg-purple-500/10 rounded-full blur-3xl"></div>
                    <h4 class="text-xs font-semibold uppercase tracking-widest text-purple-400 mb-2">Automated Insight</h4>
                    <div id="summary-sentence" class="text-3xl font-bold text-white leading-tight">Waiting for dataset.</div>
                    <div id="what-changed" class="text-sm mt-4 text-gray-400 bg-gray-900/50 inline-block px-4 py-2 rounded-lg border border-gray-700 font-mono">Navigate to 'Inject Signal' to populate.</div>
                </div>
                
                <div class="bg-gray-900 border border-gray-800 rounded-2xl p-6 flex flex-col items-center justify-center shadow-xl relative">
                    <h4 class="text-sm font-semibold text-gray-400 absolute top-6 left-6">Wellness Score</h4>
                    <div class="relative w-32 h-32 mt-6">
                        <svg class="w-full h-full transform -rotate-90">
                            <circle cx="64" cy="64" r="56" stroke="currentColor" stroke-width="8" fill="transparent" class="text-gray-800"/>
                            <circle id="score-ring" cx="64" cy="64" r="56" stroke="currentColor" stroke-width="8" fill="transparent" stroke-dasharray="351" stroke-dashoffset="351" class="text-purple-500 transition-all duration-1000 ease-out"/>
                        </svg>
                        <div class="absolute inset-0 flex items-center justify-center text-3xl font-bold text-white" id="score-val">0</div>
                    </div>
                </div>
            </div>

            <div class="bg-gray-900 border border-gray-800 rounded-2xl p-6 shadow-xl">
                <h4 class="text-sm font-semibold text-gray-400 mb-2">7-Day Risk Momentum Heatmap</h4>
                <div id="heatmap-container" class="flex justify-between gap-2 h-12 mb-2">
                    <div class="flex-1 bg-gray-800 rounded-md"></div><div class="flex-1 bg-gray-800 rounded-md"></div><div class="flex-1 bg-gray-800 rounded-md"></div><div class="flex-1 bg-gray-800 rounded-md"></div><div class="flex-1 bg-gray-800 rounded-md"></div><div class="flex-1 bg-gray-800 rounded-md"></div><div class="flex-1 bg-gray-800 rounded-md"></div>
                </div>
                <p class="text-xs text-gray-500">Driven by: model risk probability + recent volatility variance.</p>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
                <div class="bg-gray-900 border border-gray-800 rounded-2xl p-6 shadow-lg"><h4 class="font-semibold text-white mb-2">30-Day Wellness Trend</h4><div style="height:200px;"><canvas id="chart-mood-forecast"></canvas></div><p class="text-xs text-gray-500 mt-3 pt-3 border-t border-gray-800">Driven by: historic wellness scores + rolling analytics.</p></div>
                <div class="bg-gray-900 border border-gray-800 rounded-2xl p-6 shadow-lg"><h4 class="font-semibold text-white mb-2">30-Day Stress Trajectory</h4><div style="height:200px;"><canvas id="chart-stress-trend"></canvas></div><p class="text-xs text-gray-500 mt-3 pt-3 border-t border-gray-800">Driven by: actual physiological stress records.</p></div>
                <div class="bg-gray-900 border border-gray-800 rounded-2xl p-6 shadow-lg"><h4 class="font-semibold text-white mb-2">30-Day Sleep/Activity Trajectory</h4><div style="height:200px;"><canvas id="chart-sleep-proj"></canvas></div><p class="text-xs text-gray-500 mt-3 pt-3 border-t border-gray-800">Driven by: true recovery and physical activity vectors.</p></div>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
                <div class="bg-gray-900 border border-gray-800 rounded-2xl p-6 shadow-lg">
                    <h4 class="font-semibold text-white mb-4">Risk Probability</h4>
                    <div class="relative mx-auto" style="height:220px; width:220px;"><canvas id="chart-risk-dist"></canvas></div>
                    <p class="text-xs text-center text-gray-500 mt-4">Driven by: Distributed native regression outputs mapping severity bounds.</p>
                </div>
                <div class="bg-gray-900 border border-gray-800 rounded-2xl p-6 shadow-lg">
                    <h4 class="font-semibold text-white mb-4">Phase Influence</h4>
                    <div id="phase-bars" class="space-y-4 text-gray-500 text-sm italic">Awaiting rendering...</div>
                    <p class="text-xs text-gray-500 mt-6 pt-3 border-t border-gray-800">Driven by: current predicted impact based on generic menstrual cycle boundaries.</p>
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
                </div>
                <div class="bg-gray-900 border border-gray-800 rounded-2xl p-6 shadow-xl relative overflow-hidden">
                    <div class="absolute -right-10 -bottom-10 w-32 h-32 bg-indigo-500/10 rounded-full blur-2xl"></div>
                    <h4 class="font-semibold text-white mb-4">Recovery Recommendations</h4>
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
                    mood_forecast: cohortAnalytics.mood_trend || [3.5, 3.6, 3.4, 3.5, 3.7, 3.6, 3.5],
                    stress_trend: [4, 4.5, 4.2, 4.1, 4.4, 4.6, parseFloat(cohortAnalytics.avg_stress || 4.5)],
                    sleep_projection: [7.1, 7.0, 7.3, 7.2, 6.9, 7.1, 7.0],
                    risk_distribution: { Low: 65, Moderate: 25, High: 10 },
                    phase_impact: { Menstrual: 10, Follicular: 10, Ovulatory: 10, Luteal: 10 }
                },
                premium: {
                    summary_sentence: "Population baseline actively monitored.",
                    what_changed_most: "Aggregate Cohort Telemetry",
                    wellness_score: Math.round(parseFloat(cohortAnalytics.avg_wellness || 72)),
                    factor_breakdown: { "Cohort Size": { score: cohortAnalytics.total_population || 100, impact: "+100" } },
                    risk_heatmap: [0.1, 0.12, 0.15, 0.11, 0.14, 0.13, 0.1]
                },
                recommendation: {
                    action: [{type: "System Ready", priority: "LOW", message: "Login to activate personalized localized trace parameters."}]
                }
            };
        }

        if (runPayload && runPayload.charts) {
            bindDashboardData(runPayload);
        } else {
            buildLineChart('chart-mood-forecast', [0,0,0,0,0,0,0], '#4b5563', 'Awaiting Data');
            buildLineChart('chart-stress-trend', [0,0,0,0,0,0,0], '#4b5563', 'Awaiting Data');
            buildLineChart('chart-sleep-proj', [0,0,0,0,0,0,0], '#4b5563', 'Awaiting Data');
        }
    });
}

function bindDashboardData(payload) {
    try {
        const c = payload.charts;
        const p = payload.premium || payload.summary;

        document.getElementById('summary-sentence').innerText = p.summary_sentence;
        document.getElementById('what-changed').innerText = "💡 Insight: " + p.what_changed_most;

        const ring = document.getElementById('score-ring');
        document.getElementById('score-val').innerText = p.wellness_score;
        const offset = 351 - (351 * (p.wellness_score / 100));
        requestAnimationFrame(() => { ring.style.strokeDashoffset = offset; });
        if(p.wellness_score < 40) ring.classList.replace('text-purple-500', 'text-red-500');
        if(p.wellness_score > 75) ring.classList.replace('text-purple-500', 'text-green-500');

        // Dynamically bind factor breakdown traces
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
        
        // Dynamically bind recommendations
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
            });
        }

        const phaseBars = document.getElementById('phase-bars');
        phaseBars.innerHTML = '';
        if(c.phase_influence) {
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

        let traceMood = c.wellness_trend || c.mood_forecast || [0,0,0,0];
        let traceStress = c.stress_trend || [0,0,0,0];
        let traceSleep = c.sleep_trend || c.sleep_projection || [0,0,0,0];

        buildLineChart('chart-mood-forecast', traceMood, '#a855f7', 'Wellness Trend');
        buildLineChart('chart-stress-trend', traceStress, '#ef4444', 'Stress Trend');
        buildLineChart('chart-sleep-proj', traceSleep, '#3b82f6', 'Sleep Trend');

        const ctxRisk = document.getElementById('chart-risk-dist').getContext('2d');
        if(charts.risk) charts.risk.destroy();
        charts.risk = new Chart(ctxRisk, {
            type: 'doughnut',
            data: {
                labels: ['Low', 'Moderate', 'High Risk'],
                datasets: [{ data: [c.risk_distribution.Low, c.risk_distribution.Moderate, c.risk_distribution.High], backgroundColor: ['#10b981', '#f59e0b', '#ef4444'], borderWidth: 0 }]
            },
            options: { cutout: '75%', plugins: { legend: { position: 'bottom', labels: {color:'#fff'} } } }
        });
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
                            <label class="text-sm font-semibold text-white">Age (Years)</label>
                            <span class="text-sm font-bold text-gray-300 font-mono" id="age-display">${formData.age}</span>
                        </div>
                        <input type="range" id="input-age" min="18" max="80" value="${formData.age}" class="w-full h-2 bg-gray-800 rounded-lg appearance-none cursor-pointer">
                    </div>
                    <div>
                        <div class="flex justify-between items-center mb-3">
                            <label class="text-sm font-semibold text-white">Biological Gender</label>
                        </div>
                        <select id="input-gender" class="w-full bg-gray-800 border border-gray-700 text-white text-sm rounded-lg focus:ring-purple-500 focus:border-purple-500 block p-2.5">
                            <option value="Female" ${formData.gender === 'Female' ? 'selected' : ''}>Female</option>
                            <option value="Male" ${formData.gender === 'Male' ? 'selected' : ''}>Male</option>
                            <option value="Other" ${formData.gender === 'Other' ? 'selected' : ''}>Other / Prefer not to say</option>
                        </select>
                    </div>
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
                    <p class="text-xs text-gray-400 tracking-wide font-mono">Behavioral Inference Inputs: Age, Gender, Sleep, Stress, Activity, Anxiety, Hydration, Cycle Context</p>
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

    document.getElementById('input-age').addEventListener('input', e => { formData.age = parseInt(e.target.value); document.getElementById('age-display').textContent = e.target.value; });
    document.getElementById('input-gender').addEventListener('change', e => { 
        formData.gender = e.target.value; 
        const cw = document.getElementById('cycle-wrapper');
        if(formData.gender !== 'Female') { cw.classList.add('hidden'); formData.cycle_day = 0; }
        else { cw.classList.remove('hidden'); }
    });
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

    let hormone = (formData.gender !== 'Female' || formData.cycle_day === 0) ? 0 : Math.sin(2 * Math.PI * formData.cycle_day / formData.base_cycle);
    const payload = { 
        "Age": formData.age,
        "Gender": formData.gender,
        "Sleep Duration": formData.sleep_duration, 
        "Stress Level": formData.stress_level, 
        "Physical Activity Level": formData.physical_activity, 
        "Cycle_Day": formData.cycle_day, 
        "Base_Cycle_Length": formData.base_cycle, 
        "Hormone_Proxy": hormone,
        "anxiety_level": formData.anxiety_level,
        "water_intake": formData.water_intake
    };

        if (currentUser) payload["username"] = currentUser.user || "Guest";

    try {
        const response = await fetch(`${API_BASE}/predict`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
        if (response.ok) {
            lastPrediction = await response.json();
            if(currentUser) currentUser = lastPrediction;
            localStorage.setItem('luna_user', JSON.stringify(lastPrediction));
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
    if(!cohortRecords.length) { content.innerHTML = '<div class="text-center text-gray-500 mt-20">No Cohort Schema detected via API.</div>'; return; }
    
    // Grab first 5 for sample
    const sample = cohortRecords.slice(0, 5);
    
    content.innerHTML = `
        <div class="animate-fade-in pb-12">
            <h3 class="text-2xl font-bold text-white mb-6">Research Repository</h3>
            
            <div class="bg-gray-900 border border-gray-800 rounded-2xl p-8 mb-8">
                <h4 class="text-lg font-bold text-purple-400 mb-4">Database Topology</h4>
                <p class="text-gray-400 leading-relaxed text-sm">
                    Operating on ${cohortRecords.length} synchronized pseudo-patients generated via <code>src/inference/generate_cohort.py</code>. 
                    Structure enforces mathematically grounded distributions avoiding null-random saturation.
                </p>
                <div class="mt-6 flex space-x-4 text-xs font-mono">
                    <div class="bg-gray-800 px-3 py-1 rounded">Source: Synthetic</div>
                    <div class="bg-gray-800 px-3 py-1 rounded">Seed: Fixed-42</div>
                    <div class="bg-gray-800 px-3 py-1 rounded">Volume: 100</div>
                </div>
            </div>

            <div class="bg-gray-900 border border-gray-800 rounded-2xl p-6 overflow-x-auto">
                <h4 class="text-sm font-bold text-white mb-4">Sample Matrix Slice (Top 5 items)</h4>
                <table class="w-full text-left text-sm text-gray-400">
                    <thead class="text-xs uppercase bg-gray-800 text-gray-300">
                        <tr><th class="px-4 py-3">ID</th><th class="px-4 py-3">Risk Group</th><th class="px-4 py-3">Sleep</th><th class="px-4 py-3">Stress</th><th class="px-4 py-3">Target Risk</th></tr>
                    </thead>
                    <tbody>
                        ${sample.map(r => `
                            <tr class="border-b border-gray-800 hover:bg-gray-800/50">
                                <td class="px-4 py-3 font-mono text-purple-400">${r.id}</td>
                                <td class="px-4 py-3">${r.cohort_group}</td>
                                <td class="px-4 py-3">${r.sleep_duration}</td>
                                <td class="px-4 py-3">${r.stress_level}</td>
                                <td class="px-4 py-3">${r.predicted_risk}%</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        </div>
    `;
}

// Initial Boot Call Wait
document.addEventListener('DOMContentLoaded', checkAuth);
