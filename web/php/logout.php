<?php
header('Content-Type: application/json; charset=utf-8');
session_start();

// 清空 session 變數
$_SESSION = [];

// 刪除 session cookie
if (ini_get("session.use_cookies")) {
    $params = session_get_cookie_params();
    setcookie(
        session_name(),
        '',
        time() - 42000,
        $params["path"],
        $params["domain"],
        $params["secure"],
        $params["httponly"]
    );
}

// 銷毀 session
session_destroy();

echo json_encode([
    "success" => true,
    "message" => "登出成功"
], JSON_UNESCAPED_UNICODE);
?>