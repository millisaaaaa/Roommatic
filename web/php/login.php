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
$email = isset($_POST["email"]) ? trim($_POST["email"]) : "";
$password = isset($_POST["password"]) ? trim($_POST["password"]) : "";

// 基本驗證
if ($email === "" || $password === "") {
    echo json_encode([
        "success" => false,
        "message" => "Email 和密碼不可空白"
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

// 查詢使用者
$sql = "SELECT user_id, username, email, user_password FROM users WHERE email = ?";
$stmt = $conn->prepare($sql);

if (!$stmt) {
    echo json_encode([
        "success" => false,
        "message" => "SQL 預處理失敗：" . $conn->error
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

$stmt->bind_param("s", $email);
$stmt->execute();

$result = $stmt->get_result();

if ($result->num_rows === 0) {
    echo json_encode([
        "success" => false,
        "message" => "查無此帳號"
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

$user = $result->fetch_assoc();

// 目前先用純文字密碼比對
if ($password !== $user["user_password"]) {
    echo json_encode([
        "success" => false,
        "message" => "密碼錯誤"
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

// 預設先設定沒有組織
$org_id = null;
$org_name = null;
$is_admin = false;

// 查詢這個 user 有沒有加入組織
$org_sql = "
    SELECT o.org_id, o.org_name, o.org_admid
    FROM user_org uo
    INNER JOIN org o ON uo.org_id = o.org_id
    WHERE uo.user_id = ?
    LIMIT 1
";

$org_stmt = $conn->prepare($org_sql);

if (!$org_stmt) {
    echo json_encode([
        "success" => false,
        "message" => "組織查詢 SQL 預處理失敗：" . $conn->error
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

$org_stmt->bind_param("i", $user["user_id"]);
$org_stmt->execute();

$org_result = $org_stmt->get_result();

if ($org_result->num_rows > 0) {
    $org = $org_result->fetch_assoc();
    $org_id = (int)$org["org_id"];
    $org_name = $org["org_name"];
    $is_admin = ((int)$org["org_admid"] === (int)$user["user_id"]);
}

$org_stmt->close();

// 寫入 session
$_SESSION["user_id"] = (int)$user["user_id"];
$_SESSION["username"] = $user["username"];
$_SESSION["email"] = $user["email"];
$_SESSION["org_id"] = $org_id;
$_SESSION["org_name"] = $org_name;
$_SESSION["is_admin"] = $is_admin;

echo json_encode([
    "success" => true,
    "message" => "登入成功",
    "user" => [
        "user_id" => (int)$user["user_id"],
        "username" => $user["username"],
        "email" => $user["email"],
        "org_id" => $org_id,
        "org_name" => $org_name,
        "is_admin" => $is_admin
    ]
], JSON_UNESCAPED_UNICODE);

$stmt->close();
$conn->close();
?>