document.addEventListener("DOMContentLoaded", () => {
  const urlParams = new URLSearchParams(window.location.search);
  const interviewId = urlParams.get("id");
  if (interviewId) {
    loadResults(interviewId);
  } else {
    window.location.href = "dashboard.html";
  }
});

async function loadResults(id) {
  try {
    const data = await ApiService.getInterviewResults(id);
    const result = data.result || {};
    const interview = data.interview || {};
    const reviews = data.reviews || [];

    const score = Math.round(result.overall_score || interview.overall_score || 0);
    document.getElementById("overall-score-num").textContent = score;
    document.getElementById("overall-circle").style.setProperty("--score-pct", score);

    const catTag = document.getElementById("category-tag");
    let category = result.performance_category || "COMPLETED";
    
    if (score >= 85) {
      category = "EXCELLENT BUILD";
      catTag.style.color = "var(--success)";
    } else if (score >= 70) {
      category = "GOOD BUILD";
      catTag.style.color = "var(--primary)";
    } else if (score >= 50) {
      category = "AVERAGE BUILD";
      catTag.style.color = "var(--warning)";
    } else {
      category = "NEEDS WORK";
      catTag.style.color = "var(--danger)";
    }
    catTag.textContent = category;

    // Sub-scores
    updateScoreBar("bar-tech", "val-tech", result.technical_score);
    updateScoreBar("bar-correct", "val-correct", result.correctness_score);
    updateScoreBar("bar-comm", "val-comm", result.communication_score);
    updateScoreBar("bar-comp", "val-comp", result.completeness_score);

    // Debug Report text
    document.getElementById("text-strengths").textContent = result.strengths || "Good core comprehension; clean answers; clear communication.";
    document.getElementById("text-weakness").textContent = result.weak_areas || "Detailed code syntax; advanced edge case optimization.";
    document.getElementById("text-recommendations").textContent = result.recommendations || "Practice further interview runs to build complete technical mastery.";

    // Question reviews
    const container = document.getElementById("reviews-container");
    container.innerHTML = reviews.map((r, idx) => {
      const qScore = Math.round((r.score || 0) * 10);
      return `
        <div class="review-card">
          <div class="review-header" onclick="toggleAccordion(this)">
            <div style="display:flex; align-items:center;">
              <span class="badge badge-green font-mono" style="margin-right:0.6rem;">Q${r.question_order}</span>
              <strong style="color:var(--text-main); font-size:0.95rem;">${r.question_text}</strong>
            </div>
            <div style="display:flex; align-items:center; gap:0.5rem;">
              <span class="badge badge-green font-mono">${qScore} / 100</span>
              <span style="font-size:0.8rem; color:var(--text-muted);">▼</span>
            </div>
          </div>
          <div class="review-body collapsed">
            <div style="margin-bottom:1rem;">
              <strong class="font-mono" style="color:var(--text-secondary); font-size:0.825rem;">YOUR RESPONSE:</strong>
              <div style="background:var(--surface); padding:0.85rem; border-radius:var(--radius-sm); border:1px solid var(--border); margin-top:0.3rem; font-size:0.9rem;">
                ${r.user_answer ? r.user_answer : "<em>No response provided.</em>"}
              </div>
            </div>

            <div class="eval-box eval-box-well">
              <strong>Evaluation Feedback:</strong> ${r.feedback || "Good attempt."}
            </div>

            <div class="eval-box eval-box-improve">
              <strong>Recommended Fix:</strong> ${r.improvement_suggestion || "Expand technical explanation."}
            </div>

            <div class="eval-box eval-box-ideal">
              <strong>Ideal Output:</strong> ${r.ideal_answer || "N/A"}
            </div>
          </div>
        </div>
      `;
    }).join('');

  } catch (err) {
    console.error("Failed to load results:", err);
  }
}

function updateScoreBar(barId, valId, val) {
  const score = Math.round(val || 0);
  document.getElementById(valId).textContent = `${score} / 100`;
  document.getElementById(barId).style.width = `${score}%`;
}

function toggleAccordion(headerEl) {
  const body = headerEl.nextElementSibling;
  body.classList.toggle("collapsed");
}
