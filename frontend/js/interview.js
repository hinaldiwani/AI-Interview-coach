let activeSession = null;
let currentIndex = 0;
let userAnswers = {};
let remainingSeconds = 0;
let timerInterval = null;
let speechRecognizer = null;
let isListening = false;
let isSubmitting = false;
let interviewTerminated = false;
let isInterviewCompleted = false;

document.addEventListener("DOMContentLoaded", async () => {
  const dataStr = sessionStorage.getItem("active_interview");
  if (!dataStr) {
    window.location.href = "interview-setup.html";
    return;
  }
  activeSession = JSON.parse(dataStr);

  // Check remote interview status for refresh persistence
  try {
    const remoteSession = await ApiService.getInterview(activeSession.interview_id);
    if (remoteSession && remoteSession.status === "terminated") {
      interviewTerminated = true;
      showTerminationModal();
      return;
    }
  } catch (e) {
    console.warn("Could not fetch remote session status:", e);
  }

  initSpeech();
  initCountdownTimer();
  renderQuestion();
  initTabSwitchDetection();
});

function initCountdownTimer() {
  const interviewId = activeSession.interview_id;
  const durationSec = activeSession.duration_seconds || activeSession.total_duration_seconds || (activeSession.questions ? activeSession.questions.length * 180 : 1800);

  const startKey = `interview_start_timestamp_${interviewId}`;
  let startTime = sessionStorage.getItem(startKey);

  if (!startTime || isNaN(parseInt(startTime, 10))) {
    if (activeSession.start_timestamp && !isNaN(parseInt(activeSession.start_timestamp, 10))) {
      startTime = parseInt(activeSession.start_timestamp, 10);
    } else {
      startTime = Date.now();
    }
    sessionStorage.setItem(startKey, startTime);
  } else {
    startTime = parseInt(startTime, 10);
  }

  const elapsedSeconds = Math.floor((Date.now() - startTime) / 1000);
  remainingSeconds = Math.max(0, durationSec - elapsedSeconds);

  updateTimerDisplay();

  if (timerInterval) clearInterval(timerInterval);
  timerInterval = setInterval(() => {
    remainingSeconds--;
    if (remainingSeconds <= 0) {
      remainingSeconds = 0;
      updateTimerDisplay();
      clearInterval(timerInterval);
      handleTimeUp();
    } else {
      updateTimerDisplay();
    }
  }, 1000);
}

function updateTimerDisplay() {
  if (isNaN(remainingSeconds) || remainingSeconds < 0) {
    remainingSeconds = 0;
  }

  const mins = Math.floor(remainingSeconds / 60);
  const secs = remainingSeconds % 60;
  const displayStr = `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
  
  const clockEl = document.getElementById("countdown-clock");
  if (clockEl) {
    clockEl.textContent = displayStr;
    clockEl.classList.remove("clock-warning", "clock-danger");
    if (remainingSeconds <= 60) {
      clockEl.classList.add("clock-danger");
    } else if (remainingSeconds <= 300) {
      clockEl.classList.add("clock-warning");
    }
  }
}

async function handleTimeUp() {
  if (isSubmitting) return;
  isSubmitting = true;

  const banner = document.getElementById("timeout-banner");
  if (banner) banner.style.display = "block";

  // Save current response
  const q = activeSession.questions[currentIndex];
  if (q) {
    const inputEl = document.getElementById("answer-input");
    if (inputEl) userAnswers[q.id] = inputEl.value.trim();
  }

  // Submit current answer if present
  try {
    if (q && userAnswers[q.id]) {
      await ApiService.submitAnswer(activeSession.interview_id, q.id, userAnswers[q.id]);
    }
  } catch (e) {
    console.error("Auto submit answer error:", e);
  }

  setTimeout(async () => {
    await finalizeInterview();
  }, 1200);
}

function renderQuestion() {
  const q = activeSession.questions[currentIndex];
  const total = activeSession.questions.length;
  const num = currentIndex + 1;

  document.getElementById("q-number-tag").textContent = `Question ${num} of ${total}`;
  document.getElementById("q-type-tag").textContent = (q.question_type || activeSession.interview_type || "Technical").toUpperCase();
  document.getElementById("q-text").textContent = q.question_text;

  const inputEl = document.getElementById("answer-input");
  inputEl.value = userAnswers[q.id] || "";

  document.getElementById("btn-prev").disabled = (currentIndex === 0);
  const nextBtn = document.getElementById("btn-submit");
  if (num === total) {
    nextBtn.textContent = "Finish & Evaluate Interview 🏆";
  } else {
    nextBtn.textContent = "Submit Answer ➔";
  }
}

function navigateQuestion(dir) {
  const q = activeSession.questions[currentIndex];
  userAnswers[q.id] = document.getElementById("answer-input").value;
  const newIdx = currentIndex + dir;
  if (newIdx >= 0 && newIdx < activeSession.questions.length) {
    currentIndex = newIdx;
    renderQuestion();
  }
}

function skipQuestion() {
  const q = activeSession.questions[currentIndex];
  userAnswers[q.id] = "";
  if (currentIndex < activeSession.questions.length - 1) {
    currentIndex++;
    renderQuestion();
  } else {
    submitAnswer();
  }
}

async function submitAnswer() {
  if (isSubmitting) return;

  const q = activeSession.questions[currentIndex];
  const text = document.getElementById("answer-input").value.trim();
  userAnswers[q.id] = text;

  const btn = document.getElementById("btn-submit");
  btn.disabled = true;
  btn.textContent = "⏳ Evaluating Answer...";

  try {
    await ApiService.submitAnswer(activeSession.interview_id, q.id, text);

    if (currentIndex < activeSession.questions.length - 1) {
      currentIndex++;
      renderQuestion();
    } else {
      isSubmitting = true;
      await finalizeInterview();
    }
  } catch (err) {
    console.error("Submit answer error:", err);
    alert(err.message || "Unable to submit answer. Please try again.");
  } finally {
    if (!isSubmitting) {
      btn.disabled = false;
    }
  }
}

async function finalizeInterview() {
  isInterviewCompleted = true;
  if (timerInterval) {
    clearInterval(timerInterval);
    timerInterval = null;
  }
  try {
    await ApiService.completeInterview(activeSession.interview_id);
    window.location.href = `results.html?id=${activeSession.interview_id}`;
  } catch (err) {
    console.error("Finalization error:", err);
    window.location.href = `results.html?id=${activeSession.interview_id}`;
  }
}

/* --- Strict Tab Switch Detection System --- */
function initTabSwitchDetection() {
  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "hidden") {
      handleTabSwitchViolation();
    } else if (document.visibilityState === "visible") {
      if (interviewTerminated) {
        showTerminationModal();
      }
    }
  });

  window.addEventListener("blur", () => {
    handleTabSwitchViolation();
  });

  window.addEventListener("focus", () => {
    if (interviewTerminated) {
      showTerminationModal();
    }
  });
}

function handleTabSwitchViolation() {
  if (interviewTerminated || isSubmitting || isInterviewCompleted) return;
  interviewTerminated = true;

  // 1. Immediately stop countdown timer
  if (timerInterval) {
    clearInterval(timerInterval);
    timerInterval = null;
  }

  // 2. Disable UI controls
  const inputEl = document.getElementById("answer-input");
  if (inputEl) inputEl.disabled = true;
  const btnSubmit = document.getElementById("btn-submit");
  if (btnSubmit) btnSubmit.disabled = true;
  const btnPrev = document.getElementById("btn-prev");
  if (btnPrev) btnPrev.disabled = true;

  // 3. Notify backend of termination
  if (activeSession && activeSession.interview_id) {
    notifyBackendTermination(activeSession.interview_id);
  }

  // 4. If currently visible/focused, display termination modal
  if (document.visibilityState === "visible" || document.hasFocus()) {
    showTerminationModal();
  }
}

function notifyBackendTermination(interviewId) {
  const url = `${API_BASE_URL}/api/interviews/${interviewId}/terminate`;
  const token = ApiService.getAuthToken();

  if (navigator.sendBeacon && token) {
    const payload = JSON.stringify({ reason: "tab_switch" });
    fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
      },
      body: payload,
      keepalive: true
    }).catch(err => console.error("Termination fetch error:", err));
  } else {
    ApiService.terminateInterview(interviewId, "tab_switch")
      .catch(err => console.error("Terminate interview API error:", err));
  }
}

function showTerminationModal() {
  const modal = document.getElementById("termination-modal");
  if (modal) {
    modal.style.display = "flex";
  }
}

function viewTerminationResults() {
  if (activeSession && activeSession.interview_id) {
    window.location.href = `results.html?id=${activeSession.interview_id}`;
  } else {
    window.location.href = "dashboard.html";
  }
}

function initSpeech() {
  const Speech = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!Speech) return;
  speechRecognizer = new Speech();
  speechRecognizer.continuous = true;
  speechRecognizer.interimResults = true;
  speechRecognizer.lang = 'en-US';

  speechRecognizer.onresult = (e) => {
    let text = '';
    for (let i = e.resultIndex; i < e.results.length; i++) {
      text += e.results[i][0].transcript;
    }
    const input = document.getElementById("answer-input");
    input.value += (input.value ? ' ' : '') + text;
  };
}

function toggleVoiceInput() {
  if (!speechRecognizer) {
    alert("Browser speech recognition not supported.");
    return;
  }
  const btn = document.getElementById("mic-btn");
  if (isListening) {
    speechRecognizer.stop();
    isListening = false;
    btn.classList.remove("listening");
    btn.textContent = "🎙️ Start Voice Answer";
  } else {
    speechRecognizer.start();
    isListening = true;
    btn.classList.add("listening");
    btn.textContent = "🎙️ Listening... (Click to Stop)";
  }
}

function handleLogout() {
  ApiService.logout();
}
