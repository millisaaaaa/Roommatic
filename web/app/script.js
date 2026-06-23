const toggleButton = document.getElementById("toggleSidebar");
const sidebar = document.getElementById("sidebar");

const accountTrigger = document.getElementById("accountTrigger");
const accountPanel = document.getElementById("accountPanel");
const panelOverlay = document.getElementById("panelOverlay");

if (toggleButton && sidebar) {
  toggleButton.addEventListener("click", function () {
    sidebar.classList.toggle("collapsed");
  });
}

if (accountTrigger && accountPanel && panelOverlay) {
  accountTrigger.addEventListener("click", function (e) {
    e.stopPropagation();
    accountPanel.classList.toggle("show");
    panelOverlay.classList.toggle("show");
  });

  panelOverlay.addEventListener("click", function () {
    accountPanel.classList.remove("show");
    panelOverlay.classList.remove("show");
  });

  document.addEventListener("click", function (e) {
    const clickedInsidePanel = accountPanel.contains(e.target);
    const clickedTrigger = accountTrigger.contains(e.target);

    if (!clickedInsidePanel && !clickedTrigger) {
      accountPanel.classList.remove("show");
      panelOverlay.classList.remove("show");
    }
  });
}

const addRoomForm = document.getElementById("addRoomForm");

if (addRoomForm) {
  addRoomForm.addEventListener("submit", function (e) {
    e.preventDefault();

    const formData = new FormData(this);

    const data = {
      room_name: formData.get("room_name"),
      room_code: formData.get("room_code"),
      location: formData.get("location"),
      capacity: formData.get("capacity"),
      type: formData.get("type"),
      note: formData.get("note")
    };

    console.log("新增房間資料：", data);
    alert("房間資料已送出（目前為前端示意）");
  });
}

document.addEventListener("DOMContentLoaded", () => {
  initReportsPage();
  loadCurrentUser();
  bindLogout();
  loadTeamPage();
  loadAccountPage();
  loadReportsMeta();
  loadDashboardMetrics();
  loadDashboardReportsPreview();
});

function initReportsPage() {
  const trendModeSelect = document.getElementById("trendMode");
  const trendYearSelect = document.getElementById("trendYear");

  if (!trendModeSelect || !trendYearSelect) return;

  const monthlyView = document.querySelector(".monthly-view");
  const weeklyView = document.querySelector(".weekly-view");

  const monthBadge = monthlyView?.querySelector(".chart-mode-badge");
  const monthNote = monthlyView?.querySelector(".chart-mode-note");
  const monthYAxis = document.querySelector(".report-month-chart .report-y-axis");
  const monthBars = document.querySelectorAll(".month-bar");
  const monthBarLabels = document.querySelectorAll(".month-bar-item span");
  const summerBand = document.querySelector(".summer-band-q3");

  const weekBadge = weeklyView?.querySelector(".chart-mode-badge");
  const weekNote = weeklyView?.querySelector(".chart-mode-note");
  const weekYAxis = document.querySelector(".report-week-chart .report-y-axis");
  const weekLine = document.querySelector(".year-week-line");
  const weekDotsGroup = document.querySelector(".year-week-dots");
  const weekMonthLabels = document.querySelectorAll(".week-month-labels span");
  const seasonBand = document.querySelector(".season-summer");

  const comparisonSvg = document.querySelector(".comparison-svg");
  const comparisonYAxis = document.querySelector(".comparison-chart-large .line-chart-y-axis");
  const comparisonXLabelsWrap = document.querySelector(".comparison-chart-large .line-chart-xlabels");
  const comparisonLegendItems = document.querySelectorAll(".comparison-legend .legend-item");
  const compareChipInputs = document.querySelectorAll(".compare-chip input");
  const compareChipLabels = document.querySelectorAll(".compare-chip");
  const compareHelperText = document.querySelector(".compare-helper-text");

  const summaryHeadCurrent = document.querySelector(".performance-table-overall .table-head span:nth-child(2)");
  const summaryHeadPrevious = document.querySelector(".performance-table-overall .table-head span:nth-child(3)");
  const summaryRows = document.querySelectorAll(".performance-table-overall .table-row");

  const MONTH_LABELS = ["1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月"];
  const WEEK_MONTH_AXIS_LABELS = ["1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月"];
  const MONTH_WEEK_COUNTS = [4, 4, 5, 4, 4, 5, 4, 4, 5, 4, 4, 5];

  const REPORTS_DATA = {
    years: {
      2026: {
        monthly: [620, 640, 690, 750, 850, 1100, 1290, 1360, 1150, 790, 730, 670],
        usageRate: 68,
        peakPeriod: "14:00–16:00"
      },
      2025: {
        monthly: [550, 580, 640, 700, 780, 980, 1150, 1200, 1050, 740, 680, 600],
        usageRate: 63,
        peakPeriod: "15:00–17:00"
      },
      2024: {
        monthly: [590, 610, 650, 710, 800, 1020, 1180, 1240, 1080, 760, 700, 630],
        usageRate: 65,
        peakPeriod: "15:00–17:00"
      }
    }
  };

  const YEAR_COLORS = {
    2026: "#355fa8",
    2025: "#c6862c",
    2024: "#6f8f78"
  };

  const YEAR_SOFT_BACKGROUNDS = {
    2026: "#eaf1ff",
    2025: "#fff2df",
    2024: "#f2f6f3"
  };

  function buildWeeklyFromMonthly(monthlyValues, variant = "default") {
    const result = [];
    const weekOffsetsMap = {
      default: [-0.06, -0.03, 0.02, 0.06, 0.01],
      2026: [-0.05, -0.01, 0.04, 0.08, 0.02],
      2025: [-0.07, -0.03, 0.01, 0.05, -0.01],
      2024: [-0.04, -0.01, 0.03, 0.06, 0.0]
    };

    const offsets = weekOffsetsMap[variant] || weekOffsetsMap.default;

    monthlyValues.forEach((monthValue, monthIndex) => {
      const weekCount = MONTH_WEEK_COUNTS[monthIndex];
      for (let i = 0; i < weekCount; i++) {
        const ratio = offsets[i] ?? 0;
        const weekValue = Math.round(monthValue * (1 + ratio));
        result.push(weekValue);
      }
    });

    return result.slice(0, 52);
  }

  function getYearData(year) {
    const raw = REPORTS_DATA.years[year];
    if (!raw) return null;

    return {
      ...raw,
      weekly: buildWeeklyFromMonthly(raw.monthly, String(year))
    };
  }

  function getSelectedYears() {
    return Array.from(compareChipInputs)
      .filter((input) => input.checked)
      .map((input) => input.parentElement.textContent.trim());
  }

  function formatNumber(value) {
    return new Intl.NumberFormat("zh-Hant-TW").format(value);
  }

  function setAxisLabels(container, values) {
    if (!container) return;
    const spans = container.querySelectorAll("span");
    spans.forEach((span, index) => {
      span.textContent = values[index] ?? "";
    });
  }

  function makeYAxis(maxValue) {
    const roughTop = Math.ceil(maxValue / 4 / 100) * 4 * 100;
    return [roughTop, Math.round(roughTop * 0.75), Math.round(roughTop * 0.5), Math.round(roughTop * 0.25), 0];
  }

  function valuesToPolylinePoints(values, maxValue, width, height, paddingX = 16, paddingY = 18) {
    if (!values || !values.length) return "";

    const plotWidth = width - paddingX * 2;
    const plotHeight = height - paddingY * 2;
    const step = values.length === 1 ? 0 : plotWidth / (values.length - 1);

    return values.map((value, index) => {
      const x = paddingX + step * index;
      const y = paddingY + (1 - value / maxValue) * plotHeight;
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    }).join(" ");
  }

  function pointsForCircles(values, maxValue, width, height, paddingX = 16, paddingY = 18) {
    if (!values || !values.length) return [];

    const plotWidth = width - paddingX * 2;
    const plotHeight = height - paddingY * 2;
    const step = values.length === 1 ? 0 : plotWidth / (values.length - 1);

    return values.map((value, index) => {
      const x = paddingX + step * index;
      const y = paddingY + (1 - value / maxValue) * plotHeight;
      return { x, y };
    });
  }

  function updateTopChart() {
    const mode = trendModeSelect.value;
    const year = trendYearSelect.value;
    const yearData = getYearData(year);

    if (!yearData) return;

    if (mode === "month") {
      monthlyView?.classList.remove("is-hidden");
      weeklyView?.classList.add("is-hidden");

      if (monthBadge) monthBadge.textContent = `月模式｜${year} 年 1–12 月`;
      if (monthNote) monthNote.textContent = "每根柱代表一個月總耗能（kWh）";

      const monthlyValues = yearData.monthly;
      const maxValue = Math.max(...monthlyValues);
      const yAxis = makeYAxis(maxValue);

      setAxisLabels(monthYAxis, yAxis);

      monthBars.forEach((bar, index) => {
        const value = monthlyValues[index] ?? 0;
        const percent = maxValue === 0 ? 0 : (value / maxValue) * 100;
        bar.style.height = `${percent}%`;
      });

      monthBarLabels.forEach((label, index) => {
        label.textContent = MONTH_LABELS[index] ?? "";
      });

      if (summerBand) {
        summerBand.style.display = "flex";
      }
    } else {
      monthlyView?.classList.add("is-hidden");
      weeklyView?.classList.remove("is-hidden");

      if (weekBadge) weekBadge.textContent = `週模式｜${year} 年 W1–W52`;
      if (weekNote) weekNote.textContent = "每個點代表一週總耗能（kWh）";

      const weeklyValues = yearData.weekly;
      const maxValue = Math.max(...weeklyValues);
      const yAxis = makeYAxis(maxValue);

      setAxisLabels(weekYAxis, yAxis);

      if (weekLine) {
        const points = valuesToPolylinePoints(weeklyValues, maxValue, 1000, 280, 10, 18);
        weekLine.setAttribute("points", points);
        weekLine.style.color = YEAR_COLORS[year];
      }

      if (weekDotsGroup) {
        while (weekDotsGroup.firstChild) {
          weekDotsGroup.removeChild(weekDotsGroup.firstChild);
        }

        const dotPoints = pointsForCircles(weeklyValues, maxValue, 1000, 280, 10, 18);

        dotPoints.forEach((point, index) => {
          const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
          circle.setAttribute("cx", point.x.toFixed(1));
          circle.setAttribute("cy", point.y.toFixed(1));
          circle.setAttribute("r", "3.2");

          const isSummerWeek = index >= 21 && index <= 38;
          circle.setAttribute("fill", isSummerWeek ? "#df9b3d" : YEAR_COLORS[year]);

          weekDotsGroup.appendChild(circle);
        });
      }

      weekMonthLabels.forEach((label, index) => {
        label.textContent = WEEK_MONTH_AXIS_LABELS[index] ?? "";
      });

      if (seasonBand) {
        seasonBand.style.display = "flex";
      }
    }
  }

  function updateCompareChipStyles() {
    compareChipLabels.forEach((label) => {
      const input = label.querySelector("input");
      const year = label.textContent.trim();

      label.classList.remove("active");
      label.style.background = "";
      label.style.borderColor = "";

      const textSpan = label.querySelector("span");
      if (textSpan) {
        textSpan.style.color = YEAR_COLORS[year] || "#4f5d71";
      }

      if (input?.checked) {
        label.classList.add("active");
        label.style.background = YEAR_SOFT_BACKGROUNDS[year] || "#eef3fb";
        label.style.borderColor = YEAR_COLORS[year] || "#cfd7e3";
      }
    });
  }

  function updateComparisonLegend(selectedYears) {
    comparisonLegendItems.forEach((item) => {
      const yearText = item.textContent.trim();
      const dot = item.querySelector(".legend-dot");

      if (dot && YEAR_COLORS[yearText]) {
        dot.style.background = YEAR_COLORS[yearText];
      }

      item.style.opacity = selectedYears.includes(yearText) ? "1" : "0.38";
    });
  }

  function buildComparisonSvg(selectedYears) {
    if (!comparisonSvg) return;

    const mode = trendModeSelect.value;
    const allSeries = selectedYears.map((year) => {
      const yearData = getYearData(year);
      return {
        year,
        values: mode === "month" ? yearData.monthly : yearData.weekly
      };
    });

    const maxValue = Math.max(...allSeries.flatMap((series) => series.values));
    const svgWidth = 520;
    const svgHeight = 240;

    while (comparisonSvg.firstChild) {
      comparisonSvg.removeChild(comparisonSvg.firstChild);
    }

    allSeries.forEach((series) => {
      const polyline = document.createElementNS("http://www.w3.org/2000/svg", "polyline");
      polyline.setAttribute("fill", "none");
      polyline.setAttribute("stroke", YEAR_COLORS[series.year]);
      polyline.setAttribute("stroke-width", "4");
      polyline.setAttribute("stroke-linecap", "round");
      polyline.setAttribute("stroke-linejoin", "round");
      polyline.setAttribute(
        "points",
        valuesToPolylinePoints(series.values, maxValue, svgWidth, svgHeight, 18, 18)
      );
      comparisonSvg.appendChild(polyline);

      const points = pointsForCircles(series.values, maxValue, svgWidth, svgHeight, 18, 18);

      points.forEach((point) => {
        const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        circle.setAttribute("cx", point.x.toFixed(1));
        circle.setAttribute("cy", point.y.toFixed(1));
        circle.setAttribute("r", "3.2");
        circle.setAttribute("fill", YEAR_COLORS[series.year]);
        comparisonSvg.appendChild(circle);
      });
    });

    if (comparisonXLabelsWrap) {
      comparisonXLabelsWrap.innerHTML = "";

      if (mode === "month") {
        MONTH_LABELS.forEach((label) => {
          const span = document.createElement("span");
          span.textContent = label;
          comparisonXLabelsWrap.appendChild(span);
        });
      } else {
        WEEK_MONTH_AXIS_LABELS.forEach((label) => {
          const span = document.createElement("span");
          span.textContent = label;
          comparisonXLabelsWrap.appendChild(span);
        });
      }
    }

    setAxisLabels(comparisonYAxis, makeYAxis(maxValue));
  }

  function getComparisonSummary(primaryYear, secondaryYear) {
    const primary = getYearData(primaryYear);
    const secondary = secondaryYear ? getYearData(secondaryYear) : null;

    const primaryTotal = primary.monthly.reduce((sum, value) => sum + value, 0);
    const primarySummer = primary.monthly.slice(5, 9).reduce((sum, value) => sum + value, 0);
    const primarySummerRatio = Math.round((primarySummer / primaryTotal) * 100);
    const primaryAvgMonthly = Math.round(primaryTotal / 12);
    const primaryPeakMonthIndex = primary.monthly.indexOf(Math.max(...primary.monthly));
    const primaryPeakMonth = MONTH_LABELS[primaryPeakMonthIndex];

    if (!secondary) {
      return {
        headCurrent: primaryYear,
        headPrevious: "—",
        rows: [
          { metric: "年度總耗能", current: `${formatNumber(primaryTotal)} kWh`, previous: "—", changeText: "單年度檢視", changeClass: "change-neutral" },
          { metric: "夏季耗能占比", current: `${primarySummerRatio}%`, previous: "—", changeText: "單年度檢視", changeClass: "change-neutral" },
          { metric: "平均月耗能", current: `${formatNumber(primaryAvgMonthly)} kWh`, previous: "—", changeText: "單年度檢視", changeClass: "change-neutral" },
          { metric: "最高耗能月份", current: primaryPeakMonth, previous: "—", changeText: "單年度檢視", changeClass: "change-neutral" },
          { metric: "高峰使用時段", current: primary.peakPeriod, previous: "—", changeText: "單年度檢視", changeClass: "change-neutral" },
          { metric: "平均空間使用率", current: `${primary.usageRate}%`, previous: "—", changeText: "單年度檢視", changeClass: "change-neutral" }
        ]
      };
    }

    const secondaryTotal = secondary.monthly.reduce((sum, value) => sum + value, 0);
    const secondarySummer = secondary.monthly.slice(5, 9).reduce((sum, value) => sum + value, 0);
    const secondarySummerRatio = Math.round((secondarySummer / secondaryTotal) * 100);
    const secondaryAvgMonthly = Math.round(secondaryTotal / 12);
    const secondaryPeakMonthIndex = secondary.monthly.indexOf(Math.max(...secondary.monthly));
    const secondaryPeakMonth = MONTH_LABELS[secondaryPeakMonthIndex];

    const totalDiff = Math.round(((primaryTotal - secondaryTotal) / secondaryTotal) * 1000) / 10;
    const summerDiff = primarySummerRatio - secondarySummerRatio;
    const avgDiff = Math.round(((primaryAvgMonthly - secondaryAvgMonthly) / secondaryAvgMonthly) * 1000) / 10;
    const usageDiff = primary.usageRate - secondary.usageRate;

    function buildChangeText(value, isPercentage = true) {
      if (value === 0) return { text: "持平", className: "change-neutral" };
      if (value > 0) return { text: `上升 ${Math.abs(value)}${isPercentage ? "%" : ""}`, className: "change-up" };
      return { text: `下降 ${Math.abs(value)}${isPercentage ? "%" : ""}`, className: "change-down" };
    }

    const totalChange = buildChangeText(totalDiff, true);
    const summerChange = buildChangeText(summerDiff, true);
    const avgChange = buildChangeText(avgDiff, true);
    const usageChange = buildChangeText(usageDiff, true);

    const peakMonthChange =
      primaryPeakMonth === secondaryPeakMonth
        ? { text: "相同月份", className: "change-neutral" }
        : { text: `${secondaryPeakMonth} → ${primaryPeakMonth}`, className: "change-shift" };

    const peakPeriodChange =
      primary.peakPeriod === secondary.peakPeriod
        ? { text: "時段相同", className: "change-neutral" }
        : { text: `${secondary.peakPeriod} → ${primary.peakPeriod}`, className: "change-shift" };

    return {
      headCurrent: primaryYear,
      headPrevious: secondaryYear,
      rows: [
        { metric: "年度總耗能", current: `${formatNumber(primaryTotal)} kWh`, previous: `${formatNumber(secondaryTotal)} kWh`, changeText: totalChange.text, changeClass: totalChange.className },
        { metric: "夏季耗能占比", current: `${primarySummerRatio}%`, previous: `${secondarySummerRatio}%`, changeText: summerChange.text, changeClass: summerChange.className },
        { metric: "平均月耗能", current: `${formatNumber(primaryAvgMonthly)} kWh`, previous: `${formatNumber(secondaryAvgMonthly)} kWh`, changeText: avgChange.text, changeClass: avgChange.className },
        { metric: "最高耗能月份", current: primaryPeakMonth, previous: secondaryPeakMonth, changeText: peakMonthChange.text, changeClass: peakMonthChange.className },
        { metric: "高峰使用時段", current: primary.peakPeriod, previous: secondary.peakPeriod, changeText: peakPeriodChange.text, changeClass: peakPeriodChange.className },
        { metric: "平均空間使用率", current: `${primary.usageRate}%`, previous: `${secondary.usageRate}%`, changeText: usageChange.text, changeClass: usageChange.className }
      ]
    };
  }

  function renderSummary(summaryData) {
    if (!summaryRows.length) return;

    if (summaryHeadCurrent) summaryHeadCurrent.textContent = summaryData.headCurrent;
    if (summaryHeadPrevious) summaryHeadPrevious.textContent = summaryData.headPrevious;

    summaryRows.forEach((row, index) => {
      const rowData = summaryData.rows[index];
      if (!rowData) return;

      const spans = row.querySelectorAll("span");
      if (spans[0]) spans[0].textContent = rowData.metric;
      if (spans[1]) spans[1].textContent = rowData.current;
      if (spans[2]) spans[2].textContent = rowData.previous;
      if (spans[3]) {
        spans[3].textContent = rowData.changeText;
        spans[3].className = rowData.changeClass;
      }
    });
  }

  function updateComparisonSection() {
    const selectedYears = getSelectedYears();

    updateCompareChipStyles();
    updateComparisonLegend(selectedYears);
    buildComparisonSvg(selectedYears);

    const primaryYear = selectedYears[0];
    const secondaryYear = selectedYears[1] || null;
    const summaryData = getComparisonSummary(primaryYear, secondaryYear);
    renderSummary(summaryData);

    if (compareHelperText) {
      if (selectedYears.length >= 2) {
        compareHelperText.textContent = `目前顯示 ${selectedYears.join("、")}。建議同時比較 2 組資料，閱讀會最清楚。`;
      } else {
        compareHelperText.textContent = `目前僅顯示 ${selectedYears[0]}。若想觀察改善幅度，建議再選擇另一個年份。`;
      }
    }
  }

  function enforceAtLeastOneChecked(changedInput) {
    const checkedInputs = Array.from(compareChipInputs).filter((input) => input.checked);
    if (checkedInputs.length === 0 && changedInput) {
      changedInput.checked = true;
    }
  }

  trendModeSelect.addEventListener("change", () => {
    updateTopChart();
    updateComparisonSection();
  });

  trendYearSelect.addEventListener("change", () => {
    updateTopChart();
  });

  compareChipInputs.forEach((input) => {
    input.addEventListener("change", () => {
      enforceAtLeastOneChecked(input);
      updateComparisonSection();
    });
  });

  updateTopChart();
  updateComparisonSection();
}

async function loadCurrentUser() {
  try {
    const response = await fetch("../php/get_current_user.php", {
      method: "GET",
      credentials: "same-origin"
    });

    const rawText = await response.text();
    let result;

    try {
      result = JSON.parse(rawText);
      console.log("get_current_user result:", result);
    } catch (e) {
      console.error("get_current_user 回傳不是 JSON：", rawText);
      return;
    }

    if (!result.success) {
      console.warn(result.message);
      if (result.message === "尚未登入") {
        window.location.href = "../intro/login.html";
      }
      return;
    }

    const user = result.user;

    setText("sidebarUserName", user.username || "使用者名稱");
    setText("sidebarUserRole", user.is_admin ? "管理者" : "成員");
    setText("sidebarAvatar", getInitials(user.username));

    setText("panelUserName", user.username || "使用者名稱");
    setText("panelUserEmail", user.email || "user@example.com");
    setText("panelAvatar", getInitials(user.username));

    setText("orgName", user.org_name || "尚未加入組織");
    setText("orgPlanChip", translatePlanName(user.plan_name));
    setText("orgMemberCount", `${user.member_count ?? 0} 人`);
    setText("orgSpaceCount", `${user.space ?? 0} 間`);

    const orgManageLink = document.getElementById("orgManageLink");
    if (orgManageLink) {
      orgManageLink.textContent = user.is_admin ? "管理團隊 →" : "查看團隊 →";
    }

    const memberRow = document.getElementById("memberRow");
    if (memberRow) {
      memberRow.innerHTML = `<div class="member-avatar">${getInitials(user.username)}</div>`;
    }

    await loadOrgPanelTeamInfo();

  } catch (error) {
    console.error("loadCurrentUser error:", error);
  }
}

async function loadOrgPanelTeamInfo() {
  try {
    const response = await fetch("../php/get_team_info.php", {
      method: "GET",
      credentials: "same-origin"
    });

    const rawText = await response.text();
    let result;

    try {
      result = JSON.parse(rawText);
      console.log("org panel get_team_info result:", result);
    } catch (e) {
      console.error("org panel get_team_info 回傳不是 JSON：", rawText);
      return;
    }

    if (!result.success) {
      console.warn(result.message);
      return;
    }

    const team = result.team;

    setText("orgName", team.org_name || "組織名稱");
    setText("orgFounder", team.founder_name || "管理者");
    setText("orgPlanChip", translatePlanName(team.plan_name));
    setText("orgMemberCount", `${team.member_count ?? 0} 人`);
    setText("orgSpaceCount", `${team.space ?? 0} 間`);

    renderMemberRow(team.members);

    const orgManageLink = document.getElementById("orgManageLink");
    if (orgManageLink) {
      orgManageLink.textContent = team.is_admin ? "管理團隊 →" : "查看團隊 →";
    }

  } catch (error) {
    console.error("loadOrgPanelTeamInfo error:", error);
  }
}

async function loadDashboardMetrics() {
  const activeRoomCountEl = document.getElementById("activeRoomCount");
  if (!activeRoomCountEl) return;

  try {
    const response = await fetch("../php/get_dashboard_metrics.php", {
      method: "GET",
      credentials: "same-origin"
    });

    const rawText = await response.text();
    let result;

    try {
      result = JSON.parse(rawText);
      console.log("get_dashboard_metrics result:", result);
    } catch (e) {
      console.error("get_dashboard_metrics 回傳不是 JSON：", rawText);
      return;
    }

    if (!result.success) {
      console.warn(result.message);
      return;
    }

    const metrics = result.metrics || {};

    setText("activeRoomCount", metrics.active_rooms ?? 0);
    setText("totalRoomCount", metrics.total_rooms ?? 0);
    setText("todayEnergyValue", `${Number(metrics.today_energy_kwh ?? 0).toFixed(1)} kWh`);
    setText("monthlySavingValue", `${Number(metrics.monthly_saving_kwh ?? 0).toFixed(1)} kWh`);

  } catch (error) {
    console.error("loadDashboardMetrics error:", error);
  }
}

async function loadReportsMeta() {
  const reportsOrgTitle = document.getElementById("reportsOrgTitle");
  if (!reportsOrgTitle) return;

  try {
    const response = await fetch("../php/get_team_info.php", {
      method: "GET",
      credentials: "same-origin"
    });

    const rawText = await response.text();
    let result;

    try {
      result = JSON.parse(rawText);
      console.log("reports get_team_info result:", result);
    } catch (e) {
      console.error("reports get_team_info 回傳不是 JSON：", rawText);
      return;
    }

    if (!result.success) {
      console.warn(result.message);
      return;
    }

    const team = result.team;
    const orgName = team.org_name || "未命名組織";

    setText("reportsOrgTitle", `目前組織：${orgName}`);
    setText("reportsDataNote", "本頁圖表為模擬資料示意");

  } catch (error) {
    console.error("loadReportsMeta error:", error);
  }
}

function renderMemberRow(members) {
  const memberRow = document.getElementById("memberRow");
  if (!memberRow) return;

  if (!members || members.length === 0) {
    memberRow.innerHTML = `<div class="member-avatar">U</div>`;
    return;
  }

  const previewMembers = members.slice(0, 3);
  const remain = members.length - previewMembers.length;

  let html = previewMembers.map(member => {
    return `<div class="member-avatar">${getInitials(member.username)}</div>`;
  }).join("");

  if (remain > 0) {
    html += `<div class="member-more">+${remain}</div>`;
  }

  memberRow.innerHTML = html;
}

async function loadTeamPage() {
  const teamList = document.getElementById("teamMemberList");
  if (!teamList) return;

  try {
    const response = await fetch("../php/get_team_info.php", {
      method: "GET",
      credentials: "same-origin"
    });

    const rawText = await response.text();
    let result;

    try {
      result = JSON.parse(rawText);
      console.log("get_team_info result:", result);
    } catch (e) {
      console.error("get_team_info 回傳不是 JSON：", rawText);
      return;
    }

    if (!result.success) {
      console.warn(result.message);
      if (result.message === "尚未登入") {
        window.location.href = "../intro/login.html";
      }
      return;
    }

    const team = result.team;

    setText("teamOrgName", team.org_name || "組織名稱");
    setText("teamFounder", team.founder_name || "管理者");
    setText("teamPlanName", translatePlanName(team.plan_name));
    setText("teamSpaceCount", `${team.space ?? 0} 間`);
    setText("teamMemberCount", `${team.member_count ?? 0} 人`);

    setText("orgName", team.org_name || "組織名稱");
    setText("orgFounder", team.founder_name || "管理者");
    setText("orgPlanChip", translatePlanName(team.plan_name));
    setText("orgMemberCount", `${team.member_count ?? 0} 人`);
    setText("orgSpaceCount", `${team.space ?? 0} 間`);

    renderTeamMemberList(team.members, team.is_admin);
    renderMemberRow(team.members);

  } catch (error) {
    console.error("loadTeamPage error:", error);
  }
}

function renderTeamMemberList(members, currentUserIsAdmin) {
  const teamList = document.getElementById("teamMemberList");
  if (!teamList) return;

  if (!members || members.length === 0) {
    teamList.innerHTML = `
      <div class="member-item">
        <div class="member-main">
          <div class="member-circle">U</div>
          <div>
            <strong>目前沒有成員</strong>
            <p>尚未加入其他成員</p>
          </div>
        </div>
      </div>
    `;
    return;
  }

  teamList.innerHTML = members.map(member => {
    const initials = getInitials(member.username);
    const roleTag = member.is_admin
      ? `<span class="member-role founder-tag">管理者</span>`
      : (currentUserIsAdmin
          ? `<a href="#" class="member-action" data-user-id="${member.user_id}">移除</a>`
          : `<span class="member-role">成員</span>`);

    return `
      <div class="member-item">
        <div class="member-main">
          <div class="member-circle ${member.is_admin ? "founder" : ""}">${initials}</div>
          <div>
            <strong>${member.username}</strong>
            <p>${member.role}｜${member.email}</p>
          </div>
        </div>
        ${roleTag}
      </div>
    `;
  }).join("");
}

function loadAccountPage() {
  const accountNameEl = document.getElementById("accountProfileName");
  if (!accountNameEl) return;

  fetch("../php/get_current_user.php", {
    method: "GET",
    credentials: "same-origin"
  })
    .then(response => response.text())
    .then(rawText => {
      let result;
      try {
        result = JSON.parse(rawText);
      } catch (e) {
        console.error("account page get_current_user 回傳不是 JSON：", rawText);
        return;
      }

      if (!result.success) {
        console.warn(result.message);
        if (result.message === "尚未登入") {
          window.location.href = "../intro/login.html";
        }
        return;
      }

      const user = result.user;

      setText("accountProfileName", user.username || "使用者名稱");
      setText("accountProfileEmail", user.email || "user@example.com");
      setText("accountPlanName", translatePlanName(user.plan_name));
      setText("accountOrgName", user.org_name || "尚未加入組織");
    })
    .catch(error => {
      console.error("loadAccountPage error:", error);
    });
}

function bindLogout() {
  const logoutBtn = document.getElementById("logoutBtn");
  if (!logoutBtn) return;

  logoutBtn.addEventListener("click", handleLogout);
}

async function handleLogout() {
  try {
    const response = await fetch("../php/logout.php", {
      method: "POST",
      credentials: "same-origin"
    });

    const rawText = await response.text();
    let result;

    try {
      result = JSON.parse(rawText);
    } catch (e) {
      console.error("logout 回傳不是 JSON：", rawText);
      return;
    }

    if (result.success) {
      sessionStorage.removeItem("user");
      sessionStorage.removeItem("registerStep1Data");
      sessionStorage.removeItem("registerStep2Data");
      window.location.href = "../intro/login.html";
    } else {
      alert(result.message || "登出失敗");
    }
  } catch (error) {
    console.error("handleLogout error:", error);
    alert("登出失敗，請稍後再試");
  }
}

function setText(id, text) {
  const el = document.getElementById(id);
  if (el) el.textContent = text;
}

function getInitials(name) {
  if (!name) return "U";
  const parts = name.trim().split(/\s+/);
  if (parts.length >= 2) {
    return (parts[0][0] + parts[1][0]).toUpperCase();
  }
  return name.slice(0, 2).toUpperCase();
}

function translatePlanName(planName) {
  if (!planName) return "未設定";
  if (planName === "solo") return "基礎版";
  if (planName === "multi") return "團隊版";
  if (planName === "enterprise") return "企業版";
  return planName;
}

function loadDashboardReportsPreview() {
  const previewWrap = document.getElementById("dashboardReportPreview");
  if (!previewWrap) return;

  const monthlyData2026 = [620, 640, 690, 750, 850, 1100, 1290, 1360, 1150, 790, 730, 670];
  const monthLabels = ["1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月"];

  const previewValues = monthlyData2026.slice(5); // 6月~12月
  const previewLabels = monthLabels.slice(5);
  const maxValue = Math.max(...previewValues);

  const html = `
    <div class="dashboard-preview-chart">
      <div class="dashboard-preview-yhint">kWh</div>
      <div class="dashboard-preview-bars">
        ${previewValues.map((value, index) => {
          const percent = maxValue === 0 ? 0 : (value / maxValue) * 100;
          const isSummer = index <= 3; // 6~9月
          return `
            <div class="dashboard-preview-bar-item">
              <div class="dashboard-preview-bar-track">
                <div 
                  class="dashboard-preview-bar ${isSummer ? "summer" : ""}" 
                  style="height: ${percent}%;"
                  title="${previewLabels[index]}：${value} kWh"
                ></div>
              </div>
              <span>${previewLabels[index]}</span>
            </div>
          `;
        }).join("")}
      </div>
    </div>
  `;

  previewWrap.innerHTML = html;
}

