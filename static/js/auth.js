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
    window.location.href = "dashboard.html";
  } catch (err) {
    if (errorDiv) {
      errorDiv.textContent = err.message;
      errorDiv.style.display = "block";
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
    window.location.href = "dashboard.html";
  } catch (err) {
    if (errorDiv) {
      errorDiv.textContent = err.message;
      errorDiv.style.display = "block";
    }
  }
}
