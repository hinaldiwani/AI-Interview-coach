document.addEventListener("DOMContentLoaded", () => {
  if (!ApiService.getAuthToken()) {
    sessionStorage.setItem("login_notice", "Please log in to view your execution history.");
    sessionStorage.setItem("redirect_after_login", "history.html");
    window.location.href = "login.html";
    return;
  }
  loadHistory();
});

async function loadHistory() {
  try {
    const data = await ApiService.getHistory();
    const tbody = document.getElementById("history-table-body");
    
    if (!data.history || data.history.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="8" style="text-align:center; padding:2rem; color:var(--text-secondary);">
            <div class="font-mono" style="margin-bottom:0.5rem; color:var(--text-muted);">&gt; No runs yet.</div>
            <div style="font-size:0.9rem; margin-bottom:1rem;">Your first interview is waiting to be executed.</div>
            <a href="interview-setup.html" class="btn btn-primary" style="padding:0.4rem 1rem; font-size:0.85rem;">Run First Interview</a>
          </td>
        </tr>
      `;
      return;
    }

    tbody.innerHTML = data.history.map(i => {
      const dt = new Date(i.started_at).toLocaleString();
      const scoreNum = Math.round(i.overall_score);

      let scoreColor = "var(--primary)";
      let categoryClass = "badge-green";

      if (scoreNum >= 85) {
        scoreColor = "var(--success)";
        categoryClass = "badge-success";
      } else if (scoreNum >= 70) {
        scoreColor = "var(--primary)";
        categoryClass = "badge-green";
      } else if (scoreNum >= 50) {
        scoreColor = "var(--warning)";
        categoryClass = "badge-warning";
      } else {
        scoreColor = "var(--danger)";
        categoryClass = "badge-danger";
      }

      return `
        <tr>
          <td class="font-mono">#${i.id}</td>
          <td>${dt}</td>
          <td><strong>${i.role}</strong></td>
          <td>${i.interview_type}</td>
          <td><span class="badge badge-green">${i.difficulty}</span></td>
          <td><strong class="font-mono" style="color:${scoreColor};">${scoreNum}%</strong></td>
          <td><span class="badge ${categoryClass}">${i.performance_category || i.status}</span></td>
          <td>
            <a href="results.html?id=${i.id}" class="btn btn-secondary" style="padding:0.3rem 0.75rem; font-size:0.8rem;">View Output</a>
          </td>
        </tr>
      `;
    }).join('');

  } catch (err) {
    console.error("Failed to load execution history:", err);
  }
}

function handleLogout() {
  ApiService.logout();
}
