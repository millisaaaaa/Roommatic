<?php
header('Content-Type: application/json; charset=utf-8');
session_start();

include("db_connect.php");

if (!isset($_SESSION["user_id"])) {
    echo json_encode([
        "success" => false,
        "message" => "尚未登入"
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

$user_id = (int)$_SESSION["user_id"];

$sql = "
SELECT 
    u.user_id,
    u.username,
    u.email,
    o.org_id,
    o.org_name,
    o.org_admid,
    o.space,
    o.plan_id,
    p.plan_name,
    (
        SELECT COUNT(*) 
        FROM user_org uo2 
        WHERE uo2.org_id = o.org_id
    ) AS member_count
FROM users u
LEFT JOIN user_org uo ON u.user_id = uo.user_id
LEFT JOIN org o ON uo.org_id = o.org_id
LEFT JOIN plans p ON o.plan_id = p.plan_id
WHERE u.user_id = ?
LIMIT 1
";

$stmt = $conn->prepare($sql);

if (!$stmt) {
    echo json_encode([
        "success" => false,
        "message" => "SQL 預處理失敗：" . $conn->error
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

$stmt->bind_param("i", $user_id);
$stmt->execute();
$result = $stmt->get_result();

if ($result->num_rows === 0) {
    echo json_encode([
        "success" => false,
        "message" => "查無使用者資料"
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

$row = $result->fetch_assoc();

$is_admin = false;
if ($row["org_id"] !== null) {
    $is_admin = ((int)$row["org_admid"] === (int)$row["user_id"]);
}

echo json_encode([
    "success" => true,
    "user" => [
        "user_id" => (int)$row["user_id"],
        "username" => $row["username"],
        "email" => $row["email"],
        "org_id" => $row["org_id"] !== null ? (int)$row["org_id"] : null,
        "org_name" => $row["org_name"],
        "is_admin" => $is_admin,
        "space" => $row["space"] !== null ? (int)$row["space"] : null,
        "plan_name" => $row["plan_name"],
        "member_count" => $row["member_count"] !== null ? (int)$row["member_count"] : 0
    ]
], JSON_UNESCAPED_UNICODE);

$stmt->close();
$conn->close();
?>