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
        "message" => "尚未登入，無法加入組織"
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

// 檢查是否已加入組織
$check_member_sql = "SELECT org_id FROM user_org WHERE user_id = ?";
$check_member_stmt = $conn->prepare($check_member_sql);

if (!$check_member_stmt) {
    echo json_encode([
        "success" => false,
        "message" => "SQL 預處理失敗：" . $conn->error
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

$check_member_stmt->bind_param("i", $user_id);
$check_member_stmt->execute();
$check_member_result = $check_member_stmt->get_result();

if ($check_member_result->num_rows > 0) {
    echo json_encode([
        "success" => false,
        "message" => "你已經加入組織，無法重複加入"
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

$check_member_stmt->close();

// 查詢組織是否存在，且密碼是否正確
$find_org_sql = "SELECT org_id, org_name, org_admid FROM org WHERE org_name = ? AND org_password = ?";
$find_org_stmt = $conn->prepare($find_org_sql);

if (!$find_org_stmt) {
    echo json_encode([
        "success" => false,
        "message" => "SQL 預處理失敗：" . $conn->error
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

$find_org_stmt->bind_param("ss", $org_name, $org_password);
$find_org_stmt->execute();
$find_org_result = $find_org_stmt->get_result();

if ($find_org_result->num_rows === 0) {
    echo json_encode([
        "success" => false,
        "message" => "組織名稱或組織密碼錯誤"
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

$org = $find_org_result->fetch_assoc();
$org_id = (int)$org["org_id"];
$is_admin = ((int)$org["org_admid"] === $user_id);

$find_org_stmt->close();

// 新增到 user_org
$insert_sql = "INSERT INTO user_org (user_id, org_id) VALUES (?, ?)";
$insert_stmt = $conn->prepare($insert_sql);

if (!$insert_stmt) {
    echo json_encode([
        "success" => false,
        "message" => "SQL 預處理失敗：" . $conn->error
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

$insert_stmt->bind_param("ii", $user_id, $org_id);

if ($insert_stmt->execute()) {
    // 更新 session
    $_SESSION["org_id"] = $org_id;
    $_SESSION["org_name"] = $org["org_name"];
    $_SESSION["is_admin"] = $is_admin;

    echo json_encode([
        "success" => true,
        "message" => "加入組織成功",
        "org" => [
            "org_id" => $org_id,
            "org_name" => $org["org_name"],
            "org_admid" => (int)$org["org_admid"],
            "is_admin" => $is_admin
        ]
    ], JSON_UNESCAPED_UNICODE);
} else {
    echo json_encode([
        "success" => false,
        "message" => "加入組織失敗：" . $insert_stmt->error
    ], JSON_UNESCAPED_UNICODE);
}

$insert_stmt->close();
$conn->close();
?>