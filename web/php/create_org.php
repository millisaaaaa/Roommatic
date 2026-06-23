<?php
header('Content-Type: application/json; charset=utf-8');
session_start();

include("db_connect.php");

// 只接受 POST
if ($_SERVER["REQUEST_METHOD"] !== "POST") {
    echo json_encode([
        "success" => false,
        "message" => "請使用 POST 方式提交資料"
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

// 檢查是否已登入
if (!isset($_SESSION["user_id"])) {
    echo json_encode([
        "success" => false,
        "message" => "尚未登入，無法建立組織"
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

$user_id = (int)$_SESSION["user_id"];
$org_name = isset($_POST["org_name"]) ? trim($_POST["org_name"]) : "";
$org_password = isset($_POST["org_password"]) ? trim($_POST["org_password"]) : "";

// 基本驗證
if ($org_name === "" || $org_password === "") {
    echo json_encode([
        "success" => false,
        "message" => "組織名稱與組織密碼不可空白"
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

// 檢查這個 user 是否已經加入某個組織
$check_org_sql = "SELECT org_id FROM user_org WHERE user_id = ?";
$check_org_stmt = $conn->prepare($check_org_sql);

if (!$check_org_stmt) {
    echo json_encode([
        "success" => false,
        "message" => "SQL 預處理失敗：" . $conn->error
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

$check_org_stmt->bind_param("i", $user_id);
$check_org_stmt->execute();
$check_org_result = $check_org_stmt->get_result();

if ($check_org_result->num_rows > 0) {
    echo json_encode([
        "success" => false,
        "message" => "你已經加入組織，無法再建立新組織"
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

$check_org_stmt->close();

// 檢查組織名稱是否重複
$check_name_sql = "SELECT org_id FROM org WHERE org_name = ?";
$check_name_stmt = $conn->prepare($check_name_sql);

if (!$check_name_stmt) {
    echo json_encode([
        "success" => false,
        "message" => "SQL 預處理失敗：" . $conn->error
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

$check_name_stmt->bind_param("s", $org_name);
$check_name_stmt->execute();
$check_name_result = $check_name_stmt->get_result();

if ($check_name_result->num_rows > 0) {
    echo json_encode([
        "success" => false,
        "message" => "此組織名稱已存在"
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

$check_name_stmt->close();

// 預設方案與狀態
$plan_id = 1;
$space = 3;
$org_status = "active";

// 交易開始
$conn->begin_transaction();

try {
    // 1. 建立組織
    $insert_org_sql = "
        INSERT INTO org (org_name, org_admid, org_password, plan_id, start_date, end_date, space, org_status)
        VALUES (?, ?, ?, ?, NOW(), DATE_ADD(NOW(), INTERVAL 30 DAY), ?, ?)
    ";
    $insert_org_stmt = $conn->prepare($insert_org_sql);

    if (!$insert_org_stmt) {
        throw new Exception("建立組織 SQL 預處理失敗：" . $conn->error);
    }

    $insert_org_stmt->bind_param("sisiss", $org_name, $user_id, $org_password, $plan_id, $space, $org_status);

    if (!$insert_org_stmt->execute()) {
        throw new Exception("建立組織失敗：" . $insert_org_stmt->error);
    }

    $new_org_id = $insert_org_stmt->insert_id;
    $insert_org_stmt->close();

    // 2. 建立 user_org 關聯
    $insert_user_org_sql = "INSERT INTO user_org (user_id, org_id) VALUES (?, ?)";
    $insert_user_org_stmt = $conn->prepare($insert_user_org_sql);

    if (!$insert_user_org_stmt) {
        throw new Exception("建立 user_org SQL 預處理失敗：" . $conn->error);
    }

    $insert_user_org_stmt->bind_param("ii", $user_id, $new_org_id);

    if (!$insert_user_org_stmt->execute()) {
        throw new Exception("建立 user_org 關聯失敗：" . $insert_user_org_stmt->error);
    }

    $insert_user_org_stmt->close();

    // 3. 更新 session
    $_SESSION["org_id"] = $new_org_id;
    $_SESSION["org_name"] = $org_name;
    $_SESSION["is_admin"] = true;

    $conn->commit();

    echo json_encode([
        "success" => true,
        "message" => "組織建立成功",
        "org" => [
            "org_id" => $new_org_id,
            "org_name" => $org_name,
            "org_admid" => $user_id,
            "plan_id" => $plan_id,
            "space" => $space,
            "org_status" => $org_status
        ]
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