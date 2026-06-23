document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("registerStep1Form");
  const usernameInput = document.getElementById("username");
  const emailInput = document.getElementById("email");
  const passwordInput = document.getElementById("password");
  const confirmPasswordInput = document.getElementById("confirmPassword");
  const errorBox = document.getElementById("step1Error");

  if (!form) return;

  form.addEventListener("submit", async function (e) {
    e.preventDefault();

    errorBox.textContent = "";

    const username = usernameInput.value.trim();
    const email = emailInput.value.trim();
    const password = passwordInput.value.trim();
    const confirmPassword = confirmPasswordInput.value.trim();

    if (!username || !email || !password || !confirmPassword) {
      errorBox.textContent = "請完整填寫所有欄位";
      return;
    }

    if (password !== confirmPassword) {
      errorBox.textContent = "兩次密碼輸入不一致";
      return;
    }

    try {
      const formData = new FormData();
      formData.append("username", username);
      formData.append("email", email);
      formData.append("password", password);
      formData.append("confirm_password", confirmPassword);

      const response = await fetch("../php/register.php", {
        method: "POST",
        body: formData,
        credentials: "same-origin"
      });

      const result = await response.json();

      if (!result.success) {
        errorBox.textContent = result.message;
        return;
      }

      // 暫存剛註冊成功的使用者資訊，後面 step2 / step3 可以接著用
      sessionStorage.setItem("pendingRegisterUser", JSON.stringify({
        user_id: result.user_id,
        username,
        email
      }));

      // 前往下一步
      window.location.href = "register-step2.html";
    } catch (error) {
      console.error(error);
      errorBox.textContent = "註冊失敗，請稍後再試";
    }
  });
});