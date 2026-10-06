/**
 * Student Result Analysis System Using Pandas and Matplotlib
 * SRM Institute of Science and Technology, Ramapuram, Chennai
 * Department of Computer Science and Engineering
 * Course: 21CSC203P – Advanced Programming Practices (CSE/K)
 */

document.addEventListener("DOMContentLoaded", () => {
  // Global State
  const state = {
    students: [],
    summary: {},
    subjectAnalysis: [],
    classAnalysis: {},
    activeTab: "dashboard",
    searchQuery: "",
    filterResult: "all",
    sortBy: "Rank",
    sortOrder: "asc",
    currentEditReg: null
  };

  const SUBJECTS = [
    { code: "21CSC201J", short: "DSA", name: "Data Structures and Algorithms", col: "DSA_21CSC201J" },
    { code: "21CSC202J", short: "OOP", name: "Object Oriented Design & Programming", col: "OOP_21CSC202J" },
    { code: "21CSC203P", short: "APP", name: "Advanced Programming Practices", col: "APP_21CSC203P" },
    { code: "21MTH201T", short: "DM", name: "Discrete Mathematics", col: "DM_21MTH201T" },
    { code: "21CSC204J", short: "COA", name: "Computer Organization and Architecture", col: "COA_21CSC204J" }
  ];

  // DOM Elements
  const tabButtons = document.querySelectorAll(".nav-tab-btn");
  const tabPanes = document.querySelectorAll(".tab-pane");

  // Summary Metrics Elements
  const totalStudentsEl = document.getElementById("metric-total-students");
  const classAvgPctEl = document.getElementById("metric-class-avg");
  const passPctEl = document.getElementById("metric-pass-pct");
  const passCountEl = document.getElementById("metric-pass-count");
  const highestScoreEl = document.getElementById("metric-highest-score");
  const highestStudentEl = document.getElementById("metric-highest-student");
  const lowestScoreEl = document.getElementById("metric-lowest-score");
  const lowestStudentEl = document.getElementById("metric-lowest-student");

  // Tables
  const studentsTableBody = document.getElementById("students-table-body");
  const topRankersTableBody = document.getElementById("top-rankers-table-body");
  const subjectAnalysisTableBody = document.getElementById("subject-analysis-table-body");
  const classStatsTableBody = document.getElementById("class-stats-table-body");
  const gradeDistributionGrid = document.getElementById("grade-distribution-grid");

  // Filter & Search Controls
  const studentSearchInput = document.getElementById("student-search");
  const resultFilterSelect = document.getElementById("result-filter");
  const sortSelect = document.getElementById("sort-select");

  // Modals
  const addStudentModal = document.getElementById("modal-add-student");
  const editStudentModal = document.getElementById("modal-edit-student");
  const markSheetModal = document.getElementById("modal-mark-sheet");
  const addStudentForm = document.getElementById("form-add-student");
  const editStudentForm = document.getElementById("form-edit-student");

  // CSV elements
  const csvFileInput = document.getElementById("csv-file-input");
  const csvDropzone = document.getElementById("csv-dropzone");
  const csvFileNameDisplay = document.getElementById("csv-file-name");
  const btnUploadCsv = document.getElementById("btn-upload-csv");
  const btnResetData = document.getElementById("btn-reset-data");

  // Toast Container
  const toastContainer = document.getElementById("toast-container");

  // ---------------- UI Helpers & Notifications ----------------

  function showToast(message, type = "info") {
    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    toast.innerHTML = `
      <span style="font-weight:700;">${type === "success" ? "✓" : type === "error" ? "⚠" : "ℹ"}</span>
      <span>${escapeHtml(message)}</span>
    `;
    toastContainer.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = "0";
      toast.style.transition = "opacity 0.3s ease";
      setTimeout(() => toast.remove(), 300);
    }, 4000);
  }

  function escapeHtml(str) {
    if (!str) return "";
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  // ---------------- Tab Navigation ----------------

  tabButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      const targetTab = btn.getAttribute("data-tab");
      switchTab(targetTab);
    });
  });

  function switchTab(tabId) {
    state.activeTab = tabId;
    tabButtons.forEach(btn => {
      btn.classList.toggle("active", btn.getAttribute("data-tab") === tabId);
    });
    tabPanes.forEach(pane => {
      pane.classList.toggle("active", pane.id === `tab-${tabId}`);
    });

    if (tabId === "analysis") {
      loadAnalysisData();
    } else if (tabId === "visualizations") {
      refreshAllCharts();
    }
  }

  // Allow in-page quick links to switch tabs
  document.querySelectorAll("[data-nav-target]").forEach(el => {
    el.addEventListener("click", (e) => {
      e.preventDefault();
      const target = el.getAttribute("data-nav-target");
      switchTab(target);
    });
  });

  // ---------------- API Calls & Data Fetching ----------------

  async function loadSummary() {
    try {
      const res = await fetch("/api/summary");
      const json = await res.json();
      if (json.status === "success") {
        state.summary = json.data;
        renderSummaryMetrics();
      }
    } catch (err) {
      console.error("Failed to load summary:", err);
    }
  }

  async function loadStudents() {
    try {
      const params = new URLSearchParams({
        search: state.searchQuery,
        filter_result: state.filterResult,
        sort_by: state.sortBy,
        sort_order: state.sortOrder
      });

      const res = await fetch(`/api/students?${params.toString()}`);
      const json = await res.json();
      if (json.status === "success") {
        state.students = json.data;
        renderStudentsTable();
        renderTopRankersTable();
      }
    } catch (err) {
      console.error("Failed to load students:", err);
      showToast("Failed to fetch student records", "error");
    }
  }

  async function loadAnalysisData() {
    try {
      const [subjRes, classRes] = await Promise.all([
        fetch("/api/analysis/subjects"),
        fetch("/api/analysis/class")
      ]);
      const subjJson = await subjRes.json();
      const classJson = await classRes.json();

      if (subjJson.status === "success") {
        state.subjectAnalysis = subjJson.data;
        renderSubjectAnalysisTable();
      }
      if (classJson.status === "success") {
        state.classAnalysis = classJson.data;
        renderClassAnalysis();
      }
    } catch (err) {
      console.error("Failed to load analysis:", err);
    }
  }

  // ---------------- Render Functions ----------------

  function renderSummaryMetrics() {
    const s = state.summary;
    if (!s || s.total_students === 0) return;

    if (totalStudentsEl) totalStudentsEl.textContent = s.total_students;
    if (classAvgPctEl) classAvgPctEl.textContent = `${s.class_average_pct}%`;
    if (passPctEl) passPctEl.textContent = `${s.pass_percentage}%`;
    if (passCountEl) passCountEl.textContent = `${s.pass_count} Passed / ${s.fail_count} Re-appear`;
    if (highestScoreEl) highestScoreEl.textContent = `${s.highest_score} (${s.highest_pct}%)`;
    if (highestStudentEl) highestStudentEl.textContent = s.highest_student;
    if (lowestScoreEl) lowestScoreEl.textContent = `${s.lowest_score} (${s.lowest_pct}%)`;
    if (lowestStudentEl) lowestStudentEl.textContent = s.lowest_student;
  }

  function getGradeClass(grade) {
    if (!grade) return "";
    return `grade-${grade.replace("+", "-plus")}`;
  }

  function renderStudentsTable() {
    if (!studentsTableBody) return;
    studentsTableBody.innerHTML = "";

    const countDisplay = document.getElementById("student-count-display");
    if (countDisplay) {
      countDisplay.textContent = `Showing ${state.students.length} student records`;
    }

    if (state.students.length === 0) {
      studentsTableBody.innerHTML = `
        <tr>
          <td colspan="14">
            <div class="empty-state">
              <div class="empty-state-icon">📋</div>
              <div class="empty-state-text">No student records match the search or filter criteria.</div>
              <div class="empty-state-sub">Try changing your search query or reset the filters.</div>
            </div>
          </td>
        </tr>
      `;
      return;
    }

    state.students.forEach(st => {
      const tr = document.createElement("tr");
      if (st.Result === "Fail") {
        tr.className = "row-failed";
      }

      tr.innerHTML = `
        <td class="num" style="font-weight:700;">${st.Rank !== "-" ? "#" + st.Rank : "-"}</td>
        <td style="font-family:monospace; font-weight:600;">${escapeHtml(st.Register_No)}</td>
        <td style="font-weight:600; color:var(--text-dark);">${escapeHtml(st.Student_Name)}</td>
        <td class="num">${st.DSA_21CSC201J}</td>
        <td class="num">${st.OOP_21CSC202J}</td>
        <td class="num">${st.APP_21CSC203P}</td>
        <td class="num">${st.DM_21MTH201T}</td>
        <td class="num">${st.COA_21CSC204J}</td>
        <td class="num" style="font-weight:700;">${st.Total}</td>
        <td class="num">${st.Average.toFixed(1)}</td>
        <td class="num" style="font-weight:700; color:var(--primary-blue);">${st.Percentage.toFixed(1)}%</td>
        <td>
          <span class="badge ${st.Result === 'Pass' ? 'badge-pass' : 'badge-fail'}">
            ${st.Result}
          </span>
        </td>
        <td>
          <span class="badge badge-grade ${getGradeClass(st.Grade)}">
            ${st.Grade}
          </span>
        </td>
        <td>
          <div class="table-actions">
            <button class="btn btn-outline btn-sm btn-view-sheet" data-reg="${escapeHtml(st.Register_No)}" title="View Academic Mark Sheet">
              📄 View
            </button>
            <button class="btn btn-outline btn-sm btn-edit-student" data-reg="${escapeHtml(st.Register_No)}" title="Edit Marks">
              ✏ Edit
            </button>
            <button class="btn btn-danger-outline btn-sm btn-delete-student" data-reg="${escapeHtml(st.Register_No)}" title="Delete Record">
              🗑
            </button>
          </div>
        </td>
      `;

      studentsTableBody.appendChild(tr);
    });

    attachTableActionListeners();
  }

  function renderTopRankersTable() {
    if (!topRankersTableBody) return;
    topRankersTableBody.innerHTML = "";

    const topRankers = state.students
      .filter(s => s.Result === "Pass" && s.Rank !== "-")
      .slice(0, 5);

    if (topRankers.length === 0) {
      topRankersTableBody.innerHTML = `<tr><td colspan="7" class="text-center" style="padding:16px;">No rankers available.</td></tr>`;
      return;
    }

    topRankers.forEach((st, idx) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td style="font-weight:700; color:var(--accent-blue);">#${st.Rank}</td>
        <td style="font-family:monospace;">${escapeHtml(st.Register_No)}</td>
        <td style="font-weight:600;">${escapeHtml(st.Student_Name)}</td>
        <td class="num" style="font-weight:700;">${st.Total} / 500</td>
        <td class="num" style="font-weight:700; color:var(--success-color);">${st.Percentage}%</td>
        <td><span class="badge badge-grade ${getGradeClass(st.Grade)}">${st.Grade}</span></td>
        <td>
          <button class="btn btn-outline btn-sm btn-view-sheet" data-reg="${escapeHtml(st.Register_No)}">
            Transcript
          </button>
        </td>
      `;
      topRankersTableBody.appendChild(tr);
    });

    document.querySelectorAll("#top-rankers-table-body .btn-view-sheet").forEach(btn => {
      btn.addEventListener("click", () => openMarkSheetModal(btn.getAttribute("data-reg")));
    });
  }

  function renderSubjectAnalysisTable() {
    if (!subjectAnalysisTableBody) return;
    subjectAnalysisTableBody.innerHTML = "";

    state.subjectAnalysis.forEach(subj => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td style="font-family:monospace; font-weight:700;">${subj.code}</td>
        <td style="font-weight:600; color:var(--text-dark);">${subj.name} (${subj.short})</td>
        <td class="num" style="font-weight:700; color:var(--primary-blue);">${subj.average}</td>
        <td class="num" style="color:var(--success-color); font-weight:700;">${subj.highest}</td>
        <td class="num" style="color:var(--danger-color);">${subj.lowest}</td>
        <td class="num">${subj.pass_count}</td>
        <td class="num">${subj.fail_count}</td>
        <td class="num" style="font-weight:700;">${subj.pass_percentage}%</td>
        <td class="num">${subj.std_dev}</td>
        <td style="font-size:12px; color:var(--text-muted);">${escapeHtml(subj.top_scorer)}</td>
      `;
      subjectAnalysisTableBody.appendChild(tr);
    });
  }

  function renderClassAnalysis() {
    if (!classStatsTableBody || !state.classAnalysis.percentage_stats) return;

    const p = state.classAnalysis.percentage_stats;
    const t = state.classAnalysis.total_stats;

    classStatsTableBody.innerHTML = `
      <tr><td><strong>Count (N)</strong></td><td class="num">${p.count}</td><td class="num">${t.count}</td></tr>
      <tr><td><strong>Class Mean (Average)</strong></td><td class="num" style="font-weight:700; color:var(--primary-blue);">${p.mean}%</td><td class="num" style="font-weight:700;">${t.mean} / 500</td></tr>
      <tr><td><strong>Standard Deviation (Std)</strong></td><td class="num">${p.std}</td><td class="num">${t.std}</td></tr>
      <tr><td><strong>Minimum Score (Min)</strong></td><td class="num" style="color:var(--danger-color);">${p.min}%</td><td class="num" style="color:var(--danger-color);">${t.min}</td></tr>
      <tr><td><strong>25th Percentile (Q1)</strong></td><td class="num">${p["25%"]}%</td><td class="num">${t["25%"]}</td></tr>
      <tr><td><strong>50th Percentile (Median)</strong></td><td class="num" style="font-weight:700;">${p["50%"]}%</td><td class="num" style="font-weight:700;">${t["50%"]}</td></tr>
      <tr><td><strong>75th Percentile (Q3)</strong></td><td class="num">${p["75%"]}%</td><td class="num">${t["75%"]}</td></tr>
      <tr><td><strong>Maximum Score (Max)</strong></td><td class="num" style="color:var(--success-color); font-weight:700;">${p.max}%</td><td class="num" style="color:var(--success-color); font-weight:700;">${t.max}</td></tr>
    `;

    // Grade Distribution Pills
    if (gradeDistributionGrid && state.classAnalysis.grade_distribution) {
      const g = state.classAnalysis.grade_distribution;
      gradeDistributionGrid.innerHTML = `
        <div class="metric-card" style="border-left: 4px solid #7e22ce;">
          <div class="metric-card-label">Grade O (90%+)</div>
          <div class="metric-card-value">${g["O"]}</div>
          <div class="metric-card-sub">Outstanding</div>
        </div>
        <div class="metric-card" style="border-left: 4px solid #2563eb;">
          <div class="metric-card-label">Grade A+ (80-89%)</div>
          <div class="metric-card-value">${g["A+"]}</div>
          <div class="metric-card-sub">Excellent</div>
        </div>
        <div class="metric-card" style="border-left: 4px solid #3b82f6;">
          <div class="metric-card-label">Grade A (70-79%)</div>
          <div class="metric-card-value">${g["A"]}</div>
          <div class="metric-card-sub">Very Good</div>
        </div>
        <div class="metric-card" style="border-left: 4px solid #d97706;">
          <div class="metric-card-label">Grade B+ (60-69%)</div>
          <div class="metric-card-value">${g["B+"]}</div>
          <div class="metric-card-sub">Good</div>
        </div>
        <div class="metric-card" style="border-left: 4px solid #f59e0b;">
          <div class="metric-card-label">Grade B (50-59%)</div>
          <div class="metric-card-value">${g["B"]}</div>
          <div class="metric-card-sub">Above Average</div>
        </div>
        <div class="metric-card" style="border-left: 4px solid #dc2626;">
          <div class="metric-card-label">Grade RA (&lt;50%)</div>
          <div class="metric-card-value">${g["RA"]}</div>
          <div class="metric-card-sub">Re-appear / Failed</div>
        </div>
      `;
    }
  }

  // ---------------- Visualizations Module ----------------

  function refreshAllCharts() {
    const timestamp = new Date().getTime();
    document.querySelectorAll(".chart-img").forEach(img => {
      const chartType = img.getAttribute("data-chart");
      if (chartType) {
        img.src = `/api/charts/${chartType}?t=${timestamp}`;
      }
    });
  }

  document.querySelectorAll(".btn-refresh-charts").forEach(btn => {
    btn.addEventListener("click", () => {
      refreshAllCharts();
      showToast("Visualizations updated from current dataset", "success");
    });
  });

  // ---------------- Search & Filter Event Handlers ----------------

  if (studentSearchInput) {
    let debounceTimer;
    studentSearchInput.addEventListener("input", (e) => {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => {
        state.searchQuery = e.target.value;
        loadStudents();
      }, 250);
    });
  }

  if (resultFilterSelect) {
    resultFilterSelect.addEventListener("change", (e) => {
      state.filterResult = e.target.value;
      loadStudents();
    });
  }

  if (sortSelect) {
    sortSelect.addEventListener("change", (e) => {
      const val = e.target.value;
      if (val === "Rank-asc") {
        state.sortBy = "Rank";
        state.sortOrder = "asc";
      } else if (val === "Percentage-desc") {
        state.sortBy = "Percentage";
        state.sortOrder = "desc";
      } else if (val === "Percentage-asc") {
        state.sortBy = "Percentage";
        state.sortOrder = "asc";
      } else if (val === "Student_Name-asc") {
        state.sortBy = "Student_Name";
        state.sortOrder = "asc";
      } else if (val === "Register_No-asc") {
        state.sortBy = "Register_No";
        state.sortOrder = "asc";
      }
      loadStudents();
    });
  }

  // ---------------- Modal & CRUD Operations ----------------

  function attachTableActionListeners() {
    // View Mark Sheet
    document.querySelectorAll(".btn-view-sheet").forEach(btn => {
      btn.addEventListener("click", () => {
        const reg = btn.getAttribute("data-reg");
        openMarkSheetModal(reg);
      });
    });

    // Edit Student
    document.querySelectorAll(".btn-edit-student").forEach(btn => {
      btn.addEventListener("click", () => {
        const reg = btn.getAttribute("data-reg");
        openEditStudentModal(reg);
      });
    });

    // Delete Student
    document.querySelectorAll(".btn-delete-student").forEach(btn => {
      btn.addEventListener("click", () => {
        const reg = btn.getAttribute("data-reg");
        confirmDeleteStudent(reg);
      });
    });
  }

  // Add Student
  const btnOpenAddModal = document.getElementById("btn-open-add-student");
  if (btnOpenAddModal) {
    btnOpenAddModal.addEventListener("click", () => {
      addStudentForm.reset();
      addStudentModal.classList.add("active");
    });
  }

  if (addStudentForm) {
    addStudentForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const formData = new FormData(addStudentForm);
      const payload = Object.fromEntries(formData.entries());

      try {
        const res = await fetch("/api/students", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        const json = await res.json();
        if (json.status === "success") {
          showToast("Student added successfully", "success");
          addStudentModal.classList.remove("active");
          await loadAllData();
        } else {
          showToast(json.message || "Failed to add student", "error");
        }
      } catch (err) {
        showToast("Error communicating with server", "error");
      }
    });
  }

  // Edit Student
  function openEditStudentModal(regNo) {
    const student = state.students.find(s => s.Register_No === regNo);
    if (!student) return;

    state.currentEditReg = regNo;
    document.getElementById("edit-reg-no").value = student.Register_No;
    document.getElementById("edit-student-name").value = student.Student_Name;
    document.getElementById("edit-department").value = student.Department || "CSE";
    document.getElementById("edit-semester").value = student.Semester || 3;
    document.getElementById("edit-section").value = student.Section || "CSE/K";

    SUBJECTS.forEach(s => {
      const input = document.getElementById(`edit-mark-${s.short.toLowerCase()}`);
      if (input) input.value = student[s.col] || 0;
    });

    editStudentModal.classList.add("active");
  }

  if (editStudentForm) {
    editStudentForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      if (!state.currentEditReg) return;

      const formData = new FormData(editStudentForm);
      const payload = Object.fromEntries(formData.entries());

      try {
        const res = await fetch(`/api/students/${encodeURIComponent(state.currentEditReg)}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        const json = await res.json();
        if (json.status === "success") {
          showToast("Student records updated successfully", "success");
          editStudentModal.classList.remove("active");
          await loadAllData();
        } else {
          showToast(json.message || "Failed to update student", "error");
        }
      } catch (err) {
        showToast("Error updating student record", "error");
      }
    });
  }

  // Delete Student
  async function confirmDeleteStudent(regNo) {
    if (confirm(`Are you sure you want to delete student record for ${regNo}?`)) {
      try {
        const res = await fetch(`/api/students/${encodeURIComponent(regNo)}`, {
          method: "DELETE"
        });
        const json = await res.json();
        if (json.status === "success") {
          showToast(`Student ${regNo} deleted`, "success");
          await loadAllData();
        } else {
          showToast(json.message || "Failed to delete student", "error");
        }
      } catch (err) {
        showToast("Error deleting student record", "error");
      }
    }
  }

  // View Mark Sheet Modal
  function openMarkSheetModal(regNo) {
    const student = state.students.find(s => s.Register_No === regNo);
    if (!student) return;

    document.getElementById("sheet-reg-no").textContent = student.Register_No;
    document.getElementById("sheet-student-name").textContent = student.Student_Name;
    document.getElementById("sheet-department").textContent = student.Department || "Computer Science and Engineering";
    document.getElementById("sheet-semester").textContent = `${student.Semester || 3} / III Sem`;
    document.getElementById("sheet-section").textContent = student.Section || "CSE/K";
    document.getElementById("sheet-rank").textContent = student.Rank !== "-" ? `#${student.Rank}` : "N/A (Re-appear)";

    const tbody = document.getElementById("sheet-subjects-body");
    tbody.innerHTML = "";

    SUBJECTS.forEach((s, idx) => {
      const marks = student[s.col];
      const isPassed = marks >= 50;
      let grade = "RA";
      if (isPassed) {
        if (marks >= 90) grade = "O";
        else if (marks >= 80) grade = "A+";
        else if (marks >= 70) grade = "A";
        else if (marks >= 60) grade = "B+";
        else grade = "B";
      }

      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td style="text-align:center;">${idx + 1}</td>
        <td style="font-family:monospace; font-weight:600;">${s.code}</td>
        <td>${s.name}</td>
        <td class="num">100</td>
        <td class="num" style="font-weight:700;">${marks}</td>
        <td style="text-align:center;"><span class="badge badge-grade ${getGradeClass(grade)}">${grade}</span></td>
        <td style="text-align:center;"><span class="badge ${isPassed ? 'badge-pass' : 'badge-fail'}">${isPassed ? 'PASS' : 'FAIL'}</span></td>
      `;
      tbody.appendChild(tr);
    });

    document.getElementById("sheet-total-marks").textContent = `${student.Total} / 500`;
    document.getElementById("sheet-average-marks").textContent = `${student.Average.toFixed(2)}`;
    document.getElementById("sheet-percentage").textContent = `${student.Percentage.toFixed(2)}%`;
    document.getElementById("sheet-final-result").textContent = student.Result.toUpperCase();
    document.getElementById("sheet-final-grade").textContent = student.Grade;

    const resultSpan = document.getElementById("sheet-final-result");
    resultSpan.className = `badge ${student.Result === 'Pass' ? 'badge-pass' : 'badge-fail'}`;

    markSheetModal.classList.add("active");
  }

  // Print Mark Sheet
  const btnPrintSheet = document.getElementById("btn-print-mark-sheet");
  if (btnPrintSheet) {
    btnPrintSheet.addEventListener("click", () => {
      window.print();
    });
  }

  // Close modals
  document.querySelectorAll(".modal-close-btn, .btn-modal-cancel").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".modal-overlay").forEach(m => m.classList.remove("active"));
    });
  });

  // ---------------- CSV Upload & Reset ----------------

  if (csvDropzone && csvFileInput) {
    csvDropzone.addEventListener("click", () => csvFileInput.click());

    csvFileInput.addEventListener("change", () => {
      if (csvFileInput.files.length > 0) {
        csvFileNameDisplay.textContent = `Selected: ${csvFileInput.files[0].name} (${(csvFileInput.files[0].size / 1024).toFixed(1)} KB)`;
      }
    });

    csvDropzone.addEventListener("dragover", (e) => {
      e.preventDefault();
      csvDropzone.style.borderColor = "var(--accent-blue)";
    });

    csvDropzone.addEventListener("dragleave", () => {
      csvDropzone.style.borderColor = "var(--border-medium)";
    });

    csvDropzone.addEventListener("drop", (e) => {
      e.preventDefault();
      csvDropzone.style.borderColor = "var(--border-medium)";
      if (e.dataTransfer.files.length > 0) {
        csvFileInput.files = e.dataTransfer.files;
        csvFileNameDisplay.textContent = `Selected: ${e.dataTransfer.files[0].name}`;
      }
    });
  }

  if (btnUploadCsv) {
    btnUploadCsv.addEventListener("click", async () => {
      if (!csvFileInput.files || csvFileInput.files.length === 0) {
        showToast("Please choose a CSV file to upload.", "error");
        return;
      }

      const file = csvFileInput.files[0];
      const mode = document.querySelector('input[name="import-mode"]:checked')?.value || "replace";

      const formData = new FormData();
      formData.append("file", file);
      formData.append("mode", mode);

      try {
        btnUploadCsv.disabled = true;
        btnUploadCsv.textContent = "Processing Pandas analysis...";

        const res = await fetch("/api/import-csv", {
          method: "POST",
          body: formData
        });
        const json = await res.json();

        if (json.status === "success") {
          showToast(json.message, "success");
          csvFileInput.value = "";
          csvFileNameDisplay.textContent = "No file chosen";
          await loadAllData();
          switchTab("students");
        } else {
          showToast(json.message || "Failed to process CSV file.", "error");
        }
      } catch (err) {
        showToast("Network error uploading CSV", "error");
      } finally {
        btnUploadCsv.disabled = false;
        btnUploadCsv.textContent = "Upload & Analyze CSV";
      }
    });
  }

  if (btnResetData) {
    btnResetData.addEventListener("click", async () => {
      if (confirm("Reset the dataset to the original 28 SRM CSE/K sample students?")) {
        try {
          const res = await fetch("/api/reset-data", { method: "POST" });
          const json = await res.json();
          if (json.status === "success") {
            showToast(json.message, "success");
            await loadAllData();
          } else {
            showToast(json.message || "Reset failed", "error");
          }
        } catch (err) {
          showToast("Error resetting data", "error");
        }
      }
    });
  }

  // ---------------- Initialize Everything ----------------

  async function loadAllData() {
    await Promise.all([loadSummary(), loadStudents()]);
    if (state.activeTab === "analysis") loadAnalysisData();
    if (state.activeTab === "visualizations") refreshAllCharts();
  }

  loadAllData();
});
