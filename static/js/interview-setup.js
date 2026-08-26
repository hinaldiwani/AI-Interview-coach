async function handleStartInterview(e) {
  e.preventDefault();
  const btn = document.getElementById("btn-start");
  btn.disabled = true;
  btn.textContent = "⏳ Generating AI Questions...";

  const role = document.getElementById("role").value;
  const experience = document.querySelector("input[name='experience']:checked").value;
  const interview_type = document.querySelector("input[name='type']:checked").value;
  const difficulty = document.getElementById("difficulty").value;
  const total_questions = parseInt(document.getElementById("questions_count").value, 10);

  try {
    const res = await ApiService.createInterview(role, experience, interview_type, difficulty, total_questions);
    
    // Save session payload to sessionStorage
    sessionStorage.setItem("active_interview", JSON.stringify(res));
    window.location.href = "interview.html";
  } catch (err) {
    alert(`Failed to start interview: ${err.message}`);
  } finally {
    btn.disabled = false;
    btn.textContent = "🚀 Start Interview";
  }
}

function selectOptionCard(cardEl, groupName) {
  const parent = cardEl.parentElement;
  parent.querySelectorAll(".option-card").forEach(c => c.classList.remove("selected"));
  cardEl.classList.add("selected");
  const radio = cardEl.querySelector("input[type='radio']");
  if (radio) radio.checked = true;
}
