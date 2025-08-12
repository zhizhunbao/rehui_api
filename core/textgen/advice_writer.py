# core/textgen/advice_writer.py
# -*- coding: utf-8 -*-
"""
生成“有人味”的推荐文案（summary + decision_reason），零依赖。
"""

from typing import Dict, Any, List, Optional
import random
import hashlib
import os

__all__ = ["compose_advice"]

# ===================== 可调参数（阈值与风格，小写） =====================
price_small = 500        # <500 小幅
price_med = 2000         # 500~2000 明显；>=2000 显著

depr_low = 3.0           # 贬值率 <3%：压力不大
depr_mid = 7.0           # 3~7%：正常；>=7%：偏高

heat_top_strong = 10     # 热度前10名：很高
heat_top_good = 50       # 热度前50名：靠前

# 环境变量控制是否加 emoji（rehui_use_emoji=1 开启）
use_emoji = os.getenv("rehui_use_emoji", "0") not in ("0", "false", "False", "")
emoji_ok = "✅ " if use_emoji else ""
emoji_warn = "⚠️ " if use_emoji else ""

# ===================== 同义短语（小写） =====================
price_pos_tpl = [
    "价格{scale}省了≈{amt}",
    "比同款便宜≈{amt}",
    "比预估价低≈{amt}",
]
price_neg_tpl = [
    "价格{scale}偏高≈{amt}",
    "比行情高≈{amt}",
    "需要多付≈{amt}",
]
mile_pos_tpl = [
    "里程有优势，等效省≈{amt}",
    "里程偏低，等效省≈{amt}",
    "里程方面更划算≈{amt}",
]
mile_neg_tpl = [
    "里程拖后腿，等效多花≈{amt}",
    "里程偏高，等效多花≈{amt}",
    "里程劣势，多付≈{amt}",
]
depr_low_tpl = [
    "预计短期贬值≈{pct}（压力不大）",
    "预计短期贬值≈{pct}，压力不大",
]
depr_mid_tpl = [
    "预计短期贬值≈{pct}（正常范围）",
    "预计短期贬值≈{pct}，大体正常",
]
depr_high_tpl = [
    "预计短期贬值≈{pct}（偏高）",
    "预计短期贬值≈{pct}，偏高",
]
heat_tpl_strong = [
    "热度很高（全量第 {rank} 名）",
    "热门车源（全量第 {rank} 名）",
]
heat_tpl_good = [
    "热度靠前（全量第 {rank} 名）",
    "关注度不错（第 {rank} 名）",
]
heat_tpl_ok = [
    "热度不错（全量靠前）",
]

# 下一步建议（按动力类型）
next_actions_map = {
    "ev": [
        "预约看车并核对 Carfax/保养/里程一致性",
        "查看高压电池健康/保修条款，实测充电速率与续航",
        "检查轮胎/刹车/底盘；确认随车充电枪与两把钥匙",
        "车况正常可小幅议价",
    ],
    "hybrid": [
        "预约看车并核对 Carfax/保养与召回记录",
        "路试发动机-电机切换并读码排查电池/逆变器",
        "检查是否渗漏；查看轮胎/刹车磨损",
        "车况正常可小幅议价，或继续对比同款",
    ],
    "gas": [
        "预约看车并核对 Carfax/保养记录/里程一致性",
        "冷车启动与路试：注意怠速、换挡是否顺畅、是否有异响",
        "检查机舱/底盘是否渗漏；查看轮胎与刹车磨损",
        "确认两把钥匙与随车工具；车况正常可小幅议价",
    ],
    "diesel": [
        "冷车启动与路试：观察烟色/抖动/动力",
        "检查是否渗漏；了解 DPF/维护记录",
        "检查刹车与轮胎；确认两把钥匙与随车工具",
        "车况正常可小幅议价",
    ],
    "unknown": [
        "预约看车并核对记录；完成路试与常规检查",
        "车况正常可小幅议价",
    ],
}

decision_tail_map = {
    "ev": "建议尽快预约看车，核对记录与电池健康，实测充电；检查轮胎/刹车；车况正常可小幅议价。",
    "hybrid": "建议尽快预约看车，核对记录与召回；路试发动机-电机切换并读码；检查轮胎/刹车；车况正常可小幅议价。",
    "gas": "建议尽快预约看车，核对记录；冷车启动与路试；检查机舱/底盘渗漏及轮胎/刹车；车况正常可小幅议价。",
    "diesel": "建议冷车启动与路试；了解 DPF 维护；检查渗漏与轮胎/刹车；车况正常可小幅议价。",
    "unknown": "建议预约看车并完成常规检查，车况正常可小幅议价。",
}

decision_tpl_map = {
    "recommended": "{emoji}推荐：{head}。{tail}",
    "conditional": "{emoji}谨慎推荐：{head}。{tail}",
    "not_recommended": "{emoji}暂不推荐：核心优势不足。建议先观望或扩大筛选范围。",
}

# ===================== 工具函数（小写） =====================
def _seed_from_ids(*parts: str) -> int:
    raw = "|".join([p or "" for p in parts])
    h = hashlib.sha1(raw.encode("utf-8")).hexdigest()
    return int(h[:12], 16)

def _pick(rng: random.Random, candidates: List[str]) -> str:
    return candidates[rng.randrange(0, len(candidates))] if candidates else ""

def _scale_word(amount: float) -> str:
    a = abs(amount)
    if a < price_small:
        return "小幅"
    if a < price_med:
        return "明显"
    return "显著"

def _fmt_money_abs(x: float) -> str:
    return f"{int(round(abs(x))):,}"

def _norm_pct(x: float) -> float:
    return x * 100.0 if x <= 1.0 else x

def _to_float(x: Any) -> Optional[float]:
    try:
        return float(x)
    except Exception:
        return None

def _detect_powertrain(full_key: str) -> str:
    k = (full_key or "").lower()
    if "electric" in k or " ev" in k or "ev_" in k:
        return "ev"
    if "phev" in k or "plug-in" in k:
        return "hybrid"  # 并入 hybrid
    if "hybrid" in k or "_hev" in k:
        return "hybrid"
    if "diesel" in k or "_tdi" in k:
        return "diesel"
    if "gasoline" in k or " petrol" in k or " gas" in k:
        return "gas"
    return "unknown"

# ===================== 核心生成 =====================
def _points_humanized(rng: random.Random, flags: Dict[str, bool], m: Dict[str, Any]) -> List[str]:
    pts: List[str] = []

    # 价格：明确省/多花 + 强弱
    ps = _to_float(m.get("price_saving"))
    if ps is not None:
        if ps > 1e-9:
            tpl = _pick(rng, price_pos_tpl)
            pts.append(f"{emoji_ok}{tpl.format(scale=_scale_word(ps), amt=_fmt_money_abs(ps))}")
        elif ps < -1e-9:
            tpl = _pick(rng, price_neg_tpl)
            pts.append(f"{emoji_warn}{tpl.format(scale=_scale_word(ps), amt=_fmt_money_abs(ps))}")
        elif flags.get("ok_price"):
            pts.append(f"{emoji_ok}价格基本合理")

    # 里程：明确因里程省/多花
    ms = _to_float(m.get("mileage_saving"))
    if ms is not None:
        if ms > 1e-9:
            tpl = _pick(rng, mile_pos_tpl)
            pts.append(f"{emoji_ok}{tpl.format(amt=_fmt_money_abs(ms))}")
        elif ms < -1e-9:
            tpl = _pick(rng, mile_neg_tpl)
            pts.append(f"{emoji_warn}{tpl.format(amt=_fmt_money_abs(ms))}")
        elif flags.get("ok_mile"):
            pts.append(f"{emoji_ok}里程基本合理")

    # 贬值率：分段口径
    dr = _to_float(m.get("depr_rate"))
    if dr is not None:
        pct = _norm_pct(dr)
        if pct < depr_low:
            tpl = _pick(rng, depr_low_tpl)
        elif pct < depr_mid:
            tpl = _pick(rng, depr_mid_tpl)
        else:
            tpl = _pick(rng, depr_high_tpl)
        pts.append(tpl.format(pct=f"{pct:.1f}%"))

    # 热度：兜底或靠前才说
    hr = m.get("heat_rank")
    if hr not in (None, "", "—"):
        try:
            rnk = int(hr)
        except Exception:
            rnk = None
        if flags.get("hot_ok") or (rnk is not None and rnk <= heat_top_good):
            if rnk is not None and rnk <= heat_top_strong:
                tpl = _pick(rng, heat_tpl_strong)
            elif rnk is not None and rnk <= heat_top_good:
                tpl = _pick(rng, heat_tpl_good)
            else:
                tpl = _pick(rng, heat_tpl_ok)
            pts.append(tpl.format(rank=rnk if rnk is not None else "—"))

    return pts or ["暂无明显优势"]

def compose_advice(
        *,
        listing_id: Optional[str],
        full_key: str,
        flags: Dict[str, bool],
        metrics: Dict[str, Any],
        is_recommended: bool,
        max_points: int = 3,
) -> Dict[str, Any]:
    """
    入参：
      - listing_id: 用于固定随机种子（同一车源文案一致）
      - full_key:   判断动力类型
      - flags:      {ok_price, ok_mile, ok_depr, hot_ok}
      - metrics:    {price_saving, mileage_saving, depr_rate|depreciation_rate, heat_rank}
      - is_recommended: True/False
    出参：
      {"summary":{"points":[...], "next_actions":[...]}, "decision_reason":"..."}
    """
    depr = metrics.get("depr_rate", metrics.get("depreciation_rate"))
    m = {
        "price_saving": metrics.get("price_saving"),
        "mileage_saving": metrics.get("mileage_saving"),
        "depr_rate": depr,
        "heat_rank": metrics.get("heat_rank"),
    }

    seed = _seed_from_ids(str(listing_id or ""), full_key, str(m.get("heat_rank") or ""))
    rng = random.Random(seed)

    points = _points_humanized(rng, flags, m)
    head = "，".join(points[:max_points])

    pt = _detect_powertrain(full_key)
    next_actions = next_actions_map.get(pt) or next_actions_map["unknown"]

    wins = int(bool(flags.get("ok_price"))) + int(bool(flags.get("ok_mile"))) + int(bool(flags.get("ok_depr")))
    tail = decision_tail_map.get(pt) or decision_tail_map["unknown"]

    if is_recommended:
        key = "conditional" if (wins == 1 and flags.get("hot_ok")) else "recommended"
    else:
        key = "not_recommended"

    emoji = emoji_ok if is_recommended else emoji_warn
    decision_reason = decision_tpl_map[key].format(emoji=emoji, head=head, tail=tail)

    return {
        "summary": {"points": points, "next_actions": next_actions},
        "decision_reason": decision_reason
    }
