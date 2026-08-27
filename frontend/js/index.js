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
