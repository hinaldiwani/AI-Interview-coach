document.addEventListener("DOMContentLoaded", () => {
  updateNavUserUI();

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

function updateNavUserUI() {
  const token = localStorage.getItem("token");
  const user = JSON.parse(localStorage.getItem("user") || "null");

  const navAuth = document.getElementById("nav-auth-links");
  const navUser = document.getElementById("nav-user-profile");
  const userNameSpan = document.getElementById("nav-user-name");

  if (token && user) {
    if (navAuth) navAuth.style.display = "none";
    if (navUser) navUser.style.display = "flex";
    if (userNameSpan) userNameSpan.textContent = user.name || "developer";
  } else {
    if (navAuth) navAuth.style.display = "flex";
    if (navUser) navUser.style.display = "none";
  }
}

function handleLogout() {
  ApiService.logout();
}

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
