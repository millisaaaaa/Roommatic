<?php
header('Content-Type: application/json; charset=utf-8');
include("db_connect.php");

$room_id = $_GET["room_id"] ?? 0;

// 先檢查是否有資料
$check = $conn->prepare("SELECT COUNT(*) as total FROM updates WHERE room_id=?");
$check->bind_param("i", $room_id);
$check->execute();
$result = $check->get_result()->fetch_assoc();

if ($result["total"] > 0) {
    echo json_encode([
        "success"=>false,
        "message"=>"此房間已有感測資料，無法刪除"
    ]);
    exit;
}

$sql = "DELETE FROM rooms WHERE room_id=?";
$stmt = $conn->prepare($sql);
$stmt->bind_param("i", $room_id);

if ($stmt->execute()) {
    echo json_encode(["success"=>true,"message"=>"刪除成功"]);
} else {
    echo json_encode(["success"=>false,"message"=>"刪除失敗"]);
}
?>