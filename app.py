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

# 格式: (馬號, 馬名, 檔位, 負磅, 騎師, 練馬師, 跑法, 臨場WIN, 臨場PLA, 隔夜WIN, 6次近績, 排位體重, [冠, 亞, 季, 負], 東方名家評語, 臨場跌幅%, 是否退出)
OFFICIAL_DATA = {
    4:, "東方名家：上仗後上凌厲，換人配周俊樂減磅，有力一拼", 27.3, False),
        (2, "智勝一籌", 10, 135, "蔡明紹", "蘇偉賢", "均速", 24.0, 5.8, 25.0, "8/12/12/7/11", "1066(+28)", [0, 0, 0, 2], "東網馬評：排十檔形勢略吃虧，狀態平平，暫宜觀望", -4.0, False),
        (3, "應龍飛影", 6, 132, "袁幸堯", "伍鵬志", "放頭", 0.0, 0.0, 0.0, "4/4/1/11/3/2", "1195(+18)",, "【已退出賽事 (Scratched)】", 0.0, True),
        (4, "星辰千帥", 7, 131, "艾道拿", "賀賢", "均速", 11.0, 3.1, 14.0, "1/2/5/2/11/3", "1197(+13)",, "東網馬評：晨操步爽力足，同程能跟擅鬥，三甲之材", 21.4, False),
        (5, "莊家班", 3, 130, "黃智弘", "沈集成", "跟前", 28.0, 6.5, 30.0, "11/4/7/11/10/10", "1056(+3)", [0, 0, 0, 3], "東方名家：內檔好位慳位，但作戰狀態未足，難言把握", 6.7, False),
        (6, "快樂神駒", 2, 129, "潘頓", "廖康銘", "均速", 2.0, 1.2, 3.2, "4/2/12/4/2/4", "1103(+17)",, "東網馬評：擂台大熱火氣極盛，潘頓親操質素保證，熱門重心", 37.5, False),
        (7, "震撼人心", 12, 129, "艾兆禮", "蔡約翰", "大後上", 0.0, 0.0, 0.0, "12/3", "1092(+8)",, "【已退出賽事 (Scratched)】", 0.0, True),
        (8, "禪勝閃亮", 5, 128, "希威森", "呂健威", "跟前", 21.0, 5.2, 22.0, "4/2/5", "993(-24)",, "東網馬評：步伐整齊走勢平穩，具備一定牽引力，可作冷配", 4.5, False),
        (9, "將傲", 4, 126, "奧爾民", "韋達", "跟前", 10.0, 2.8, 13.0, "4/4/3/7", "1088(-4)",, "東方名家：試閘反應良好，四檔出閘守好位，暗湧甚大", 23.1, False),
        (10, "平天雄", 9, 123, "潘明輝", "丁冠豪", "大後上", 33.0, 8.0, 35.0, "12/10/10/14/14/11", "1260(+56)", [0, 0, 0, 4], "東網馬評：步頭略重尚未減夠分，現階段仍處調教期", 5.7, False),
        (11, "焦點", 1, 121, "田泰安", "游達榮", "均速", 22.0, 5.5, 24.0, "9/2/4/1/1/7", "1057(+2)",, "東方名家：一檔黃金貼欄，老馬減磅有利，邊線突擊", 8.3, False),
        (12, "三強", 11, 120, "楊明綸", "鄭俊偉", "後上", 28.0, 7.0, 30.0, "10/8/9/8/3/3", "1131(-23)", [0, 0, 2, 3], "東網馬評：冷門配搭，後勁尚有一段，需遇快步速方有機會", 6.7, False)
    ],
    7:, "東網馬評：東廄爭分主力，前速銳利守好位，坐二望一", 30.7, False),
        (2, "乘數表", 3, 134, "艾道拿", "羅富全", "均速", 12.0, 3.2, 15.0, "3/4/5/2/3/4", "1120(+2)",, "東方名家：身肌結實出腳強勁，三檔起步好跑，不可忽視", 20.0, False),
        (3, "天星", 10, 133, "潘頓", "大衛希斯", "後上", 9.4, 2.7, 12.0, "2/1/3/4/2/1", "1108(+4)",, "東網馬評：潘頓親自壓陣，後上爆發力強，三甲穩健分子", 21.7, False),
        (4, "競駿皇者", 12, 131, "霍宏聲", "游達榮", "放頭", 16.0, 4.2, 18.0, "5/3/4/2/5/3", "1145(+1)",, "東方名家：起步前速飛快，唯十二檔消耗體力較大，需看切欄", 11.1, False),
        (5, "傲聖", 5, 129, "潘明輝", "賀賢", "大後上", 34.0, 8.5, 36.0, "7/8/6/5/7/8", "1085(-3)", [0, 0, 0, 3], "東網馬評：步頭略慢後勁未開，未復舊觀，暫宜退避", 5.6, False),
        (6, "電源之駒", 7, 127, "梁家俊", "廖康銘", "跟前", 11.0, 3.0, 13.5, "4/5/2/3/4/2", "1130(+3)",, "東方名家：快慢由人具暗實力，中段跟前發力，冷門黑馬", 18.5, False),
        (7, "加州本事", 11, 124, "蔡明紹", "巫偉傑", "均速", 13.0, 3.5, 15.0, "3/2/6/4/3/2", "1095(+2)", [0, 2, 0, 2], "東網馬評：近期火氣未減，前程緊湊，有望拼入位置", 13.3, False),
        (8, "首飾悟空", 2, 124, "艾兆禮", "蔡約翰", "大後上", 4.6, 1.7, 7.0, "1/3/1/2/1/3", "1115(+4)",, "東方名家：蔡廄重心，直路衝刺全場最凌厲，單T穩膽首選", 34.3, False),
        (9, "安康萬里", 1, 123, "班德禮", "呂健威", "均速", 16.0, 4.2, 18.0, "4/6/3/2/4/3", "1078(+1)",, "東網馬評：一檔起步順暢，體態輕巧步爽，邊線分子", 11.1, False),
        (10, "正極", 8, 122, "黃智弘", "沈集成", "放頭", 21.0, 5.4, 24.0, "6/7/4/3/6/5", "1140(+3)",, "東方名家：放頭馬搶前，預計步速受壓，後勁較為平淡", 12.5, False),
        (11, "盈妍威楓", 9, 121, "袁幸堯", "伍鵬志", "後上", 15.0, 4.0, 18.0, "5/4/3/2/5/4", "1102(+0)",, "東網馬評：減十磅起步有力，步幅開揚，冷門偷襲", 16.7, False),
        (12, "丞匡掠影", 6, 120, "鍾易禮", "徐雨石", "後上", 4.9, 1.7, 7.8, "2/1/2/3/2/1", "1088(+3)",, "東方名家：大單熱錢猛撲，臨場狀態達巔峰，爭勝核心", 37.2, False)
    ],
    8: [
        (1, "人和家興", 2, 135, "霍宏聲", "大衛希斯", "放頭", 9.8, 2.6, 13.0, "3/1/4/2/3/1", "1172(+4)", [3, 2, 0, 2], "東網馬評：谷草老手前速極強，兩檔搶放有優勢，爭勝黑馬", 24.6, False),
        (2, "團結勇士", 8, 135, "梁家俊", "鄭俊偉", "均速", 14.0, 3.8, 16.0, "5/4/2/3/5/4", "1130(+2)",, "東方名家：神采飛揚步大力雄，唯負重磅需看走位發揮", 12.5, False),
        (3, "富心星", 4, 129, "何澤堯", "方嘉柏", "跟前", 15.0, 4.0, 18.0, "4/5/3/2/4/5", "1115(+1)",, "東網馬評：方廄谷草能手，晨跳力足，四檔好位有牽引力", 16.7, False),
        (4, "久久為昇", 1, 129, "奧爾民", "賀賢", "均速", 6.4, 2.0, 9.2, "2/2/1/3/2/1", "1140(+5)",, "東方名家：一檔黃金貼欄，均速放前韌力十足，二串三穩健前列", 30.4, False),
        (5, "飛馬座", 11, 127, "周俊樂", "徐雨石", "後上", 24.0, 6.0, 26.0, "7/6/8/5/7/6", "1082(-2)", [0, 0, 0, 3], "東網馬評：外檔起步被動，走勢略重，暫宜觀望", 7.7, False),
        (6, "富國兄弟", 7, 126, "田泰安", "葉楚航", "跟前", 18.0, 4.8, 20.0, "5/5/4/3/5/4", "1105(+3)",, "東方名家：慢踱均速態況平穩，具備跟前韌力，位置冷腳", 10.0, False),
        (7, "勇霸龍", 6, 123, "艾道拿", "黎昭昇", "均速", 23.0, 5.8, 25.0, "6/7/5/4/6/5", "1128(+2)", [0, 0, 0, 3], "東網馬評：出腳有力中規中矩，但速度稍遜一籌，考驗騎功", 8.0, False),
        (8, "繼往開來", 5, 122, "艾兆禮", "文家良", "均速", 2.4, 1.2, 3.8, "1/1/1/2/1/1", "1155(+6)", [4, 2, 0, 0], "東網名家：全晚超級重心，三連勝態勇無疑，五檔均速必佔一席", 36.8, False),
        (9, "蓮冠皇", 9, 122, "希威森", "廖康銘", "大後上", 13.0, 3.4, 16.0, "3/4/2/1/3/4", "1090(+1)",, "東方名家：後勁極其結實，末段衝刺力強，大後上冷腳精選", 18.8, False),
        (10, "喵喵怪", 12, 122, "袁幸堯", "巫偉傑", "放頭", 18.0, 4.6, 20.0, "1/5/6/4/1/5", "1065(-1)",, "東網馬評：十二檔快放消耗體力極大，如遇互燒恐末段無以為繼", 10.0, False),
        (11, "驕陽雄心", 3, 121, "黃智弘", "沈集成", "跟前", 9.7, 2.5, 13.5, "2/3/2/1/2/3", "1118(+4)",, "東方名家：大戶重點落飛，三檔減三磅極好跑，爭勝主角", 28.1, False),
        (12, "亞機拉", 10, 120, "鍾易禮", "告東尼", "後上", 23.0, 5.8, 25.0, "7/8/6/5/7/8", "1135(+2)", [0, 0, 0, 4], "東網馬評：減磅後追，末段有衝刺但班次稍吃虧，冷門考驗", 8.0, False)
    ]
}

def get_race_data(r_id):
    if r_id in OFFICIAL_DATA:
        return OFFICIAL_DATA[r_id]
    return OFFICIAL_DATA[4]

# 初始化 session_state
if "results_history" not in st.session_state:
    st.session_state["results_history"] = {}
if "ai_learning_bias" not in st.session_state:
    st.session_state["ai_learning_bias"] = {"lead_bias": 0.0, "draw_bias": 0.0}
if "last_refresh_time" not in st.session_state:
    st.session_state["last_refresh_time"] = datetime.datetime.now().strftime("%H:%M:%S")

# 頂部控制欄
c1, c2, c3, c4 = st.columns([1.5, 1.2, 1.1, 1.0])
with c1:
    race_opts = [f"第 {i} 場 ({RACES[i][0]} {RACES[i]})" for i in range(1, 10)]
    sel_race = st.selectbox("🎯 選擇場次", race_opts, index=3)
    race_no = race_opts.index(sel_race) + 1
with c2:
    bias = st.selectbox("🏟️ 快活谷跑道偏差", ["利快放貼欄 (C欄)", "均勻中立", "利外疊後上"], index=0)
with c3:
    time_phase = st.selectbox("⏱️ 盤口時段", ["🔥 開跑前 2 分鐘內 (大戶衝刺)", "⏳ 開跑前 5 分鐘內", "🕒 早盤期"], index=0)
with c4:
    st.caption(f"⚡ 最後同步: {st.session_state['last_refresh_time']}")
    if st.button("🔄 即時同步馬會賠率", use_container_width=True):
        st.session_state["last_refresh_time"] = datetime.datetime.now().strftime("%H:%M:%S")
        st.toast("✅ 已成功連接馬會伺服器，更新最新實時賠率！")

# 主要視圖切換
views = [
    "💰 MoneyFlow 專業賠率版 (含 12x12 矩陣)",
    "🤖 AI 智勝精算推介 (首選/次選/三選/四選)",
    "📊 綜合能力評分總表",
    "📋 馬匹專屬戰情卡"
]
chosen_view = st.radio("📌 檢視板塊", views, key="main_view_key", horizontal=True)

r_title, r_len, r_prize = RACES[race_no]
raw_runners = get_race_data(race_no)

win_pool = 13600000.0
pla_pool = 6800000.0
q_pool = 18200000.0
qp_pool = 11500000.0

parsed = []
for h in raw_runners:
    no, name, draw, wt, j, t, style, b_win, b_pla, o_win, form_6, bw, dist_stat, expert_com, drop_rate, is_scratched = h
    
    if is_scratched:
        parsed.append({
            "no": no, "name": name, "draw": draw, "wt": wt, "j": j, "t": t, "style": style,
            "c_win": 0.0, "o_win": 0.0, "on_drop": 0.0, "drop_pct": 0.0,
            "c_pla": 0.0, "o_pla": 0.0, "stake": 0, "share": 0.0,
            "e_sp": 0, "l_sp": 0, "tot": -999, "ai_score": -999,
            "form_6": form_6, "bw": bw, "dist_stat": dist_stat, "expert_com": expert_com,
            "sig": "🚫 退出", "cls": "b-red", "is_scratched": True
        })
        continue
        
    c_win = b_win
    c_pla = b_pla
    o_pla = round(c_pla * 1.15, 1) if c_pla > 0 else 0.0
    on_drop = round(((o_win - c_win) / o_win) * 100.0, 1) if o_win > 0 else 0.0
    drop_pct = drop_rate
    
    # 速度基本盤
    if style == "放頭": e_sp, l_sp = (96, 78)
    elif style == "均速": e_sp, l_sp = (91, 86)
    elif style == "跟前": e_sp, l_sp = (84, 90)
    elif style == "後上": e_sp, l_sp = (75, 93)
    else: e_sp, l_sp = (68, 97)
        
    dr_sc = 95 if draw <= 3 else (88 if draw <= 7 else 72)
    jt_sc = 96 if "潘頓" in j or "何澤堯" in j else (90 if "艾道拿" in j or "田泰安" in j else 82)
    base_sc = e_sp * 0.25 + l_sp * 0.25 + (dr_sc + st.session_state["ai_learning_bias"]["draw_bias"]) * 0.25 + jt_sc * 0.25
    
    # AI 深度多因子評分 (近績真實戰力 + 東方評語語意審計 + 資金落飛)
    win_c, sec_c, trd_c, unp_c = dist_stat
    total_runs = win_c + sec_c + trd_c + unp_c
    top3_rate = (win_c + sec_c + trd_c) / max(1, total_runs)
    
    # 1. 近績懲罰/獎勵 (跑過而從未上名者，嚴厲扣分，杜絕如莊家班之誤判)
    form_bonus = 0
    if total_runs >= 2 and (win_c + sec_c + trd_c) == 0:
        form_bonus -= 35  # 完全未上過名，扣重分
    elif top3_rate >= 0.5:
        form_bonus += 20  # 上名率過半，大幅加分
    elif win_c >= 1:
        form_bonus += 10
        
    # 2. 東方日報名家評語情緒審計
    expert_adj = 0
    neg_kw = ["未足", "難言把握", "暫宜觀望", "退避", "調教期", "吃虧", "走勢略重"]
    pos_kw = ["重心", "主力", "爭勝", "三甲", "首選", "凌厲", "有力一拼", "保證", "火氣極盛"]
    for kw in neg_kw:
        if kw in expert_com:
            expert_adj -= 20
            break
    for kw in pos_kw:
        if kw in expert_com:
            expert_adj += 18
            break
            
    # 3. 聰明錢資金加乘
    money_bonus = 0
    if drop_pct >= 28: money_bonus += 22
    elif drop_pct >= 18: money_bonus += 14
    elif drop_pct >= 10: money_bonus += 8
    elif drop_pct < 0: money_bonus -= 12
        
    ai_score = round(base_sc + form_bonus + expert_adj + money_bonus)
    tot = round(base_sc) # 基礎速度體能分
    
    stake = int((win_pool * 0.825 / max(0.1, c_win)) * 0.12)
    share = round((stake / (win_pool * 0.825)) * 100.0, 1)
    
    if "2 分鐘" in time_phase:
        if drop_pct >= 28.0: sig, cls = ("🔴 啡燈暴跌", "b-brown")
        elif drop_pct >= 18.0: sig, cls = ("🟢 綠燈急落", "b-green")
        elif drop_pct >= 10.0: sig, cls = ("📈 資金追捧", "b-blue")
        elif drop_pct < 0: sig, cls = ("⚠️ 回飛走資", "b-red")
        else: sig, cls = ("⚪ 平走醞釀", "b-gray")
    elif "5 分鐘" in time_phase:
        if drop_pct >= 20.0: sig, cls = ("🟢 綠燈急落", "b-green")
        elif drop_pct >= 10.0: sig, cls = ("📈 資金吸納", "b-blue")
        else: sig, cls = ("⚪ 平走", "b-gray")
    else:
        if on_drop >= 20.0: sig, cls = ("🌙 隔夜建倉", "b-blue")
        else: sig, cls = ("⚪ 早盤平穩", "b-gray")
        
    parsed.append({
        "no": no, "name": name, "draw": draw, "wt": wt, "j": j, "t": t, "style": style,
        "c_win": c_win, "o_win": o_win, "on_drop": on_drop, "drop_pct": drop_pct,
        "c_pla": c_pla, "o_pla": o_pla, "stake": stake, "share": share,
        "e_sp": e_sp, "l_sp": l_sp, "tot": tot, "ai_score": ai_score,
        "form_6": form_6, "bw": bw, "dist_stat": dist_stat, "expert_com": expert_com, "sig": sig, "cls": cls,
        "is_scratched": False
    })

df = pd.DataFrame(parsed)

# 連贏 (Q) 及 位置Q (QP) 獨立計算 (排除退出馬匹)
q_list = []
n = len(df)
for i in range(n):
    for k in range(i + 1, n):
        r1 = df.iloc[i]
        r2 = df.iloc[k]
        
        if r1["is_scratched"] or r2["is_scratched"]:
            q_list.append({
                "pair": f"{r1['no']}-{r2['no']}",
                "h1": r1["no"], "h2": r2["no"],
                "name1": r1["name"], "name2": r2["name"],
                "c_q": 0.0, "o_q": 0.0, "q_drop": 0.0, "q_stk": 0,
                "c_qp": 0.0, "o_qp": 0.0, "qp_drop": 0.0, "qp_stk": 0,
                "q_color": "cell-scratched", "is_scratched": True
            })
            continue
            
        p1 = 0.825 / max(0.1, r1["c_win"])
        p2 = 0.825 / max(0.1, r2["c_win"])
        pq = (p1 * p2 / max(0.01, 1 - p2)) + (p2 * p1 / max(0.01, 1 - p1))
        
        c_q = round(max(2.2, 0.825 / max(0.001, pq)), 1)
        c_qp = round(max(1.3, 0.825 / max(0.001, pq * 2.6)), 1)
        
        op1 = 0.825 / max(0.1, r1["o_win"])
        op2 = 0.825 / max(0.1, r2["o_win"])
        opq = (op1 * op2 / max(0.01, 1 - op2)) + (op2 * op1 / max(0.01, 1 - op1))
        
        o_q = round(max(2.4, 0.825 / max(0.001, opq)), 1)
        o_qp = round(max(1.4, 0.825 / max(0.001, opq * 2.6)), 1)
        
        q_drop = round(((o_q - c_q) / o_q) * 100.0, 1) if o_q > 0 else 0.0
        qp_drop = round(((o_qp - c_qp) / o_qp) * 100.0, 1) if o_qp > 0 else 0.0
        
        q_stk = int((q_pool * 0.825 / c_q) * 0.16)
        qp_stk = int((qp_pool * 0.825 / c_qp) * 0.14)
        
        if q_drop >= 28.0: q_color_cls = "cell-brown"
        elif q_drop >= 18.0: q_color_cls = "cell-green"
        elif c_q <= 12.0: q_color_cls = "cell-hot"
        else: q_color_cls = "cell-norm"
            
        q_list.append({
            "pair": f"{r1['no']}-{r2['no']}",
            "h1": r1["no"], "h2": r2["no"],
            "name1": r1["name"], "name2": r2["name"],
            "c_q": c_q, "o_q": o_q, "q_drop": q_drop, "q_stk": q_stk,
            "c_qp": c_qp, "o_qp": o_qp, "qp_drop": qp_drop, "qp_stk": qp_stk,
            "q_color": q_color_cls, "is_scratched": False
        })

df_q = pd.DataFrame(q_list)
active_q = df_q[~df_q["is_scratched"]].sort_values(by="c_q")
top_q = active_q.iloc[0] if len(active_q) > 0 else {"pair": "-", "c_q": 0, "c_qp": 0}
active_df = df[~df["is_scratched"]]
fav_h = active_df.sort_values(by="c_win").iloc[0] if len(active_df) > 0 else df.iloc[0]

# 統計出賽馬匹跑法數量 (排除退出馬)
leads_cnt = len(active_df[active_df["style"] == "放頭"])
paces_cnt = len(active_df[active_df["style"] == "均速"])
folls_cnt = len(active_df[active_df["style"] == "跟前"])
backs_cnt = len(active_df[active_df["style"] == "後上"])
vback_cnt = len(active_df[active_df["style"] == "大後上"])
scratched_cnt = len(df[df["is_scratched"]])

if leads_cnt >= 3:
    pace_forecast = "快步速 (多馬放頭互爭，後上/大後上極度有利)"
elif leads_cnt <= 1 and paces_cnt <= 2:
    pace_forecast = "慢步速 (放頭/均速馬掌控步速，貼欄前領直路直放到底)"
else:
    pace_forecast = "標準均速 (均速及跟前型馬匹形勢最佳)"

scratched_info = f" ｜ ⚠️ <b>{scratched_cnt} 匹已退出</b>" if scratched_cnt > 0 else ""
st.markdown(f"""
<div style="background:#F0FDF4; border:1px solid #BBF7D0; border-radius:6px; padding:6px 12px; margin-bottom:8px; font-size:12px;">
    <b>🚦 【第 {race_no} 場 {r_title}】出賽跑法分佈：</b>
    放頭 <b>{leads_cnt}</b> 匹 ｜ 均速 <b>{paces_cnt}</b> 匹 ｜ 跟前 <b>{folls_cnt}</b> 匹 ｜ 後上 <b>{backs_cnt}</b> 匹 ｜ 大後上 <b>{vback_cnt}</b> 匹{scratched_info}
    <span style="color:#15803D; margin-left:8px; font-weight:bold;">➤ 步速推演：{pace_forecast}</span>
</div>
""", unsafe_allow_html=True)

# 頂部彩池指標
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(f'<div class="stat-card"><b>HK$ {int(win_pool):,}</b><br><span style="color:#64748B; font-size:11px;">獨贏 (WIN) 彩池</span></div>', unsafe_allow_html=True)
with m2:
    st.markdown(f'<div class="stat-card"><b>HK$ {int(pla_pool):,}</b><br><span style="color:#64748B; font-size:11px;">位置 (PLA) 彩池</span></div>', unsafe_allow_html=True)
with m3:
    st.markdown(f'<div class="stat-card"><b style="color:#B45309;">HK$ {int(q_pool):,}</b><br><span style="color:#B45309; font-size:11px; font-weight:bold;">連贏 (Q) 彩池 · 熱Q: {top_q["pair"]} ({top_q["c_q"]}倍)</span></div>', unsafe_allow_html=True)
with m4:
    st.markdown(f'<div class="stat-card"><b style="color:#1D4ED8;">HK$ {int(qp_pool):,}</b><br><span style="color:#1D4ED8; font-size:11px; font-weight:bold;">位置Q (QP) 彩池 · 熱QP: {top_q["pair"]} ({top_q["c_qp"]}倍)</span></div>', unsafe_allow_html=True)

# 輔助函數：渲染圓圈賽績
def render_dist_circles(stat):
    w, s, t, u = stat
    return f"""<div class="dist-circles">
    <span class="c-circle c-gold" title="冠軍: {w}次">{w}</span>
    <span class="c-circle c-silver" title="亞軍: {s}次">{s}</span>
    <span class="c-circle c-bronze" title="季軍: {t}次">{t}</span>
    <span class="c-circle c-gray" title="負/未入三甲: {u}次">{u}</span>
    </div>"""

# ----------------- 視圖 1: 賠率版 -----------------
if "專業賠率版" in chosen_view:
    st.markdown(f"##### 🏇 第 {race_no} 場《{r_title}》獨贏及位置實時走勢 (同程數據：🟡冠 ⚪亞 🟤季 ⚫負)")
    
    tbl1 = """<table class="compact-table"><thead><tr>
    <th>馬號</th><th>馬名</th>
    <th style="background:#EFF6FF; color:#1D4ED8;">檔位</th>
    <th style="background:#EFF6FF; color:#1D4ED8;">跑法</th>
    <th style="background:#FEF9C3; color:#854D0E;">同程數據 (冠-亞-季-負)</th>
    <th>負磅</th><th>騎師</th><th>練馬師</th>
    <th>隔夜WIN</th><th style="background:#FEF3C7;">臨場WIN</th>
    <th>🌙隔夜落飛</th><th>臨場跌幅</th>
    <th>隔夜PLA</th><th style="background:#FEF3C7;">臨場PLA</th>
    <th>🔥最熱Q配搭</th>
    <th>新增注碼</th><th>熱錢佔比</th><th>訊號</th>
    </tr></thead><tbody>"""
    
    for _, r in df.sort_values(by=["is_scratched", "stake"], ascending=[True, False]).iterrows():
        if r["is_scratched"]:
            tbl1 += f"""<tr class="scratched-row">
            <td><span class="circle-no" style="background:#94A3B8;">{r['no']}</span></td>
            <td><del>{r['name']}</del><span class="scratched-tag">退出</span></td>
            <td>-</td><td>-</td>
            <td>{render_dist_circles(r['dist_stat'])}</td>
            <td>{r['wt']}磅</td><td>{r['j']}</td><td>{r['t']}</td>
            <td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td>
            <td>-</td><td>$0</td><td>0.0%</td>
            <td><span class="badge b-red">🚫 退出</span></td>
            </tr>"""
            continue
            
        c_cls = "circle-no fav-no" if r["no"] == fav_h["no"] else "circle-no"
        q_matches = active_q[(active_q["h1"] == r["no"]) | (active_q["h2"] == r["no"])]
        if len(q_matches) > 0:
            q_pair_match = q_matches.iloc[0]
            oppo = q_pair_match["h2"] if q_pair_match["h1"] == r["no"] else q_pair_match["h1"]
            top_q_txt = f"{oppo}號 ({q_pair_match['c_q']}倍)"
        else:
            top_q_txt = "-"
            
        on_txt = f"{r['on_drop']:+.1f}%" if r["on_drop"] != 0 else "平"
        if r["on_drop"] >= 20.0: on_txt += " 🌙"
        
        tbl1 += f"""<tr>
        <td><span class="{c_cls}">{r['no']}</span></td>
        <td><b>{r['name']}</b></td>
        <td style="font-weight:bold; color:#1D4ED8; background:#EFF6FF;">{r['draw']}檔</td>
        <td style="font-weight:bold; background:#EFF6FF;">{r['style']}</td>
        <td style="background:#FEFCE8;">{render_dist_circles(r['dist_stat'])}</td>
        <td>{r['wt']}磅</td><td>{r['j']}</td><td>{r['t']}</td>
        <td>{r['o_win']}</td>
        <td style="background:#FFFBEB; font-weight:bold; color:#DC2626;">{r['c_win']}</td>
        <td style="font-weight:bold; color:#15803D;">{on_txt}</td>
        <td style="font-weight:bold;
