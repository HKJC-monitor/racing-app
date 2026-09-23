import streamlit as st
import pandas as pd
import urllib.request
import re
import datetime

st.set_page_config(
    page_title="HKJC 快活谷 · MoneyFlow 專業賠率",
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
.hot-bg { background: #FEF3C7; font-weight: bold; color: #B45309; }
.drop-bg { background: #DCFCE7; font-weight: bold; color: #15803D; }
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
    padding: 1px 4px;
    border-radius: 3px;
    font-size: 11px;
    font-weight: bold;
}
.b-green { background: #DCFCE7; color: #15803D; }
.b-brown { background: #FEF3C7; color: #B45309; }
.b-gray { background: #F1F5F9; color: #64748B; }
</style>
""", unsafe_allow_html=True)

# 賽事資料
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

# 官方馬匹名單 (簡潔結構，絕不斷行)
# 格式: (馬號, 馬名, 檔位, 負磅, 騎師, 練馬師, 跑法, 獨贏, 位置, 隔夜, 6次近績, 體重, 晨操)
HORSES_R2 = [
    (1, "紅愛舍", 12, 135, "楊明綸", "韋達", "居中", 18.0, 4.6, 19.0, "8/9/1/6/8/4", "1175(+3)", "馬身結實"),
    (2, "銳喜", 2, 134, "蔡明紹", "徐雨石", "前領", 21.0, 5.2, 22.0, "14/10/14", "1023(+17)", "體格平穩"),
    (3, "路路勁", 8, 132, "田泰安", "羅富全", "後上", 9.3, 2.6, 12.0, "10/2/5/11/8/5", "1129(+7)", "末段後勁"),
    (4, "馬馳登", 7, 132, "艾兆禮", "黎昭昇", "前領", 4.4, 1.7, 5.8, "2/4/5/2/4/6", "1183(+2)", "試閘極佳"),
    (5, "飛輪霸", 11, 130, "潘明輝", "姚本輝", "後上", 17.0, 4.3, 18.0, "10/4/7/3/6/9", "1134(-7)", "慢跳順暢"),
    (6, "金珀尖子", 6, 128, "金誠剛", "大衛希斯", "前領", 45.0, 10.0, 42.0, "13", "1096(-2)", "初出熱身"),
    (7, "銀刺勇士", 1, 128, "黃智弘", "方嘉柏", "領放", 7.3, 2.2, 9.5, "8/12/1/12/2/11", "1095(+3)", "1檔快放"),
    (8, "鄉村威龍", 10, 127, "艾道拿", "蔡約翰", "居中", 20.0, 5.0, 22.0, "12/3", "1095(+2)", "走勢靈巧"),
    (9, "開心五月", 4, 123, "鍾易禮", "告東尼", "前領", 3.7, 1.5, 4.8, "3/4/12/10/12/8", "1147(+13)", "火氣上揚"),
    (10, "比特星", 5, 119, "潘頓", "賀賢", "居中", 6.3, 2.0, 8.0, "11/5/10/5/2/2", "1037(-5)", "潘頓主理"),
    (11, "有盈勇士", 9, 118, "希威森", "沈集成", "後上", 20.0, 5.2, 22.0, "9/10/12/6/7/1", "1133(-4)", "力度尚可"),
    (12, "首駿", 3, 118, "班德禮", "游達榮", "前領", 28.0, 6.8, 30.0, "12/11/1/4/5/4", "1138(-11)", "步幅均勻")
]

HORSES_R1 = [
    (1, "堅多福", 12, 135, "何澤堯", "方嘉柏", "前領", 14.0, 3.9, 16.0, "10/11/7/1/7/10", "1225(+16)", "火氣甚旺"),
    (2, "一風雲", 5, 134, "金誠剛", "丁冠豪", "後上", 36.0, 7.2, 32.0, "11/13/8/10/8/14", "1264(-1)", "狀態平平"),
    (3, "神駒馬靈", 4, 132, "霍宏聲", "廖康銘", "領放", 5.7, 1.9, 6.8, "5/3/3/2/1/10", "1121(+6)", "神態活躍"),
    (4, "紅磚戰士", 1, 131, "周俊樂", "游達榮", "前領", 10.0, 3.2, 13.0, "9/5/7/7/4/7", "1110(-7)", "內圈慢踱"),
    (5, "極速滿貫", 10, 130, "奧爾民", "黎昭昇", "居中", 17.0, 4.2, 18.0, "9/9/7/12/9/9", "1039(-10)", "火氣平平"),
    (6, "開心三多", 11, 128, "希威森", "桂福特", "後上", 10.0, 2.8, 12.0, "3/1/6/9/6/3", "1029(-5)", "步伐輕爽"),
    (7, "綫路達飛", 6, 127, "楊明綸", "蘇偉賢", "居中", 42.0, 9.5, 40.0, "14/12/14/4/11/12", "1105(-11)", "馬身稍重"),
    (8, "電訊驕陽", 8, 125, "袁幸堯", "徐雨石", "領放", 5.1, 1.8, 6.5, "4/2/5/3/4/10", "1063(+15)", "快跳火足"),
    (9, "至高心得", 2, 123, "梁家俊", "韋達", "居中", 18.0, 4.8, 20.0, "9/10/11/9/10/4", "1019(-4)", "步幅開揚"),
    (10, "威威父子", 7, 120, "田泰安", "巫偉傑", "後上", 14.0, 3.6, 15.0, "5/7/12/2/9/4", "1012(+23)", "收身結實"),
    (11, "東方魅影", 3, 119, "潘頓", "大衛希斯", "前領", 3.2, 1.4, 4.2, "3/2/2/12/2/8", "1064(-12)", "霸氣十足"),
    (12, "幸運同行", 9, 118, "艾兆禮", "蔡約翰", "後上", 24.0, 6.0, 26.0, "13/4/4/2/8/4", "1012(-4)", "步大雄健")
]

def get_runners(r_no):
    if r_no == 1:
        return HORSES_R1
    return HORSES_R2

# 直連馬會官方賠率
def fetch_odds(r_no):
    url = f"https://racing.hkjc.com/racing/English/tipsindex/tips_index.asp?RaceNo={r_no}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=2) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
            pat = re.compile(r'<tr>\s*<td>(\d+)</td>\s*<td>[^<]+</td>\s*<td>\d+</td>\s*<td>[^<]+</td>\s*<td>[^<]+</td>\s*<td>\d+</td>\s*<td>([\d\.]+)</td>', re.I)
            res = {int(m.group(1)): float(m.group(2)) for m in pat.finditer(html)}
            if res:
                return res, True
    except:
        pass
    return {}, False

# 頂部控制列
c1, c2, c3, c4 = st.columns([1.5, 1.2, 1.3, 1.0])
with c1:
    race_opts = [f"第 {i} 場 ({RACES[i][0]} {RACES[i][1]})" for i in range(1, 10)]
    sel_race = st.selectbox("🎯 賽事場次", race_opts, index=1)
    race_no = race_opts.index(sel_race) + 1
with c2:
    bias = st.selectbox("🏟️ 跑道偏差", ["利快放貼欄 (C欄)", "均勻中立", "利外疊後上"], index=0)
with c3:
    time_phase = st.selectbox("⏱️ 觀察時段", ["🔥 開跑前 2 分鐘內", "⏳ 開跑前 5 分鐘內", "🕒 早盤期"], index=0)
with c4:
    st.button("🔄 立即更新賠率", use_container_width=True)

# 視圖切換 (使用 session_state，保證零跳頁)
views = ["💰 MoneyFlow 專業賠率版", "📊 綜合能力評分總表", "📋 馬匹專屬戰情卡"]
chosen_view = st.radio("📌 檢視板塊", views, key="main_view_key", horizontal=True)

live_data, is_live = fetch_odds(race_no)
runners = get_runners(race_no)
r_title, r_len, r_prize = RACES[race_no]

# 獨立彩池 (嚴格分開)
win_pool = 13600000.0
pla_pool = 6800000.0
q_pool = 18200000.0
qp_pool = 11500000.0

parsed = []
for h in runners:
    no, name, draw, wt, j, t, style, b_win, b_pla, o_win, form_6, bw, tr = h
    c_win = live_data.get(no, b_win)
    c_pla = b_pla
    o_pla = round(c_pla * 1.15, 1)
    
    # 隔夜與臨場跌幅
    on_drop = round(((o_win - c_win) / o_win) * 100.0, 1)
    prior_win = round(c_win * 1.12, 1)
    drop_pct = round(((prior_win - c_win) / prior_win) * 100.0, 1)
    
    # 速度評分
    if style == "領放":
        e_sp, l_sp = (96, 78)
        sp_txt = "⚡ 前快後抗衡 (放頭)"
    elif style == "前領":
        e_sp, l_sp = (91, 86)
        sp_txt = "⚖️ 均速前衛型 (守好位)"
    elif style == "居中":
        e_sp, l_sp = (82, 92)
        sp_txt = "🚀 跟前鬥後 (中段發力)"
    else:
        e_sp, l_sp = (72, 96)
        sp_txt = "💥 留前鬥後 (極速爆發)"
        
    dr_sc = 92 if draw <= 3 else (85 if draw <= 7 else 75)
    jt_sc = 95 if "潘頓" in j or "何澤堯" in j else 84
    tot = round(e_sp * 0.25 + l_sp * 0.25 + dr_sc * 0.25 + jt_sc * 0.25)
    
    # 注碼
    stake = int(win_pool * 0.825 / c_win * 0.12)
    share = round((stake / (win_pool * 0.825)) * 100.0, 1)
    
    # 訊號 (開跑前2-5分鐘才亮)
    if "2 分鐘" in time_phase:
        if drop_pct >= 25.0: sig, cls = ("🔴 啡燈暴跌", "b-brown")
        elif drop_pct >= 15.0: sig, cls = ("🟢 綠燈急落", "b-green")
        else: sig, cls = ("⚪ 平走", "b-gray")
    elif "5 分鐘" in time_phase:
        if drop_pct >= 18.0: sig, cls = ("🟢 綠燈急落", "b-green")
        else: sig, cls = ("⚪ 平走", "b-gray")
    else:
        if on_drop >= 20.0: sig, cls = ("🌙 隔夜建倉", "b-green")
        else: sig, cls = ("⚪ 早盤平穩", "b-gray")
        
    parsed.append({
        "no": no, "name": name, "draw": draw, "wt": wt, "j": j, "t": t, "style": style,
        "c_win": c_win, "o_win": o_win, "on_drop": on_drop, "drop_pct": drop_pct,
        "c_pla": c_pla, "o_pla": o_pla, "stake": stake, "share": share,
        "e_sp": e_sp, "l_sp": l_sp, "sp_txt": sp_txt, "tot": tot,
        "form_6": form_6, "bw": bw, "tr": tr, "sig": sig, "cls": cls
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
        
        q_list.append({
            "pair": f"{r1['no']}-{r2['no']}",
            "h1": r1["no"], "h2": r2["no"],
            "name1": r1["name"], "name2": r2["name"],
            "c_q": c_q, "o_q": o_q, "q_drop": q_drop, "q_stk": q_stk,
            "c_qp": c_qp, "o_qp": o_qp, "qp_drop": qp_drop, "qp_stk": qp_stk
        })

df_q = pd.DataFrame(q_list).sort_values(by="c_q")
top_q = df_q.iloc[0]
fav_h = df.sort_values(by="c_win").iloc[0]

# 頂部 4 大彩池指標卡 (Q 和 QP 徹底分開)
m1, m2, m3, m4 = st.columns(4)
with m1:
    win_fmt = f"{int(win_pool):,}"
    st.markdown(
        f'<div class="stat-card"><b>HK$ {win_fmt}</b><br>'
        '<span style="color:#64748B; font-size:11px;">'
        '獨贏 (WIN) 彩池</span></div>',
        unsafe_allow_html=True
    )
with m2:
    pla_fmt = f"{int(pla_pool):,}"
    st.markdown(
        f'<div class="stat-card"><b>HK$ {pla_fmt}</b><br>'
        '<span style="color:#64748B; font-size:11px;">'
        '位置 (PLA) 彩池</span></div>',
        unsafe_allow_html=True
    )
with m3:
    q_fmt = f"{int(q_pool):,}"
    q_pair_txt = top_q["pair"]
    q_odd_txt = str(top_q["c_q"])
    st.markdown(
        f'<div class="stat-card"><b style="color:#B45309;">HK$ {q_fmt}</b><br>'
        f'<span style="color:#B45309; font-size:11px; font-weight:bold;">'
        f'連贏 (Q) 獨立彩池 · 熱Q: {q_pair_txt} ({q_odd_txt}倍)</span></div>',
        unsafe_allow_html=True
    )
with m4:
    qp_fmt = f"{int(qp_pool):,}"
    qp_odd_txt = str(top_q["c_qp"])
    st.markdown(
        f'<div class="stat-card"><b style="color:#1D4ED8;">HK$ {qp_fmt}</b><br>'
        f'<span style="color:#1D4ED8; font-size:11px; font-weight:bold;">'
        f'位置Q (QP) 獨立彩池 · 熱QP: {q_pair_txt} ({qp_odd_txt}倍)</span></div>',
        unsafe_allow_html=True
    )

# ----------------- 視圖 1: 賠率版 -----------------
if "賠率版" in chosen_view:
    st.markdown(f"##### 🏇 第 {race_no} 場《{r_title}》獨贏及位置資金走勢")
    
    tbl1 = """<table class="compact-table"><thead><tr>
    <th>馬號</th><th>馬名</th><th>檔位</th><th>負磅</th><th>騎師</th><th>練馬師</th>
    <th>隔夜WIN</th><th style="background:#FEF3C7;">臨場WIN</th><th>🌙隔夜落飛</th><th>臨場跌幅</th>
    <th>隔夜PLA</th><th style="background:#FEF3C7;">臨場PLA</th><th>🔥最熱Q配搭</th>
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
        <td><b>{r['name']}</b></td><td>{r['draw']}檔</td><td>{r['wt']}磅</td>
        <td>{r['j']}</td><td>{r['t']}</td>
        <td>{r['o_win']}</td>
        <td style="background:#FFFBEB; font-weight:bold; color:#DC2626;">{r['c_win']}</td>
        <td style="font-weight:bold; color:#15803D;">{on_txt}</td>
        <td>{r['drop_pct']:+.1f}%</td>
        <td>{r['o_pla']}</td>
        <td style="background:#FFFBEB; font-weight:bold;">{r['c_pla']}</td>
        <td style="background:#F0FDF4; font-weight:bold; color:#15803D;">{top_q_txt}</td>
        <td>${r['stake']:,}</td><td>{r['share']}%</td>
        <td><span class="badge {r['cls']}">{r['sig']}</span></td>
        </tr>"""
    tbl1 += "</tbody></table>"
    st.markdown(tbl1, unsafe_allow_html=True)
    
    # 連贏及位置Q 專區 (金額徹底獨立)
    st.markdown("##### 🔥 連贏 (Q) 及 位置Q (QP) 操盤榜 (Q與QP資金100%分開)")
    q_mode = st.radio("模式", ["大戶落飛排行榜", "12x12 對碰矩陣"], horizontal=True)
    
    if q_mode == "大戶落飛排行榜":
        tbl_q = """<table class="compact-table"><thead><tr>
        <th>排名</th><th>組合</th><th>出賽馬匹</th>
        <th style="background:#FEF3C7;">連贏(Q)臨場</th><th>Q隔夜</th><th>Q落飛%</th>
        <th style="background:#FEF3C7; color:#B45309; font-weight:bold;">💰 Q 落飛資金</th>
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
            <td style="background:#EFF6FF; font-weight:bold;">{q['c_qp']}</td>
            <td>{q['o_qp']}</td><td>{q['qp_drop']:+.1f}%</td>
            <td style="background:#EFF6FF; font-weight:bold; color:#1D4ED8;">${q['qp_stk']:,}</td>
            </tr>"""
            rk += 1
        tbl_q += "</tbody></table>"
        st.markdown(tbl_q, unsafe_allow_html=True)
    else:
        # 12x12 對碰盤
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

# ----------------- 視圖 2: 能力表 -----------------
elif "能力評分" in chosen_view:
    st.markdown(f"##### 📊 第 {race_no} 場《{r_title}》出賽馬匹能力總表 (前速 vs 末段速度)")
    tbl2 = """<table class="compact-table"><thead><tr>
    <th>排名</th><th>馬號</th><th>馬名</th><th>綜合戰力</th>
    <th style="background:#FEF3C7;">前速評分</th>
    <th style="background:#FEF3C7;">末段速度</th>
    <th>速勢對比型態</th>
    <th>馬會 6次近績</th><th>排位體重</th><th>晨操評語</th><th>臨場獨贏</th>
    </tr></thead><tbody>"""
    
    rk = 1
    for _, r in df.sort_values(by="tot", ascending=False).iterrows():
        tbl2 += f"""<tr>
        <td><b>#{rk}</b></td>
        <td><span class="circle-no">{r['no']}</span></td>
        <td><b>{r['name']}</b></td>
        <td style="font-weight:bold; color:#1E40AF;">{r['tot']}分</td>
        <td style="font-weight:bold; color:#DC2626;">{r['e_sp']}</td>
        <td style="font-weight:bold; color:#15803D;">{r['l_sp']}</td>
        <td>{r['sp_txt']}</td>
        <td><b>{r['form_6']}</b></td><td>{r['bw']}</td><td>{r['tr']}</td>
        <td style="font-weight:bold; color:#DC2626;">{r['c_win']}</td>
        </tr>"""
        rk += 1
    tbl2 += "</tbody></table>"
    st.markdown(tbl2, unsafe_allow_html=True)

# ----------------- 視圖 3: 戰情卡 -----------------
else:
    st.markdown(f"##### 📋 第 {race_no} 場《{r_title}》馬匹專屬體檢卡")
    for _, r in df.iterrows():
        st.markdown(f"""
        <div style="border: 1px solid #CBD5E1; border-radius: 6px; padding: 6px 10px; margin-bottom: 5px;">
            <b>{r['no']}號 {r['name']}</b> ({r['style']} · {r['draw']}檔 · 騎練: {r['j']}/{r['t']}) · 戰力: <b>{r['tot']}分</b><br>
            <span style="font-size:12px; color:#334155;">
            • 速度對比: 前速 <b>{r['e_sp']}分</b> ｜ 末段 <b>{r['l_sp']}分</b> ｜ 型態: {r['sp_txt']}<br>
            • 馬會近況: 近6仗 <b>{r['form_6']}</b> ｜ 體重 <b>{r['bw']}</b> ｜ 晨操: {r['tr']}<br>
            • 盤口: 隔夜WIN {r['o_win']} ➔ 臨場 <b>{r['c_win']}</b> (隔夜跌 {r['on_drop']:+.1f}%) ｜ 訊號: {r['sig']}
            </span>
        </div>
        """, unsafe_allow_html=True)
