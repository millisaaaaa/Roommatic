document.addEventListener("DOMContentLoaded", function () {
  setupStep1();
  setupStep2();
  setupStep3();
});

// ====================
// Step 1
// ====================
function setupStep1() {
  const form = document.getElementById("registerStep1Form");
  if (!form) return;

  const usernameInput = document.getElementById("username");
  const emailInput = document.getElementById("email");
  const passwordInput = document.getElementById("password");
  const confirmPasswordInput = document.getElementById("confirmPassword");
  const errorBox = document.getElementById("step1Error");

  form.addEventListener("submit", function (e) {
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

    const registerStep1Data = {
      username,
      email,
      password,
      confirm_password: confirmPassword
    };

    sessionStorage.setItem("registerStep1Data", JSON.stringify(registerStep1Data));
    window.location.href = "register-step2.html";
  });
}

// ====================
// Step 2
// ====================
function setupStep2() {
  const form = document.getElementById("registerStep2Form");
  if (!form) return;

  const errorBox = document.getElementById("step2Error");
  const savedStep2 = JSON.parse(sessionStorage.getItem("registerStep2Data") || "null");

  if (savedStep2) {
    if (savedStep2.mode === "create") {
      selectRegisterMode("create");
      const createOrgName = document.getElementById("createOrgName");
      const createOrgType = document.getElementById("createOrgType");
      const createOrgJoinCode = document.getElementById("createOrgJoinCode");

      if (createOrgName) createOrgName.value = savedStep2.create_org_name || "";
      if (createOrgType) createOrgType.value = savedStep2.create_org_type || "";
      if (createOrgJoinCode) createOrgJoinCode.value = savedStep2.create_org_join_code || "";
    } else if (savedStep2.mode === "join") {
      selectRegisterMode("join");
      const joinOrgName = document.getElementById("joinOrgName");
      const joinOrgPassword = document.getElementById("joinOrgPassword");

      if (joinOrgName) joinOrgName.value = savedStep2.join_org_name || "";
      if (joinOrgPassword) joinOrgPassword.value = savedStep2.join_org_password || "";
    }
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();

    errorBox.textContent = "";

    const selectedMode = window.selectedRegisterMode;

    if (!selectedMode) {
      errorBox.textContent = "請先選擇開始方式";
      return;
    }

    const step2Data = { mode: selectedMode };

    if (selectedMode === "create") {
      const createOrgName = document.getElementById("createOrgName").value.trim();
      const createOrgType = document.getElementById("createOrgType").value.trim();
      const createOrgJoinCode = document.getElementById("createOrgJoinCode").value.trim();

      if (!createOrgName || !createOrgType || !createOrgJoinCode) {
        errorBox.textContent = "請完整填寫建立組織資料";
        return;
      }

      step2Data.create_org_name = createOrgName;
      step2Data.create_org_type = createOrgType;
      step2Data.create_org_join_code = createOrgJoinCode;
    }

    if (selectedMode === "join") {
      const joinOrgName = document.getElementById("joinOrgName").value.trim();
      const joinOrgPassword = document.getElementById("joinOrgPassword").value.trim();

      if (!joinOrgName || !joinOrgPassword) {
        errorBox.textContent = "請完整填寫加入組織資料";
        return;
      }

      step2Data.join_org_name = joinOrgName;
      step2Data.join_org_password = joinOrgPassword;
    }

    sessionStorage.setItem("registerStep2Data", JSON.stringify(step2Data));
    window.location.href = "register-step3.html";
  });
}

function selectRegisterMode(mode) {
  window.selectedRegisterMode = mode;

  const createCard = document.getElementById("createCard");
  const joinCard = document.getElementById("joinCard");
  const createFields = document.getElementById("createFields");
  const joinFields = document.getElementById("joinFields");

  if (!createCard || !joinCard || !createFields || !joinFields) return;

  createCard.classList.remove("active");
  joinCard.classList.remove("active");

  if (mode === "create") {
    createCard.classList.add("active");
    createFields.style.display = "block";
    joinFields.style.display = "none";
  }

  if (mode === "join") {
    joinCard.classList.add("active");
    createFields.style.display = "none";
    joinFields.style.display = "block";
  }
}

function goToStep1() {
  window.location.href = "register-step1.html";
}

// ====================
// Step 3
// ====================
function setupStep3() {
  const usernameEl = document.getElementById("summaryUsername");
  if (!usernameEl) return;

  const step1Data = JSON.parse(sessionStorage.getItem("registerStep1Data") || "null");
  const step2Data = JSON.parse(sessionStorage.getItem("registerStep2Data") || "null");
  const errorBox = document.getElementById("step3Error");

  if (!step1Data || !step2Data) {
    errorBox.textContent = "註冊資料不完整，請重新開始";
    return;
  }

  document.getElementById("summaryUsername").textContent = step1Data.username || "-";
  document.getElementById("summaryEmail").textContent = step1Data.email || "-";
  document.getElementById("summaryPassword").textContent = "******";

  if (step2Data.mode === "create") {
    document.getElementById("summaryMode").textContent = "建立新組織";
    document.getElementById("summaryOrgName").textContent = step2Data.create_org_name || "-";
    document.getElementById("summaryOrgType").textContent = translateOrgType(step2Data.create_org_type);

    const orgTypeRow = document.getElementById("summaryOrgTypeRow");
    const orgPasswordRow = document.getElementById("summaryOrgPasswordRow");
    const orgPassword = document.getElementById("summaryOrgPassword");

    if (orgTypeRow) orgTypeRow.style.display = "flex";
    if (orgPasswordRow) orgPasswordRow.style.display = "block";
    if (orgPassword) orgPassword.textContent = "******";
  } else {
    document.getElementById("summaryMode").textContent = "加入既有組織";
    document.getElementById("summaryOrgName").textContent = step2Data.join_org_name || "-";

    const orgTypeRow = document.getElementById("summaryOrgTypeRow");
    const orgPasswordRow = document.getElementById("summaryOrgPasswordRow");
    const orgPassword = document.getElementById("summaryOrgPassword");

    if (orgTypeRow) orgTypeRow.style.display = "none";
    if (orgPasswordRow) orgPasswordRow.style.display = "block";
    if (orgPassword) orgPassword.textContent = "******";
  }
}

function translateOrgType(type) {
  if (type === "personal") return "個人版（1-3 個空間）";
  if (type === "team") return "團隊版（4-10 個空間）";
  if (type === "enterprise") return "企業版（11-30 個空間）";
  return "-";
}

function goToStep2() {
  window.location.href = "register-step2.html";
}

async function finishRegister() {
  const errorBox = document.getElementById("step3Error");
  const agreeTerms = document.getElementById("agreeTerms");

  errorBox.textContent = "";

  if (!agreeTerms.checked) {
    errorBox.textContent = "請先同意服務條款與隱私政策";
    return;
  }

  const step1Data = JSON.parse(sessionStorage.getItem("registerStep1Data") || "null");
  const step2Data = JSON.parse(sessionStorage.getItem("registerStep2Data") || "null");

  if (!step1Data || !step2Data) {
    errorBox.textContent = "註冊資料不完整，請重新開始";
    return;
  }

  try {
    const formData = new FormData();

    formData.append("username", step1Data.username || "");
    formData.append("email", step1Data.email || "");
    formData.append("password", step1Data.password || "");
    formData.append("confirm_password", step1Data.confirm_password || "");

    formData.append("mode", step2Data.mode || "");

    if (step2Data.mode === "create") {
      formData.append("create_org_name", step2Data.create_org_name || "");
      formData.append("create_org_type", step2Data.create_org_type || "");
      formData.append("create_org_join_code", step2Data.create_org_join_code || "");
    }

    if (step2Data.mode === "join") {
      formData.append("join_org_name", step2Data.join_org_name || "");
      formData.append("join_org_password", step2Data.join_org_password || "");
    }

    formData.append("agree_terms", "true");

    const response = await fetch("../php/complete_register.php", {
      method: "POST",
      body: formData,
      credentials: "same-origin"
    });

    const rawText = await response.text();
    console.log("complete_register raw response:", rawText);

    let result;
    try {
      result = JSON.parse(rawText);
    } catch (e) {
      throw new Error("後端回傳不是 JSON，請檢查 PHP 錯誤或路徑是否正確");
    }

    if (!result.success) {
      errorBox.textContent = result.message || "註冊失敗";
      return;
    }

    // 註冊成功後不要直接視為已登入
    sessionStorage.removeItem("user");
    sessionStorage.removeItem("registerStep1Data");
    sessionStorage.removeItem("registerStep2Data");

    alert("註冊成功，請重新登入");
    window.location.href = "login.html";
  } catch (error) {
    console.error("finishRegister error:", error);
    errorBox.textContent = "註冊失敗：" + error.message;
  }
}

// ====================
// Modal
// ====================
function openPolicyModal(type) {
  const modal = document.getElementById("policyModal");
  const title = document.getElementById("policyModalTitle");
  const body = document.getElementById("policyModalBody");

  if (!modal || !title || !body) return;

  if (type === "terms") {
    title.textContent = "服務條款";
    body.innerHTML = `
      <p>歡迎使用 ROOMMATIC。使用本服務即表示你同意遵守本平台之使用規範。</p>
      <p>請勿以不正當方式使用系統、冒用他人身份或干擾平台運作。</p>
    `;
  } else {
    title.textContent = "隱私政策";
    body.innerHTML = `
      <p>我們會蒐集你註冊與使用過程中的必要資料，以提供帳號、組織與系統功能。</p>
      <p>我們不會在未經同意的情況下將個人資料提供給第三方。</p>
    `;
  }

  modal.style.display = "flex";
}

function closePolicyModal() {
  const modal = document.getElementById("policyModal");
  if (modal) {
    modal.style.display = "none";
  }
}