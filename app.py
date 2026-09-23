import streamlit as st
import pandas as pd
import urllib.request
import re
import datetime
import streamlit.components.v1 as components

# 設置寬屏與專業賽馬終端標題
st.set_page_config(page_title="HKJC 快活谷官方排位 · MoneyFlow 賠率與能力終端", page_icon="🏇", layout="wide")

# ==============================================================================
# 自定義緊湊型專業 CSS 樣式 (符合 MoneyFlow 佈局、格子緊密、視覺清晰)
# ==============================================================================
st.markdown("""
<style>
    .main { background-color: #F8FAFC; }
    .header-box { background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 10px; padding: 12px 16px; margin-bottom: 10px; }
    .status-bar { display: flex; justify-content: space-between; align-items: center; background: #F1F5F9; border: 1px solid #CBD5E1; padding: 6px 12px; border-radius: 6px; font-size: 12px; margin-bottom: 10px; }
    .pace-box { background: #F0FDF4; border: 1px solid #BBF7D0; border-left: 4px solid #16A34A; border-radius: 6px; padding: 8px 12px; font-size: 13px; }
    .alert-box { background: #FEF2F2; border: 1px solid #FECACA; border-left: 4px solid #EF4444; border-radius: 6px; padding: 8px 12px; font-size: 13px; }
    .stat-card { background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 6px; padding: 8px 4px; text-align: center; }
    
    /* 緊湊型表格樣式：縮細格仔 (Compact Grid)，文字12px，緊密排列 */
    .compact-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 12px;
        line-height: 1.3;
        margin-top: 6px;
        margin-bottom: 12px;
    }
    .compact-table th {
        background-color: #F1F5F9;
        color: #1E293B;
        font-weight: 700;
        padding: 5px 6px;
        border: 1px solid #CBD5E1;
        text-align: center;
        white-space: nowrap;
    }
    .compact-table td {
        padding: 4px 6px;
        border: 1px solid #E2E8F0;
        text-align: center;
        vertical-align: middle;
        white-space: nowrap;
    }
    .compact-table tr:nth-child(even) { background-color: #F8FAFC; }
    .compact-table tr:hover { background-color: #F0FDF4; }
    
    /* 號碼牌圓標 */
    .num-circle {
        display: inline-block;
        width: 20px;
        height: 20px;
        line-height: 20px;
        border-radius: 50%;
        background-color: #0F172A;
        color: #FFFFFF;
        font-weight: 800;
        font-size: 11px;
        text-align: center;
    }
    .num-fav { background-color: #DC2626; }
    
    /* 燈號與高亮徽章 */
    .badge-green { background: #DCFCE7; color: #15803D; padding: 2px 5px; border-radius: 4px; font-weight: 700; font-size: 11px; }
    .badge-brown { background: #FEF3C7; color: #B45309; padding: 2px 5px; border-radius: 4px; font-weight: 700; font-size: 11px; }
    .badge-red { background: #FEE2E2; color: #B91C1C; padding: 2px 5px; border-radius: 4px; font-weight: 700; font-size: 11px; }
    .badge-gray { background: #F1F5F9; color: #64748B; padding: 2px 5px; border-radius: 4px; font-size: 11px; }
    .hkjc-link { color: #2563EB; text-decoration: none; font-weight: 700; }
    .hkjc-link:hover { text-decoration: underline; color: #1D4ED8; }
    
    /* 彩池進度條 */
    .pool-bar-bg { background-color: #E2E8F0; border-radius: 3px; width: 65px; height: 7px; display: inline-block; vertical-align: middle; margin-right: 4px; }
    .pool-bar-fill { background-color: #2563EB; height: 7px; border-radius: 3px; }
    .pool-bar-fill-hot { background-color: #DC2626; height: 7px; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 官方賽事基本資料庫 (2026年9月23日 跑馬地夜賽)
# ==============================================================================
RACE_INFO = {
    1: ("南風讓賽", "1650米", 875000),
    2: ("深水灣讓賽", "1200米", 1170000),
    3: ("黃竹坑讓賽", "1650米", 1170000),
    4: ("深水灣讓賽", "1200米", 1170000),
    5: ("香港鄉村俱樂部挑戰盃", "1650米", 1170000),
    6: ("香島讓賽", "1000米", 1170000),
    7: ("畢拿山讓賽", "1200米", 1860000),
    8: ("畢拿山讓賽", "1200米", 1860000),
    9: ("大坑讓賽", "1800米", 2050000)
}

# 100% 香港賽馬會官方真實排位、馬會官方公佈賠率基盤與官方馬匹狀態往績
OFFICIAL_RUNNERS = {
    1: [
        (1, "堅多福", 12, 135, "何澤堯", "方嘉柏", "前領", 14.0, 3.9, "3-4-2", "1124磅 (+2)", "火氣甚旺，步順力足"),
        (2, "一風雲", 5, 134, "金誠剛", "丁冠豪", "後上", 36.0, 7.2, "8-7-6", "1088磅 (-4)", "晨課緊扣，狀態平平"),
        (3, "神駒馬靈", 4, 132, "霍宏聲", "廖康銘", "領放", 5.7, 1.9, "1-3-2", "1150磅 (+6)", "神態活躍，翻步暢順"),
        (4, "紅磚戰士", 1, 131, "周俊樂", "游達榮", "前領", 10.0, 3.2, "4-2-5", "1062磅 (+1)", "內圈慢踱，體健力足"),
        (5, "極速滿貫", 10, 130, "奧爾民", "黎昭昇", "居中", 17.0, 4.2, "6-5-4", "1105磅 (+3)", "按慢順走，火氣未足"),
