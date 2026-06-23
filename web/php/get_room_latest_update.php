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

$sql = "
    SELECT update_time, ta, Rh, people_num, light_status, con_status, con_temp
    FROM updates
    WHERE room_id = ?
    ORDER BY update_time DESC
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

$stmt->bind_param("i", $room_id);
$stmt->execute();
$result = $stmt->get_result();

if ($result->num_rows === 0) {
    echo json_encode([
        "success" => false,
        "message" => "此房間目前沒有感測資料"
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

$data = $result->fetch_assoc();

echo json_encode([
    "success" => true,
    "data" => [
        "update_time" => $data["update_time"],
        "ta" => $data["ta"],
        "Rh" => $data["Rh"],
        "people_num" => $data["people_num"],
        "light_status" => $data["light_status"],
        "con_status" => $data["con_status"],
        "con_temp" => $data["con_temp"]
    ]
], JSON_UNESCAPED_UNICODE);

$stmt->close();
$conn->close();
?>