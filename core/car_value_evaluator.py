# car_value_evaluator.py
# -*- coding: utf-8 -*-

from typing import List, Dict, Any, Tuple
import json
import pandas as pd

# =============================
# 小工具（最简实现，不做校验）
# =============================
def ensure_list(x) -> List[str]:
    if isinstance(x, list):
        return x
    if isinstance(x, str):
        try:
            v = json.loads(x)
            return v if isinstance(v, list) else []
        except Exception:
            return []
    return []

def translate_list(items: List[str], mapping: Dict[str, str]) -> List[str]:
    return [mapping.get(i, i) for i in items]

def simple_rank(df: pd.DataFrame, row: pd.Series, field: str, *, ascending_better: bool) -> int:
    series = df[field]
    value  = row[field]
    return int((series < value).sum() + 1) if ascending_better else int((series > value).sum() + 1)

# =============================
# 评估函数（全部自包含常量；不返回 is_value/top_k）
# =============================
def eval_price_saving(df: pd.DataFrame, row: pd.Series) -> Dict[str, Any]:
    price_saving_field = "price_saving"
    actual_price_field = "actual_price"
    y_pred_field       = "y_pred"

    rank  = simple_rank(df, row, price_saving_field, ascending_better=False)
    n     = int(len(df))
    value = row[price_saving_field]

    return {
        "value": value,
        "rank": int(rank),
        "actual_price": row[actual_price_field],
        "y_pred": row[y_pred_field],
        "msg": f"价格回血 {value}，排 {rank}/{n}"
    }

def eval_mileage_saving(df: pd.DataFrame, row: pd.Series) -> Dict[str, Any]:
    mileage_saving_field = "mileage_saving"
    mileage_field        = "mileage"
    mileage_y_pred_field = "mileage_y_pred"
    price_per_km_field   = "price_per_km"

    rank  = simple_rank(df, row, mileage_saving_field, ascending_better=False)
    n     = int(len(df))
    value = row[mileage_saving_field]

    return {
        "value": value,
        "rank": int(rank),
        "mileage": row[mileage_field],
        "mileage_y_pred": row[mileage_y_pred_field],
        "price_per_km": row[price_per_km_field],
        "msg": f"里程回血 {value}，排 {rank}/{n}"
    }

def eval_expected_depreciation(df: pd.DataFrame, row: pd.Series) -> Dict[str, Any]:
    depreciation_field       = "expected_depreciation"
    y_pred_field             = "y_pred"
    next_bin_avg_price_field = "next_bin_avg_price"

    rates = (df[y_pred_field] - df[next_bin_avg_price_field]) / df[y_pred_field]
    rate  = (row[y_pred_field] - row[next_bin_avg_price_field]) / row[y_pred_field]
    rank  = int((rates < rate).sum() + 1)   # 贬值率越小越好
    n     = int(len(df))
    value = row[depreciation_field]

    return {
        "value": value,
        "depreciation_rate": round(rate, 4),
        "rank": int(rank),
        "y_pred": row[y_pred_field],
        "next_bin_avg_price": row[next_bin_avg_price_field],
        "msg": f"贬值 {value}，贬值率 {round(rate*100, 2)}%，排 {rank}/{n}",
    }

def eval_heat_rank(df: pd.DataFrame, row: pd.Series) -> Dict[str, Any]:
    heat_rank_field = "heat_rank"   # 全量热度排名（数值越小越好）
    bin_field       = "mileage_bin"

    value = int(row[heat_rank_field])
    mbin  = row[bin_field]

    return {
        "value": value,               # 全量热度排名
        "mileage_bin": mbin,          # 里程分箱
        "msg": f"全量热度排名：第 {value} 名"
    }

def eval_trustworthiness(row: pd.Series) -> Dict[str, Any]:
    certified_field     = "certified"
    accident_free_field = "accident_free"
    carfax_field        = "carfax"
    as_is_field         = "as_is"
    pos_fields          = [certified_field, accident_free_field, carfax_field]
    zh_map              = {
        certified_field: "认证车",
        accident_free_field: "无事故",
        carfax_field: "Carfax 记录",
        as_is_field: "按现状出售（AS-IS）",
    }

    as_is     = bool(row.get(as_is_field))
    positives = [f for f in pos_fields if bool(row.get(f))]

    if as_is:
        value_en, value_zh = [], []
        msg = f"可信度：风险（{zh_map[as_is_field]}）"
    elif positives:
        value_en = positives
        value_zh = [zh_map[f] for f in positives]
        msg = "可信度：" + "，".join(value_zh)
    else:
        value_en, value_zh = [], []
        msg = "可信度：—"

    return {"value_en": value_en, "value_zh": value_zh, "msg": msg}

def eval_options(row: pd.Series) -> Dict[str, Any]:
    options_field = "options"
    option_allowed = {
        "Leather Seats", "Navigation System", "Sunroof/Moonroof", "Heated Seats",
        "Heated Steering Wheel", "Remote Start", "Third Row Seating",
        "Premium Sound System", "Adaptive Cruise Control", "Ventilated Seats",
        "Heads-Up Display", "Multi Zone Climate Control"
    }
    OPT_EN2CN = {
        "Leather Seats": "真皮座椅",
        "Navigation System": "导航系统",
        "Sunroof/Moonroof": "天窗",
        "Heated Seats": "前排座椅加热",
        "Heated Steering Wheel": "方向盘加热",
        "Remote Start": "远程启动",
        "Third Row Seating": "第三排座椅",
        "Premium Sound System": "高级音响",
        "Adaptive Cruise Control": "自适应巡航",
        "Ventilated Seats": "座椅通风",
        "Heads-Up Display": "抬头显示",
        "Multi Zone Climate Control": "分区空调"
    }

    opts_en = [x for x in ensure_list(row.get(options_field)) if x in option_allowed]
    opts_zh = translate_list(opts_en, OPT_EN2CN)

    return {
        "value_en": opts_en,
        "value_zh": opts_zh,
        "msg": ("高价值配置：" + "，".join(opts_zh)) if opts_zh else "高价值配置：—"
    }

def eval_safety_features(row: pd.Series) -> Dict[str, Any]:
    safety_field = "safety_features"
    safety_allowed = {
        "Automatic Emergency Braking", "Lane Departure Warning", "Blind Spot Monitoring",
        "Rear Cross Traffic Alert", "Adaptive Cruise Control", "Parking Sensors",
        "Backup Camera", "Curtain Airbags", "Frontal Collision Warning", "ABS Brakes"
    }
    SAFE_EN2CN = {
        "Automatic Emergency Braking": "主动刹车",
        "Lane Departure Warning": "车道偏离预警",
        "Blind Spot Monitoring": "盲点监测",
        "Rear Cross Traffic Alert": "后方交叉来车预警",
        "Adaptive Cruise Control": "自适应巡航",
        "Parking Sensors": "倒车雷达/驻车雷达",
        "Backup Camera": "倒车影像",
        "Curtain Airbags": "侧气帘",
        "Frontal Collision Warning": "前方碰撞预警",
        "ABS Brakes": "防抱死制动"
    }

    saf_en = [x for x in ensure_list(row.get(safety_field)) if x in safety_allowed]
    saf_zh = translate_list(saf_en, SAFE_EN2CN)

    return {
        "value_en": saf_en,
        "value_zh": saf_zh,
        "msg": ("关键安全配置：" + "，".join(saf_zh)) if saf_zh else "关键安全配置：—"
    }

# =============================
# 综合推荐判定（分位数 + 三选二 + 可信度放宽 + 热度兜底）
# =============================
def decide_is_recommended(df: pd.DataFrame, row: pd.Series) -> Tuple[bool, str, Dict[str, bool]]:
    min_samples         = 20
    price_field         = "price_saving"          # 越大越好
    mile_field          = "mileage_saving"        # 越大越好
    y_pred_field        = "y_pred"
    next_bin_avg_field  = "next_bin_avg_price"
    heat_rank_field     = "heat_rank"             # 全量热度排名，越小越好
    certified_field     = "certified"
    accident_free_field = "accident_free"
    carfax_field        = "carfax"
    as_is_field         = "as_is"

    n = int(len(df))
    if n < min_samples:
        return False, f"暂不推荐：同款样本太少（{n} 台），价格与里程参考不够稳定，建议观望或扩大筛选范围。", {
            "ok_price": False, "ok_mile": False, "ok_depr": False, "hot_ok": False
        }
    if bool(row.get(as_is_field)):
        return False, "不推荐：按现状出售（AS-IS），存在较大不确定风险，除非明显低价且可接受自负维修。", {
            "ok_price": False, "ok_mile": False, "ok_depr": False, "hot_ok": False
        }

    depr_rates = (df[y_pred_field] - df[next_bin_avg_field]) / df[y_pred_field]
    row_depr   = (row[y_pred_field] - row[next_bin_avg_field]) / row[y_pred_field]

    has_trust = bool(row.get(certified_field) or row.get(accident_free_field) or row.get(carfax_field))
    p_price = 0.75 if not has_trust else 0.70
    p_mile  = 0.40 if not has_trust else 0.35
    p_depr  = 0.60 if not has_trust else 0.65  # 贬值率越小越好（放宽=更高分位）

    th_price = df[price_field].quantile(p_price)
    th_mile  = df[mile_field].quantile(p_mile)
    th_depr  = depr_rates.quantile(p_depr)

    ok_price = row[price_field] >= th_price
    ok_mile  = row[mile_field]  >= th_mile
    ok_depr  = row_depr         <= th_depr
    wins     = int(ok_price) + int(ok_mile) + int(ok_depr)

    heat_rank = int(row.get(heat_rank_field, 10**9))
    hot_ok    = (heat_rank <= max(1, int(0.10 * n)))  # 全量前10%

    def _desc():
        parts = []
        if ok_price:
            parts.append(f"价格有优势（≈{int(round(float(row[price_field]))):,}）")
        if ok_mile:
            parts.append(f"里程不吃亏（里程回血≈{int(round(float(row[mile_field]))):,}）")
        if ok_depr:
            parts.append(f"预计短期贬值较小（≈{row_depr*100:.1f}%）")
        if hot_ok and wins < 2:
            parts.append(f"热度高（全量第 {heat_rank} 名）")
        return "，".join(parts) if parts else "暂无明显优势"

    flags = {"ok_price": ok_price, "ok_mile": ok_mile, "ok_depr": ok_depr, "hot_ok": hot_ok}

    if wins >= 2:
        reason = (
            f"推荐：{_desc()}。建议尽快预约看车，核对 Carfax/保养记录与电池健康，"
            f"现场检查轮胎刹车与随车充电配件；车况无异常可小幅议价。"
        )
        return True, reason, flags

    if wins == 1 and hot_ok:
        reason = (
            f"谨慎推荐：{_desc()}。热度靠前，可能很快售出；若车况与预算匹配，建议尽快约看，"
            f"否则继续对比同款以获得更好的价格或里程。"
        )
        return True, reason, flags

    reason = (
        f"暂不推荐：核心优势仅 {wins}/3。建议先观望或扩大筛选范围，"
        f"优先寻找价格更有优势或里程更优的车源。"
    )
    return False, reason, flags

# =============================
# 扁平 JSON 摘要（仅一层 & 无重复键）
# =============================
def format_summary_json_flat(
        *,
        flags: Dict[str, bool],
        price_res: Dict[str, Any],
        mile_res: Dict[str, Any],
        depr_res: Dict[str, Any],
        heat_res: Dict[str, Any],
) -> Dict[str, Any]:
    def _fmt_money(x):
        try:
            return f"{int(round(float(x))):,}"
        except Exception:
            return str(x)

    def _fmt_pct(x):
        try:
            return f"{float(x)*100:.1f}%"
        except Exception:
            return str(x)

    points = []
    if flags.get("ok_price"):
        points.append(f"价格有优势（≈{_fmt_money(price_res.get('value'))}）")
    if flags.get("ok_mile"):
        points.append(f"里程不吃亏（里程回血≈{_fmt_money(mile_res.get('value'))}）")
    if flags.get("ok_depr"):
        points.append(f"预计短期贬值较小（≈{_fmt_pct(depr_res.get('depreciation_rate'))}）")
    if flags.get("hot_ok"):
        points.append(f"热度高（全量第 {heat_res.get('value')} 名）")

    if not points:
        points = ["暂无明显优势"]

    return {
        "points": points,
        "next_actions": [
            "预约看车并核对 Carfax / 保养记录 / 里程一致性",
            "现场检查电池健康、轮胎与刹车、随车充电配件/钥匙",
            "车况正常可小幅议价；不合适继续对比同款",
        ],
    }

# =============================
# 聚合输出（单脚本只输出一个 json）
# =============================
def evaluate(df: pd.DataFrame, row: pd.Series) -> Dict[str, Any]:
    listing_id_field = "listing_id"
    full_key_field   = "full_key"
    year_field       = "year"
    url_field        = "url"

    sample_size = int(len(df))
    price_res = eval_price_saving(df, row)
    mile_res  = eval_mileage_saving(df, row)
    depr_res  = eval_expected_depreciation(df, row)
    heat_res  = eval_heat_rank(df, row)
    trust_res = eval_trustworthiness(row)
    opts_res  = eval_options(row)
    saf_res   = eval_safety_features(row)

    is_recommended, reason, flags = decide_is_recommended(df, row)

    # 用 flags 构建简洁亮点（可选：保留以兼容旧前端）
    highlights = []
    if flags["ok_price"]: highlights.append("price_saving")
    if flags["ok_mile"]:  highlights.append("mileage_saving")
    if flags["ok_depr"]:  highlights.append("expected_depreciation")
    if flags["hot_ok"]:   highlights.append("heat_rank")

    # 仅一层、无重复信息的 summary
    summary_flat = format_summary_json_flat(
        flags=flags,
        price_res=price_res,
        mile_res=mile_res,
        depr_res=depr_res,
        heat_res=heat_res,
    )

    return {
        "listing_id": str(row[listing_id_field]),
        "full_key": row[full_key_field],
        "year": int(row[year_field]),
        "url": row[url_field],
        "sample_size": sample_size,
        "highlights": highlights,
        "is_recommended": is_recommended,
        "decision_reason": reason,
        "summary": summary_flat,   # ← 仅一层 & 去重
        "evaluations": {
            "price_saving": price_res,
            "mileage_saving": mile_res,
            "expected_depreciation": depr_res,
            "heat_rank": heat_res,
            "trustworthiness": trust_res,
            "options": opts_res,
            "safety_features": saf_res,
        },
    }
