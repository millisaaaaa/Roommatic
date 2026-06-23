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

// 取得前端送來的資料
$username = isset($_POST["username"]) ? trim($_POST["username"]) : "";
$email = isset($_POST["email"]) ? trim($_POST["email"]) : "";
$password = isset($_POST["password"]) ? trim($_POST["password"]) : "";
$confirm_password = isset($_POST["confirm_password"]) ? trim($_POST["confirm_password"]) : "";

// 基本驗證
if ($username === "" || $email === "" || $password === "" || $confirm_password === "") {
    echo json_encode([
        "success" => false,
        "message" => "所有欄位都必填"
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

// 檢查 email 是否已存在
$check_sql = "SELECT user_id FROM users WHERE email = ?";
$check_stmt = $conn->prepare($check_sql);

if (!$check_stmt) {
    echo json_encode([
        "success" => false,
        "message" => "SQL 預處理失敗：" . $conn->error
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

$check_stmt->bind_param("s", $email);
$check_stmt->execute();
$check_result = $check_stmt->get_result();

if ($check_result->num_rows > 0) {
    echo json_encode([
        "success" => false,
        "message" => "此 Email 已被註冊"
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

$check_stmt->close();

// 先做簡單版：直接存純文字密碼
// 之後正式版可改成 password_hash($password, PASSWORD_DEFAULT)
$insert_sql = "INSERT INTO users (username, email, user_password) VALUES (?, ?, ?)";
$insert_stmt = $conn->prepare($insert_sql);

if (!$insert_stmt) {
    echo json_encode([
        "success" => false,
        "message" => "SQL 預處理失敗：" . $conn->error
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

$insert_stmt->bind_param("sss", $username, $email, $password);

if ($insert_stmt->execute()) {
    echo json_encode([
        "success" => true,
        "message" => "註冊成功",
        "user_id" => $insert_stmt->insert_id
    ], JSON_UNESCAPED_UNICODE);
} else {
    echo json_encode([
        "success" => false,
        "message" => "註冊失敗：" . $insert_stmt->error
    ], JSON_UNESCAPED_UNICODE);
}

$insert_stmt->close();
$conn->close();
?>