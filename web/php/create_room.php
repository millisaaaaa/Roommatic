<?php
header('Content-Type: application/json; charset=utf-8');
include("db_connect.php");

$org_id = $_POST["org_id"] ?? 0;
$room_name = trim($_POST["room_name"] ?? "");
$type = $_POST["type"] ?? "";

if ($room_name == "") {
    echo json_encode(["success"=>false,"message"=>"房間名稱不可空白"]);
    exit;
}

$sql = "INSERT INTO rooms (org_id, room_name, type)
        VALUES (?, ?, ?)";

$stmt = $conn->prepare($sql);
$stmt->bind_param("iss", $org_id, $room_name, $type);

if ($stmt->execute()) {
    echo json_encode(["success"=>true,"message"=>"房間新增成功"]);
} else {
    echo json_encode(["success"=>false,"message"=>"新增失敗"]);
}
?>