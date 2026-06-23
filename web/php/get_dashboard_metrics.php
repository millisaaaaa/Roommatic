<?php
header('Content-Type: application/json; charset=utf-8');
session_start();

if (!isset($_SESSION['user_id'])) {
    echo json_encode([
        "success" => false,
        "message" => "尚未登入"
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

require_once "db_connect.php";

$user_id = (int) $_SESSION['user_id'];

try {
    // 取得目前使用者所屬組織、組織空間數、方案最大空間數
    $sql = "
        SELECT 
            u.user_id,
            u.username,
            u.email,
            uo.org_id,
            o.org_name,
            o.plan_id,
            o.space AS org_space,
            p.max_space
        FROM users u
        LEFT JOIN user_org uo ON u.user_id = uo.user_id
        LEFT JOIN org o ON uo.org_id = o.org_id
        LEFT JOIN plans p ON o.plan_id = p.plan_id
        WHERE u.user_id = ?
        LIMIT 1
    ";

    $stmt = $conn->prepare($sql);
    if (!$stmt) {
        throw new Exception("prepare 失敗：" . $conn->error);
    }

    $stmt->bind_param("i", $user_id);
    $stmt->execute();
    $result = $stmt->get_result();
    $user = $result->fetch_assoc();
    $stmt->close();

    if (!$user) {
        echo json_encode([
            "success" => false,
            "message" => "找不到使用者資料"
        ], JSON_UNESCAPED_UNICODE);
        exit;
    }

    $org_id = isset($user['org_id']) ? (int)$user['org_id'] : 0;

    if ($org_id <= 0) {
        echo json_encode([
            "success" => false,
            "message" => "目前使用者尚未加入組織"
        ], JSON_UNESCAPED_UNICODE);
        exit;
    }

// 已建立房間數：Dashboard 分母應該顯示目前已建立的房間數，不是方案上限
$roomCountSql = "
    SELECT COUNT(*) AS room_count
    FROM rooms
    WHERE org_id = ?
";
$stmtRoom = $conn->prepare($roomCountSql);
if (!$stmtRoom) {
    throw new Exception("prepare 失敗：" . $conn->error);
}

$stmtRoom->bind_param("i", $org_id);
$stmtRoom->execute();
$roomCountResult = $stmtRoom->get_result()->fetch_assoc();
$stmtRoom->close();

$created_rooms = (int)($roomCountResult['room_count'] ?? 0);

// Dashboard 顯示：使用中空間數 / 已建立空間數
$total_rooms = $created_rooms;

    // 使用中空間數：
    // 如果目前沒有建立任何房間，直接是 0
    $active_rooms = 0;

    if ($created_rooms > 0) {
        $activeRoomSql = "
            SELECT COUNT(*) AS active_count
            FROM rooms r
            INNER JOIN (
                SELECT u1.room_id, u1.people_num
                FROM updates u1
                INNER JOIN (
                    SELECT room_id, MAX(update_time) AS latest_time
                    FROM updates
                    GROUP BY room_id
                ) u2
                ON u1.room_id = u2.room_id
                AND u1.update_time = u2.latest_time
            ) latest
            ON r.room_id = latest.room_id
            WHERE r.org_id = ?
              AND latest.people_num > 0
        ";

        $stmtActive = $conn->prepare($activeRoomSql);
        if (!$stmtActive) {
            throw new Exception("prepare 失敗：" . $conn->error);
        }

        $stmtActive->bind_param("i", $org_id);
        $stmtActive->execute();
        $activeResult = $stmtActive->get_result()->fetch_assoc();
        $stmtActive->close();

        $active_rooms = (int)($activeResult['active_count'] ?? 0);
    }

    // 本日總用電量：目前資料表沒有 kWh 欄位，先示意
    $today_energy_kwh = 17.3;

    // 本月預估節省電量：先推估
    $baseline_today_kwh = 21.5;
    $daily_saving_kwh = max(0, $baseline_today_kwh - $today_energy_kwh);
    $monthly_saving_kwh = round($daily_saving_kwh * 30, 1);

    echo json_encode([
        "success" => true,
        "metrics" => [
            "active_rooms" => $active_rooms,
            "total_rooms" => $total_rooms,
            "created_rooms" => $created_rooms,
            "today_energy_kwh" => $today_energy_kwh,
            "monthly_saving_kwh" => $monthly_saving_kwh,
            "org_id" => $org_id
        ]
    ], JSON_UNESCAPED_UNICODE);

} catch (Exception $e) {
    echo json_encode([
        "success" => false,
        "message" => "取得 Dashboard 指標失敗：" . $e->getMessage()
    ], JSON_UNESCAPED_UNICODE);
}
?>