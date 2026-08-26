document.addEventListener("DOMContentLoaded", () => {
  if (!ApiService.getAuthToken()) {
    sessionStorage.setItem("login_notice", "Please log in to access your dashboard.");
    sessionStorage.setItem("redirect_after_login", "dashboard.html");
    window.location.href = "login.html";
    return;
  }
  loadDashboardData();
});

async function loadDashboardData() {
  try {
    const data = await ApiService.getDashboard();

    const welcomeEl = document.getElementById("welcome-user-name");
    if (welcomeEl) welcomeEl.textContent = data.user_name || "developer";

    document.getElementById("stat-total").textContent = data.total_interviews;
    document.getElementById("stat-avg").textContent = `${Math.round(data.average_score)}%`;
    document.getElementById("stat-best").textContent = `${Math.round(data.best_score)}%`;
    document.getElementById("stat-latest").textContent = `${Math.round(data.latest_score)}%`;

    const recentBody = document.getElementById("recent-table-body");
    if (!data.recent_interviews || data.recent_interviews.length === 0) {
      recentBody.innerHTML = `
        <tr>
          <td colspan="6" style="text-align:center; padding:2rem; color:var(--text-secondary);">
            <div class="font-mono" style="margin-bottom:0.5rem; color:var(--text-muted);">&gt; No runs yet.</div>
            <div style="font-size:0.9rem; margin-bottom:1rem;">Your first interview is waiting to be executed.</div>
            <a href="interview-setup.html" class="btn btn-primary" style="padding:0.4rem 1rem; font-size:0.85rem;">Run First Interview</a>
          </td>
        </tr>
      `;
      return;
    }

    recentBody.innerHTML = data.recent_interviews.map(i => {
      const dt = new Date(i.started_at).toLocaleDateString();
      const scoreNum = Math.round(i.overall_score);
      let scoreColor = "var(--primary)";
      if (scoreNum >= 85) scoreColor = "var(--success)";
      else if (scoreNum >= 70) scoreColor = "var(--primary)";
      else if (scoreNum >= 50) scoreColor = "var(--warning)";
      else scoreColor = "var(--danger)";

      return `
        <tr>
          <td>${dt}</td>
          <td><strong>${i.role}</strong></td>
          <td>${i.interview_type}</td>
          <td><span class="badge badge-green">${i.difficulty}</span></td>
          <td><strong class="font-mono" style="color:${scoreColor};">${scoreNum}%</strong></td>
          <td>
            <a href="results.html?id=${i.id}" class="btn btn-secondary" style="padding:0.3rem 0.75rem; font-size:0.8rem;">View Output</a>
          </td>
        </tr>
      `;
    }).join('');

  } catch (err) {
    console.error("Failed to load dashboard statistics:", err);
  }
}
