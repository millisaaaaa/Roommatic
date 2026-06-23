<?php
header('Content-Type: application/json; charset=utf-8');
include("db_connect.php");

$room_id = $_POST["room_id"] ?? 0;
$room_name = trim($_POST["room_name"] ?? "");
$type = $_POST["type"] ?? "";

if ($room_name == "") {
    echo json_encode(["success"=>false,"message"=>"名稱不可空白"]);
    exit;
}

$sql = "UPDATE rooms SET room_name=?, type=? WHERE room_id=?";
$stmt = $conn->prepare($sql);
$stmt->bind_param("ssi", $room_name, $type, $room_id);

if ($stmt->execute()) {
    echo json_encode(["success"=>true,"message"=>"更新成功"]);
} else {
    echo json_encode(["success"=>false,"message"=>"更新失敗"]);
}
?>