document.addEventListener("DOMContentLoaded", () => {
  updateNavUserUI();
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
