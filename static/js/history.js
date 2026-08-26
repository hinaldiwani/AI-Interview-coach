document.addEventListener("DOMContentLoaded", () => {
  loadHistory();
});

async function loadHistory() {
  try {
    const data = await ApiService.getHistory();
    const tbody = document.getElementById("history-table-body");
    
    if (!data.history || data.history.length === 0) {
      tbody.innerHTML = `<tr><td colspan="8" style="text-align:center; color:var(--text-muted);">No interview history found.</td></tr>`;
      return;
    }

    tbody.innerHTML = data.history.map(i => {
      const dt = new Date(i.started_at).toLocaleString();
      const scoreNum = Math.round(i.overall_score);

      let scoreColor = "var(--primary)";
      let categoryClass = "badge-teal";

      if (scoreNum >= 85) {
        scoreColor = "var(--success)";
        categoryClass = "badge-success";
      } else if (scoreNum >= 70) {
        scoreColor = "var(--primary)";
        categoryClass = "badge-teal";
      } else if (scoreNum >= 50) {
        scoreColor = "var(--warning)";
        categoryClass = "badge-warning";
      } else {
        scoreColor = "var(--danger)";
        categoryClass = "badge-danger";
      }

      return `
        <tr>
          <td>#${i.id}</td>
          <td>${dt}</td>
          <td><strong>${i.role}</strong></td>
          <td>${i.interview_type}</td>
          <td><span class="badge badge-teal">${i.difficulty}</span></td>
          <td><strong style="color:${scoreColor};">${scoreNum}%</strong></td>
          <td><span class="badge ${categoryClass}">${i.performance_category || i.status}</span></td>
          <td>
            <a href="results.html?id=${i.id}" class="btn btn-secondary" style="padding:0.3rem 0.75rem; font-size:0.8rem;">View Result</a>
          </td>
        </tr>
      `;
    }).join('');

  } catch (err) {
    console.error("Failed to load interview history:", err);
  }
}
