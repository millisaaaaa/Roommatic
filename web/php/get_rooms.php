<?php
header('Content-Type: application/json; charset=utf-8');
include("db_connect.php");

$sql = "
    SELECT
        r.room_id,
        r.org_id,
        r.room_name,
        r.type,
        u.update_time,
        u.ta,
        u.Rh,
        u.people_num,
        u.PMV,
        u.PPD,
        u.light_status,
        u.con_status,
        u.con_temp
    FROM rooms r
    LEFT JOIN (
        SELECT u1.*
        FROM updates u1
        INNER JOIN (
            SELECT room_id, MAX(update_time) AS latest_update_time
            FROM updates
            GROUP BY room_id
        ) latest
        ON u1.room_id = latest.room_id
        AND u1.update_time = latest.latest_update_time
    ) u
    ON r.room_id = u.room_id
    WHERE r.room_id IN (1, 2, 3, 4)
    ORDER BY FIELD(r.room_id, 1, 2, 3, 4)
";

$result = $conn->query($sql);

if (!$result) {
    echo json_encode([
        "success" => false,
        "message" => "房間清單查詢失敗：" . $conn->error,
        "latest_update_time" => null,
        "rooms" => []
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

$rooms = [];
$latest_update_time = null;

while ($row = $result->fetch_assoc()) {
    $row["room_id"] = (int)$row["room_id"];
    $row["org_id"] = (int)$row["org_id"];

    $row["people_num"] = $row["people_num"] !== null ? (int)$row["people_num"] : 0;
    $row["ta"] = $row["ta"] !== null ? (float)$row["ta"] : null;
    $row["Rh"] = $row["Rh"] !== null ? (float)$row["Rh"] : null;
    $row["PMV"] = $row["PMV"] !== null ? (float)$row["PMV"] : null;
    $row["PPD"] = $row["PPD"] !== null ? (float)$row["PPD"] : null;
    $row["con_temp"] = $row["con_temp"] !== null ? (float)$row["con_temp"] : null;

    if (!empty($row["update_time"])) {
        if ($latest_update_time === null || strtotime($row["update_time"]) > strtotime($latest_update_time)) {
            $latest_update_time = $row["update_time"];
        }
    }

    $rooms[] = $row;
}

echo json_encode([
    "success" => true,
    "latest_update_time" => $latest_update_time,
    "rooms" => $rooms
], JSON_UNESCAPED_UNICODE);

$conn->close();
?>