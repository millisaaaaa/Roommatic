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

// 每筆 updates 約代表 10 分鐘
$minutes_per_record = 10;

// 圖表預設最大值
// peopleTrend 會用前端 maxValue = 9
// lightBars / acBars 目前前端是用百分比高度，所以這裡用 8 小時當滿格
$max_people = 9;
$max_hours = 8;

// =========================
// 1. 今日人數趨勢：對應 08,10,12,14,16,18 六個時段
// =========================
$peopleSlots = [
    ["08:00:00", "10:00:00"],
    ["10:00:00", "12:00:00"],
    ["12:00:00", "14:00:00"],
    ["14:00:00", "16:00:00"],
    ["16:00:00", "18:00:00"],
    ["18:00:00", "20:00:00"]
];

$peopleTrend = [];

foreach ($peopleSlots as $slot) {
    $sql = "
        SELECT AVG(people_num) AS avg_people
        FROM updates
        WHERE room_id = ?
          AND DATE(update_time) = CURDATE()
          AND TIME(update_time) >= ?
          AND TIME(update_time) < ?
    ";

    $stmt = $conn->prepare($sql);
    $stmt->bind_param("iss", $room_id, $slot[0], $slot[1]);
    $stmt->execute();
    $row = $stmt->get_result()->fetch_assoc();

    $value = $row && $row["avg_people"] !== null
        ? round(floatval($row["avg_people"]), 1)
        : 0;

    $peopleTrend[] = $value;
}

// =========================
// 2. 本週使用率趨勢：一到日，每天 people_num > 0 的比例
// =========================
$usageTrend = array_fill(0, 7, 0);

$sqlUsage = "
    SELECT
        WEEKDAY(update_time) AS weekday_index,
        COUNT(*) AS total_count,
        SUM(CASE WHEN people_num > 0 THEN 1 ELSE 0 END) AS used_count
    FROM updates
    WHERE room_id = ?
      AND YEARWEEK(update_time, 1) = YEARWEEK(CURDATE(), 1)
    GROUP BY WEEKDAY(update_time)
";

$stmt = $conn->prepare($sqlUsage);
$stmt->bind_param("i", $room_id);
$stmt->execute();
$result = $stmt->get_result();

while ($row = $result->fetch_assoc()) {
    $index = intval($row["weekday_index"]); // 0=週一, 6=週日
    $total = intval($row["total_count"]);
    $used = intval($row["used_count"]);

    $usageTrend[$index] = $total > 0
        ? round($used / $total * 100)
        : 0;
}

// =========================
// 3. 本週燈光開啟時長：轉成柱狀圖百分比高度
// =========================
$lightBars = array_fill(0, 7, 0);

$sqlLight = "
    SELECT
        WEEKDAY(update_time) AS weekday_index,
        SUM(CASE WHEN light_status = 'on' THEN 1 ELSE 0 END) AS on_count
    FROM updates
    WHERE room_id = ?
      AND YEARWEEK(update_time, 1) = YEARWEEK(CURDATE(), 1)
    GROUP BY WEEKDAY(update_time)
";

$stmt = $conn->prepare($sqlLight);
$stmt->bind_param("i", $room_id);
$stmt->execute();
$result = $stmt->get_result();

while ($row = $result->fetch_assoc()) {
    $index = intval($row["weekday_index"]);
    $onCount = intval($row["on_count"]);

    $hours = $onCount * $minutes_per_record / 60;
    $percent = round(min($hours / $max_hours * 100, 100));

    $lightBars[$index] = $percent;
}

// =========================
// 4. 本週冷氣開啟時長：轉成柱狀圖百分比高度
// =========================
$acBars = array_fill(0, 7, 0);

$sqlAc = "
    SELECT
        WEEKDAY(update_time) AS weekday_index,
        SUM(CASE WHEN con_status = 'on' THEN 1 ELSE 0 END) AS on_count
    FROM updates
    WHERE room_id = ?
      AND YEARWEEK(update_time, 1) = YEARWEEK(CURDATE(), 1)
    GROUP BY WEEKDAY(update_time)
";

$stmt = $conn->prepare($sqlAc);
$stmt->bind_param("i", $room_id);
$stmt->execute();
$result = $stmt->get_result();

while ($row = $result->fetch_assoc()) {
    $index = intval($row["weekday_index"]);
    $onCount = intval($row["on_count"]);

    $hours = $onCount * $minutes_per_record / 60;
    $percent = round(min($hours / $max_hours * 100, 100));

    $acBars[$index] = $percent;
}

// =========================
// 5. meta 文字
// =========================
$peopleMax = count($peopleTrend) > 0 ? max($peopleTrend) : 0;
$usageAvg = count($usageTrend) > 0 ? round(array_sum($usageTrend) / count($usageTrend)) : 0;

$lightMaxPercent = count($lightBars) > 0 ? max($lightBars) : 0;
$acAvgPercent = count($acBars) > 0 ? round(array_sum($acBars) / count($acBars)) : 0;

$lightMaxHours = round($lightMaxPercent / 100 * $max_hours, 1);
$acAvgHours = round($acAvgPercent / 100 * $max_hours, 1);

echo json_encode([
    "success" => true,
    "peopleTrend" => $peopleTrend,
    "usageTrend" => $usageTrend,
    "lightBars" => $lightBars,
    "acBars" => $acBars,
    "peopleMeta" => "最高 " . $peopleMax . " 人",
    "usageMeta" => "平均 " . $usageAvg . "%",
    "lightMeta" => "本週最高 " . $lightMaxHours . " hr",
    "acMeta" => "本週平均 " . $acAvgHours . " hr"
], JSON_UNESCAPED_UNICODE);
?>