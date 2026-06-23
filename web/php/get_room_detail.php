<?php
header('Content-Type: application/json; charset=utf-8');
include("db_connect.php");

$room_id = isset($_GET["room_id"]) ? (int)$_GET["room_id"] : 0;

if ($room_id <= 0) {
    echo json_encode([
        "success" => false,
        "message" => "缺少 room_id"
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

// 先查房間基本資料
$sql_room = "SELECT room_id, room_name, type FROM rooms WHERE room_id = ?";
$stmt_room = $conn->prepare($sql_room);

if (!$stmt_room) {
    echo json_encode([
        "success" => false,
        "message" => "房間查詢預處理失敗：" . $conn->error
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

$stmt_room->bind_param("i", $room_id);
$stmt_room->execute();
$result_room = $stmt_room->get_result();

if ($result_room->num_rows === 0) {
    echo json_encode([
        "success" => false,
        "message" => "查無此房間"
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

$room = $result_room->fetch_assoc();

// 再查最新一筆 updates
$sql_update = "
    SELECT ta, Rh, people_num, PMV, PPD, light_status, con_status, con_temp, update_time
    FROM updates
    WHERE room_id = ?
    ORDER BY update_time DESC
    LIMIT 1
";
$stmt_update = $conn->prepare($sql_update);

if (!$stmt_update) {
    echo json_encode([
        "success" => false,
        "message" => "更新資料查詢預處理失敗：" . $conn->error
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

$stmt_update->bind_param("i", $room_id);
$stmt_update->execute();
$result_update = $stmt_update->get_result();

$latest_update = $result_update->fetch_assoc();

// 如果沒有 updates，也要能正常顯示
$data = [
    "success" => true,
    "room_id" => (int)$room["room_id"],
    "room_name" => $room["room_name"],
    "type" => $room["type"],
    "ta" => $latest_update["ta"] ?? null,
    "Rh" => $latest_update["Rh"] ?? null,
    "people_num" => $latest_update["people_num"] ?? null,
    "PMV" => $latest_update["PMV"] ?? null,
    "PPD" => $latest_update["PPD"] ?? null,
    "light_status" => $latest_update["light_status"] ?? null,
    "con_status" => $latest_update["con_status"] ?? null,
    "con_temp" => $latest_update["con_temp"] ?? null,
    "update_time" => $latest_update["update_time"] ?? null
];

echo json_encode($data, JSON_UNESCAPED_UNICODE);

$stmt_room->close();
$stmt_update->close();
$conn->close();
?>