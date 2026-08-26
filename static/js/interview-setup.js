document.addEventListener("DOMContentLoaded", () => {
  restoreSavedConfig();
});

function restoreSavedConfig() {
  const saved = sessionStorage.getItem("saved_interview_config");
  if (!saved) return;

  try {
    const config = JSON.parse(saved);
    if (config.role) {
      const roleEl = document.getElementById("role");
      if (roleEl) roleEl.value = config.role;
    }
    if (config.experience) {
      const expRadio = document.querySelector(`input[name='experience'][value='${config.experience}']`);
      if (expRadio) {
        expRadio.checked = true;
        const card = expRadio.closest(".option-card");
        if (card) selectOptionCard(card, "experience");
      }
    }
    if (config.interview_type || config.type) {
      const typeVal = config.interview_type || config.type;
      const typeRadio = document.querySelector(`input[name='type'][value='${typeVal}']`);
      if (typeRadio) {
        typeRadio.checked = true;
        const card = typeRadio.closest(".option-card");
        if (card) selectOptionCard(card, "type");
      }
    }
    if (config.difficulty) {
      const diffEl = document.getElementById("difficulty");
      if (diffEl) diffEl.value = config.difficulty;
    }
    if (config.total_questions) {
      const countEl = document.getElementById("questions_count");
      if (countEl) countEl.value = config.total_questions;
    }

    const setupNotice = document.getElementById("setup-notice");
    if (setupNotice) {
      setupNotice.textContent = "✓ Your selected interview configuration has been restored.";
      setupNotice.style.display = "block";
    }

    sessionStorage.removeItem("saved_interview_config");
  } catch (e) {
    console.error("Failed to restore saved interview config:", e);
  }
}

async function handleStartInterview(e) {
  e.preventDefault();

  const role = document.getElementById("role").value;
  const expEl = document.querySelector("input[name='experience']:checked");
  const typeEl = document.querySelector("input[name='type']:checked");
  const experience = expEl ? expEl.value : "Fresher";
  const interview_type = typeEl ? typeEl.value : "Technical";
  const difficulty = document.getElementById("difficulty").value;
  const total_questions = parseInt(document.getElementById("questions_count").value, 10);

  // 1. Detect if user is NOT logged in BEFORE making API request
  const token = ApiService.getAuthToken();
  if (!token) {
    // Preserve interview configuration
    const config = { role, experience, interview_type, difficulty, total_questions };
    sessionStorage.setItem("saved_interview_config", JSON.stringify(config));
    sessionStorage.setItem("redirect_after_login", "interview-setup.html");
    sessionStorage.setItem("login_notice", "Please log in to run an interview.");

    // Show user-friendly notice with explicit Login action
    const noticeDiv = document.getElementById("auth-notice");
    if (noticeDiv) {
      noticeDiv.innerHTML = `
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.5rem;">
          <span>🔒 Please log in to run an interview. Your configuration has been saved.</span>
          <a href="login.html" class="btn btn-primary" style="padding:0.35rem 0.85rem; font-size:0.8rem;">Log In Now →</a>
        </div>
      `;
      noticeDiv.style.display = "block";
      noticeDiv.scrollIntoView({ behavior: 'smooth' });
    }

    // Redirect to login page
    setTimeout(() => {
      window.location.href = "login.html";
    }, 1200);
    return;
  }

  const btn = document.getElementById("btn-start");
  btn.disabled = true;
  btn.textContent = "⏳ Compiling questions...";

  try {
    const res = await ApiService.createInterview(role, experience, interview_type, difficulty, total_questions);
    
    sessionStorage.removeItem("saved_interview_config");
    sessionStorage.setItem("active_interview", JSON.stringify(res));
    window.location.href = "interview.html";
  } catch (err) {
    const noticeDiv = document.getElementById("auth-notice");
    if (noticeDiv) {
      noticeDiv.textContent = err.message || "Execution failed. Please try again.";
      noticeDiv.style.display = "block";
    } else {
      alert(err.message || "Execution failed. Please try again.");
    }
  } finally {
    btn.disabled = false;
    btn.textContent = "▶ Run Interview";
  }
}

function selectOptionCard(cardEl, groupName) {
  const parent = cardEl.parentElement;
  parent.querySelectorAll(".option-card").forEach(c => c.classList.remove("selected"));
  cardEl.classList.add("selected");
  const radio = cardEl.querySelector("input[type='radio']");
  if (radio) radio.checked = true;
}
