import streamlit as st
import pandas as pd
import math

st.set_page_config(page_title="HKJC 9月23日快活谷夜賽 · 官方排位全能盤", page_icon="🏇", layout="wide")

st.markdown("""
<style>
    .main { background-color: #F8FAFC; }
    .header-box { background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 14px 18px; margin-bottom: 14px; }
    .pace-box { background: #F0FDF4; border: 1px solid #BBF7D0; border-left: 5px solid #16A34A; border-radius: 8px; padding: 10px 14px; }
    .alert-box { background: #FEF2F2; border: 1px solid #FECACA; border-left: 5px solid #EF4444; border-radius: 8px; padding: 10px 14px; }
    .stat-card { background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 10px; text-align: center; }
    .horse-card { background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 10px; padding: 12px 16px; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

RACE_INFO = {
    1: ("南風讓賽", "1650米", 9800000),
    2: ("深水灣讓賽", "1200米", 11200000),
    3: ("黃竹坑讓賽", "1650米", 12500000),
    4: ("深水灣讓賽", "1200米", 11800000),
    5: ("香港鄉村俱樂部盃", "1650米", 13600000),
    6: ("香島讓賽", "1000米", 12100000),
    7: ("畢拿山讓賽", "1200米", 14200000),
    8: ("畢拿山讓賽", "1200米", 15800000),
    9: ("大坑讓賽", "1800米", 16500000)
}

HORSES = {
    1: [(1,"堅多福",3,135,"何澤堯","方嘉柏",5,"前領",3.8,2.6,"頂峰狀態"),
        (2,"一風雲",7,134,"金誠剛","丁冠豪",6,"後上",9.5,14.0,"平穩"),
        (3,"神駒馬靈",2,132,"霍宏聲","廖康銘",4,"領放",8.0,4.2,"大熟大勇"),
        (4,"紅磚戰士",1,129,"周俊樂","游達榮",5,"前領",7.0,5.5,"良好"),
        (5,"極速滿貫",9,130,"奧爾曼","黎昭昇",6,"居中",18.0,24.0,"平穩"),
        (6,"開心三多",5,128,"希威森","桂福特",5,"後上",8.5,6.8,"勇銳"),
        (7,"綫路達飛",8,126,"楊明綸","蘇偉賢",6,"居中",25.0,32.0,"平穩"),
        (8,"電訊驕陽",4,116,"袁幸堯","徐雨石",5,"領放",14.0,7.5,"受讓10磅"),
        (9,"至高心得",6,124,"班德禮","韋達",5,"居中",15.0,17.0,"平穩"),
        (10,"威威父子",11,120,"田泰安","巫偉傑",5,"後上",22.0,30.0,"平穩"),
        (11,"東方魅影",10,132,"潘頓","大衛希斯",4,"前領",4.5,3.1,"頂峰狀態")],
    2: [(1,"鑽飾璀璨",2,135,"潘頓","容天鵬",5,"前領",3.5,2.4,"勇銳"),
        (2,"連連歡呼",6,132,"何澤堯","告東尼",5,"後上",6.8,8.0,"平穩"),
        (3,"合夥奔馳",1,130,"布文","呂健威",4,"領放",4.2,2.8,"頂峰狀態"),
        (4,"耀寶",4,128,"霍宏聲","方嘉柏",4,"前領",9.0,11.0,"良好"),
        (5,"大力猴王",9,126,"巴度","伍鵬志",5,"後上",14.0,18.0,"平穩"),
        (6,"酷霸王",3,125,"田泰安","蔡約翰",4,"前領",7.5,5.2,"勇銳"),
        (7,"佳運發",8,123,"希威森","韋達",6,"居中",20.0,26.0,"平穩"),
        (8,"怡昌奇兵",5,121,"周俊樂","黎昭昇",5,"居中",15.0,12.0,"良好"),
        (9,"駿皇星",10,120,"班德禮","蘇偉賢",6,"後上",30.0,38.0,"老馬"),
        (10,"添開心",7,118,"鍾易禮","文家良",5,"領放",12.0,7.8,"受讓5磅"),
        (11,"宇宙動力",11,116,"艾兆禮","鄭俊偉",5,"後上",40.0,55.0,"平穩"),
        (12,"精彩勇士",12,115,"楊明綸","沈集成",7,"後上",50.0,65.0,"退化期")],
    3: [(1,"超超比",4,135,"周俊樂","沈集成",5,"後上",4.2,3.1,"勇銳"),
        (2,"友瑩仁",1,133,"潘頓","伍鵬志",4,"前領",2.8,2.0,"頂峰狀態"),
        (3,"喜蓮勇略",5,130,"布文","告東尼",4,"領放",6.5,4.6,"良好"),
        (4,"建測羣英",8,128,"何澤堯","大衛希斯",5,"居中",8.0,9.5,"良好"),
        (5,"飛躍精英",2,126,"巴度","蔡約翰",5,"前領",9.5,7.2,"良好"),
        (6,"浪漫老撾",10,125,"田泰安","巫偉傑",6,"後上",15.0,20.0,"平穩"),
        (7,"滿歡笑",6,124,"希威森","方嘉柏",5,"居中",14.0,14.0,"平穩"),
        (8,"都靈福星",7,122,"班德禮","葉楚航",5,"後上",22.0,28.0,"平穩"),
        (9,"浪漫戰神",11,121,"霍宏聲","賀賢",5,"後上",28.0,35.0,"平穩"),
        (10,"歡樂至寶",3,120,"艾兆禮","黎昭昇",5,"居中",12.0,8.8,"良好"),
        (11,"精彩非凡",9,118,"鍾易禮","容天鵬",6,"領放",25.0,33.0,"受讓5磅"),
        (12,"大千氣象",12,116,"楊明綸","姚本輝",6,"後上",45.0,60.0,"平穩")],
    4: [(1,"風中勁草",2,135,"潘頓","蔡約翰",5,"前領",3.0,2.2,"頂峰狀態"),
        (2,"常常有餘",5,132,"布文","沈集成",4,"領放",5.5,3.6,"勇銳"),
        (3,"競駿輝煌",1,130,"何澤堯","呂健威",4,"前領",6.0,4.5,"1檔極利")],
    5: [(1, "獨步天下", 3, 135, "何澤堯", "方嘉柏", 5, "前領", 3.6, 2.5, "頂峰狀態"),
        (2, "綠族威", 1, 133, "潘頓", "伍鵬志", 4, "領放", 3.2, 2.2, "大熟大勇")
    ],
    6: [
        (1, "萬事快", 2, 135, "何澤堯", "告東尼", 5, "領放", 3.5, 2.3, "頂峰放頭"),
        (2, "謙謙君子", 4, 132, "布文", "廖康銘", 4, "前領", 5.0, 3.6, "良好")
    ],
    7: [(1,"正極",3,135,"潘頓","大衛希斯",4,"前領",3.0,2.0,"頂峰狀態"),
        (2,"首飾悟空",7,133,"布文","蔡約翰",5,"後上",8.5,6.0,"狀態復甦"),
        (3,"競駿皇者",2,130,"何澤堯","方嘉柏",4,"領放",6.0,4.0,"2檔利放")],
    8: [(1,"繼往開來",2,135,"潘頓","伍鵬志",4,"前領",2.5,1.8,"頂峰狀態"),
        (2,"驕陽雄心",4,131,"何澤堯","呂健威",4,"前領",4.5,3.2,"大熟大勇"),
        (3,"喵喵怪",1,116,"袁幸堯","徐雨石",4,"領放",8.0,4.8,"受讓10磅")],
    9: [(1,"嘉應傳承",4,135,"布文","告東尼",5,"前領",3.5,2.4,"落班秤先"),
        (2,"紫荊傳令",2,132,"潘頓","沈集成",4,"居中",4.2,3.0,"初跑谷草"),
        (3,"豐辰",5,130,"何澤堯","蔡約翰",5,"後上",6.0,4.5,"演出穩定")]
}

st.markdown("""
<div class="header-box">
    <div style="font-size: 20px; font-weight: 800; color: #0F172A;">🏇 2026年9月23日 快活谷夜賽 · 官方排位全能盤</div>
    <div style="font-size: 13px; color: #64748B; margin-top: 3px;">跑馬地草地 "C" 賽道 · 香港賽馬會官方全晚9場獨立排位 · 雲端全天候在線</div>
</div>
""", unsafe_allow_html=True)

c_race, c_bias = st.columns(2)
with c_race:
    race_options = [f"第 {i} 場 ({RACE_INFO[i][0]} {RACE_INFO[i]})" for i in range(1, 10)]
    sel_race = st.selectbox("🎯 選擇場次 (全晚共9場)", race_options, index=0)
    race_no = race_options.index(sel_race) + 1

with c_bias:
    bias = st.selectbox("🏟️ 當日場地跑道偏差", ["利快放貼欄 (快活谷C欄典型偏差)", "均勻中立 (各跑法平均)", "利中外疊後上 (前快後追有利)"], index=0)

r_name, r_dist, curr_pool = RACE_INFO.get(race_no, RACE_INFO)
prev_pool = curr_pool * 0.85
raw_list = HORSES.get(race_no, HORSES)

leads = [h for h in raw_list if h[7] == "領放"]
fwds = [h for h in raw_list if h[7] == "前領"]
mids = [h for h in raw_list if h[7] == "居中"]
backs = [h for h in raw_list if h[7] == "後上"]

pace_txt = "快步速 🔥 (多馬搶欄互燒)" if (len(leads) >= 3 or (len(leads) >= 2 and len(fwds) >= 2)) else ("慢步速 ⏳ (單騎慢放利前領)" if len(leads) <= 1 else "標準均速 ⚖️")

rows = []
for h in raw_list:
    no, name, draw, wt, j, t, age, style, o_odds, c_odds, cond = h
    drop_pct = round(((o_odds - c_odds) / o_odds * 100), 1) if o_odds > 0 else 0
    p_odds = round(c_odds * 1.15, 1) if drop_pct > 0 else round(c_odds * 0.95, 1)
    
    prev_s = (prev_pool * 0.825 / p_odds) if p_odds > 0 else 0
    curr_s = (curr_pool * 0.825 / c_odds) if c_odds > 0 else 0
    delta_s = max(0, curr_s - prev_s)
    
    sp_score = 92 if ("頂峰" in cond or drop_pct > 20) else (85 if drop_pct > 0 else 75)
    ab_score = round(sp_score * 0.45 + 85 * 0.35 + 80 * 0.20)
    
    rows.append({
        "馬號": no, "馬名": name, "檔位": f"{draw}檔", "負磅": f"{wt}磅",
        "騎師": j, "練馬師": t, "跑法": style, "年齡": f"{age}歲", "狀態": cond,
        "隔夜賠率": o_odds, "即時獨贏": c_odds, "跌幅": f"{drop_pct:+.1f}%",
        "delta_s": delta_s, "能力分": ab_score, "速度分": sp_score
    })

df = pd.DataFrame(rows)
avg_delta = df["delta_s"].mean() if len(df) > 0 else 1
df["倍數"] = (df["delta_s"] / avg_delta).round(1)
df["新增注碼"] = df["delta_s"].apply(lambda x: f"${int(x):,}")

def get_sig(r):
    if r["倍數"] >= 3.5: return "🔥 【雙熱錢爆發】谷草極限穩膽"
    elif r["倍數"] >= 2.5: return "🚨 【大戶大單重注】急掃落飛"
    elif r["倍數"] >= 1.5 and "-" in r["跌幅"]: return "📈 【熱錢持續進駐】資金追捧"
    elif r["即時獨贏"] > r["隔夜賠率"] * 1.2: return "⚠️ 【熱錢撤退】回飛冷淡"
    return "⚪ 【散戶走勢】平穩正常"

df["訊號"] = df.apply(get_sig, axis=1)

col1, col2 = st.columns(2)
with col1:
    st.markdown(f"""
    <div class="pace-box">
        <div style="font-weight:700; color:#15803D;">🚦 【第 {race_no} 場 {r_name} {r_dist}】步速推演：<b>{pace_txt}</b></div>
        <div style="font-size:13px; color:#166534; margin-top:3px;">領放 {len(leads)} 匹 · 前領 {len(fwds)} 匹 · 居中 {len(mids)} 匹 · 後上 {len(backs)} 匹</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    hots = df[df["訊號"].str.contains("雙熱錢|大單")]
    hot_txt = " · ".join([f"{r['馬號']}號「{r['馬名']}」({r['倍數']}x)" for _, r in hots.iterrows()]) if len(hots) > 0 else "暫無異常大額異動"
    st.markdown(f"""
    <div class="alert-box">
        <div style="font-weight:700; color:#991B1B;">🚨 【第 {race_no} 場】MoneyFlow 熱錢焦點</div>
        <div style="font-size:13px; color:#7F1D1D; margin-top:3px;">{hot_txt}</div>
    </div>
    """, unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)
with m1: st.markdown(f'<div class="stat-card"><div style="font-size:18px; font-weight:800;">HK$ {curr_pool:,}</div><div style="font-size:12px; color:#64748B;">即時獨贏彩池</div></div>', unsafe_allow_html=True)
with m2: st.markdown(f'<div class="stat-card"><div style="font-size:18px; font-weight:800;">HK$ {int(curr_pool-prev_pool):,}</div><div style="font-size:12px; color:#64748B;">近段資金增量</div></div>', unsafe_allow_html=True)
with m3: st.markdown(f'<div class="stat-card"><div style="font-size:18px; font-weight:800;">HK$ {int(avg_delta):,}</div><div style="font-size:12px; color:#64748B;">全場平均注碼</div></div>', unsafe_allow_html=True)
with m4: st.markdown(f'<div class="stat-card"><div style="font-size:18px; font-weight:800; color:#2563EB;">{df.iloc[0]["馬名"]}</div><div style="font-size:12px; color:#64748B;">綜合能力第 1 名</div></div>', unsafe_allow_html=True)

t1, t2, t3 = st.tabs(["🔥 【MoneyFlow 熱錢流向表】", "📊 【能力評分總表】", "📋 【馬匹專屬體檢卡】"])

with t1:
    st.subheader(f"🔥 第 {race_no} 場 {r_name} 熱錢流向大盤 (照熱錢強度排序)")
    mf_df = df.sort_values(by="delta_s", ascending=False)[["馬號","馬名","檔位","騎師","練馬師","隔夜賠率","即時獨贏","跌幅","新增注碼","倍數","訊號"]].copy()
    mf_df.rename(columns={"倍數": "熱錢倍數"}, inplace=True)
    st.dataframe(mf_df, use_container_width=True, hide_index=True)

with t2:
    st.subheader(f"📊 第 {race_no} 場出賽馬匹能力評分表 (照能力排名排序)")
    ab_df = df.sort_values(by="能力分", ascending=False)[["能力分","馬號","馬名","速度分","檔位","負磅","騎師","練馬師","狀態","即時獨贏"]].copy()
    st.dataframe(ab_df, use_container_width=True, hide_index=True)

with t3:
    st.subheader(f"📋 第 {race_no} 場出賽馬匹專屬體檢卡")
    for _, r in df.iterrows():
        is_hot = "雙熱錢" in r["訊號"] or "大單" in r["訊號"]
        b_color = "#EF4444" if is_hot else "#E2E8F0"
        st.markdown(f"""
        <div class="horse-card" style="border: 2px solid {b_color};">
            <div style="display:flex; justify-content:space-between;">
                <div style="font-size:17px; font-weight:800;">🐴 {r['馬號']} 號 【{r['馬名']}】 <span style="font-size:13px; font-weight:normal; color:#64748B;">({r['年齡']} · {r['跑法']} · {r['檔位']} · {r['負磅']})</span></div>
                <div style="background:#2563EB; color:white; padding:3px 10px; border-radius:12px; font-weight:700; font-size:13px;">能力：{r['能力分']}分</div>
            </div>
            <div style="margin-top:8px; font-size:13px; color:#334155; line-height:1.6;">
                • 速度分：<b>{r['速度分']}分</b> ｜ 騎師：<b>{r['騎師']}</b> ｜ 練馬師：<b>{r['練馬師']}</b> ｜ 狀態：<b>{r['狀態']}</b><br>
                • 賠率：隔夜 {r['隔夜賠率']} ➔ 即時 <b>{r['即時獨贏']}</b> (跌 {r['跌幅']}) ｜ 新增注碼：<b>{r['新增注碼']} ({r['倍數']}x)</b> ｜ <span style="font-weight:700; color:{'#DC2626' if is_hot else '#2563EB'};">{r['訊號']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
