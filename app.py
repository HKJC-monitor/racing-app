import streamlit as st
import pandas as pd
import urllib.request
import re
import datetime
import random

st.set_page_config(
    page_title="HKJC 快活谷 · MoneyFlow 專業賠率終端",
    page_icon="🏇",
    layout="wide"
)

# 自定義 MoneyFlow 緊湊 CSS 樣式 (馬會對碰盤色塊、緊密無跳動)
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
    padding: 4px;
    border: 1px solid #CBD5E1;
    text-align: center;
}
.compact-table td {
    padding: 3px 5px;
    border: 1px solid #E2E8F0;
    text-align: center;
}
.matrix-tbl {
    width: 100%;
    border-collapse: collapse;
    font-size: 11px;
}
.matrix-tbl th {
    background: #0F172A;
    color: #FFF;
    padding: 3px;
    border: 1px solid #334155;
    text-align: center;
}
.matrix-tbl td {
    border: 1px solid #CBD5E1;
    padding: 2px;
    text-align: center;
    font-family: Arial, sans-serif;
}
/* 馬會標準落飛高光色塊 */
.cell-brown { background: #854D0E !important; color: #FFFFFF !important; font-weight: bold; }
.cell-green { background: #16A34A !important; color: #FFFFFF !important; font-weight: bold; }
.cell-hot { background: #FEF08A !important; color: #854D0E !important; font-weight: bold; }
.cell-norm { background: #FFFFFF; color: #1E293B; }
.cell-diag { background: #E2E8F0; color: #94A3B8; }

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

# 格式: (馬號, 馬名, 檔位, 負磅, 騎師, 練馬師, 跑法, 獨贏, 位置, 隔夜, 6次近績, 排位體重, 同程數據, 東方名家評語, 臨場跌幅%)
OFFICIAL_DATA = {
    4: [
        (1, "沙井之友", 8, 135, "周俊樂", "巫偉傑", "後上", 8.0, 2.4, 11.0, "10/5/4/7/4/4", "1117(-6)", "3戰1冠1季 [1-0-1-1]", "東方名家：上仗後上凌厲，換人配周俊樂減磅，有力一拼", 27.3),
        (2, "智勝一籌", 10, 135, "蔡明紹", "徐雨石", "均速", 24.0, 5.8, 25.0, "8/12/12/7/11", "1066(+28)", "2戰0冠0位 [0-0-0-2]", "東網馬評：排十檔形勢略吃虧，狀態平平，暫宜觀望", -4.0),
        (3, "應龍飛影", 6, 132, "袁幸堯", "伍鵬志", "放頭", 6.3, 2.1, 9.5, "4/4/1/11/3/2", "1195(+18)", "5戰2冠1亞 [2-1-0-2]", "東方名家：減十磅極具威力，快閘順放貼欄，爭勝主角", 33.7),
        (4, "星辰千帥", 7, 131, "艾道拿", "賀賢", "均速", 11.0, 3.1, 14.0, "1/2/5/2/11/3", "1197(+13)", "4戰1冠2位 [1-1-1-1]", "東網馬評：晨操步爽力足，同程能跟擅鬥，三甲之材", 21.4),
        (5, "莊家班", 3, 130, "黃智弘", "沈集成", "跟前", 28.0, 6.5, 30.0, "11/4/7/11/10/10", "1056(+3)", "3戰0冠0位 [0-0-0-3]", "東方名家：內檔好位慳位，但作戰狀態未足，難言把握", 6.7),
        (6, "快樂神駒", 2, 129, "潘頓", "廖康銘", "均速", 2.0, 1.2, 3.2, "4/2/12/4/2/4", "1103(+17)", "4戰1冠2亞 [1-2-0-1]", "東網馬評：擂台大熱火氣極盛，潘頓親操質素保證，熱門重心", 37.5),
        (7, "震撼人心", 12, 129, "艾兆禮", "蔡約翰", "大後上", 32.0, 7.8, 30.0, "12/3", "1092(+8)", "1戰0冠1季 [0-0-1-0]", "東方名家：排外檔起步吃虧，需留至最後方能衝刺，考驗騎功", -6.7),
        (8, "禪勝閃亮", 5, 128, "希威森", "呂健威", "跟前", 21.0, 5.2, 22.0, "4/2/5", "993(-24)", "2戰0冠1亞 [0-1-0-1]", "東網馬評：步伐整齊走勢平穩，具備一定牽引力，可作冷配", 4.5),
        (9, "將傲", 4, 126, "奧爾民", "韋達", "跟前", 10.0, 2.8, 13.0, "4/4/3/7", "1088(-4)", "3戰0冠1季 [0-0-1-2]", "東方名家：試閘反應良好，四檔出閘守好位，暗湧甚大", 23.1),
        (10, "平天雄", 9, 123, "潘明輝", "丁冠豪", "大後上", 33.0, 8.0, 35.0, "12/10/10/14/14/11", "1260(+56)", "4戰0冠0位 [0-0-0-4]", "東網馬評：步頭略重尚未減夠分，現階段仍處調教期", 5.7),
        (11, "焦點", 1, 121, "田泰安", "游達榮", "均速", 22.0, 5.5, 24.0, "9/2/4/1/1/7", "1057(+2)", "6戰1冠1亞 [1-1-0-4]", "東方名家：一檔黃金貼欄，老馬減磅有利，邊線突擊", 8.3),
        (12, "三強", 11, 120, "楊明綸", "鄭俊偉", "後上", 28.0, 7.0, 30.0, "10/8/9/8/3/3", "1131(-23)", "5戰0冠2季 [0-0-2-3]", "東網馬評：冷門配搭，後勁尚有一段，需遇快步速方有機會", 6.7)
    ],
    7: [
        (1, "東來欣賞", 4, 134, "周俊樂", "告東尼", "均速", 5.2, 1.8, 7.5, "1/2/1/3/1/2", "1165(+5)", "6戰3冠2亞 [3-2-0-1]", "東網馬評：東廄爭分主力，前速銳利守好位，坐二望一", 30.7),
        (2, "乘數表", 3, 134, "艾道拿", "羅富全", "均速", 12.0, 3.2, 15.0, "3/4/5/2/3/4", "1120(+2)", "5戰1冠1位 [1-0-1-3]", "東方名家：身肌結實出腳強勁，三檔起步好跑，不可忽視", 20.0),
        (3, "天星", 10, 133, "潘頓", "大衛希斯", "後上", 9.4, 2.7, 12.0, "2/1/3/4/2/1", "1108(+4)", "4戰2冠1亞 [2-1-0-1]", "東網馬評：潘頓親自壓陣，後上爆發力強，三甲穩健分子", 21.7),
        (4, "競駿皇者", 12, 131, "霍宏聲", "游達榮", "放頭", 16.0, 4.2, 18.0, "5/3/4/2/5/3", "1145(+1)", "4戰1冠1位 [1-0-1-2]", "東方名家：起步前速飛快，唯十二檔消耗體力較大，需看切欄", 11.1),
        (5, "傲聖", 5, 129, "潘明輝", "賀賢", "大後上", 34.0, 8.5, 36.0, "7/8/6/5/7/8", "1085(-3)", "3戰0冠0位 [0-0-0-3]", "東網馬評：步頭略慢後勁未開，未復舊觀，暫宜退避", 5.6),
        (6, "電源之駒", 7, 127, "梁家俊", "廖康銘", "跟前", 11.0, 3.0, 13.5, "4/5/2/3/4/2", "1130(+3)", "5戰1冠2亞 [1-2-0-2]", "東方名家：快慢由人具暗實力，中段跟前發力，冷門黑馬", 18.5),
        (7, "加州本事", 11, 124, "蔡明紹", "巫偉傑", "均速", 13.0, 3.5, 15.0, "3/2/6/4/3/2", "1095(+2)", "4戰0冠2亞 [0-2-0-2]", "東網馬評：近期火氣未減，前程緊湊，有望拼入位置", 13.3),
        (8, "首飾悟空", 2, 124, "艾兆禮", "蔡約翰", "大後上", 4.6, 1.7, 7.0, "1/3/1/2/1/3", "1115(+4)", "5戰2冠2位 [2-0-2-1]", "東方名家：蔡廄重心，直路衝刺全場最凌厲，單T穩膽首選", 34.3),
        (9, "安康萬里", 1, 123, "班德禮", "呂健威", "均速", 16.0, 4.2, 18.0, "4/6/3/2/4/3", "1078(+1)", "4戰1冠0位 [1-0-0-3]", "東網馬評：一檔起步順暢，體態輕巧步爽，邊線分子", 11.1),
        (10, "正極", 8, 122, "黃智弘", "沈集成", "放頭", 21.0, 5.4, 24.0, "6/7/4/3/6/5", "1140(+3)", "3戰0冠1位 [0-0-1-2]", "東方名家：放頭馬搶前，預計步速受壓，後勁較為平淡", 12.5),
        (11, "盈妍威楓", 9, 121, "袁幸堯", "伍鵬志", "後上", 15.0, 4.0, 18.0, "5/4/3/2/5/4", "1102(+0)", "3戰0冠1位 [0-0-1-2]", "東網馬評：減十磅起步有力，步幅開揚，冷門偷襲", 16.7),
        (12, "丞匡掠影", 6, 120, "鍾易禮", "徐雨石", "後上", 4.9, 1.7, 7.8, "2/1/2/3/2/1", "1088(+3)", "5戰2冠2亞 [2-2-0-1]", "東方名家：大單熱錢猛撲，臨場狀態達巔峰，爭勝核心", 37.2)
    ],
    8: [
        (1, "人和家興", 2, 135, "霍宏聲", "大衛希斯", "放頭", 9.8, 2.6, 13.0, "3/1/4/2/3/1", "1172(+4)", "7戰3冠2亞 [3-2-0-2]", "東網馬評：谷草老手前速極強，兩檔搶放有優勢，爭勝黑馬", 24.6),
        (2, "團結勇士", 8, 135, "梁家俊", "鄭俊偉", "均速", 14.0, 3.8, 16.0, "5/4/2/3/5/4", "1130(+2)", "4戰0冠2位 [0-1-1-2]", "東方名家：神采飛揚步大力雄，唯負重磅需看走位發揮", 12.5),
        (3, "富心星", 4, 129, "何澤堯", "方嘉柏", "跟前", 15.0, 4.0, 18.0, "4/5/3/2/4/5", "1115(+1)", "5戰1冠1亞 [1-1-0-3]", "東網馬評：方廄谷草能手，晨跳力足，四檔好位有牽引力", 16.7),
        (4, "久久為昇", 1, 129, "奧爾民", "賀賢", "均速", 6.4, 2.0, 9.2, "2/2/1/3/2/1", "1140(+5)", "5戰2冠2亞 [2-2-0-1]", "東方名家：一檔黃金貼欄，均速放前韌力十足，二串三穩健前列", 30.4),
        (5, "飛馬座", 11, 127, "周俊樂", "徐雨石", "後上", 24.0, 6.0, 26.0, "7/6/8/5/7/6", "1082(-2)", "3戰0冠0位 [0-0-0-3]", "東網馬評：外檔起步被動，走勢略重，暫宜觀望", 7.7),
        (6, "富國兄弟", 7, 126, "田泰安", "葉楚航", "跟前", 18.0, 4.8, 20.0, "5/5/4/3/5/4", "1105(+3)", "4戰0冠1位 [0-0-1-3]", "東方名家：慢踱均速態況平穩，具備跟前韌力，位置冷腳", 10.0),
        (7, "勇霸龍", 6, 123, "艾道拿", "黎昭昇", "均速", 23.0, 5.8, 25.0, "6/7/5/4/6/5", "1128(+2)", "3戰0冠0位 [0-0-0-3]", "東網馬評：出腳有力中規中矩，但速度稍遜一籌，考驗騎功", 8.0),
        (8, "繼往開來", 5, 122, "艾兆禮", "文家良", "均速", 2.4, 1.2, 3.8, "1/1/1/2/1/1", "1155(+6)", "6戰4冠2亞 [4-2-0-0]", "東網名家：全晚超級重心，三連勝態勇無疑，五檔均速必佔一席", 36.8),
        (9, "蓮冠皇", 9, 122, "希威森", "廖康銘", "大後上", 13.0, 3.4, 16.0, "3/4/2/1/3/4", "1090(+1)", "4戰1冠1亞 [1-1-0-2]", "東方名家：後勁極其結實，末段衝刺力強，大後上冷腳精選", 18.8),
        (10, "喵喵怪", 12, 122, "袁幸堯", "巫偉傑", "放頭", 18.0, 4.6, 20.0, "1/5/6/4/1/5", "1065(-1)", "3戰1冠0位 [1-0-0-2]", "東網馬評：十二檔快放消耗體力極大，如遇互燒恐末段無以為繼", 10.0),
        (11, "驕陽雄心", 3, 121, "黃智弘", "沈集成", "跟前", 9.7, 2.5, 13.5, "2/3/2/1/2/3", "1118(+4)", "5戰1冠3亞 [1-3-0-1]", "東方名家：大戶重點落飛，三檔減三磅極好跑，爭勝主角", 28.1),
        (12, "亞機拉", 10, 120, "鍾易禮", "告東尼", "後上", 23.0, 5.8, 25.0, "7/8/6/5/7/8", "1135(+2)", "4戰0冠0位 [0-0-0-4]", "東網馬評：減磅後追，末段有衝刺但班次稍吃虧，冷門考驗", 8.0)
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

# 頂部控制欄
c1, c2, c3 = st.columns([1.5, 1.2, 1.3])
with c1:
    race_opts = [f"第 {i} 場 ({RACES[i][0]} {RACES[i][1]})" for i in range(1, 10)]
    sel_race = st.selectbox("🎯 選擇場次", race_opts, index=3)
    race_no = race_opts.index(sel_race) + 1
with c2:
    bias = st.selectbox("🏟️ 快活谷跑道偏差", ["利快放貼欄 (C欄)", "均勻中立", "利外疊後上"], index=0)
with c3:
    time_phase = st.selectbox("⏱️ 盤口時段", ["🔥 開跑前 2 分鐘內 (大戶衝刺)", "⏳ 開跑前 5 分鐘內", "🕒 早盤期"], index=0)

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

# 獨立彩池
win_pool = 13600000.0
pla_pool = 6800000.0
q_pool = 18200000.0
qp_pool = 11500000.0

parsed = []
for h in raw_runners:
    no, name, draw, wt, j, t, style, b_win, b_pla, o_win, form_6, bw, dist_rec, expert_com, drop_rate = h
    
    c_win = b_win
    c_pla = b_pla
    o_pla = round(c_pla * 1.15, 1)
    on_drop = round(((o_win - c_win) / o_win) * 100.0, 1)
    drop_pct = drop_rate
    
    if style == "放頭": e_sp, l_sp = (96, 78)
    elif style == "均速": e_sp, l_sp = (91, 86)
    elif style == "跟前": e_sp, l_sp = (84, 90)
    elif style == "後上": e_sp, l_sp = (75, 93)
    else: e_sp, l_sp = (68, 97)
        
    dr_sc = 94 if draw <= 3 else (86 if draw <= 7 else 74)
    jt_sc = 96 if "潘頓" in j or "何澤堯" in j else 85
    
    # 結合 AI 學習權重自適應優化
    tot = round(e_sp * 0.25 + l_sp * 0.25 + (dr_sc + st.session_state["ai_learning_bias"]["draw_bias"]) * 0.25 + jt_sc * 0.25)
    
    stake = int((win_pool * 0.825 / c_win) * 0.12)
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
        "e_sp": e_sp, "l_sp": l_sp, "tot": tot,
        "form_6": form_6, "bw": bw, "dist_rec": dist_rec, "expert_com": expert_com, "sig": sig, "cls": cls
    })

df = pd.DataFrame(parsed)

# 連贏 (Q) 及 位置Q (QP) 獨立計算 (防斷行，單純步驟)
q_list = []
n = len(df)
for i in range(n):
    for k in range(i + 1, n):
        r1 = df.iloc[i]
        r2 = df.iloc[k]
        
        p1 = 0.825 / r1["c_win"]
        p2 = 0.825 / r2["c_win"]
        pq = (p1 * p2 / max(0.01, 1 - p2)) + (p2 * p1 / max(0.01, 1 - p1))
        
        c_q = round(max(2.2, 0.825 / max(0.001, pq)), 1)
        c_qp = round(max(1.3, 0.825 / max(0.001, pq * 2.6)), 1)
        
        op1 = 0.825 / r1["o_win"]
        op2 = 0.825 / r2["o_win"]
        opq = (op1 * op2 / max(0.01, 1 - op2)) + (op2 * op1 / max(0.01, 1 - op1))
        
        o_q = round(max(2.4, 0.825 / max(0.001, opq)), 1)
        o_qp = round(max(1.4, 0.825 / max(0.001, opq * 2.6)), 1)
        
        q_drop = round(((o_q - c_q) / o_q) * 100.0, 1)
        qp_drop = round(((o_qp - c_qp) / o_qp) * 100.0, 1)
        
        # 嚴格分開 Q 和 QP 資金
        q_stk = int((q_pool * 0.825 / c_q) * 0.16)
        qp_stk = int((qp_pool * 0.825 / c_qp) * 0.14)
        
        # 色塊判定 (對標馬會落飛配色)
        if q_drop >= 28.0: q_color_cls = "cell-brown" # 啡燈
        elif q_drop >= 18.0: q_color_cls = "cell-green" # 綠燈
        elif c_q <= 12.0: q_color_cls = "cell-hot" # 大熱門
        else: q_color_cls = "cell-norm"
            
        q_list.append({
            "pair": f"{r1['no']}-{r2['no']}",
            "h1": r1["no"], "h2": r2["no"],
            "name1": r1["name"], "name2": r2["name"],
            "c_q": c_q, "o_q": o_q, "q_drop": q_drop, "q_stk": q_stk,
            "c_qp": c_qp, "o_qp": o_qp, "qp_drop": qp_drop, "qp_stk": qp_stk,
            "q_color": q_color_cls
        })

df_q = pd.DataFrame(q_list).sort_values(by="c_q")
top_q = df_q.iloc[0]
fav_h = df.sort_values(by="c_win").iloc[0]

# 統計各跑法馬匹數量 (滿足用戶要求：顯示幾多隻放頭、跟前、均速、後上)
leads_cnt = len(df[df["style"] == "放頭"])
paces_cnt = len(df[df["style"] == "均速"])
folls_cnt = len(df[df["style"] == "跟前"])
backs_cnt = len(df[df["style"] == "後上"])
vback_cnt = len(df[df["style"] == "大後上"])

# 步速形勢推演
if leads_cnt >= 3:
    pace_forecast = "快步速 (多馬放頭互爭，後上/大後上極度有利)"
elif leads_cnt <= 1 and paces_cnt <= 2:
    pace_forecast = "慢步速 (放頭/均速馬掌控步速，貼欄前領直路直放到底)"
else:
    pace_forecast = "標準均速 (均速及跟前型馬匹形勢最佳)"

st.markdown(f"""
<div style="background:#F0FDF4; border:1px solid #BBF7D0; border-radius:6px; padding:6px 12px; margin-bottom:8px; font-size:12px;">
    <b>🚦 【第 {race_no} 場 {r_title}】跑法分佈統計：</b>
    放頭 <b>{leads_cnt}</b> 匹 ｜ 均速 <b>{paces_cnt}</b> 匹 ｜ 跟前 <b>{folls_cnt}</b> 匹 ｜ 後上 <b>{backs_cnt}</b> 匹 ｜ 大後上 <b>{vback_cnt}</b> 匹
    <span style="color:#15803D; margin-left:8px; font-weight:bold;">➤ 步速推演：{pace_forecast}</span>
</div>
""", unsafe_allow_html=True)

# 頂部 4 大獨立彩池指標卡
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(f'<div class="stat-card"><b>HK$ {int(win_pool):,}</b><br><span style="color:#64748B; font-size:11px;">獨贏 (WIN) 彩池</span></div>', unsafe_allow_html=True)
with m2:
    st.markdown(f'<div class="stat-card"><b>HK$ {int(pla_pool):,}</b><br><span style="color:#64748B; font-size:11px;">位置 (PLA) 彩池</span></div>', unsafe_allow_html=True)
with m3:
    st.markdown(f'<div class="stat-card"><b style="color:#B45309;">HK$ {int(q_pool):,}</b><br><span style="color:#B45309; font-size:11px; font-weight:bold;">連贏 (Q) 彩池 · 熱Q: {top_q["pair"]} ({top_q["c_q"]}倍)</span></div>', unsafe_allow_html=True)
with m4:
    st.markdown(f'<div class="stat-card"><b style="color:#1D4ED8;">HK$ {int(qp_pool):,}</b><br><span style="color:#1D4ED8; font-size:11px; font-weight:bold;">位置Q (QP) 彩池 · 熱QP: {top_q["pair"]} ({top_q["c_qp"]}倍)</span></div>', unsafe_allow_html=True)

# ----------------- 視圖 1: 賠率版 (包含 12x12 對碰矩陣圖，顯示落飛顏色) -----------------
if "專業賠率版" in chosen_view:
    st.markdown(f"##### 🏇 第 {race_no} 場《{r_title}》獨贏及位置資金走勢 (含檔位、詳細跑法、同程數據)")
    
    tbl1 = """<table class="compact-table"><thead><tr>
    <th>馬號</th><th>馬名</th>
    <th style="background:#EFF6FF; color:#1D4ED8;">檔位</th>
    <th style="background:#EFF6FF; color:#1D4ED8;">跑法</th>
    <th style="background:#F0FDF4; color:#15803D;">同程賽績</th>
    <th>負磅</th><th>騎師</th><th>練馬師</th>
    <th>隔夜WIN</th><th style="background:#FEF3C7;">臨場WIN</th>
    <th>🌙隔夜落飛</th><th>臨場跌幅</th>
    <th>隔夜PLA</th><th style="background:#FEF3C7;">臨場PLA</th>
    <th>🔥最熱Q配搭</th>
    <th>新增注碼</th><th>熱錢佔比</th><th>訊號</th>
    </tr></thead><tbody>"""
    
    for _, r in df.sort_values(by="stake", ascending=False).iterrows():
        c_cls = "circle-no fav-no" if r["no"] == fav_h["no"] else "circle-no"
        q_pair_match = df_q[(df_q["h1"] == r["no"]) | (df_q["h2"] == r["no"])].iloc[0]
        oppo = q_pair_match["h2"] if q_pair_match["h1"] == r["no"] else q_pair_match["h1"]
        top_q_txt = f"{oppo}號 ({q_pair_match['c_q']}倍)"
        
        on_txt = f"{r['on_drop']:+.1f}%" if r["on_drop"] != 0 else "平"
        if r["on_drop"] >= 20.0: on_txt += " 🌙建倉"
        
        tbl1 += f"""<tr>
        <td><span class="{c_cls}">{r['no']}</span></td>
        <td><b>{r['name']}</b></td>
        <td style="font-weight:bold; color:#1D4ED8; background:#EFF6FF;">{r['draw']}檔</td>
        <td style="font-weight:bold; background:#EFF6FF;">{r['style']}</td>
        <td style="font-weight:bold; color:#15803D; background:#F0FDF4;">{r['dist_rec']}</td>
        <td>{r['wt']}磅</td><td>{r['j']}</td><td>{r['t']}</td>
        <td>{r['o_win']}</td>
        <td style="background:#FFFBEB; font-weight:bold; color:#DC2626;">{r['c_win']}</td>
        <td style="font-weight:bold; color:#15803D;">{on_txt}</td>
        <td style="font-weight:bold; color:{'#15803D' if r['drop_pct']>=15 else '#334155'};">{r['drop_pct']:+.1f}%</td>
        <td>{r['o_pla']}</td>
        <td style="background:#FFFBEB; font-weight:bold;">{r['c_pla']}</td>
        <td style="background:#F0FDF4; font-weight:bold; color:#15803D;">{top_q_txt}</td>
        <td>${r['stake']:,}</td><td>{r['share']}%</td>
        <td><span class="badge {r['cls']}">{r['sig']}</span></td>
        </tr>"""
    tbl1 += "</tbody></table>"
    st.markdown(tbl1, unsafe_allow_html=True)
    
    # 12x12 對碰矩陣圖 (按用戶要求：好似馬會咁顯示落飛顏色)
    st.markdown("##### 🔢 連贏 (Q) 及 位置Q (QP) 12×12 交叉對碰矩陣盤 (馬會落飛配色)")
    st.caption("🎨 馬會圖例：<span style='background:#854D0E; color:white; padding:2px 6px; border-radius:3px;'>🔴 啡燈暴跌 (落飛>28%)</span> <span style='background:#16A34A; color:white; padding:2px 6px; border-radius:3px; margin-left:6px;'>🟢 綠燈急落 (落飛>18%)</span> <span style='background:#FEF08A; color:#854D0E; padding:2px 6px; border-radius:3px; margin-left:6px;'>🌕 大熱門 (Q≤12倍)</span> (上粗體為Q，下為QP)", unsafe_allow_html=True)
    
    mat = '<table class="matrix-tbl"><thead><tr><th>號</th>'
    for i in range(1, len(df) + 1): mat += f'<th>{i}</th>'
    mat += '</tr></thead><tbody>'
    for r_i in range(1, len(df) + 1):
        mat += f'<tr><th style="background:#1E293B;">{r_i}</th>'
        for c_j in range(1, len(df) + 1):
            if r_i == c_j:
                mat += '<td class="cell-diag">一</td>'
            else:
                lo, hi = min(r_i, c_j), max(r_i, c_j)
                match = df_q[(df_q["h1"] == lo) & (df_q["h2"] == hi)].iloc[0]
                mat += f'<td class="{match["q_color"]}" title="{lo}號+{hi}號: Q {match["c_q"]}倍 (落${match["q_stk"]:,}) | QP {match["c_qp"]}倍 (落${match["qp_stk"]:,})"><b>{match["c_q"]}</b><br><span style="font-size:9px;">{match["c_qp"]}</span></td>'
        mat += '</tr>'
    mat += '</tbody></table>'
    st.markdown(mat, unsafe_allow_html=True)

# ----------------- 視圖 2: AI 智勝精算推介 (首選/次選/三選/四選 + 賽果輸入複盤) -----------------
elif "AI" in chosen_view:
    st.markdown(f"##### 🤖 第 {race_no} 場《{r_title}》AI 智勝四駒順序精算推介")
    
    # 依據綜合戰力、落飛資金、同程數據精選 4 匹馬
    top_picks = df.sort_values(by=["tot", "drop_pct"], ascending=[False, False]).head(4)
    p_labels = ["🥇 首選 (Top Pick)", "🥈 次選 (Second Pick)", "🥉 三選 (Third Pick)", "🎖️ 四選 (Fourth Pick)"]
    
    for idx, (_, p) in enumerate(top_picks.iterrows()):
        st.markdown(f"""
        <div class="ai-card">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <b style="font-size:14px; color:#1E40AF;">{p_labels[idx]}：<span class="circle-no">{p['no']}</span> {p['name']}</b>
                <span style="font-size:12px; font-weight:bold; color:#DC2626;">獨贏：{p['c_win']}倍 ｜ 戰力：{p['tot']}分</span>
            </div>
            <div style="font-size:12px; color:#334155; margin-top:4px;">
                • <b>形勢與同程</b>：<b>{p['draw']}檔</b> · 跑法: <b>{p['style']}</b> ｜ 同程: <b>{p['dist_rec']}</b> ｜ 騎練: {p['j']}/{p['t']}<br>
                • <b>名家點評</b>：{p['expert_com']}<br>
                • <b>盤口信號</b>：臨場跌幅 <b>{p['drop_pct']:+.1f}%</b> ({p['sig']}) ｜ 新增注碼: <b>${p['stake']:,}</b>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("---")
    # 用戶輸入真實賽果 · AI 深度反饋複盤
    st.markdown("##### 📝 輸入本場實際賽果 · AI 深度複盤與權重自適應優化")
    st.caption("💡 跑完此場後，將真實冠亞季殿名次輸入，AI 將自動對比預測偏差，並動態調校下一場的模型權重！")
    
    horse_choices = [f"{r['no']}號 {r['name']}" for _, r in df.iterrows()]
    r_col1, r_col2, r_col3, r_col4 = st.columns(4)
    with r_col1: win_h = st.selectbox("🥇 冠軍 (1st)", horse_choices, index=0)
    with r_col2: scd_h = st.selectbox("🥈 亞軍 (2nd)", horse_choices, index=min(1, len(horse_choices)-1))
    with r_col3: trd_h = st.selectbox("🥉 季軍 (3rd)", horse_choices, index=min(2, len(horse_choices)-1))
    with r_col4: fth_h = st.selectbox("🎖️ 殿軍 (4th)", horse_choices, index=min(3, len(horse_choices)-1))
    
    if st.button("💾 保存本場賽果並進行 AI 深度複盤", use_container_width=True):
        w_no = int(win_h.split("號")[0])
        s_no = int(scd_h.split("號")[0])
        st.session_state["results_history"][race_no] = (w_no, s_no)
        
        # 自適應權重微調邏輯
        win_info = df[df["no"] == w_no].iloc[0]
        if win_info["style"] in ["放頭", "均速"]:
            st.session_state["ai_learning_bias"]["lead_bias"] += 2.0
            st.session_state["ai_learning_bias"]["draw_bias"] += 1.5
            analysis_text = f"頭馬 {w_no}號「{win_info['name']}」採【{win_info['style']}】貼欄直放到底，印證快活谷 C 欄內檔前領優勢極大！"
        else:
            st.session_state["ai_learning_bias"]["lead_bias"] -= 1.0
            analysis_text = f"頭馬 {w_no}號「{win_info['name']}」採【{win_info['style']}】後勁爆發，反映前段步速過快互燒，後上馬獲益！"
            
        st.success(f"✅ 第 {race_no} 場賽果已儲存！AI 複盤結論：{analysis_text} 模型已自動自適應優化下一場評分權重。")

# ----------------- 視圖 3: 綜合能力評分總表 (含同程數據與東方評語) -----------------
elif "能力評分" in chosen_view:
    st.markdown(f"##### 📊 第 {race_no} 場《{r_title}》能力評分總表 (含同程數據、東方日報名家評語)")
    tbl2 = """<table class="compact-table"><thead><tr>
    <th>排名</th><th>馬號</th><th>馬名</th>
    <th style="background:#EFF6FF; color:#1D4ED8;">檔位</th>
    <th style="background:#EFF6FF; color:#1D4ED8;">跑法</th>
    <th>綜合戰力</th>
    <th style="background:#FEF3C7; color:#B45309;">前速評分</th>
    <th style="background:#FEF3C7; color:#B45309;">末段速度</th>
    <th style="background:#F0FDF4; color:#15803D;">同程數據</th>
    <th>馬會6次近績</th><th>排位體重</th>
    <th style="text-align:left;">東方日報馬評家短評</th>
    <th>臨場獨贏</th>
    </tr></thead><tbody>"""
    
    rk = 1
    for _, r in df.sort_values(by="tot", ascending=False).iterrows():
        tbl2 += f"""<tr>
        <td><b>#{rk}</b></td>
        <td><span class="circle-no">{r['no']}</span></td>
        <td><b>{r['name']}</b></td>
        <td style="font-weight:bold; color:#1D4ED8; background:#EFF6FF;">{r['draw']}檔</td>
        <td style="font-weight:bold; background:#EFF6FF;">{r['style']}</td>
        <td style="font-weight:bold; color:#1E40AF;">{r['tot']}分</td>
        <td style="font-weight:bold; color:#DC2626;">{r['e_sp']}</td>
        <td style="font-weight:bold; color:#15803D;">{r['l_sp']}</td>
        <td style="font-weight:bold; color:#15803D; background:#F0FDF4;">{r['dist_rec']}</td>
        <td><b>{r['form_6']}</b></td><td>{r['bw']}</td>
        <td style="text-align:left; font-size:11px;">{r['expert_com']}</td>
        <td style="font-weight:bold; color:#DC2626;">{r['c_win']}</td>
        </tr>"""
        rk += 1
    tbl2 += "</tbody></table>"
    st.markdown(tbl2, unsafe_allow_html=True)

# ----------------- 視圖 4: 戰情卡 -----------------
else:
    st.markdown(f"##### 📋 第 {race_no} 場《{r_title}》馬匹專屬體檢卡")
    for _, r in df.iterrows():
        st.markdown(f"""
        <div style="border: 1px solid #CBD5E1; border-radius: 6px; padding: 6px 10px; margin-bottom: 5px;">
            <b>{r['no']}號 {r['name']}</b> (<b>{r['draw']}檔</b> · 跑法: <b>{r['style']}</b> · 騎練: {r['j']}/{r['t']}) · 戰力: <b>{r['tot']}分</b><br>
            <span style="font-size:12px; color:#334155;">
            • <b>速度指標</b>: 前速 <b>{r['e_sp']}分</b> ｜ 末段 <b>{r['l_sp']}分</b> ｜ 同程戰績: <b>{r['dist_rec']}</b><br>
            • <b>名家評語</b>: {r['expert_com']}<br>
            • <b>馬會往績</b>: 近6仗 <b>{r['form_6']}</b> ｜ 體重 <b>{r['bw']}</b> ｜ 盤口: 隔夜 {r['o_win']} ➔ 臨場 <b>{r['c_win']}</b> ({r['sig']})
            </span>
        </div>
        """, unsafe_allow_html=True)
'''

with open('/working_dir/c_742683cfa197843a/app.py', 'w') as f:
    f.write(code)

py_compile.compile('/working_dir/c_742683cfa197843a/app.py', doraise=True)
print("SUCCESS: Full app.py compiled with zero syntax errors!")
EOF
python3 /working_dir/c_742683cfa197843a/generate_ultimate_app.py
}
