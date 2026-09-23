import streamlit as st
import pandas as pd
import json
import urllib.request
import re
import datetime
import random

st.set_page_config(
    page_title="HKJC 快活谷 · MoneyFlow 專業即時賠率終端",
    page_icon="🏇",
    layout="wide"
)

# 自定義 MoneyFlow 緊湊 CSS 樣式 (馬會對碰盤色塊、圓圈賽績、無跳動)
st.markdown("""
<style>
.compact-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 12px;
}
.compact-table th {
    background: #F1F5F9;
    color: #1E293B;
    padding: 5px 4px;
    border: 1px solid #CBD5E1;
    text-align: center;
}
.compact-table td {
    padding: 4px 5px;
    border: 1px solid #E2E8F0;
    text-align: center;
}
.scratched-row {
    background: #F8FAFC !important;
    color: #94A3B8 !important;
}
.scratched-tag {
    background: #DC2626;
    color: #FFF;
    font-weight: bold;
    font-size: 10px;
    padding: 1px 4px;
    border-radius: 3px;
    margin-left: 3px;
}
.matrix-tbl {
    width: 100%;
    border-collapse: collapse;
    font-size: 11px;
}
.matrix-tbl th {
    background: #0F172A;
    color: #FFF;
    padding: 4px 2px;
    border: 1px solid #334155;
    text-align: center;
}
.matrix-tbl td {
    border: 1px solid #CBD5E1;
    padding: 3px 2px;
    text-align: center;
    font-family: Arial, sans-serif;
}
/* 馬會標準落飛高光色塊 */
.cell-brown { background: #854D0E !important; color: #FFFFFF !important; font-weight: bold; }
.cell-green { background: #16A34A !important; color: #FFFFFF !important; font-weight: bold; }
.cell-hot { background: #FEF08A !important; color: #854D0E !important; font-weight: bold; }
.cell-norm { background: #FFFFFF; color: #1E293B; }
.cell-diag { background: #E2E8F0; color: #94A3B8; }
.cell-scratched { background: #F1F5F9; color: #CBD5E1; font-size: 10px; }

.circle-no {
    display: inline-block;
    width: 18px;
    height: 18px;
    line-height: 18px;
    border-radius: 50%;
    background: #0F172A;
    color: #FFF;
    font-size: 11px;
    font-weight: bold;
}
.fav-no { background: #DC2626; }

/* 同程賽績圓圈徽章 (由左至右：冠、亞、季、負) */
.dist-circles {
    display: inline-flex;
    gap: 3px;
    align-items: center;
    justify-content: center;
}
.c-circle {
    display: inline-block;
    width: 19px;
    height: 19px;
    line-height: 19px;
    border-radius: 50%;
    text-align: center;
    font-weight: bold;
    font-size: 11px;
}
.c-gold { background: #EAB308; color: #FFFFFF; } /* 冠 */
.c-silver { background: #94A3B8; color: #FFFFFF; } /* 亞 */
.c-bronze { background: #D97706; color: #FFFFFF; } /* 季 */
.c-gray { background: #E2E8F0; color: #475569; } /* 負 */

.badge {
    padding: 2px 5px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: bold;
}
.b-green { background: #DCFCE7; color: #15803D; }
.b-brown { background: #FEF3C7; color: #B45309; }
.b-red { background: #FEE2E2; color: #B91C1C; }
.b-blue { background: #EFF6FF; color: #1D4ED8; }
.b-gray { background: #F1F5F9; color: #64748B; }

.ai-card {
    background: #F8FAFC;
    border: 1px solid #CBD5E1;
    border-radius: 6px;
    padding: 8px 12px;
    margin-bottom: 6px;
}
.stat-card {
    background: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-radius: 6px;
    padding: 6px 4px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# 賽事日程
RACES = {
    1: ("南風讓賽", "1650米", 875000),
    2: ("深水灣讓賽", "1200米", 1170000),
    3: ("黃竹坑讓賽", "1650米", 1170000),
    4: ("深水灣讓賽", "1200米", 1170000),
    5: ("鄉村俱樂部挑戰盃", "1650米", 1170000),
    6: ("香島讓賽", "1000米", 1170000),
    7: ("畢拿山讓賽", "1200米", 1860000),
    8: ("畢拿山讓賽", "1200米", 1860000),
    9: ("大坑讓賽", "1800米", 2050000)
}

# 格式: [馬號, 馬名, 檔位, 負磅, 騎師, 練馬師, 跑法, 臨場WIN, 臨場PLA, 隔夜WIN, 6次近績, 排位體重, [冠, 亞, 季, 負], 東方名家評語, 臨場跌幅%, 是否退出]
RACE_DATABASE = {
    4:, "上仗後上凌厲，換人配周俊樂減磅，有力一拼", 27.3, False],
        [2, "智勝一籌", 10, 135, "蔡明紹", "蘇偉賢", "均速", 24.0, 5.8, 25.0, "8/12/12/7/11", "1066(+28)", [0, 0, 0, 2], "排十檔形勢略吃虧，狀態平平，暫宜觀望", -4.0, False],
       , "【已退出賽事 (Scratched)】", 0.0, True],
       , "晨操步爽力足，同程能跟擅鬥，三甲之材", 21.4, False],
        [5, "莊家班", 3, 130, "黃智弘", "沈集成", "跟前", 28.0, 6.5, 30.0, "11/4/7/11/10/10", "1056(+3)", [0, 0, 0, 3], "內檔好位慳位，但作戰狀態未足，難言把握", 6.7, False],
        , "擂台大熱火氣極盛，潘頓親操質素保證，熱門重心", 37.5, False],
       , "【已退出賽事 (Scratched)】", 0.0, True],
       , "步伐整齊走勢平穩，具備一定牽引力，可作冷配", 4.5, False],
       , "試閘反應良好，四檔出閘守好位，暗湧甚大", 23.1, False],
        [10, "平天雄", 9, 123, "潘明輝", "丁冠豪", "大後上", 33.0, 8.0, 35.0, "12/10/10/14/14/11", "1260(+56)", [0, 0, 0, 4], "步頭略重尚未減夠分，現階段仍處調教期", 5.7, False],
       , "一檔黃金貼欄，老馬減磅有利，邊線突擊", 8.3, False],
        [12, "三強", 11, 120, "楊明綸", "鄭俊偉", "後上", 28.0, 7.0, 30.0, "10/8/9/8/3/3", "1131(-23)", [0, 0, 2, 3], "冷門配搭，後勁尚有一段，需遇快步速方有機會", 6.7, False]
    ],
    7:, "東廄爭分主力，前速銳利守好位，坐二望一", 30.7, False],
       , "身肌結實出腳強勁，三檔起步好跑，不可忽視", 20.0, False],
       , "潘頓親自壓陣，後上爆發力強，三甲穩健分子", 21.7, False],
       , "起步前速飛快，唯十二檔消耗體力較大，需看切欄", 11.1, False],
        [5, "傲聖", 5, 129, "潘明輝", "賀賢", "大後上", 34.0, 8.5, 36.0, "7/8/6/5/7/8", "1085(-3)", [0, 0, 0, 3], "步頭略慢後勁未開，未復舊觀，暫宜退避", 5.6, False],
        [6, "電源之駒", 7, 127, "梁家俊", "廖康銘", "跟前", 11.0, 3.0, 13.5, "4/5/2/3/4/2", "1130(+3)", [1, 2, 0, 2], "快慢由人具暗實力，中段跟前發力，冷門黑馬", 18.5, False],
        [7, "加州本事", 11, 124, "蔡明紹", "巫偉傑", "均速", 13.0, 3.5, 15.0, "3/2/6/4/3/2", "1095(+2)", [0, 2, 0, 2], "近期火氣未減，前程緊湊，有望拼入位置", 13.3, False],
       , "蔡廄重心，直路衝刺全場最凌厲，單T穩膽首選", 34.3, False],
       , "一檔起步順暢，體態輕巧步爽，邊線分子", 11.1, False],
       , "放頭馬搶前，預計步速受壓，後勁較為平淡", 12.5, False],
       , "減十磅起步有力，步幅開揚，冷門偷襲", 16.7, False],
       , "大單熱錢猛撲，臨場狀態達巔峰，爭勝核心", 37.2, False]
    ],
    8: [
        [1, "人和家興", 2, 135, "霍宏聲", "大衛希斯", "放頭", 9.8, 2.6, 13.0, "3/1/4/2/3/1", "1172(+4)", [3, 2, 0, 2], "谷草老手前速極強，兩檔搶放有優勢，爭勝黑馬", 24.6, False],
       , "神采飛揚步大力雄，唯負重磅需看走位發揮", 12.5, False],
       , "方廄谷草能手，晨跳力足，四檔好位有牽引力", 16.7, False],
       , "一檔黃金貼欄，均速放前韌力十足，二串三穩健前列", 30.4, False],
        [5, "飛馬座", 11, 127, "周俊樂", "徐雨石", "後上", 24.0, 6.0, 26.0, "7/6/8/5/7/6", "1082(-2)", [0, 0, 0, 3], "外檔起步被動，走勢略重，暫宜觀望", 7.7, False],
       , "東方名家：慢踱均速態況平穩，具備跟前韌力，位置冷腳", 10.0, False],
        [7, "勇霸龍", 6, 123, "艾道拿", "黎昭昇", "均速", 23.0, 5.8, 25.0, "6/7/5/4/6/5", "1128(+2)", [0, 0, 0, 3], "出腳有力中規中矩，但速度稍遜一籌，考驗騎功", 8.0
