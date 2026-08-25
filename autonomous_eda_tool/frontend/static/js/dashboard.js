const filePath = sessionStorage.getItem("file_path");
const dataProfileRaw = sessionStorage.getItem("data_profile");
if (!filePath || !dataProfileRaw) { window.location.href = "/"; }

const profile = JSON.parse(dataProfileRaw);
document.getElementById("statRows").innerText = profile.summary.total_rows.toLocaleString();
document.getElementById("statCols").innerText = profile.summary.total_cols.toLocaleString();
document.getElementById("statMissing").innerText = profile.summary.total_missing_cells.toLocaleString();
document.getElementById("statDuplicates").innerText = profile.summary.duplicate_rows.toLocaleString();

// Charts and Preferences initialization (same as before)
new ApexCharts(document.getElementById("chartTypes"), {
    chart: { type: 'donut', height: '100%', background: 'transparent' },
    theme: { mode: 'dark' }, series: Object.values(profile.charts.data_types_breakdown), labels: Object.keys(profile.charts.data_types_breakdown), colors: ['#3b82f6', '#10b981', '#8b5cf6', '#f59e0b', '#ef4444'], stroke: { colors: ['#111827'], width: 2 }
}).render();

new ApexCharts(document.getElementById("chartMissing"), {
    chart: { type: 'bar', height: '100%', background: 'transparent', toolbar: { show: false } },
    theme: { mode: 'dark' }, series: [{ name: 'Missing', data: profile.charts.missing_values_per_column.map(i => i.missing_count) }], xaxis: { categories: profile.charts.missing_values_per_column.map(i => i.column) }, colors: ['#f59e0b'], grid: { padding: { top: -10, bottom: 0, left: 10, right: 10 } }
}).render();

const preferencesContainer = document.getElementById("preferencesContainer");
Object.keys(profile.columns).forEach(col => {
    const info = profile.columns[col];
    preferencesContainer.innerHTML += `
        <div class="card-panel p-4 space-y-2">
            <div class="flex justify-between items-center"><span class="font-semibold text-white text-sm">${col}</span><span class="text-xs text-slate-400">${info.data_type}</span></div>
            <select data-col="${col}" class="pref-select w-full bg-slate-950 border border-slate-700 rounded-md text-xs text-slate-200 p-2 outline-none">
                <option value="Auto-Detect">AI Recommended (Auto)</option>
                <option value="Impute Median">Impute with Median</option>
                <option value="Drop Column">Drop Column</option>
            </select>
        </div>`;
});

document.getElementById("btnRunPipeline").addEventListener("click", async () => {
    document.getElementById("executionOutputSection").classList.remove("hidden");
    const userPrefs = {};
    document.querySelectorAll(".pref-select").forEach(s => userPrefs[s.getAttribute("data-col")] = s.value);

    const res = await fetch("/api/process/", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ file_path: filePath, data_profile: profile, user_preferences: userPrefs })
    });
    const result = await res.json();
    document.getElementById("terminalLogs").innerText = result.execution_logs;
    document.getElementById("codeDisplay").innerText = result.generated_code;
    if (result.cleaned_file_path) {
        const fn = result.cleaned_file_path.split(/[/\\]/).pop();
        const btn = document.getElementById("btnDownload");
        btn.href = `/api/upload/download/${fn}`;
        btn.classList.remove("hidden");
    }
});