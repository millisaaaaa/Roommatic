document.addEventListener("DOMContentLoaded", function () {
  const loginForm = document.getElementById("loginForm");
  const loginEmail = document.getElementById("loginEmail");
  const loginPassword = document.getElementById("loginPassword");
  const loginError = document.getElementById("loginError");

  if (!loginForm) return;

  loginForm.addEventListener("submit", async function (e) {
    e.preventDefault();

    loginError.textContent = "";

    const email = loginEmail.value.trim();
    const password = loginPassword.value.trim();

    if (!email || !password) {
      loginError.textContent = "請輸入 Email 和密碼";
      return;
    }

    try {
      const formData = new FormData();
      formData.append("email", email);
      formData.append("password", password);

      const response = await fetch("../php/login.php", {
        method: "POST",
        body: formData,
        credentials: "same-origin"
      });

      const result = await response.json();

      if (!result.success) {
        loginError.textContent = result.message;
        return;
      }

      sessionStorage.setItem("user", JSON.stringify(result.user));

      window.location.href = "../app/dashboard.html";
    } catch (error) {
      console.error(error);
      loginError.textContent = "登入失敗，請稍後再試";
    }
  });
});

function showForgotPassword() {
  alert("忘記密碼功能尚未開放");
}