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

// 先找目前使用者所在組織
$orgSql = "
SELECT 
    o.org_id,
    o.org_name,
    o.org_admid,
    o.space,
    p.plan_name,
    admin_user.username AS admin_name
FROM user_org uo
INNER JOIN org o ON uo.org_id = o.org_id
LEFT JOIN plans p ON o.plan_id = p.plan_id
LEFT JOIN users admin_user ON o.org_admid = admin_user.user_id
WHERE uo.user_id = ?
LIMIT 1
";

$orgStmt = $conn->prepare($orgSql);

if (!$orgStmt) {
    echo json_encode([
        "success" => false,
        "message" => "SQL 預處理失敗：" . $conn->error
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

$orgStmt->bind_param("i", $user_id);
$orgStmt->execute();
$orgResult = $orgStmt->get_result();

if ($orgResult->num_rows === 0) {
    echo json_encode([
        "success" => false,
        "message" => "尚未加入組織"
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

$org = $orgResult->fetch_assoc();
$org_id = (int)$org["org_id"];
$is_admin = ((int)$org["org_admid"] === $user_id);

$orgStmt->close();

// 查組織成員
$memberSql = "
SELECT 
    u.user_id,
    u.username,
    u.email
FROM user_org uo
INNER JOIN users u ON uo.user_id = u.user_id
WHERE uo.org_id = ?
ORDER BY 
    CASE WHEN u.user_id = ? THEN 0 ELSE 1 END,
    u.user_id ASC
";

$memberStmt = $conn->prepare($memberSql);

if (!$memberStmt) {
    echo json_encode([
        "success" => false,
        "message" => "SQL 預處理失敗：" . $conn->error
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

$memberStmt->bind_param("ii", $org_id, $org["org_admid"]);
$memberStmt->execute();
$memberResult = $memberStmt->get_result();

$members = [];

while ($row = $memberResult->fetch_assoc()) {
    $member_is_admin = ((int)$row["user_id"] === (int)$org["org_admid"]);

    $members[] = [
        "user_id" => (int)$row["user_id"],
        "username" => $row["username"],
        "email" => $row["email"],
        "role" => $member_is_admin ? "管理者" : "成員",
        "is_admin" => $member_is_admin
    ];
}

$memberStmt->close();

echo json_encode([
    "success" => true,
    "team" => [
        "org_id" => $org_id,
        "org_name" => $org["org_name"],
        "founder_name" => $org["admin_name"] ?: "管理者",
        "plan_name" => $org["plan_name"],
        "space" => (int)$org["space"],
        "member_count" => count($members),
        "is_admin" => $is_admin,
        "members" => $members
    ]
], JSON_UNESCAPED_UNICODE);

$conn->close();
?>