<?php
header('Content-Type: application/json; charset=utf-8');

include("db_connect.php");

$room_id = $_GET["room_id"] ?? null;

if (!$room_id) {
    echo json_encode([
        "success" => false,
        "message" => "缺少 room_id"
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

$room_id = intval($room_id);

// 假設每筆 updates 約代表 10 分鐘
$minutes_per_record = 10;

// =========================
// 今日統計
// =========================
$sqlToday = "
    SELECT
        COUNT(*) AS total_count,
        SUM(CASE WHEN people_num > 0 THEN 1 ELSE 0 END) AS used_count,
        SUM(CASE WHEN light_status = 'on' THEN 1 ELSE 0 END) AS light_on_count,
        SUM(CASE WHEN con_status = 'on' THEN 1 ELSE 0 END) AS ac_on_count,
        AVG(people_num) AS avg_people_today
    FROM updates
    WHERE room_id = ?
      AND DATE(update_time) = CURDATE()
";

$stmt = $conn->prepare($sqlToday);
$stmt->bind_param("i", $room_id);
$stmt->execute();
$today = $stmt->get_result()->fetch_assoc();

$totalCount = intval($today["total_count"] ?? 0);
$usedCount = intval($today["used_count"] ?? 0);
$lightOnCount = intval($today["light_on_count"] ?? 0);
$acOnCount = intval($today["ac_on_count"] ?? 0);

$todayUsage = $totalCount > 0
    ? round($usedCount / $totalCount * 100)
    : 0;

$lightHours = round($lightOnCount * $minutes_per_record / 60, 1);
$acHours = round($acOnCount * $minutes_per_record / 60, 1);


// =========================
// 本週平均人數與平均使用率
// =========================
$sqlWeek = "
    SELECT
        DATE(update_time) AS day,
        AVG(people_num) AS avg_people,
        SUM(CASE WHEN people_num > 0 THEN 1 ELSE 0 END) / COUNT(*) * 100 AS usage_rate
    FROM updates
    WHERE room_id = ?
      AND update_time >= DATE_SUB(CURDATE(), INTERVAL 6 DAY)
    GROUP BY DATE(update_time)
";

$stmt = $conn->prepare($sqlWeek);
$stmt->bind_param("i", $room_id);
$stmt->execute();
$result = $stmt->get_result();

$weekRows = [];
while ($row = $result->fetch_assoc()) {
    $weekRows[] = $row;
}

$avgPeople = 0;
$avgUsage = 0;

if (count($weekRows) > 0) {
    $sumPeople = 0;
    $sumUsage = 0;

    foreach ($weekRows as $row) {
        $sumPeople += floatval($row["avg_people"]);
        $sumUsage += floatval($row["usage_rate"]);
    }

    $avgPeople = round($sumPeople / count($weekRows), 1);
    $avgUsage = round($sumUsage / count($weekRows));
}


// =========================
// 最多人流時間點
// =========================
$sqlPeakFlow = "
    SELECT update_time, people_num
    FROM updates
    WHERE room_id = ?
      AND DATE(update_time) = CURDATE()
    ORDER BY people_num DESC, update_time ASC
    LIMIT 1
";

$stmt = $conn->prepare($sqlPeakFlow);
$stmt->bind_param("i", $room_id);
$stmt->execute();
$peakFlow = $stmt->get_result()->fetch_assoc();

$peakFlowTime = $peakFlow
    ? date("H:i", strtotime($peakFlow["update_time"]))
    : "--";

echo json_encode([
    "success" => true,
    "today_usage" => $todayUsage,
    "light_hours" => $lightHours,
    "ac_hours" => $acHours,
    "avg_people" => $avgPeople,
    "avg_usage" => $avgUsage,
    "peak_flow_time" => $peakFlowTime,
    "peak_time" => "--"
], JSON_UNESCAPED_UNICODE);
?>