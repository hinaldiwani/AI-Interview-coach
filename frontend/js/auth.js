async function handleLogin(e) {
  e.preventDefault();
  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value.trim();
  const errorDiv = document.getElementById("error-msg");
  if (errorDiv) errorDiv.style.display = "none";

  try {
    const res = await ApiService.login(email, password);
    localStorage.setItem("token", res.token);
    localStorage.setItem("user", JSON.stringify(res.user));

    const redirectUrl = sessionStorage.getItem("redirect_after_login");
    if (redirectUrl) {
      sessionStorage.removeItem("redirect_after_login");
      window.location.href = redirectUrl;
    } else {
      window.location.href = "dashboard.html";
    }
  } catch (err) {
    if (errorDiv) {
      let msg = err.message;
      if (msg.includes("Authorization header missing") || msg.includes("Could not validate credentials")) {
        msg = "Invalid email or password.";
      }
      errorDiv.textContent = msg;
      errorDiv.style.display = "block";
      errorDiv.style.backgroundColor = "";
      errorDiv.style.color = "";
      errorDiv.style.borderColor = "";
    }
  }
}

async function handleRegister(e) {
  e.preventDefault();
  const name = document.getElementById("name").value.trim();
  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value.trim();
  const confirmPassword = document.getElementById("confirmPassword").value.trim();
  const errorDiv = document.getElementById("error-msg");
  if (errorDiv) errorDiv.style.display = "none";

  if (password !== confirmPassword) {
    if (errorDiv) {
      errorDiv.textContent = "Passwords do not match!";
      errorDiv.style.display = "block";
    }
    return;
  }

  try {
    const res = await ApiService.register(name, email, password);
    localStorage.setItem("token", res.token);
    localStorage.setItem("user", JSON.stringify(res.user));

    const redirectUrl = sessionStorage.getItem("redirect_after_login");
    if (redirectUrl) {
      sessionStorage.removeItem("redirect_after_login");
      window.location.href = redirectUrl;
    } else {
      window.location.href = "dashboard.html";
    }
  } catch (err) {
    if (errorDiv) {
      errorDiv.textContent = err.message;
      errorDiv.style.display = "block";
    }
  }
}

// Display session notices (e.g. "Please log in to start an interview.") when login page loads
document.addEventListener("DOMContentLoaded", () => {
  const notice = sessionStorage.getItem("login_notice");
  if (notice) {
    const errorDiv = document.getElementById("error-msg");
    if (errorDiv) {
      errorDiv.textContent = notice;
      errorDiv.style.display = "block";
      errorDiv.style.backgroundColor = "var(--primary-light)";
      errorDiv.style.color = "var(--primary-dark)";
      errorDiv.style.borderColor = "rgba(15, 118, 110, 0.3)";
    }
    sessionStorage.removeItem("login_notice");
  }
});
