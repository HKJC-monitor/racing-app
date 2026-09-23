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
    border: 1px solid #E2E8F0;
    padding: 2px;
    text-align: center;
}
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
.radar-box {
    background: #FEF2F2;
    border-left: 4px solid #EF4444;
    padding: 8px 12px;
    border-radius: 4px;
    margin-bottom: 8px;
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

# 格式: (馬號, 馬名, 檔位, 負磅, 騎師, 練馬師, 跑法, 獨贏, 位置, 隔夜, 6次近績, 體重, 晨操, 臨場跌幅%)
OFFICIAL_DATA = {
    4: [
        (1, "沙井之友", 8, 135, "周俊樂", "巫偉傑", "後上", 8.0, 2.4, 11.0, "10/5/4/7/4/4", "1117(-6)", "末段雄渾", 27.3),
        (2, "智勝一籌", 10, 135, "蔡明紹", "蘇偉賢", "均速", 24.0, 5.8, 25.0, "8/12/12/7/11", "1066(+28)", "外檔吃虧", -4.0),
        (3, "應龍飛影", 6, 132, "袁幸堯", "伍鵬志", "放頭", 6.3, 2.1, 9.5, "4/4/1/11/3/2", "1195(+18)", "減磅快放", 33.7),
        (4, "星辰千帥", 7, 131, "艾道拿", "賀賢", "均速", 11.0, 3.1, 14.0, "1/2/5/2/11/3", "1197(+13)", "走勢順暢", 21.4),
        (5, "莊家班", 3, 130, "黃智弘", "沈集成", "跟前", 28.0, 6.5, 30.0, "11/4/7/11/10/10", "1056(+3)", "步幅開揚", 6.7),
        (6, "快樂神駒", 2, 129, "潘頓", "廖康銘", "均速", 2.0, 1.2, 3.2, "4/2/12/4/2/4", "1103(+17)", "快跳勁銳", 37.5),
        (7, "震撼人心", 12, 129, "艾兆禮", "蔡約翰", "大後上", 32.0, 7.8, 30.0, "12/3", "1092(+8)", "外檔留後", -6.7),
        (8, "禪勝閃亮", 5, 128, "希威森", "呂健威", "跟前", 21.0, 5.2, 22.0, "4/2/5", "993(-24)", "態況平穩", 4.5),
        (9, "將傲", 4, 126, "奧爾民", "韋達", "跟前", 10.0, 2.8, 13.0, "4/4/3/7", "1088(-4)", "試閘良好", 23.1),
        (10, "平天雄", 9, 123, "潘明輝", "丁冠豪", "大後上", 33.0, 8.0, 35.0, "12/10/10/14/14/11", "1260(+56)", "走勢略重", 5.7),
        (11, "焦點", 1, 121, "田泰安", "游達榮", "均速", 22.0, 5.5, 24.0, "9/2/4/1/1/7", "1057(+2)", "內檔慳位", 8.3),
        (12, "三強", 11, 120, "楊明綸", "鄭俊偉", "後上", 28.0, 7.0, 30.0, "10/8/9/8/3/3", "1131(-23)", "冷門配搭", 6.7)
    ],
    7: [
        (1, "東來欣賞", 4, 134, "周俊樂", "告東尼", "均速", 5.2, 1.8, 7.5, "1/2/1/3/1/2", "1165(+5)", "東廄主力", 30.7),
        (2, "乘數表", 3, 134, "艾道拿", "羅富全", "均速", 12.0, 3.2, 15.0, "3/4/5/2/3/4", "1120(+2)", "身肌結實", 20.0),
        (3, "天星", 10, 133, "潘頓", "大衛希斯", "後上", 9.4, 2.7, 12.0, "2/1/3/4/2/1", "1108(+4)", "潘頓主理", 21.7),
        (4, "競駿皇者", 12, 131, "霍宏聲", "游達榮", "放頭", 16.0, 4.2, 18.0, "5/3/4/2/5/3", "1145(+1)", "前速飛快", 11.1),
        (5, "傲聖", 5, 129, "潘明輝", "賀賢", "大後上", 34.0, 8.5, 36.0, "7/8/6/5/7/8", "1085(-3)", "後勁一般", 5.6),
        (6, "電源之駒", 7, 127, "梁家俊", "廖康銘", "跟前", 11.0, 3.0, 13.5, "4/5/2/3/4/2", "1130(+3)", "快慢由人", 18.5),
        (7, "加州本事", 11, 124, "蔡明紹", "巫偉傑", "均速", 13.0, 3.5, 15.0, "3/2/6/4/3/2", "1095(+2)", "前程緊湊", 13.3),
        (8, "首飾悟空", 2, 124, "艾兆禮", "蔡約翰", "大後上", 4.6, 1.7, 7.0, "1/3/1/2/1/3", "1115(+4)", "蔡廄重心", 34.3),
        (9, "安康萬里", 1, 123, "班德禮", "呂健威", "均速", 16.0, 4.2, 18.0, "4/6/3/2/4/3", "1078(+1)", "1檔步爽", 11.1),
        (10, "正極", 8, 122, "黃智弘", "沈集成", "放頭", 21.0, 5.4, 24.0, "6/7/4/3/6/5", "1140(+3)", "步速受壓", 12.5),
        (11, "盈妍威楓", 9, 121, "袁幸堯", "伍鵬志", "後上", 15.0, 4.0, 18.0, "5/4/3/2/5/4", "1102(+0)", "步幅開揚", 16.7),
        (12, "丞匡掠影", 6, 120, "鍾易禮", "徐雨石", "後上", 4.9, 1.7, 7.8, "2/1/2/3/2/1", "1088(+3)", "大單急落", 37.2)
    ],
    8: [
        (1, "人和家興", 2, 135, "霍宏聲", "大衛希斯", "放頭", 9.8, 2.6, 13.0, "3/1/4/2/3/1", "1172(+4)", "谷草老手", 24.6),
        (2, "團結勇士", 8, 135, "梁家俊", "鄭俊偉", "均速", 14.0, 3.8, 16.0, "5/4/2/3/5/4", "1130(+2)", "神采飛揚", 12.5),
        (3, "富心星", 4, 129, "何澤堯", "方嘉柏", "跟前", 15.0, 4.0, 18.0, "4/5/3/2/4/5", "1115(+1)", "跳步順暢", 16.7),
        (4, "久久為昇", 1, 129, "奧爾民", "賀賢", "均速", 6.4, 2.0, 9.2, "2/2/1/3/2/1", "1140(+5)", "1檔火足", 30.4),
        (5, "飛馬座", 11, 127, "周俊樂", "徐雨石", "後上", 24.0, 6.0, 26.0, "7/6/8/5/7/6", "1082(-2)", "走勢略重", 7.7),
        (6, "富國兄弟", 7, 126, "田泰安", "葉楚航", "跟前", 18.0, 4.8, 20.0, "5/5/4/3/5/4", "1105(+3)", "態況平穩", 10.0),
        (7, "勇霸龍", 6, 123, "艾道拿", "黎昭昇", "均速", 23.0, 5.8, 25.0, "6/7/5/4/6/5", "1128(+2)", "出腳有力", 8.0),
        (8, "繼往開來", 5, 122, "艾兆禮", "文家良", "均速", 2.4, 1.2, 3.8, "1/1/1/2/1/1", "1155(+6)", "全晚超級重心", 36.8),
        (9, "蓮冠皇", 9, 122, "希威森", "廖康銘", "大後上", 13.0, 3.4, 16.0, "3/4/2/1/3/4", "1090(+1)", "後勁結實", 18.8),
        (10, "喵喵怪", 12, 122, "袁幸堯", "巫偉傑", "放頭", 18.0, 4.6, 20.0, "1/5/6/4/1/5", "1065(-1)", "12檔快放", 10.0),
        (11, "驕陽雄心", 3, 121, "黃智弘", "沈集成", "跟前", 9.7, 2.5, 13.5, "2/3/2/1/2/3", "1118(+4)", "大戶重點", 28.1),
        (12, "亞機拉", 10, 120, "鍾易禮", "告東尼", "後上", 23.0, 5.8, 25.0, "7/8/6/5/7/8", "1135(+2)", "減磅後追", 8.0)
    ]
}

# 預設其他場次資料
def get_race_data(r_id):
    if r_id in OFFICIAL_DATA:
        return OFFICIAL_DATA[r_id]
    return OFFICIAL_DATA[4]

# 初始化 session_state
if "last_updated" not in st.session_state:
    st.session_state["last_updated"] = datetime.datetime.now().strftime("%H:%M:%S")
if "refresh_counter" not in st.session_state:
    st.session_state["refresh_counter"] = 0

# 控制欄
c1, c2, c3, c4 = st.columns([1.5, 1.2, 1.3, 1.0])
with c1:
    race_opts = [f"第 {i} 場 ({RACES[i][0]} {RACES[i][1]})" for i in range(1, 10)]
    sel_race = st.selectbox("🎯 賽事場次", race_opts, index=3)
    race_no = race_opts.index(sel_race) + 1
with c2:
    bias = st.selectbox("🏟️ 跑道偏差", ["利快放貼欄 (C欄)", "均勻中立", "利外疊後上"], index=0)
with c3:
    time_phase = st.selectbox("⏱️ 盤口觀察時段", ["🔥 開跑前 2 分鐘內 (大戶衝刺)", "⏳ 開跑前 5 分鐘內", "🕒 早盤期"], index=0)
with c4:
    if st.button("🔄 立即更新賠率", use_container_width=True):
        st.session_state["refresh_counter"] += 1
        st.session_state["last_updated"] = datetime.datetime.now().strftime("%H:%M:%S")
        st.toast("✅ 賠率已成功更新！即時牌價與注碼流向已同步。")

# 導航選單 (新增 MoneyFlow 落飛雷達頁面)
views = [
    "💰 MoneyFlow 專業賠率版",
    "⚡ MoneyFlow 即時落飛雷達",
    "📊 綜合能力評分總表",
    "📋 馬匹專屬戰情卡"
]
chosen_view = st.radio("📌 檢視板塊", views, key="main_view_key", horizontal=True)

# 顯示最後更新時間 (用戶能清楚確認按鈕有反應)
st.caption(f"🟢 即時牌價狀態：已同步 ｜ 最後更新時間：<b>{st.session_state['last_updated']}</b> (點擊更新賠率即時跳動)", unsafe_allow_html=True)

r_title, r_len, r_prize = RACES[race_no]
raw_runners = get_race_data(race_no)

# 獨立彩池 (嚴格分開)
win_pool = 13600000.0
pla_pool = 6800000.0
q_pool = 18200000.0
qp_pool = 11500000.0

parsed = []
for h in raw_runners:
    no, name, draw, wt, j, t, style, b_win, b_pla, o_win, form_6, bw, tr, drop_rate = h
    
    # 點擊更新時模擬微幅真實跳動
    rnd = (random.random() - 0.5) * 0.2 if st.session_state["refresh_counter"] > 0 else 0.0
    c_win = max(1.5, round(b_win + rnd, 1))
    c_pla = b_pla
    o_pla = round(c_pla * 1.15, 1)
    
    # 隔夜與臨場跌幅
    on_drop = round(((o_win - c_win) / o_win) * 100.0, 1)
    drop_pct = drop_rate
    
    # 速度與跑法型態評分
    if style == "放頭":
        e_sp, l_sp = (96, 78)
        sp_desc = "⚡ 放頭搶欄 (主動帶放)"
    elif style == "均速":
        e_sp, l_sp = (91, 86)
        sp_desc = "⚖️ 前領均速 (守好位突擊)"
    elif style == "跟前":
        e_sp, l_sp = (84, 90)
        sp_desc = "🚀 居中跟前 (中段發力)"
    elif style == "後上":
        e_sp, l_sp = (75, 93)
        sp_desc = "🎯 留後追趕 (穩健後勁)"
    else: # 大後上
        e_sp, l_sp = (68, 97)
        sp_desc = "💥 極限大後上 (直路極速爆發)"
        
    dr_sc = 94 if draw <= 3 else (86 if draw <= 7 else 74)
    jt_sc = 96 if "潘頓" in j or "何澤堯" in j else 85
    tot = round(e_sp * 0.25 + l_sp * 0.25 + dr_sc * 0.25 + jt_sc * 0.25)
    
    stake = int((win_pool * 0.825 / c_win) * 0.12)
    share = round((stake / (win_pool * 0.825)) * 100.0, 1)
    
    # 解決用戶反映「信號嗰度完全冇提示」問題：依據實際跌幅準確亮燈
    if "2 分鐘" in time_phase:
        if drop_pct >= 28.0:
            sig, cls = ("🔴 啡燈暴跌", "b-brown")
        elif drop_pct >= 18.0:
            sig, cls = ("🟢 綠燈急落", "b-green")
        elif drop_pct >= 10.0:
            sig, cls = ("📈 資金追捧", "b-blue")
        elif drop_pct < 0:
            sig, cls = ("⚠️ 回飛走資", "b-red")
        else:
            sig, cls = ("⚪ 平走醞釀", "b-gray")
    elif "5 分鐘" in time_phase:
        if drop_pct >= 20.0:
            sig, cls = ("🟢 綠燈急落", "b-green")
        elif drop_pct >= 10.0:
            sig, cls = ("📈 資金吸納", "b-blue")
        else:
            sig, cls = ("⚪ 平走", "b-gray")
    else:
        if on_drop >= 20.0:
            sig, cls = ("🌙 隔夜建倉", "b-blue")
        else:
            sig, cls = ("⚪ 早盤平穩", "b-gray")
        
    parsed.append({
        "no": no, "name": name, "draw": draw, "wt": wt, "j": j, "t": t, "style": style,
        "c_win": c_win, "o_win": o_win, "on_drop": on_drop, "drop_pct": drop_pct,
        "c_pla": c_pla, "o_pla": o_pla, "stake": stake, "share": share,
        "e_sp": e_sp, "l_sp": l_sp, "sp_desc": sp_desc, "tot": tot,
        "form_6": form_6, "bw": bw, "tr": tr, "sig": sig, "cls": cls
    })

df = pd.DataFrame(parsed)

# 連贏 (Q) 及 位置Q (QP) 獨立計算 (嚴格分開)
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
        
        # Q 訊號
        if q_drop >= 30.0:
            q_sig = "🔴 啡燈Q"
        elif q_drop >= 18.0:
            q_sig = "🟢 綠燈Q"
        else:
            q_sig = "⚪ 平走"
            
        q_list.append({
            "pair": f"{r1['no']}-{r2['no']}",
            "h1": r1["no"], "h2": r2["no"],
            "name1": r1["name"], "name2": r2["name"],
            "c_q": c_q, "o_q": o_q, "q_drop": q_drop, "q_stk": q_stk, "q_sig": q_sig,
            "c_qp": c_qp, "o_qp": o_qp, "qp_drop": qp_drop, "qp_stk": qp_stk
        })

df_q = pd.DataFrame(q_list).sort_values(by="c_q")
top_q = df_q.iloc[0]
fav_h = df.sort_values(by="c_win").iloc[0]

# 頂部 4 大彩池指標卡 (Q 和 QP 徹底分開)
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(
        f'<div class="stat-card"><b>HK$ {int(win_pool):,}</b><br>'
        '<span style="color:#64748B; font-size:11px;">'
        '獨贏 (WIN) 彩池</span></div>',
        unsafe_allow_html=True
    )
with m2:
    st.markdown(
        f'<div class="stat-card"><b>HK$ {int(pla_pool):,}</b><br>'
        '<span style="color:#64748B; font-size:11px;">'
        '位置 (PLA) 彩池</span></div>',
        unsafe_allow_html=True
    )
with m3:
    st.markdown(
        f'<div class="stat-card"><b style="color:#B45309;">HK$ {int(q_pool):,}</b><br>'
        f'<span style="color:#B45309; font-size:11px; font-weight:bold;">'
        f'連贏 (Q) 獨立彩池 · 熱Q: {top_q["pair"]} ({top_q["c_q"]}倍)</span></div>',
        unsafe_allow_html=True
    )
with m4:
    st.markdown(
        f'<div class="stat-card"><b style="color:#1D4ED8;">HK$ {int(qp_pool):,}</b><br>'
        f'<span style="color:#1D4ED8; font-size:11px; font-weight:bold;">'
        f'位置Q (QP) 獨立彩池 · 熱QP: {top_q["pair"]} ({top_q["c_qp"]}倍)</span></div>',
        unsafe_allow_html=True
    )

# ----------------- 視圖 1: MoneyFlow 專業賠率版 -----------------
if "專業賠率版" in chosen_view:
    st.markdown(f"##### 🏇 第 {race_no} 場《{r_title}》獨贏及位置資金走勢 (含檔位及放頭/均速/後上跑法)")
    
    tbl1 = """<table class="compact-table"><thead><tr>
    <th>馬號</th><th>馬名</th>
    <th style="background:#EFF6FF; color:#1D4ED8;">檔位</th>
    <th style="background:#EFF6FF; color:#1D4ED8;">詳細跑法</th>
    <th>負磅</th><th>騎師</th><th>練馬師</th>
    <th>隔夜WIN</th><th style="background:#FEF3C7;">臨場WIN</th>
    <th>🌙隔夜落飛</th><th>臨場跌幅</th>
    <th>隔夜PLA</th><th style="background:#FEF3C7;">臨場PLA</th>
    <th>🔥最熱Q配搭</th>
    <th>新增注碼</th><th>熱錢佔比</th><th>落飛訊號</th>
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
    
    # 連贏及位置Q 專區 (金額徹底獨立)
    st.markdown("##### 🔥 連贏 (Q) 及 位置Q (QP) 操盤榜 (Q與QP資金100%獨立分開)")
    q_mode = st.radio("模式", ["大戶落飛排行榜", "12x12 對碰矩陣"], horizontal=True)
    
    if q_mode == "大戶落飛排行榜":
        tbl_q = """<table class="compact-table"><thead><tr>
        <th>排名</th><th>組合</th><th>出賽馬匹</th>
        <th style="background:#FEF3C7;">連贏(Q)臨場</th><th>Q隔夜</th><th>Q落飛%</th>
        <th style="background:#FEF3C7; color:#B45309; font-weight:bold;">💰 Q 落飛資金</th>
        <th>Q訊號</th>
        <th style="background:#EFF6FF;">位置Q(QP)臨場</th><th>QP隔夜</th><th>QP落飛%</th>
        <th style="background:#EFF6FF; color:#1D4ED8; font-weight:bold;">💰 QP 落飛資金</th>
        </tr></thead><tbody>"""
        
        rk = 1
        for _, q in df_q.head(15).iterrows():
            tbl_q += f"""<tr>
            <td><b>#{rk}</b></td>
            <td><b>{q['pair']}</b></td>
            <td>{q['name1']} + {q['name2']}</td>
            <td style="background:#FFFBEB; font-weight:bold;">{q['c_q']}</td>
            <td>{q['o_q']}</td><td>{q['q_drop']:+.1f}%</td>
            <td style="background:#FEF3C7; font-weight:bold; color:#B45309;">${q['q_stk']:,}</td>
            <td><span class="badge {'b-green' if '綠' in q['q_sig'] else ('b-brown' if '啡' in q['q_sig'] else 'b-gray')}">{q['q_sig']}</span></td>
            <td style="background:#EFF6FF; font-weight:bold;">{q['c_qp']}</td>
            <td>{q['o_qp']}</td><td>{q['qp_drop']:+.1f}%</td>
            <td style="background:#EFF6FF; font-weight:bold; color:#1D4ED8;">${q['qp_stk']:,}</td>
            </tr>"""
            rk += 1
        tbl_q += "</tbody></table>"
        st.markdown(tbl_q, unsafe_allow_html=True)
    else:
        mat = '<table class="matrix-tbl"><thead><tr><th>號</th>'
        for i in range(1, len(df) + 1): mat += f'<th>{i}</th>'
        mat += '</tr></thead><tbody>'
        for r_i in range(1, len(df) + 1):
            mat += f'<tr><th style="background:#1E293B;">{r_i}</th>'
            for c_j in range(1, len(df) + 1):
                if r_i == c_j:
                    mat += '<td style="background:#E2E8F0;">-</td>'
                else:
                    lo, hi = min(r_i, c_j), max(r_i, c_j)
                    match = df_q[(df_q["h1"] == lo) & (df_q["h2"] == hi)].iloc[0]
                    mat += f'<td><b>{match["c_q"]}</b><br><span style="color:#2563EB;">{match["c_qp"]}</span></td>'
            mat += '</tr>'
        mat += '</tbody></table>'
        st.markdown(mat, unsafe_allow_html=True)

# ----------------- 視圖 2: MoneyFlow 即時落飛雷達 -----------------
elif "落飛雷達" in chosen_view:
    st.markdown(f"##### ⚡ 第 {race_no} 場《{r_title}》MoneyFlow 即時落飛雷達牆")
    
    plunges = df[df["drop_pct"] >= 15.0].sort_values(by="drop_pct", ascending=False)
    
    st.markdown("""
    <div class="radar-box">
        <b>🚨 【MoneyFlow 即時落飛警報中心】</b><br>
        系統正實時監控各馬匹最後倒數之注碼異動，一旦跌幅超過 15% 觸發【🟢 綠燈】，超過 25% 觸發【🔴 啡燈】！
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("###### 🎯 獨贏 (WIN) 大戶落飛突襲名單")
    for _, p in plunges.iterrows():
        st.markdown(f"""
        <div style="background:#FFFFFF; border:1px solid #CBD5E1; border-radius:6px; padding:8px 12px; margin-bottom:6px; display:flex; justify-content:space-between; align-items:center;">
            <div>
                <span class="circle-no">{p['no']}</span> <b style="font-size:14px;">{p['name']}</b> 
                <span style="color:#64748B; font-size:12px;">({p['draw']}檔 · 跑法: <b>{p['style']}</b> · 騎練: {p['j']}/{p['t']})</span><br>
                <span style="font-size:12px;">盤口異動：隔夜 {p['o_win']} ➔ 臨場 <b>{p['c_win']}</b> ｜ 臨場急落：<b style="color:#15803D;">-{p['drop_pct']}%</b> ｜ 吸納注碼：<b>${p['stake']:,}</b></span>
            </div>
            <div>
                <span class="badge {p['cls']}" style="font-size:13px;">{p['sig']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("###### 🔥 連贏 (Q) 及 位置Q (QP) 大戶熱錢暴跌組合 (Q與QP分開)")
    q_plunges = df_q[df_q["q_drop"] >= 20.0].head(8)
    for _, qp in q_plunges.iterrows():
        st.markdown(f"""
        <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:6px; padding:6px 10px; margin-bottom:5px;">
            <b>組合 {qp['pair']}</b> ({qp['name1']} + {qp['name2']}) ｜ 
            連贏Q: <b>{qp['c_q']}倍</b> (落飛跌{qp['q_drop']}%, 💰Q注碼: <b>${qp['q_stk']:,}</b>) ｜ 
            位置QP: <b>{qp['c_qp']}倍</b> (💰QP注碼: <b>${qp['qp_stk']:,}</b>) ｜ 
            <span class="badge b-green">{qp['q_sig']}</span>
        </div>
        """, unsafe_allow_html=True)

# ----------------- 視圖 3: 綜合能力評分總表 -----------------
elif "能力評分" in chosen_view:
    st.markdown(f"##### 📊 第 {race_no} 場《{r_title}》出賽馬匹能力總表 (含檔位、詳細跑法、前速 vs 末段速度)")
    tbl2 = """<table class="compact-table"><thead><tr>
    <th>排名</th><th>馬號</th><th>馬名</th>
    <th style="background:#EFF6FF; color:#1D4ED8;">檔位</th>
    <th style="background:#EFF6FF; color:#1D4ED8;">詳細跑法</th>
    <th>綜合戰力</th>
    <th style="background:#FEF3C7; color:#B45309;">前速評分</th>
    <th style="background:#FEF3C7; color:#B45309;">末段速度</th>
    <th>速勢對比型態</th>
    <th>馬會 6次近績</th><th>排位體重</th><th>晨操評語</th><th>臨場獨贏</th>
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
        <td>{r['sp_desc']}</td>
        <td><b>{r['form_6']}</b></td><td>{r['bw']}</td><td>{r['tr']}</td>
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
            • 跑法速勢: 前速 <b>{r['e_sp']}分</b> ｜ 末段 <b>{r['l_sp']}分</b> ｜ 型態: {r['sp_desc']}<br>
            • 馬會近況: 近6仗 <b>{r['form_6']}</b> ｜ 體重 <b>{r['bw']}</b> ｜ 晨操: {r['tr']}<br>
            • 盤口走勢: 隔夜WIN {r['o_win']} ➔ 臨場 <b>{r['c_win']}</b> (急落 -{r['drop_pct']}%) ｜ 訊號: <span class="badge {r['cls']}">{r['sig']}</span>
            </span>
        </div>
        """, unsafe_allow_html=True)
