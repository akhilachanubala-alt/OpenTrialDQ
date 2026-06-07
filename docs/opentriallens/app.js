(() => {
  const SAMPLE_ROWS = [
    { nct_id: "NCT10000001", overall_status: "Recruiting", start_date: "2025-04-01", completion_date: "2027-09-30", phases: "Phase 2", sponsor_name: "Academic Medical Center", sponsor_class: "Other", enrollment_count: 420, conditions: "Cardiovascular Diseases", countries: "United States|Canada", source_system: "Synthetic sample" },
    { nct_id: "NCT10000002", overall_status: "Completed", start_date: "2022-02-15", completion_date: "2024-11-15", phases: "Phase 3", sponsor_name: "Life Sciences Sponsor A", sponsor_class: "Industry", enrollment_count: 1180, conditions: "Diabetes Mellitus", countries: "United States|Germany|India", source_system: "Synthetic sample" },
    { nct_id: "NCT10000003", overall_status: "Recruiting", start_date: "2024-10-05", completion_date: "2029-03-01", phases: "Not applicable", sponsor_name: "Research Foundation", sponsor_class: "Other", enrollment_count: 850, conditions: "Rare Diseases", countries: "United States|United Kingdom", source_system: "Synthetic sample" },
    { nct_id: "NCT10000004", overall_status: "Terminated", start_date: "2021-06-20", completion_date: "2023-01-10", phases: "Phase 1|Phase 2", sponsor_name: "Life Sciences Sponsor B", sponsor_class: "Industry", enrollment_count: 65, conditions: "Breast Cancer", countries: "United States", source_system: "Synthetic sample" },
    { nct_id: "NCT10000005", overall_status: "Not yet recruiting", start_date: "2026-08-01", completion_date: "2028-06-01", phases: "", sponsor_name: "", sponsor_class: "Other", enrollment_count: "", conditions: "Clinical Trial Operations", countries: "", source_system: "Synthetic sample" },
    { nct_id: "NCT10000006", overall_status: "Active, not recruiting", start_date: "2023-05-01", completion_date: "2026-03-31", phases: "Phase 4", sponsor_name: "Public Health Institute", sponsor_class: "Other", enrollment_count: 320, conditions: "Cardiometabolic Syndrome", countries: "United States|Mexico", source_system: "Synthetic sample" }
  ];

  const state = { rows: [], failures: [], audit: null, sourceLabel: "No data" };
  const $ = (id) => document.getElementById(id);
  const els = {
    form: $("searchForm"), queryTerm: $("queryTerm"), pageSize: $("pageSize"), status: $("statusMessage"), sampleButton: $("sampleButton"), csvFile: $("csvFile"),
    totalTrials: $("totalTrials"), qualityScore: $("qualityScore"), recruitingTrials: $("recruitingTrials"), failedChecks: $("failedChecks"), totalEnrollment: $("totalEnrollment"),
    scoreRing: $("scoreRing"), scoreRingText: $("scoreRingText"), qualityBadge: $("qualityBadge"), issueList: $("qualityIssueList"),
    failedBody: $("failedTableBody"), recordsBody: $("recordsTableBody"), exportClean: $("exportCleanButton"), exportFailed: $("exportFailedButton"), exportAudit: $("exportAuditButton")
  };
  const colors = ["#147d77", "#2855a6", "#b46a00", "#b33a4b", "#237a4b", "#6d5a8d"];

  els.form.addEventListener("submit", async (event) => { event.preventDefault(); await searchLiveData(); });
  els.sampleButton.addEventListener("click", () => updateDashboard(SAMPLE_ROWS, "Synthetic sample data"));
  els.csvFile.addEventListener("change", async (event) => {
    const file = event.target.files && event.target.files[0];
    if (!file) return;
    try {
      updateDashboard(parseCsv(await file.text()).map(normalizeCsvRow), `Uploaded CSV: ${file.name}`);
      els.csvFile.value = "";
    } catch (error) { setStatus(`CSV upload failed: ${error.message}`, true); }
  });
  els.exportClean.addEventListener("click", () => downloadFile("opentriallens-clean-records.csv", toCsv(state.rows), "text/csv"));
  els.exportFailed.addEventListener("click", () => downloadFile("opentriallens-failed-records.csv", toCsv(state.failures), "text/csv"));
  els.exportAudit.addEventListener("click", () => downloadFile("opentriallens-audit-summary.json", JSON.stringify({ source: state.sourceLabel, generated_at: new Date().toISOString(), total_records: state.rows.length, failed_checks: state.failures.length, quality_score: state.audit ? state.audit.score : 0, issue_summary: state.audit ? state.audit.issueSummary : {} }, null, 2), "application/json"));

  async function searchLiveData() {
    const queryTerm = els.queryTerm.value.trim();
    if (!queryTerm) { setStatus("Enter a condition to search.", true); return; }
    setBusy(true); setStatus(`Searching ClinicalTrials.gov for ${queryTerm}...`, false);
    try {
      const params = new URLSearchParams({ "query.term": queryTerm, pageSize: els.pageSize.value, format: "json" });
      const response = await fetch(`https://clinicaltrials.gov/api/v2/studies?${params.toString()}`, { headers: { Accept: "application/json" } });
      if (!response.ok) throw new Error(`ClinicalTrials.gov returned ${response.status}`);
      const payload = await response.json();
      updateDashboard(flattenStudies(payload.studies || []), `ClinicalTrials.gov: ${queryTerm}`);
    } catch (error) {
      setStatus(`Live search failed: ${error.message}. Sample data loaded.`, true);
      updateDashboard(SAMPLE_ROWS, "Synthetic sample data");
    } finally { setBusy(false); }
  }

  function flattenStudies(studies) {
    return studies.map((study) => {
      const protocol = study.protocolSection || {};
      const identification = protocol.identificationModule || {};
      const status = protocol.statusModule || {};
      const sponsors = protocol.sponsorCollaboratorsModule || {};
      const design = protocol.designModule || {};
      const conditions = protocol.conditionsModule || {};
      const locations = ((protocol.contactsLocationsModule || {}).locations || []);
      const leadSponsor = sponsors.leadSponsor || {};
      const enrollment = design.enrollmentInfo || {};
      return {
        nct_id: identification.nctId || "",
        overall_status: formatEnum(status.overallStatus),
        start_date: dateValue(status.startDateStruct),
        completion_date: dateValue(status.completionDateStruct),
        phases: joinValues((design.phases || []).map(formatPhase)),
        sponsor_name: leadSponsor.name || "",
        sponsor_class: formatEnum(leadSponsor.class),
        enrollment_count: enrollment.count || "",
        conditions: joinValues(conditions.conditions || []),
        countries: joinValues(uniqueValues(locations.map((item) => item.country).filter(Boolean))),
        source_system: "ClinicalTrials.gov"
      };
    });
  }

  function updateDashboard(rows, sourceLabel) {
    state.rows = rows.map(normalizeRow);
    state.sourceLabel = sourceLabel;
    state.audit = evaluateDataQuality(state.rows);
    state.failures = state.audit.failures;
    renderMetrics(); renderQuality(); renderCharts(); renderTables();
    setStatus(`${sourceLabel} - ${state.rows.length} records processed.`, false);
  }
  function evaluateDataQuality(rows) {
    const failures = [];
    const required = [
      ["nct_id", "NCT ID is required", "critical"], ["overall_status", "Study status is required", "high"], ["phases", "Trial phase is missing", "medium"],
      ["sponsor_name", "Sponsor name is required", "high"], ["enrollment_count", "Enrollment count is required", "medium"], ["conditions", "Condition list is required", "high"], ["countries", "Location country coverage is missing", "medium"]
    ];
    const idCounts = countBy(rows, (row) => row.nct_id || "Missing");
    let totalChecks = rows.length * (required.length + 4);
    rows.forEach((row, index) => {
      required.forEach(([field, reason, severity]) => { if (!hasValue(row[field])) failures.push(makeFailure(row, index, field, "required", severity, reason)); });
      if (hasValue(row.enrollment_count) && !isPositiveNumber(row.enrollment_count)) failures.push(makeFailure(row, index, "enrollment_count", "numeric_positive", "medium", "Enrollment count should be a positive number"));
      if (hasValue(row.start_date) && isFutureDate(row.start_date)) failures.push(makeFailure(row, index, "start_date", "date_not_future", "medium", "Start date is in the future"));
      if (hasValue(row.start_date) && hasValue(row.completion_date) && Date.parse(row.completion_date) < Date.parse(row.start_date)) failures.push(makeFailure(row, index, "completion_date", "date_order", "high", "Completion date is before start date"));
      if (hasValue(row.nct_id) && idCounts[row.nct_id] > 1) failures.push(makeFailure(row, index, "nct_id", "unique", "critical", "Duplicate NCT ID found"));
    });
    if (!rows.length) totalChecks = 1;
    const score = Math.max(0, Math.round(((totalChecks - failures.length) / totalChecks) * 100));
    return { failures, totalChecks, score, issueSummary: countBy(failures, (failure) => failure.rule) };
  }

  function renderMetrics() {
    const statusCounts = countBy(state.rows, (row) => row.overall_status || "Missing");
    const totalEnrollment = state.rows.reduce((sum, row) => sum + (Number(row.enrollment_count) || 0), 0);
    els.totalTrials.textContent = formatNumber(state.rows.length);
    els.qualityScore.textContent = `${state.audit.score}%`;
    els.recruitingTrials.textContent = formatNumber(statusCounts.Recruiting || 0);
    els.failedChecks.textContent = formatNumber(state.failures.length);
    els.totalEnrollment.textContent = formatNumber(totalEnrollment);
  }

  function renderQuality() {
    els.scoreRing.style.setProperty("--score", state.audit.score);
    els.scoreRingText.textContent = `${state.audit.score}%`;
    els.qualityBadge.textContent = state.audit.score >= 90 ? "Strong" : state.audit.score >= 75 ? "Review" : "Needs work";
    const entries = Object.entries(state.audit.issueSummary).sort((a, b) => b[1] - a[1]).slice(0, 6);
    els.issueList.innerHTML = entries.length ? entries.map(([label, value]) => `<div class="issue-row"><span>${escapeHtml(label)}</span><strong>${value}</strong></div>`).join("") : '<div class="empty">No failed checks for this dataset.</div>';
  }

  function renderCharts() {
    renderBars("statusChart", countBy(state.rows, (row) => row.overall_status || "Missing"));
    renderBars("phaseChart", countSplitValues(state.rows, "phases"));
    renderBars("sponsorChart", countBy(state.rows, (row) => row.sponsor_class || "Missing"));
    renderBars("countryChart", countSplitValues(state.rows, "countries"), 10);
    renderBars("yearChart", countBy(state.rows, (row) => yearValue(row.start_date) || "Missing"), 12, true);
  }

  function renderBars(targetId, counts, limit = 8, sortByLabel = false) {
    const target = $(targetId);
    let entries = Object.entries(counts).filter(([, value]) => value > 0);
    entries = sortByLabel ? entries.sort((a, b) => String(a[0]).localeCompare(String(b[0]))) : entries.sort((a, b) => b[1] - a[1] || String(a[0]).localeCompare(String(b[0]))).slice(0, limit);
    if (!entries.length) { target.innerHTML = '<div class="empty">No values available.</div>'; return; }
    const max = Math.max(...entries.map(([, value]) => value), 1);
    target.innerHTML = entries.map(([label, value], index) => {
      const width = Math.max(5, Math.round((value / max) * 100));
      const color = colors[index % colors.length];
      return `<div class="bar-row" title="${escapeHtml(label)}: ${value}"><span class="bar-label">${escapeHtml(label)}</span><span class="bar-track"><span class="bar-fill" style="width:${width}%;background:${color}"></span></span><strong class="bar-value">${value}</strong></div>`;
    }).join("");
  }

  function renderTables() {
    els.failedBody.innerHTML = state.failures.length ? state.failures.slice(0, 40).map((failure) => `<tr><td>${escapeHtml(failure.nct_id || "Missing")}</td><td>${escapeHtml(failure.field)}</td><td>${escapeHtml(failure.rule)}</td><td>${escapeHtml(failure.severity)}</td><td>${escapeHtml(failure.reason)}</td></tr>`).join("") : '<tr><td colspan="5"><div class="empty">No failed records.</div></td></tr>';
    els.recordsBody.innerHTML = state.rows.length ? state.rows.slice(0, 50).map((row) => `<tr><td>${escapeHtml(row.nct_id || "Missing")}</td><td>${escapeHtml(row.overall_status || "Missing")}</td><td>${escapeHtml(row.phases || "Missing")}</td><td>${escapeHtml(row.sponsor_name || "Missing")}</td><td>${escapeHtml(String(row.enrollment_count || "Missing"))}</td><td>${escapeHtml(row.countries || "Missing")}</td></tr>`).join("") : '<tr><td colspan="6"><div class="empty">No records loaded.</div></td></tr>';
  }

  function normalizeRow(row) { return { nct_id: text(row.nct_id), overall_status: text(row.overall_status), start_date: text(row.start_date), completion_date: text(row.completion_date), phases: text(row.phases), sponsor_name: text(row.sponsor_name), sponsor_class: text(row.sponsor_class), enrollment_count: text(row.enrollment_count), conditions: text(row.conditions), countries: text(row.countries), source_system: text(row.source_system) }; }
  function normalizeCsvRow(row) { const normalized = {}; Object.entries(row).forEach(([key, value]) => { normalized[normalizeHeader(key)] = value; }); return { nct_id: pick(normalized, ["nct_id", "nctid", "nct_number"]), overall_status: pick(normalized, ["overall_status", "study_status", "status"]), start_date: pick(normalized, ["start_date", "study_start_date"]), completion_date: pick(normalized, ["completion_date", "primary_completion_date", "end_date"]), phases: pick(normalized, ["phases", "phase", "trial_phase"]), sponsor_name: pick(normalized, ["sponsor_name", "sponsor", "lead_sponsor"]), sponsor_class: pick(normalized, ["sponsor_class", "sponsor_type"]), enrollment_count: pick(normalized, ["enrollment_count", "enrollment", "participants"]), conditions: pick(normalized, ["conditions", "condition", "disease"]), countries: pick(normalized, ["countries", "country", "locations"]), source_system: "Uploaded CSV" }; }
  function parseCsv(source) { const rows = []; let row = []; let value = ""; let quoted = false; for (let i = 0; i < source.length; i += 1) { const char = source[i]; const next = source[i + 1]; if (char === '"' && quoted && next === '"') { value += '"'; i += 1; } else if (char === '"') { quoted = !quoted; } else if (char === "," && !quoted) { row.push(value); value = ""; } else if ((char === "\n" || char === "\r") && !quoted) { if (char === "\r" && next === "\n") i += 1; row.push(value); if (row.some((cell) => cell.trim() !== "")) rows.push(row); row = []; value = ""; } else { value += char; } } row.push(value); if (row.some((cell) => cell.trim() !== "")) rows.push(row); if (!rows.length) return []; const headers = rows[0].map((header) => header.trim()); return rows.slice(1).map((cells) => Object.fromEntries(headers.map((header, index) => [header, cells[index] || ""]))); }
  function toCsv(rows) { if (!rows.length) return ""; const headers = Object.keys(rows[0]); return [headers.join(","), ...rows.map((row) => headers.map((header) => csvEscape(row[header])).join(","))].join("\n"); }
  function csvEscape(value) { const output = value == null ? "" : String(value); return /[",\n\r]/.test(output) ? `"${output.replace(/"/g, '""')}"` : output; }
  function downloadFile(name, content, type) { const blob = new Blob([content], { type: `${type};charset=utf-8` }); const url = URL.createObjectURL(blob); const link = document.createElement("a"); link.href = url; link.download = name; document.body.appendChild(link); link.click(); link.remove(); URL.revokeObjectURL(url); }
  function makeFailure(row, index, field, rule, severity, reason) { return { record_index: index + 1, nct_id: row.nct_id || "", field, rule, severity, reason }; }
  function countBy(items, getter) { return items.reduce((counts, item) => { const key = getter(item) || "Missing"; counts[key] = (counts[key] || 0) + 1; return counts; }, {}); }
  function countSplitValues(rows, field) { const counts = {}; rows.forEach((row) => { const values = hasValue(row[field]) ? String(row[field]).split(/[|;]/).map((item) => item.trim()).filter(Boolean) : []; if (!values.length) counts.Missing = (counts.Missing || 0) + 1; values.forEach((value) => { counts[value] = (counts[value] || 0) + 1; }); }); return counts; }
  function pick(record, keys) { for (const key of keys) if (Object.hasOwn(record, key) && hasValue(record[key])) return record[key]; return ""; }
  function normalizeHeader(value) { return String(value || "").trim().toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_+|_+$/g, ""); }
  function text(value) { return value == null ? "" : String(value).trim(); }
  function hasValue(value) { return value !== null && value !== undefined && String(value).trim() !== ""; }
  function isPositiveNumber(value) { return Number.isFinite(Number(value)) && Number(value) > 0; }
  function isFutureDate(value) { const time = Date.parse(value); if (Number.isNaN(time)) return false; const today = new Date(); today.setHours(23, 59, 59, 999); return time > today.getTime(); }
  function yearValue(value) { const match = String(value || "").match(/\d{4}/); return match ? match[0] : ""; }
  function dateValue(value) { return value && value.date ? value.date : ""; }
  function joinValues(values) { return uniqueValues((values || []).filter(Boolean).map(String)).join("|"); }
  function uniqueValues(values) { return [...new Set(values.map((value) => String(value).trim()).filter(Boolean))]; }
  function formatEnum(value) { return value ? String(value).replace(/_/g, " ").toLowerCase().replace(/\b\w/g, (letter) => letter.toUpperCase()) : ""; }
  function formatPhase(value) { if (!value) return ""; const normalized = String(value).toUpperCase(); if (normalized === "NA" || normalized === "N/A") return "Not applicable"; const match = normalized.match(/^PHASE(\d)$/); return match ? `Phase ${match[1]}` : formatEnum(value); }
  function formatNumber(value) { return new Intl.NumberFormat("en-US").format(value || 0); }
  function escapeHtml(value) { return String(value == null ? "" : value).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;"); }
  function setStatus(message, error) { els.status.textContent = message; els.status.classList.toggle("error", Boolean(error)); }
  function setBusy(busy) { els.form.querySelectorAll("button, input, select, label.button").forEach((element) => { if (element.tagName === "LABEL") { element.style.pointerEvents = busy ? "none" : ""; element.style.opacity = busy ? "0.6" : ""; } else { element.disabled = busy; } }); }

  updateDashboard(SAMPLE_ROWS, "Synthetic sample data");
})();