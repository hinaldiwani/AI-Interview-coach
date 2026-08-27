document.addEventListener("DOMContentLoaded", async () => {
  if (!ApiService.getAuthToken()) {
    sessionStorage.setItem("login_notice", "Please log in to view your developer profile.");
    sessionStorage.setItem("redirect_after_login", "profile.html");
    window.location.href = "login.html";
    return;
  }
  try {
    const profileData = await ApiService.getProfile();
    const u = profileData.user;
    document.getElementById("prof-name").value = u.name;
    document.getElementById("prof-email").value = u.email;
    document.getElementById("prof-created").value = new Date(u.created_at).toLocaleString();
  } catch (e) {
    console.error(e);
  }
});

function handleLogout() {
  ApiService.logout();
}
