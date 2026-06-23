<?php
header('Content-Type: application/json; charset=utf-8');
session_start();

include("db_connect.php");

if ($_SERVER["REQUEST_METHOD"] !== "POST") {
    echo json_encode([
        "success" => false,
        "message" => "請使用 POST 方式提交資料"
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

// 基本帳號資料
$username = isset($_POST["username"]) ? trim($_POST["username"]) : "";
$email = isset($_POST["email"]) ? trim($_POST["email"]) : "";
$password = isset($_POST["password"]) ? trim($_POST["password"]) : "";
$confirm_password = isset($_POST["confirm_password"]) ? trim($_POST["confirm_password"]) : "";

// 組織流程資料
$mode = isset($_POST["mode"]) ? trim($_POST["mode"]) : "";

// create 模式
$create_org_name = isset($_POST["create_org_name"]) ? trim($_POST["create_org_name"]) : "";
$create_org_type = isset($_POST["create_org_type"]) ? trim($_POST["create_org_type"]) : "";
$create_org_join_code = isset($_POST["create_org_join_code"]) ? trim($_POST["create_org_join_code"]) : "";

// join 模式
$join_org_name = isset($_POST["join_org_name"]) ? trim($_POST["join_org_name"]) : "";
$join_org_password = isset($_POST["join_org_password"]) ? trim($_POST["join_org_password"]) : "";

// 條款
$agree_terms = isset($_POST["agree_terms"]) ? trim($_POST["agree_terms"]) : "false";

// 驗證基本欄位
if ($username === "" || $email === "" || $password === "" || $confirm_password === "") {
    echo json_encode([
        "success" => false,
        "message" => "基本資料未填完整"
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
    echo json_encode([
        "success" => false,
        "message" => "Email 格式不正確"
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

if ($password !== $confirm_password) {
    echo json_encode([
        "success" => false,
        "message" => "兩次密碼輸入不一致"
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

if (mb_strlen($password) < 6) {
    echo json_encode([
        "success" => false,
        "message" => "密碼至少要 6 碼"
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

if ($agree_terms !== "true") {
    echo json_encode([
        "success" => false,
        "message" => "請先同意服務條款與隱私政策"
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

// 驗證 mode
if ($mode !== "create" && $mode !== "join") {
    echo json_encode([
        "success" => false,
        "message" => "開始方式錯誤"
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

// 檢查 email 是否已存在
$check_email_sql = "SELECT user_id FROM users WHERE email = ?";
$check_email_stmt = $conn->prepare($check_email_sql);

if (!$check_email_stmt) {
    echo json_encode([
        "success" => false,
        "message" => "SQL 預處理失敗：" . $conn->error
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

$check_email_stmt->bind_param("s", $email);
$check_email_stmt->execute();
$check_email_result = $check_email_stmt->get_result();

if ($check_email_result->num_rows > 0) {
    echo json_encode([
        "success" => false,
        "message" => "此 Email 已被註冊"
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

$check_email_stmt->close();

// create 模式預設
$plan_id = 1;
$space = 3;
$org_status = "active";

// create 模式驗證
if ($mode === "create") {
    if ($create_org_name === "" || $create_org_type === "" || $create_org_join_code === "") {
        echo json_encode([
            "success" => false,
            "message" => "建立組織資料未填完整"
        ], JSON_UNESCAPED_UNICODE);
        exit;
    }

    // 組織名稱是否重複
    $check_org_name_sql = "SELECT org_id FROM org WHERE org_name = ?";
    $check_org_name_stmt = $conn->prepare($check_org_name_sql);

    if (!$check_org_name_stmt) {
        echo json_encode([
            "success" => false,
            "message" => "SQL 預處理失敗：" . $conn->error
        ], JSON_UNESCAPED_UNICODE);
        exit;
    }

    $check_org_name_stmt->bind_param("s", $create_org_name);
    $check_org_name_stmt->execute();
    $check_org_name_result = $check_org_name_stmt->get_result();

    if ($check_org_name_result->num_rows > 0) {
        echo json_encode([
            "success" => false,
            "message" => "此組織名稱已存在"
        ], JSON_UNESCAPED_UNICODE);
        exit;
    }

    $check_org_name_stmt->close();

    // 組織類型對應方案
    if ($create_org_type === "personal") {
        $plan_id = 1;
        $space = 3;
    } elseif ($create_org_type === "team") {
        $plan_id = 2;
        $space = 10;
    } elseif ($create_org_type === "enterprise") {
        $plan_id = 3;
        $space = 30;
    } else {
        echo json_encode([
            "success" => false,
            "message" => "組織類型錯誤"
        ], JSON_UNESCAPED_UNICODE);
        exit;
    }
}

// join 模式驗證
$target_org_id = null;
$target_org_name = null;

if ($mode === "join") {
    if ($join_org_name === "" || $join_org_password === "") {
        echo json_encode([
            "success" => false,
            "message" => "加入組織資料未填完整"
        ], JSON_UNESCAPED_UNICODE);
        exit;
    }

    $find_org_sql = "SELECT org_id, org_name FROM org WHERE org_name = ? AND org_password = ?";
    $find_org_stmt = $conn->prepare($find_org_sql);

    if (!$find_org_stmt) {
        echo json_encode([
            "success" => false,
            "message" => "SQL 預處理失敗：" . $conn->error
        ], JSON_UNESCAPED_UNICODE);
        exit;
    }

    $find_org_stmt->bind_param("ss", $join_org_name, $join_org_password);
    $find_org_stmt->execute();
    $find_org_result = $find_org_stmt->get_result();

    if ($find_org_result->num_rows === 0) {
        echo json_encode([
            "success" => false,
            "message" => "組織名稱或加入組織碼錯誤"
        ], JSON_UNESCAPED_UNICODE);
        exit;
    }

    $org = $find_org_result->fetch_assoc();
    $target_org_id = (int)$org["org_id"];
    $target_org_name = $org["org_name"];

    $find_org_stmt->close();
}

// 開始交易
$conn->begin_transaction();

try {
    // 1. 建立 users
    $insert_user_sql = "INSERT INTO users (username, email, user_password) VALUES (?, ?, ?)";
    $insert_user_stmt = $conn->prepare($insert_user_sql);

    if (!$insert_user_stmt) {
        throw new Exception("建立使用者 SQL 預處理失敗：" . $conn->error);
    }

    $insert_user_stmt->bind_param("sss", $username, $email, $password);

    if (!$insert_user_stmt->execute()) {
        throw new Exception("建立使用者失敗：" . $insert_user_stmt->error);
    }

    $new_user_id = $insert_user_stmt->insert_id;
    $insert_user_stmt->close();

    // 2. 根據 mode 建立或加入組織
    if ($mode === "create") {
        $insert_org_sql = "
            INSERT INTO org (org_name, org_admid, org_password, plan_id, start_date, end_date, space, org_status)
            VALUES (?, ?, ?, ?, NOW(), DATE_ADD(NOW(), INTERVAL 30 DAY), ?, ?)
        ";
        $insert_org_stmt = $conn->prepare($insert_org_sql);

        if (!$insert_org_stmt) {
            throw new Exception("建立組織 SQL 預處理失敗：" . $conn->error);
        }

        $insert_org_stmt->bind_param("sisiss", $create_org_name, $new_user_id, $create_org_join_code, $plan_id, $space, $org_status);

        if (!$insert_org_stmt->execute()) {
            throw new Exception("建立組織失敗：" . $insert_org_stmt->error);
        }

        $new_org_id = $insert_org_stmt->insert_id;
        $insert_org_stmt->close();
    } else {
        $new_org_id = $target_org_id;
    }

    // 3. 建立 user_org
    $insert_user_org_sql = "INSERT INTO user_org (user_id, org_id) VALUES (?, ?)";
    $insert_user_org_stmt = $conn->prepare($insert_user_org_sql);

    if (!$insert_user_org_stmt) {
        throw new Exception("建立 user_org SQL 預處理失敗：" . $conn->error);
    }

    $insert_user_org_stmt->bind_param("ii", $new_user_id, $new_org_id);

    if (!$insert_user_org_stmt->execute()) {
        throw new Exception("建立 user_org 關聯失敗：" . $insert_user_org_stmt->error);
    }

    $insert_user_org_stmt->close();

    // 4. 不自動登入：清掉可能殘留的 session 資料
    if (session_status() === PHP_SESSION_ACTIVE) {
        session_unset();
    }

    $conn->commit();

    echo json_encode([
        "success" => true,
        "message" => "註冊完成，請重新登入"
    ], JSON_UNESCAPED_UNICODE);

} catch (Exception $e) {
    $conn->rollback();

    echo json_encode([
        "success" => false,
        "message" => $e->getMessage()
    ], JSON_UNESCAPED_UNICODE);
}

$conn->close();
?>