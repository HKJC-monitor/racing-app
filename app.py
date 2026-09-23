import streamlit as st
import pandas as pd
import math
import time

st.set_page_config(
    page_title="HKJC 9月23日快活谷夜賽 · 官方排位全能盤",
    page_icon="🏇",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .main { background-color: #F8FAFC; }
    .app-header { background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 16px 20px; margin-bottom: 16px; box-shadow: 0 1px 4px rgba(0,0,0,0.03); }
    .app-title { font-size: 22px; font-weight: 800; color: #0F172A; margin: 0; }
    .app-desc { font-size: 13px; color: #64748B; margin-top: 4px; }
    .mf-alert-box { background: #FEF2F2; border: 1px solid #FECACA; border-left: 6px solid #EF4444; border-radius: 10px; padding: 12px 16px; margin-bottom: 14px; }
    .pace-alert-box { background: #F0FDF4; border: 1px solid #BBF7D0; border-left: 6px solid #16A34A; border-radius: 10px; padding: 12px 16px; margin-bottom: 14px; }
    .stat-card { background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 10px; padding: 10px; text-align: center; box-shadow: 0 1px 2px rgba(0,0,0,0.02); }
    .stat-num { font-size: 18px; font-weight: 700; color: #0F172A; }
    .stat-lbl { font-size: 12px; color: #64748B; }
    .horse-card { background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 15px 18px; margin-bottom: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.02); }
</style>
""", unsafe_allow_html=True)

RACE_INFO = {
    1: {"name": "南風讓賽", "dist": "1650米", "cls": "第五班", "pool": 9800000.0},
    2: {"name": "深水灣讓賽", "dist": "1200米", "cls": "第四班", "pool": 11200000.0},
    3: {"name": "黃竹坑讓賽", "dist": "1650米", "cls": "第四班", "pool": 12500000.0},
    4: {"name": "深水灣讓賽", "dist": "1200米", "cls": "第四班", "pool": 11800000.0},
    5: {"name": "香港鄉村俱樂部挑戰盃", "dist": "1650米", "cls": "第四班", "pool": 13600000.0},
    6: {"name": "香島讓賽", "dist": "1000米", "cls": "第四班", "pool": 12100000.0},
    7: {"name": "畢拿山讓賽", "dist": "1200米", "cls": "第三班", "pool": 14200000.0},
    8: {"name": "畢拿山讓賽", "dist": "1200米", "cls": "第三班", "pool": 15800000.0},
    9: {"name": "大坑讓賽", "dist": "1800米", "cls": "第三班", "pool": 16500000.0},
}

def h(no, name, draw, wt, jockey, trainer, age, style, o_odds, c_odds, cond="良好"):
    drop = (o_odds - c_odds) / o_odds if o_odds > 0 else 0
    p_odds = round(c_odds * 1.15, 1) if drop > 0 else round(c_odds * 0.95, 1)
    t15_odds = round((o_odds + p_odds) / 2.0, 1)
    sp_map = {"領放": (95, 82), "前領": (90, 86), "居中": (80, 84), "後上": (72, 90)}
    sp_e, sp_l = sp_map.get(style, (80, 80))
    time_diff = -0.35 if drop > 0.25 else (-0.15 if drop > 0 else 0.10)
    return {
        "horse_no": no, "horse_name": name, "draw": draw, "weight": wt,
        "jockey": jockey, "trainer": trainer, "age": age, "pace_style": style,
        "time_diff": time_diff, "early_speed": sp_e, "late_speed": sp_l,
        "best_sectional": 22.5 if sp_l >= 88 else 23.0,
        "form_rating": 90 if drop > 0.2 else (82 if drop > 0 else 72),
        "combo_win_rate": 26.0 if "潘頓" in jockey or "何澤堯" in jockey else 15.0,
        "condition": cond, "vet_issue": "正常",
        "overnight_odds": float(o_odds), "t15_odds": float(t15_odds),
        "prev_odds": float(p_odds), "current_odds": float(c_odds)
    }

RACE_RAW_DATA = {
    1: [
        h(1, "堅多福", 3, 135, "何澤堯", "方嘉柏", 5, "前領", 3.8, 2.6, "頂峰狀態 (谷草專長)"),
        h(2, "一風雲", 7, 134, "金誠剛", "丁冠豪", 6, "後上", 9.5, 14.0, "平穩"),
        h(3, "神駒馬靈", 2, 132, "霍宏聲", "廖康銘", 4, "領放", 8.0, 4.2, "大熟大勇 (試閘好)"),
        h(4, "紅磚戰士", 1, 129, "周俊樂", "游達榮", 5, "前領", 7.0, 5.5, "良好 (1檔極利)"),
        h(5, "極速滿貫", 9, 130, "奧爾曼", "黎昭昇", 6, "居中", 18.0, 24.0, "成熟平穩"),
        h(6, "開心三多", 5, 128, "希威森", "桂福特", 5, "後上", 8.5, 6.8, "勇銳爆發期"),
        h(7, "綫路達飛", 8, 126, "楊明綸", "蘇偉賢", 6, "居中", 25.0, 32.0, "平穩"),
        h(8, "電訊驕陽", 4, 116, "袁幸堯", "徐雨石", 5, "領放", 14.0, 7.5, "受讓10磅優勢"),
        h(9, "至高心得", 6, 124, "班德禮", "韋達", 5, "居中", 15.0, 17.0, "平穩"),
        h(10, "威威父子", 11, 120, "田泰安", "巫偉傑", 5, "後上", 22.0, 30.0, "平穩"),
        h(11, "東方魅影", 10, 132, "潘頓", "大衛希斯", 4, "前領", 4.5, 3.1, "頂峰狀態 (配潘頓)")
    ],
    2: [
        h(1, "鑽飾璀璨", 2, 135, "潘頓", "容天鵬", 5, "前領", 3.5, 2.4, "勇銳 (2檔好位)"),
        h(2, "連連歡呼", 6, 132, "何澤堯", "告東尼", 5, "後上", 6.8, 8.0, "平穩"),
        h(3, "合夥奔馳", 1, 130, "布文", "呂健威", 4, "領放", 4.2, 2.8, "頂峰狀態 (1檔放頭)"),
        h(4, "耀寶", 4, 128, "霍宏聲", "方嘉柏", 4, "前領", 9.0, 11.0, "良好"),
        h(5, "大力猴王", 9, 126, "巴度", "伍鵬志", 5, "後上", 14.0, 18.0, "平穩"),
        h(6, "酷霸王", 3, 125, "田泰安", "蔡約翰", 4, "前領", 7.5, 5.2, "勇銳爆發期"),
        h(7, "佳運發", 8, 123, "希威森", "韋達", 6, "居中", 20.0, 26.0, "平穩"),
        h(8, "怡昌奇兵", 5, 121, "周俊樂", "黎昭昇", 5, "居中", 15.0, 12.0, "良好"),
        h(9, "駿皇星", 10, 120, "班德禮", "蘇偉賢", 6, "後上", 30.0, 38.0, "老馬平平"),
        h(10, "添開心", 7, 118, "鍾易禮", "文家良", 5, "領放", 12.0, 7.8, "減5磅有助搶放"),
        h(11, "宇宙動力", 11, 116, "艾兆禮", "鄭俊偉", 5, "後上", 40.0, 55.0, "平穩"),
        h(12, "精彩勇士", 12, 115, "楊明綸", "沈集成", 7, "後上", 50.0, 65.0, "退化期")
    ],
    3: [
        h(1, "超超比", 4, 135, "周俊樂", "沈集成", 5, "後上", 4.2, 3.1, "勇銳爆發期"),
        h(2, "友瑩仁", 1, 133, "潘頓", "伍鵬志", 4, "前領", 2.8, 2.0, "頂峰狀態 (1檔)"),
        h(3, "喜蓮勇略", 5, 130, "布文", "告東尼", 4, "領放", 6.5, 4.6, "良好"),
        h(4, "建測羣英", 8, 128, "何澤堯", "大衛希斯", 5, "居中", 8.0, 9.5, "良好"),
        h(5, "飛躍精英", 2, 126, "巴度", "蔡約翰", 5, "前領", 9.5, 7.2, "2檔好位"),
        h(6, "浪漫老撾", 10, 125, "田泰安", "巫偉傑", 6, "後上", 15.0, 20.0, "平穩"),
        h(7, "滿歡笑", 6, 124, "希威森", "方嘉柏", 5, "居中", 14.0, 14.0, "平穩"),
        h(8, "都靈福星", 7, 122, "班德禮", "葉楚航", 5, "後上", 22.0, 28.0, "平穩"),
        h(9, "浪漫戰神", 11, 121, "霍宏聲", "賀賢", 5, "後上", 2
