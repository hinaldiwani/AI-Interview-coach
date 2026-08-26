let activeSession = null;
let currentIndex = 0;
let userAnswers = {};
let timeElapsed = 0;
let timerInterval = null;
let speechRecognizer = null;
let isListening = false;

document.addEventListener("DOMContentLoaded", () => {
  const dataStr = sessionStorage.getItem("active_interview");
  if (!dataStr) {
    window.location.href = "interview-setup.html";
    return;
  }
  activeSession = JSON.parse(dataStr);
  initSpeech();
  startTimer();
  renderQuestion();
});

function renderQuestion() {
  const q = activeSession.questions[currentIndex];
  const total = activeSession.questions.length;
  const num = currentIndex + 1;

  document.getElementById("q-number-tag").textContent = `Question ${num} of ${total}`;
  document.getElementById("q-type-tag").textContent = q.question_type || "Technical";
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
      await finalizeInterview();
    }
  } catch (err) {
    alert(`Error: ${err.message}`);
  } finally {
    btn.disabled = false;
  }
}

async function finalizeInterview() {
  clearInterval(timerInterval);
  try {
    const res = await ApiService.completeInterview(activeSession.interview_id);
    window.location.href = `results.html?id=${activeSession.interview_id}`;
  } catch (err) {
    alert(`Finalization Error: ${err.message}`);
  }
}

function startTimer() {
  timerInterval = setInterval(() => {
    timeElapsed++;
    const mins = Math.floor(timeElapsed / 60);
    const secs = timeElapsed % 60;
    document.getElementById("timer-display").textContent = `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
  }, 1000);
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
