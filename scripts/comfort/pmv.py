# /home/pi/Roommatic/scripts/comfort/pmv.py

from __future__ import annotations
import math


def calculate_pmv_ppd(
    ta: float,
    rh: float,
    tr: float | None = None,
    vel: float = 0.1,
    met: float = 1.1,
    clo: float = 0.7,
    wme: float = 0.0,
) -> dict:
    """
    ASHRAE 55-2023 Appendix B 版本 PMV / PPD 計算。

    - ta: air temperature (°C)
    - rh: relative humidity (%)
    - tr: mean radiant temperature (°C)，若未給則預設等於 ta
    - vel: average air speed Va (m/s)
    - met: metabolic rate (met)
    - clo: clothing insulation Icl (clo)
    - wme: external work (met)

    回傳:
    {
        "pmv": float,
        "ppd": float
    }
    """

    if tr is None:
        tr = ta

    # 1. ASHRAE 55-2023 Appendix B:
    # met >= 1.2 時，clo 需修正
    if met >= 1.2:
        clo = clo * (0.6 + 0.4 / met)

    # 2. ASHRAE 55-2023 Appendix B:
    # Vel = average air speed Va + activity-generated air speed Vag
    vag = 0.0 if met <= 1.0 else 0.3 * (met - 1.0)
    vel = vel + vag

    # water vapor partial pressure, Pa
    pa = rh * 10 * math.exp(16.6536 - 4030.183 / (ta + 235))

    icl = 0.155 * clo
    m = met * 58.15
    w = wme * 58.15
    mw = m - w

    if icl <= 0.078:
        fcl = 1 + 1.29 * icl
    else:
        fcl = 1.05 + 0.645 * icl

    hcf = 12.1 * math.sqrt(vel)
    taa = ta + 273
    tra = tr + 273
    tcla = taa + (35.5 - ta) / (3.5 * icl + 0.1)

    p1 = icl * fcl
    p2 = p1 * 3.96
    p3 = p1 * 100
    p4 = p1 * taa
    p5 = 308.7 - 0.028 * mw + p2 * (tra / 100) ** 4

    # 3. 改成文件 Appendix B 的迭代寫法
    xn = tcla / 100
    xf = tcla / 50
    eps = 0.00015
    n = 0

    while abs(xn - xf) > eps:
        xf = (xf + xn) / 2
        hcn = 2.38 * abs(100.0 * xf - taa) ** 0.25
        hc = max(hcf, hcn)
        xn = (p5 + p4 * hc - p2 * xf**4) / (100 + p3 * hc)

        n += 1
        if n > 150:
            raise RuntimeError("PMV calculation max iterations exceeded")

    tcl = 100 * xn - 273

    hl1 = 3.05 * 0.001 * (5733 - 6.99 * mw - pa)
    hl2 = 0.42 * (mw - 58.15) if mw > 58.15 else 0
    hl3 = 1.7 * 0.00001 * m * (5867 - pa)
    hl4 = 0.0014 * m * (34 - ta)
    hl5 = 3.96 * fcl * (xn**4 - (tra / 100) ** 4)
    hl6 = fcl * hc * (tcl - ta)

    ts = 0.303 * math.exp(-0.036 * m) + 0.028
    pmv = ts * (mw - hl1 - hl2 - hl3 - hl4 - hl5 - hl6)

    # 4. PPD 公式
    ppd = 100.0 - 95.0 * math.exp(
        -0.03353 * pmv**4.0 - 0.2179 * pmv**2.0
    )

    return {
        "pmv": round(pmv, 3),
        "ppd": round(ppd, 2),
    }


def calculate_pmv(
    ta: float,
    rh: float,
    tr: float | None = None,
    vel: float = 0.1,
    met: float = 1.1,
    clo: float = 0.7,
    wme: float = 0.0,
) -> float:
    """
    保留舊版介面，避免 main.py 或其他程式壞掉。
    """
    result = calculate_pmv_ppd(
        ta=ta,
        rh=rh,
        tr=tr,
        vel=vel,
        met=met,
        clo=clo,
        wme=wme,
    )
    return result["pmv"]


def calculate_ppd(pmv: float) -> float:
    """
    單獨用 PMV 計算 PPD。
    """
    ppd = 100.0 - 95.0 * math.exp(
        -0.03353 * pmv**4.0 - 0.2179 * pmv**2.0
    )
    return round(ppd, 2)


def classify_pmv(pmv: float) -> str:
    """
    依 Roommatic 節能控制需求做簡化分類。
    注意：ASHRAE 舒適區通常是 -0.5 < PMV < +0.5；
    這裡 PMV > 0.3 提早判定 slightly_hot，是你們自己的控制策略。
    """
    if pmv < -0.5:
        return "cold"
    elif -0.5 <= pmv <= 0.3:
        return "comfortable"
    elif 0.3 < pmv <= 0.8:
        return "slightly_hot"
    else:
        return "hot"