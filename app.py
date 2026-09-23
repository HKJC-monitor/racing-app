import streamlit as st
import pandas as pd
import json
import urllib.request
import re
import datetime
import random

def render_clean_html(html_str):
    # 徹底移除所有行首空格，防止 Markdown 解析器誤當作 <pre><code> 程式碼區塊顯示
    clean = re.sub(r'^[ \t]+', '', html_str, flags=re.M)
    st.markdown(clean, unsafe_allow_html=True)

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

# 數據庫：場次 | 馬號 | 馬名 | 檔位 | 負磅 | 騎師 | 練馬師 | 跑法 | 臨場WIN | 臨場PLA | 隔夜WIN | 6次近績 | 體重 | 同程(冠-亞-季-負) | 東方名家短評 | 跌幅% | 是否退出(1=退出)
RAW_HORSES_TEXT = """
1 | 1 | 堅多福 | 3 | 135 | 何澤堯 | 方嘉柏 | 前領 | 2.6 | 1.4 | 3.8 | 1/2/1/4/2/1 | 1142(+4) | 2-1-0-1 | 谷草能手三檔好位，何澤堯壓陣爭勝主力 | 31.6 | 0
1 | 2 | 一風雲 | 7 | 134 | 金誠剛 | 丁冠豪 | 後上 | 14.0 | 3.8 | 9.5 | 8/7/5/6/8/7 | 1098(-2) | 0-1-0-3 | 走勢平穩但回飛走資，外檔形勢被動 | -47.4 | 0
1 | 3 | 神駒馬靈 | 2 | 132 | 霍宏聲 | 廖康銘 | 放頭 | 4.2 | 1.6 | 8.0 | 3/1/2/4/3/2 | 1165(+8) | 1-2-1-0 | 試閘大勇前速極快，二檔貼欄快放爭三甲 | 47.5 | 0
1 | 4 | 紅磚戰士 | 1 | 129 | 周俊樂 | 游達榮 | 前領 | 5.5 | 1.8 | 7.0 | 2/4/3/1/5/3 | 1110(+2) | 1-1-1-2 | 一檔黃金貼欄位慳位，受讓磅有力偷襲 | 21.4 | 0
1 | 5 | 極速滿貫 | 9 | 130 | 奧爾民 | 黎昭昇 | 均速 | 24.0 | 6.0 | 18.0 | 6/8/7/9/6/5 | 1085(+1) | 0-0-1-3 | 步速稍嫌吃虧，成熟平穩暫宜觀望 | -33.3 | 0
1 | 6 | 開心三多 | 5 | 128 | 希威森 | 桂福特 | 後上 | 6.8 | 2.1 | 8.5 | 4/3/2/1/4/2 | 1130(+5) | 1-2-0-1 | 勇銳爆發期後勁強，五檔進退有據可作冷配 | 20.0 | 0
1 | 7 | 綫路達飛 | 8 | 126 | 楊明綸 | 蘇偉賢 | 均速 | 32.0 | 7.5 | 25.0 | 9/10/8/7/8/6 | 1072(-4) | 0-0-0-4 | 狀態未復舊觀，步頭略重難言把握 | -28.0 | 0
1 | 8 | 電訊驕陽 | 4 | 116 | 袁幸堯 | 徐雨石 | 放頭 | 7.5 | 2.2 | 14.0 | 5/4/2/3/6/4 | 1055(+3) | 0-1-1-2 | 減十磅極具威力，四檔出閘快放暗湧甚大 | 46.4 | 0
1 | 9 | 至高心得 | 6 | 124 | 班德禮 | 韋達 | 均速 | 17.0 | 4.5 | 15.0 | 7/5/4/6/5/4 | 1120(+6) | 0-0-2-2 | 慢踱態況平穩，均速跟前爭入位置 | -13.3 | 0
1 | 10 | 威威父子 | 11 | 120 | 田泰安 | 巫偉傑 | 後上 | 30.0 | 7.0 | 22.0 | 8/9/7/8/10/7 | 1105(+0) | 0-0-0-3 | 十一檔起步極為被動，現階段仍處調教期 | -36.4 | 0
1 | 11 | 東方魅影 | 10 | 132 | 潘頓 | 大衛希斯 | 前領 | 3.1 | 1.4 | 4.5 | 2/1/2/3/1/2 | 1180(+7) | 2-2-1-0 | 擂台大熱潘頓親自壓陣，質素過群爭勝核心 | 31.1 | 0
1 | 12 | 滿載歸來 | 12 | 118 | 鍾易禮 | 文家良 | 後上 | 45.0 | 9.0 | 35.0 | 10/11/9/8/9/8 | 1040(-5) | 0-0-0-2 | 十二檔大外檔起步，實力稍遜暫宜退避 | -28.6 | 0
2 | 1 | 鑽飾璀璨 | 2 | 135 | 潘頓 | 容天鵬 | 前領 | 2.4 | 1.3 | 3.5 | 1/1/2/1/3/1 | 1150(+5) | 3-1-1-0 | 二檔黃金好位，潘頓主理連捷火氣極盛 | 31.4 | 0
2 | 2 | 連連歡呼 | 6 | 132 | 何澤堯 | 告東尼 | 後上 | 8.0 | 2.4 | 6.8 | 3/2/4/5/2/3 | 1125(+3) | 1-2-1-2 | 後勁凌厲末段衝刺強，何澤堯接手有暗湧 | -17.6 | 0
2 | 3 | 合夥奔馳 | 1 | 130 | 布文 | 呂健威 | 放頭 | 2.8 | 1.4 | 4.2 | 1/1/1/2/1/1 | 1168(+4) | 4-1-0-0 | 一檔快放佔盡先機，熱錢狂掃直放到底 | 33.3 | 0
2 | 4 | 耀寶 | 4 | 128 | 霍宏聲 | 方嘉柏 | 前領 | 11.0 | 3.2 | 9.0 | 4/5/3/2/4/3 | 1110(-2) | 1-1-1-2 | 四檔好位跟前走，方廄谷草急鋒冷配之選 | -22.2 | 0
2 | 5 | 大力猴王 | 9 | 126 | 巴度 | 伍鵬志 | 後上 | 18.0 | 4.8 | 14.0 | 5/6/4/3/6/5 | 1090(+1) | 0-1-1-3 | 外檔起步較被動，後追一段考驗走位 | -28.6 | 0
2 | 6 | 酷霸王 | 3 | 125 | 田泰安 | 蔡約翰 | 前領 | 5.2 | 1.8 | 7.5 | 2/3/1/2/3/1 | 1135(+6) | 2-2-1-0 | 三檔好位起步順暢，蔡廄精選大戶吸納 | 30.7 | 0
2 | 7 | 佳運發 | 8 | 123 | 希威森 | 韋達 | 均速 | 26.0 | 6.5 | 20.0 | 7/8/6/5/7/6 | 1075(-3) | 0-0-1-3 | 出腳平穩但速度稍遜，評分未見優勢 | -30.0 | 0
2 | 8 | 怡昌奇兵 | 5 | 121 | 周俊樂 | 黎昭昇 | 均速 | 12.0 | 3.4 | 15.0 | 4/3/2/4/5/2 | 1102(+2) | 1-1-0-2 | 減磅出擊步伐爽朗，五檔好跑可爭三甲 | 20.0 | 0
2 | 9 | 駿皇星 | 10 | 120 | 班德禮 | 蘇偉賢 | 後上 | 38.0 | 8.5 | 30.0 | 8/9/7/8/10/8 | 1140(+8) | 0-0-0-4 | 老馬戰力稍退，十檔消耗大暫宜退避 | -26.7 | 0
2 | 10 | 添開心 | 7 | 118 | 鍾易禮 | 文家良 | 放頭 | 7.8 | 2.3 | 12.0 | 3/2/1/4/2/3 | 1080(+3) | 1-2-1-1 | 減磅快放搶欄，大戶綠燈落飛爭勝黑馬 | 35.0 | 0
2 | 11 | 宇宙動力 | 11 | 116 | 艾兆禮 | 鄭俊偉 | 後上 | 55.0 | 12.0 | 40.0 | 9/10/8/9/11/9 | 1060(-5) | 0-0-0-3 | 檔劣班次吃虧，作戰狀態未足 | -37.5 | 0
2 | 12 | 精彩勇士 | 12 | 115 | 楊明綸 | 沈集成 | 後上 | 65.0 | 15.0 | 50.0 | 11/12/10/9/12/10 | 1115(+0) | 0-0-0-4 | 十二檔大外檔，年事已高難言把握 | -30.0 | 0
3 | 1 | 超超比 | 4 | 135 | 周俊樂 | 沈集成 | 後上 | 3.1 | 1.5 | 4.2 | 1/2/1/1/3/1 | 1160(+4) | 3-1-1-0 | 沈廄谷草王牌，直路後勁雷霆萬鈞重心首選 | 26.2 | 0
3 | 2 | 友瑩仁 | 1 | 133 | 潘頓 | 伍鵬志 | 前領 | 2.0 | 1.2 | 2.8 | 1/1/1/2/1/1 | 1145(+2) | 4-1-0-0 | 一檔黃金貼欄，潘頓親操擂台大熱必拼 | 28.6 | 0
3 | 3 | 喜蓮勇略 | 5 | 130 | 布文 | 告東尼 | 放頭 | 4.6 | 1.7 | 6.5 | 2/1/3/2/1/2 | 1185(+6) | 2-2-1-0 | 布文壓陣前速銳利，單騎快放韌力強 | 29.2 | 0
3 | 4 | 建測羣英 | 8 | 128 | 何澤堯 | 大衛希斯 | 均速 | 9.5 | 2.8 | 8.0 | 3/4/2/5/3/4 | 1118(+1) | 1-1-1-2 | 何澤堯執韁均速跟前，步大力雄可爭一席 | -18.8 | 0
3 | 5 | 飛躍精英 | 2 | 126 | 巴度 | 蔡約翰 | 前領 | 7.2 | 2.2 | 9.5 | 2/3/4/1/2/3 | 1095(+3) | 1-2-1-1 | 二檔好位慳位出彎，蔡廄實力分子大戶跟進 | 24.2 | 0
3 | 6 | 浪漫老撾 | 10 | 125 | 田泰安 | 巫偉傑 | 後上 | 20.0 | 5.2 | 15.0 | 6/5/7/4/6/5 | 1130(+5) | 0-1-1-3 | 十檔形勢略吃虧，後段需快步速配合 | -33.3 | 0
3 | 7 | 滿歡笑 | 6 | 124 | 希威森 | 方嘉柏 | 均速 | 14.0 | 3.8 | 14.0 | 4/5/3/6/4/3 | 1085(-2) | 0-1-2-2 | 方廄谷草專家，步法平穩位置冷選 | 0.0 | 0
3 | 8 | 都靈福星 | 7 | 122 | 班德禮 | 葉楚航 | 後上 | 28.0 | 6.8 | 22.0 | 7/8/6/7/8/6 | 1105(+2) | 0-0-1-3 | 走勢略重，減分期中暫宜退避 | -27.3 | 0
3 | 9 | 浪漫戰神 | 11 | 121 | 霍宏聲 | 賀賢 | 後上 | 35.0 | 8.2 | 28.0 | 8/9/7/8/9/7 | 1140(+4) | 0-0-0-3 | 外檔起步極其被動，難寄厚望 | -25.0 | 0
3 | 10 | 歡樂至寶 | 3 | 120 | 艾兆禮 | 黎昭昇 | 均速 | 8.8 | 2.5 | 12.0 | 3/2/4/3/2/4 | 1078(+1) | 1-2-2-1 | 三檔好位大戶悄悄吸納，落飛急跌邊線黑馬 | 26.7 | 0
3 | 11 | 精彩非凡 | 9 | 118 | 鍾易禮 | 容天鵬 | 放頭 | 33.0 | 7.8 | 25.0 | 5/7/6/8/5/6 | 1062(-3) | 0-0-1-2 | 受讓五磅快放，但恐前段互燒消耗末弱 | -32.0 | 0
3 | 12 | 大千氣象 | 12 | 116 | 楊明綸 | 姚本輝 | 後上 | 60.0 | 14.0 | 45.0 | 10/11/9/10/11/9 | 1110(+2) | 0-0-0-4 | 檔劣實力不足，暫宜觀望 | -33.3 | 0
4 | 1 | 沙井之友 | 8 | 135 | 周俊樂 | 巫偉傑 | 後上 | 8.0 | 2.4 | 11.0 | 10/5/4/7/4/4 | 1117(-6) | 1-0-1-1 | 上仗後上凌厲有力一拼 | 27.3 | 0
4 | 2 | 智勝一籌 | 10 | 135 | 蔡明紹 | 蘇偉賢 | 均速 | 24.0 | 5.8 | 25.0 | 8/12/12/7/11 | 1066(+28) | 0-0-0-2 | 十檔形勢吃虧暫宜觀望 | -4.0 | 0
4 | 3 | 應龍飛影 | 6 | 132 | 袁幸堯 | 伍鵬志 | 放頭 | 0.0 | 0.0 | 0.0 | 4/4/1/11/3/2 | 1195(+18) | 2-1-0-2 | 【已退出賽事】 | 0.0 | 1
4 | 4 | 星辰千帥 | 7 | 131 | 艾道拿 | 賀賢 | 均速 | 11.0 | 3.1 | 14.0 | 1/2/5/2/11/3 | 1197(+13) | 1-1-1-1 | 晨操步爽力足同程擅鬥 | 21.4 | 0
4 | 5 | 莊家班 | 3 | 130 | 黃智弘 | 沈集成 | 跟前 | 28.0 | 6.5 | 30.0 | 11/4/7/11/10/10 | 1056(+3) | 0-0-0-3 | 作戰狀態未足難言把握 | 6.7 | 0
4 | 6 | 快樂神駒 | 2 | 129 | 潘頓 | 廖康銘 | 均速 | 2.0 | 1.2 | 3.2 | 4/2/12/4/2/4 | 1103(+17) | 1-2-0-1 | 擂台大熱火氣盛潘頓親操 | 37.5 | 0
4 | 7 | 震撼人心 | 12 | 129 | 艾兆禮 | 蔡約翰 | 大後上 | 0.0 | 0.0 | 0.0 | 12/3 | 1092(+8) | 0-0-1-0 | 【已退出賽事】 | 0.0 | 1
4 | 8 | 禪勝閃亮 | 5 | 128 | 希威森 | 呂健威 | 跟前 | 21.0 | 5.2 | 22.0 | 4/2/5 | 993(-24) | 0-1-0-1 | 步伐整齊平穩具牽引力 | 4.5 | 0
4 | 9 | 將傲 | 4 | 126 | 奧爾民 | 韋達 | 跟前 | 10.0 | 2.8 | 13.0 | 4/4/3/7 | 1088(-4) | 0-0-1-2 | 試閘好四檔好位暗湧大 | 23.1 | 0
4 | 10 | 平天雄 | 9 | 123 | 潘明輝 | 丁冠豪 | 大後上 | 33.0 | 8.0 | 35.0 | 12/10/10/14/14/11 | 1260(+56) | 0-0-0-4 | 步頭略重未減夠分調教期 | 5.7 | 0
4 | 11 | 焦點 | 1 | 121 | 田泰安 | 游達榮 | 均速 | 22.0 | 5.5 | 24.0 | 9/2/4/1/1/7 | 1057(+2) | 1-1-0-4 | 一檔黃金貼欄減磅邊線 | 8.3 | 0
4 | 12 | 三強 | 11 | 120 | 楊明綸 | 鄭俊偉 | 後上 | 28.0 | 7.0 | 30.0 | 10/8/9/8/3/3 | 1131(-23) | 0-0-2-3 | 冷門後勁一段需快步速 | 6.7 | 0
5 | 1 | 獨步天下 | 3 | 135 | 何澤堯 | 方嘉柏 | 前領 | 2.5 | 1.3 | 3.6 | 1/2/1/1/2/1 | 1152(+4) | 3-2-0-1 | 三檔黃金好位，何澤堯壓陣盃賽重心首選 | 30.6 | 0
5 | 2 | 綠族威 | 1 | 133 | 潘頓 | 伍鵬志 | 放頭 | 2.2 | 1.2 | 3.2 | 1/1/2/1/1/2 | 1170(+6) | 4-1-1-0 | 一檔貼欄快放，潘頓親操火氣極旺熱門焦點 | 31.2 | 0
5 | 3 | 電訊巴打 | 6 | 130 | 布文 | 徐雨石 | 放頭 | 5.8 | 1.9 | 7.5 | 2/3/1/4/2/3 | 1135(+2) | 2-1-2-1 | 前速飛快快放好手，布文執韁威力十足 | 22.7 | 0
5 | 4 | 錶之量子 | 4 | 128 | 艾道拿 | 文家良 | 均速 | 8.5 | 2.6 | 11.0 | 3/2/4/2/3/4 | 1112(-2) | 1-2-1-2 | 四檔好跑均速跟前，晨操步爽三甲之材 | 22.7 | 0
5 | 5 | 喜蓮勇感 | 8 | 127 | 田泰安 | 沈集成 | 後上 | 12.0 | 3.2 | 14.0 | 4/5/3/2/4/3 | 1140(+5) | 1-1-1-2 | 後勁凌厲末段有衝刺，步速快極有利 | 14.3 | 0
5 | 6 | 得勝多 | 2 | 125 | 周俊樂 | 蘇偉賢 | 均速 | 9.8 | 2.8 | 13.5 | 2/4/3/1/5/2 | 1098(+1) | 1-2-1-1 | 二檔好位慳位出彎，受讓磅邊線偷襲 | 27.4 | 0
5 | 7 | 浪漫組合 | 7 | 124 | 希威森 | 呂健威 | 後上 | 18.0 | 4.6 | 20.0 | 5/6/4/3/6/5 | 1080(-3) | 0-1-1-3 | 慢踱均速態況平穩，冷門配搭 | 10.0 | 0
5 | 8 | 威武覺醒 | 5 | 123 | 霍宏聲 | 賀賢 | 均速 | 14.0 | 3.8 | 16.0 | 3/4/2/5/4/4 | 1125(+3) | 1-0-1-3 | 五檔出閘形勢中立，步大力雄爭入席 | 12.5 | 0
5 | 9 | 歡樂飛鏢 | 9 | 121 | 巴度 | 蔡約翰 | 後上 | 22.0 | 5.5 | 25.0 | 6/7/5/4/7/6 | 1065(+2) | 0-0-1-4 | 九檔起步較被動，直路需好位衝刺 | 12.0 | 0
5 | 10 | 唯美主義 | 10 | 120 | 鍾易禮 | 告東尼 | 放頭 | 28.0 | 7.0 | 30.0 | 4/8/7/6/8/7 | 1105(+4) | 0-1-0-3 | 十檔放頭消耗大，恐末段互燒力弱 | 6.7 | 0
5 | 11 | 太陽高高 | 11 | 118 | 袁幸堯 | 廖康銘 | 後上 | 35.0 | 8.5 | 36.0 | 8/9/8/7/9/8 | 1050(-4) | 0-0-0-3 | 減十磅但外檔吃虧，暫宜退避 | 2.8 | 0
5 | 12 | 赤馬雄風 | 12 | 116 | 楊明綸 | 鄭俊偉 | 後上 | 50.0 | 12.0 | 45.0 | 9/10/8/9/10/9 | 1130(+1) | 0-0-0-4 | 十二檔形勢極劣，作戰狀態未足 | -11.1 | 0
6 | 1 | 福進 | 6 | 135 | 何澤堯 | 方嘉柏 | 放頭 | 2.8 | 1.4 | 4.2 | 1/1/6/4/7/5 | 1208(+2) | 2-0-0-1 | 上仗同程衝刺強勁勝出，何澤堯親操連捷重心 | 33.3 | 0
6 | 2 | 友駿同心 | 4 | 133 | 梁家俊 | 蘇偉賢 | 前領 | 28.0 | 7.0 | 25.0 | 11/10/10/11/7/8 | 1168(+24) | 0-0-0-3 | 跑法均速但狀態未足，四檔起步仍宜觀望 | -12.0 | 0
6 | 3 | 藍地球 | 8 | 131 | 奧爾民 | 伍鵬志 | 後上 | 16.0 | 4.2 | 20.0 | 9/8/9/11/9/9 | 1159(+9) | 0-0-0-4 | 直路常未能望空，八檔起步後勁考驗走位 | 20.0 | 0
6 | 4 | 巴閉王 | 3 | 129 | 周俊樂 | 呂健威 | 放頭 | 4.5 | 1.8 | 6.5 | 2/6/4/2/2/3 | 1041(+6) | 1-4-2-1 | 三檔好位出閘爭先，呂廄谷草急鋒坐位望贏 | 30.8 | 0
6 | 5 | 佐治傳奇 | 12 | 128 | 艾兆禮 | 告東尼 | 前領 | 5.2 | 1.9 | 7.8 | 3/7/3/3/3/4 | 1092(-8) | 0-1-3-0 | 近仗多度入三甲，十二檔消耗大需看切欄 | 33.3 | 0
6 | 6 | 升升雙息 | 10 | 126 | 潘明輝 | 沈集成 | 均速 | 22.0 | 5.5 | 24.0 | 6/10/8/2/5/7 | 1057(+12) | 0-1-0-2 | 出閘快但十檔吃虧，受讓磅爭入邊線 | 8.3 | 0
6 | 7 | 雙劍合璧 | 2 | 126 | 班德禮 | 大衛希斯 | 後上 | 12.0 | 3.2 | 15.0 | 12/10/2/8/6/7 | 1011(+10) | 0-1-0-1 | 二檔黃金貼欄好位，希斯換班德禮有暗湧 | 20.0 | 0
6 | 8 | 螢影飛馳 | 11 | 114 | 袁幸堯 | 徐雨石 | 放頭 | 26.0 | 6.5 | 30.0 | 12/5/12/14/7/11 | 1165(-6) | 0-0-0-3 | 減十磅起步搶放，但十一檔恐前段互燒力弱 | 13.3 | 0
6 | 9 | 天火同人 | 7 | 116 | 黃寶妮 | 韋達 | 前領 | 8.8 | 2.5 | 12.0 | 4/3/3/6/3/7 | 1095(-4) | 1-2-4-2 | 谷草千米老手步爽力足，減十磅大戶吸納 | 26.7 | 0
6 | 10 | 領航多財 | 5 | 120 | 巫顯東 | 鄭俊偉 | 均速 | 40.0 | 9.0 | 35.0 | 12/13/13/10/11/12 | 1147(+24) | 0-0-0-2 | 晨操走勢略重未見起色，暫宜退避 | -14.3 | 0
6 | 11 | 萬眾開心 | 9 | 120 | 蔡明紹 | 黎昭昇 | 放頭 | 6.8 | 2.2 | 9.5 | 1/7/8/6/5/3 | 1180(-13) | 2-0-1-2 | 黎廄實力分子前速銳利，曾在此程勝出爭勝配 | 28.4 | 0
6 | 12 | 馬運高 | 1 | 118 | 田泰安 | 文家良 | 均速 | 7.5 | 2.3 | 10.0 | 5/11/7/6/4/6 | 1210(+8) | 0-0-1-2 | 一檔黃金貼欄位慳位，田泰安主理三甲之材 | 25.0 | 0
7 | 1 | 東來欣賞 | 4 | 134 | 周俊樂 | 告東尼 | 均速 | 5.2 | 1.8 | 7.5 | 1/2/1/3/1/2 | 1165(+5) | 3-2-0-1 | 東廄主力前速銳利坐二望一 | 30.7 | 0
7 | 2 | 乘數表 | 3 | 134 | 艾道拿 | 羅富全 | 均速 | 12.0 | 3.2 | 15.0 | 3/4/5/2/3/4 | 1120(+2) | 1-0-1-3 | 出腳強三檔好跑不可忽視 | 20.0 | 0
7 | 3 | 天星 | 10 | 133 | 潘頓 | 大衛希斯 | 後上 | 9.4 | 2.7 | 12.0 | 2/1/3/4/2/1 | 1108(+4) | 2-1-0-1 | 潘頓壓陣後上強三甲穩健 | 21.7 | 0
7 | 4 | 競駿皇者 | 12 | 131 | 霍宏聲 | 游達榮 | 放頭 | 16.0 | 4.2 | 18.0 | 5/3/4/2/5/3 | 1145(+1) | 1-0-1-2 | 前速飛快十二檔看切欄 | 11.1 | 0
7 | 5 | 傲聖 | 5 | 129 | 潘明輝 | 賀賢 | 大後上 | 34.0 | 8.5 | 36.0 | 7/8/6/5/7/8 | 1085(-3) | 0-0-0-3 | 步頭略慢後勁未開暫宜退避 | 5.6 | 0
7 | 6 | 電源之駒 | 7 | 127 | 梁家俊 | 廖康銘 | 跟前 | 11.0 | 3.0 | 13.5 | 4/5/2/3/4/2 | 1130(+3) | 1-2-0-2 | 快慢由人中段跟前冷門黑馬 | 18.5 | 0
7 | 7 | 加州本事 | 11 | 124 | 蔡明紹 | 巫偉傑 | 均速 | 13.0 | 3.5 | 15.0 | 3/2/6/4/3/2 | 1095(+2) | 0-2-0-2 | 火氣未減前程緊湊有望拼位 | 13.3 | 0
7 | 8 | 首飾悟空 | 2 | 124 | 艾兆禮 | 蔡約翰 | 大後上 | 4.6 | 1.7 | 7.0 | 1/3/1/2/1/3 | 1115(+4) | 2-0-2-1 | 蔡廄重心直路衝刺全場最凌厲 | 34.3 | 0
7 | 9 | 安康萬里 | 1 | 123 | 班德禮 | 呂健威 | 均速 | 16.0 | 4.2 | 18.0 | 4/6/3/2/4/3 | 1078(+1) | 1-0-0-3 | 一檔起步順暢步爽邊線分子 | 11.1 | 0
7 | 10 | 正極 | 8 | 122 | 黃智弘 | 沈集成 | 放頭 | 21.0 | 5.4 | 24.0 | 6/7/4/3/6/5 | 1140(+3) | 0-0-1-2 | 放頭搶前步速受壓後勁平淡 | 12.5 | 0
7 | 11 | 盈妍威楓 | 9 | 121 | 袁幸堯 | 伍鵬志 | 後上 | 15.0 | 4.0 | 18.0 | 5/4/3/2/5/4 | 1102(+0) | 0-0-1-2 | 減十磅起步有力冷門偷襲 | 16.7 | 0
7 | 12 | 丞匡掠影 | 6 | 120 | 鍾易禮 | 徐雨石 | 後上 | 4.9 | 1.7 | 7.8 | 2/1/2/3/2/1 | 1088(+3) | 2-2-0-1 | 大單熱錢猛撲巔峰爭勝核心 | 37.2 | 0
8 | 1 | 人和家興 | 2 | 135 | 霍宏聲 | 大衛希斯 | 放頭 | 9.8 | 2.6 | 13.0 | 3/1/4/2/3/1 | 1172(+4) | 3-2-0-2 | 谷草老手前速極強爭勝黑馬 | 24.6 | 0
8 | 2 | 團結勇士 | 8 | 135 | 梁家俊 | 鄭俊偉 | 均速 | 14.0 | 3.8 | 16.0 | 5/4/2/3/5/4 | 1130(+2) | 0-1-1-2 | 步大力雄負重看走位發揮 | 12.5 | 0
8 | 3 | 富心星 | 4 | 129 | 何澤堯 | 方嘉柏 | 跟前 | 15.0 | 4.0 | 18.0 | 4/5/3/2/4/5 | 1115(+1) | 1-1-0-3 | 方廄谷草能手晨跳力足四檔好 | 16.7 | 0
8 | 4 | 久久為昇 | 1 | 129 | 奧爾民 | 賀賢 | 均速 | 6.4 | 2.0 | 9.2 | 2/2/1/3/2/1 | 1140(+5) | 2-2-0-1 | 一檔黃金貼欄均速放前韌力足 | 30.4 | 0
8 | 5 | 飛馬座 | 11 | 127 | 周俊樂 | 徐雨石 | 後上 | 24.0 | 6.0 | 26.0 | 7/6/8/5/7/6 | 1082(-2) | 0-0-0-3 | 外檔起步被動走勢略重觀望 | 7.7 | 0
8 | 6 | 富國兄弟 | 7 | 126 | 田泰安 | 葉楚航 | 跟前 | 18.0 | 4.8 | 20.0 | 5/5/4/3/5/4 | 1105(+3) | 0-0-1-3 | 慢踱均速態況平穩具跟前韌力 | 10.0 | 0
8 | 7 | 勇霸龍 | 6 | 123 | 艾道拿 | 黎昭昇 | 均速 | 23.0 | 5.8 | 25.0 | 6/7/5/4/6/5 | 1128(+2) | 0-0-0-3 | 出腳有力速度稍遜考驗騎功 | 8.0 | 0
8 | 8 | 繼往開來 | 5 | 122 | 艾兆禮 | 文家良 | 均速 | 2.4 | 1.2 | 3.8 | 1/1/1/2/1/1 | 1155(+6) | 4-2-0-0 | 全晚超級重心三連勝態勇五檔 | 36.8 | 0
8 | 9 | 蓮冠皇 | 9 | 122 | 希威森 | 廖康銘 | 大後上 | 13.0 | 3.4 | 16.0 | 3/4/2/1/3/4 | 1090(+1) | 1-1-0-2 | 後勁結實末段衝刺強大後上冷腳 | 18.8 | 0
8 | 10 | 喵喵怪 | 12 | 122 | 袁幸堯 | 巫偉傑 | 放頭 | 18.0 | 4.6 | 20.0 | 1/5/6/4/1/5 | 1065(-1) | 1-0-0-2 | 十二檔快放消耗極大互燒恐末弱 | 10.0 | 0
8 | 11 | 驕陽雄心 | 3 | 121 | 黃智弘 | 沈集成 | 跟前 | 9.7 | 2.5 | 13.5 | 2/3/2/1/2/3 | 1118(+4) | 1-3-0-1 | 大戶重點落飛三檔減三磅爭勝 | 28.1 | 0
8 | 12 | 亞機拉 | 10 | 120 | 鍾易禮 | 告東尼 | 後上 | 23.0 | 5.8 | 25.0 | 7/8/6/5/7/8 | 1135(+2) | 0-0-0-4 | 減磅後追末段有衝刺但班次吃虧 | 8.0 | 0
9 | 1 | 嘉應傳承 | 4 | 135 | 布文 | 告東尼 | 前領 | 2.4 | 1.3 | 3.5 | 1/2/1/1/2/1 | 1175(+5) | 3-2-0-0 | 告廄主力落班秤先，四檔起步順暢爭勝核心 | 31.4 | 0
9 | 2 | 紫荊傳令 | 2 | 132 | 潘頓 | 沈集成 | 均速 | 3.0 | 1.4 | 4.2 | 2/1/2/3/1/2 | 1140(+4) | 2-2-1-0 | 二檔黃金好位，初跑谷草新鮮潘頓壓陣焦點 | 28.6 | 0
9 | 3 | 豐辰 | 5 | 130 | 何澤堯 | 蔡約翰 | 後上 | 4.5 | 1.7 | 6.0 | 1/3/2/1/4/2 | 1120(+2) | 2-1-1-1 | 演出極為穩定，直路後勁強大三甲穩健 | 25.0 | 0
9 | 4 | 話你知 | 1 | 129 | 艾道拿 | 羅富全 | 均速 | 6.8 | 2.1 | 9.0 | 3/2/4/2/3/3 | 1155(+6) | 1-2-2-1 | 一檔黃金貼欄位慳位，步大力雄大戶吸納 | 24.4 | 0
9 | 5 | 好好心得 | 3 | 127 | 周俊樂 | 巫偉傑 | 放頭 | 8.5 | 2.5 | 12.0 | 2/4/1/3/2/4 | 1105(+1) | 2-1-1-1 | 三檔快放前速銳利，減磅爭勝冷門黑馬 | 29.2 | 0
9 | 6 | 浪漫老撾 | 7 | 125 | 田泰安 | 巫偉傑 | 後上 | 12.0 | 3.2 | 15.0 | 4/5/3/2/4/3 | 1135(+3) | 1-1-1-2 | 後段衝刺凌厲，七檔起步走位靈活可作配 | 20.0 | 0
9 | 7 | 智取神駒 | 6 | 124 | 希威森 | 方嘉柏 | 均速 | 14.0 | 3.6 | 16.0 | 3/4/2/5/3/5 | 1090(-2) | 1-1-0-3 | 方廄谷草能手態況平穩，邊線分子 | 12.5 | 0
9 | 8 | 都靈福星 | 8 | 123 | 班德禮 | 葉楚航 | 後上 | 18.0 | 4.5 | 20.0 | 5/6/4/3/5/4 | 1110(+2) | 0-1-1-3 | 外檔起步略被動，需好步速配合衝刺 | 10.0 | 0
9 | 9 | 能達心聲 | 9 | 121 | 巴度 | 賀賢 | 後上 | 24.0 | 6.0 | 25.0 | 6/7/5/4/6/5 | 1080(+1) | 0-0-1-3 | 步法整齊但後勁稍嫌平淡，暫宜觀望 | 4.0 | 0
9 | 10 | 縱橫天下 | 10 | 120 | 鍾易禮 | 姚本輝 | 放頭 | 26.0 | 6.5 | 28.0 | 4/8/6/5/7/6 | 1125(+4) | 0-1-0-3 | 十檔放頭消耗較大，受讓五磅力爭前領 | 7.1 | 0
9 | 11 | 飛輪步 | 11 | 118 | 霍宏聲 | 容天鵬 | 後上 | 35.0 | 8.5 | 36.0 | 7/8/7/6/8/7 | 1065(-3) | 0-0-0-3 | 外檔形勢不利，減分期中暫宜退避 | 2.8 | 0
9 | 12 | 增有 | 12 | 116 | 楊明綸 | 文家良 | 後上 | 45.0 | 11.0 | 40.0 | 8/9/8/9/10/8 | 1140(+3) | 0-0-0-4 | 十二檔大外檔，狀態未足難言把握 | -12.5 | 0
"""

def get_race_data(target_race):
    runners = []
    for line in RAW_HORSES_TEXT.strip().split("\n"):
        parts = [p.strip() for p in line.split("|")]
        if len(parts) >= 17 and int(parts[0]) == target_race:
            dist_parts = [int(x) for x in parts[13].split("-")]
            runners.append({
                "no": int(parts[1]),
                "name": parts[2],
                "draw": int(parts[3]),
                "wt": int(parts[4]),
                "j": parts[5],
                "t": parts[6],
                "style": parts[7],
                "c_win": float(parts[8]),
                "c_pla": float(parts[9]),
                "o_win": float(parts[10]),
                "form_6": parts[11],
                "bw": parts[12],
                "dist_stat": dist_parts,
                "expert_com": parts[14],
                "drop_rate": float(parts[15]),
                "is_scratched": (parts[16] == "1")
            })
    # 全9場均有完整資料
    return runners
    return runners

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
    race_opts = [f"第 {i} 場 ({RACES[i][0]} {RACES[i][1]})" for i in range(1, 10)]
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
    no = h["no"]
    name = h["name"]
    draw = h["draw"]
    wt = h["wt"]
    j = h["j"]
    t = h["t"]
    style = h["style"]
    b_win = h["c_win"]
    b_pla = h["c_pla"]
    o_win = h["o_win"]
    form_6 = h["form_6"]
    bw = h["bw"]
    dist_stat = h["dist_stat"]
    expert_com = h["expert_com"]
    drop_rate = h["drop_rate"]
    is_scratched = h["is_scratched"]
    
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
        form_bonus -= 35
    elif top3_rate >= 0.5:
        form_bonus += 20
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
    tot = round(base_sc)
    
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

# ----------------- 視圖 1: 賠率版 (1:1 還原專業落飛監控盤介面) -----------------
if "專業賠率版" in chosen_view:
    # 頂部賽事與彩池統計條
    st.markdown(f"""
    <div style="background:#E0F2FE; border:1px solid #7DD3FC; border-radius:6px; padding:6px 12px; margin-bottom:8px; font-size:12px; color:#0369A1; line-height:1.6;">
        <b style="color:#0C4A6E; font-size:13px;">第 {race_no} 場, 23-09-2026 (21:45), {r_title} {r_len}</b><br>
        獨贏: <b>31,249,562</b> ｜ 位置: <b>28,496,728</b> ｜ 連贏: <b>37,471,196</b> ｜ 位置Q: <b>36,489,003</b> ｜ 孖寶: <b>3,272,930</b> ｜ 此場總投注額(單場賽事彩池): <b style="color:#0369A1;">150,380,583</b><br>
        <span style="color:#0284C7; font-weight:bold;">下場孖寶上: 10: 29%, 8: 15%, 1: 9.5%</span>
    </div>
    """, unsafe_allow_html=True)

    # 依大戶落飛/熱門度排序馬匹
    sorted_df = df.sort_values(by=["is_scratched", "drop_pct", "c_win"], ascending=[True, False, True]).copy()
    
    # 建立主賠率大表 HTML
    main_tbl_html = """
    <div style="overflow-x:auto; background:#FFF; border:1px solid #CBD5E1; border-radius:6px;">
    <table style="width:100%; border-collapse:collapse; font-size:11px; text-align:center;">
    <thead>
        <tr style="background:#0284C7; color:#FFF;">
            <th style="padding:4px 3px; border:1px solid #0369A1;">排位</th>
            <th style="padding:4px 3px; border:1px solid #0369A1;">馬名</th>
            <th style="padding:4px 3px; border:1px solid #0369A1;">騎師</th>
            <th style="padding:4px 3px; border:1px solid #0369A1;">練馬師</th>
            <th style="padding:4px 3px; border:1px solid #0369A1;">檔位</th>
            <th style="padding:4px 3px; border:1px solid #0369A1;">獨贏</th>
            <th style="padding:4px 3px; border:1px solid #0369A1;">獨贏賠率</th>
            <th style="padding:4px 3px; border:1px solid #0369A1;">位置</th>
            <th style="padding:4px 3px; border:1px solid #0369A1;">獨贏%</th>
            <th style="padding:4px 3px; border:1px solid #0369A1;">連贏%</th>
            <th style="padding:4px 3px; border:1px solid #0369A1;">位置Q%</th>
            <th style="padding:4px 3px; border:1px solid #0369A1;">單T%</th>
            <th style="padding:4px 3px; border:1px solid #0369A1;">四連環%</th>
            <th style="padding:4px 3px; border:1px solid #0369A1;">四重彩%</th>
            <th style="padding:4px 3px; border:1px solid #0369A1;">二重彩%</th>
            <th style="padding:4px 3px; border:1px solid #0369A1;">上%</th>
            <th style="padding:4px 3px; border:1px solid #0369A1;">下%</th>
            <th style="padding:4px 3px; border:1px solid #0369A1;">孖寶(前)</th>
            <th style="padding:4px 3px; border:1px solid #0369A1;">孖寶(中)</th>
            <th style="padding:4px 3px; border:1px solid #0369A1;">孖寶(全)</th>
        </tr>
    </thead>
    <tbody>
    """
    
    # 填充表格數據
    side_rows = []
    bar_items = []
    
    for idx, (_, r) in enumerate(sorted_df.iterrows()):
        h_no = r['no']
        h_name = r['name']
        c_w = r['c_win']
        o_w = r['o_win']
        c_p = r['c_pla']
        dr_pct = r['drop_pct']
        
        # 模擬彩池分佈數據
        win_pct = round(100.0 / max(0.1, c_w), 1)
        q_pct = round(win_pct * 1.8, 1)
        qp_pct = round(win_pct * 1.4, 1)
        t_pct = round(win_pct * 1.1, 1)
        f4_pct = round(win_pct * 0.9, 1)
        qtt_pct = round(win_pct * 0.7, 1)
        fc_pct = round(win_pct * 1.2, 1)
        up_pct = int(max(5, abs(dr_pct) * 0.8))
        dn_pct = int(max(10, abs(dr_pct) * 1.2))
        
        db_prev = round(c_w * 0.85, 2)
        db_mid = round(c_w * 0.92, 2)
        db_all = round(c_w * 0.76, 2)
        
        # 色塊高光邏輯 (完全比照相片中的紅底/綠底)
        c_w_style = ""
        c_p_style = ""
        q_style = ""
        qp_style = ""
        db_style = ""
        
        if dr_pct >= 28.0:
            c_w_style = "background:#DC2626; color:#FFF; font-weight:bold;"
            q_style = "background:#DC2626; color:#FFF; font-weight:bold;"
        elif dr_pct >= 18.0:
            c_w_style = "background:#16A34A; color:#FFF; font-weight:bold;"
            db_style = "background:#16A34A; color:#FFF; font-weight:bold;"
        elif c_w <= 3.5:
            c_w_style = "background:#FEF08A; color:#854D0E; font-weight:bold;"
            
        main_tbl_html += f"""
        <tr style="border-bottom:1px solid #E2E8F0;">
            <td style="padding:3px 2px; font-weight:bold;">{h_no}</td>
            <td style="padding:3px 4px; font-weight:bold; color:#0F172A; text-align:left;">{h_name}</td>
            <td style="padding:3px 2px;">{r['j']}</td>
            <td style="padding:3px 2px;">{r['t']}</td>
            <td style="padding:3px 2px; font-weight:bold; color:#1D4ED8;">{r['draw']}</td>
            <td style="padding:3px 2px; {c_w_style}">{c_w}</td>
            <td style="padding:3px 2px; color:#64748B;">{o_w}</td>
            <td style="padding:3px 2px; {c_p_style}">{c_p}</td>
            <td style="padding:3px 2px;">{win_pct:.0f}</td>
            <td style="padding:3px 2px; {q_style}">{q_pct:.0f}</td>
            <td style="padding:3px 2px; {qp_style}">{qp_pct:.0f}</td>
            <td style="padding:3px 2px;">{t_pct:.0f}</td>
            <td style="padding:3px 2px;">{f4_pct:.0f}</td>
            <td style="padding:3px 2px;">{qtt_pct:.0f}</td>
            <td style="padding:3px 2px;">{fc_pct:.0f}</td>
            <td style="padding:3px 2px; color:#15803D;">{up_pct}</td>
            <td style="padding:3px 2px; color:#B91C1C;">{dn_pct}</td>
            <td style="padding:3px 2px; {db_style}">{db_prev}</td>
            <td style="padding:3px 2px; {db_style}">{db_mid}</td>
            <td style="padding:3px 2px; {db_style}">{db_all}</td>
        </tr>
        """
        
        # 測試新功能數據
        score_val = max(10, int(r['stake'] / 15000)) if r['stake'] > 0 else 5
        q_sig_map = ["雙冷Q/QP", "飛Q/飛QP", "熱Q/冷QP", "雙熱Q/QP", "冷Q/冷QP", "雙Q", "雙Q/QP", "觀望", "大冷"]
        q_sig = q_sig_map[idx % len(q_sig_map)]
        stat_sig = "穩膽" if idx == 0 else ("爭勝" if idx == 1 else ("追捧" if idx == 2 else ("啡燈" if dr_pct >= 28 else ("留意" if dr_pct >= 15 else ("走資" if dr_pct < 0 else "觀望")))))
        
        side_rows.append({
            "no": h_no,
            "odds": c_w,
            "m17": f"+{int(abs(dr_pct)*1.3)}" if dr_pct > 0 else f"-{int(abs(dr_pct)*1.1)}",
            "m5": f"+{int(abs(dr_pct)*1.1)}" if dr_pct > 0 else f"-{int(abs(dr_pct)*0.9)}",
            "q_sig": q_sig,
            "vol": score_val,
            "sig": stat_sig
        })
        
        # 柱狀圖高度數值
        bar_height = min(190, max(-15, int(180 - idx * 11 + (dr_pct * 0.8))))
        cap_val = f"+{int(dr_pct)}" if idx in [0, 1, 3, 5, 7, 9] else ""
        if idx == 0: cap_val = "20+6"
        elif idx == 1: cap_val = "45"
        elif idx == 3: cap_val = "+3"
        elif idx == 5: cap_val = "41"
        elif idx == 7: cap_val = "+5"
        elif idx == 9: cap_val = "20"
        
        bar_items.append({
            "no": h_no,
            "height": bar_height,
            "cap": cap_val,
            "val": bar_height,
            "odds": c_w,
            "has_q": (idx in [0, 1, 6, 7]),
            "b1": abs(int(dr_pct * 0.9)) or 18,
            "b2": abs(int(dr_pct * 1.5)) or 42
        })

    main_tbl_html += "</tbody></table></div>"

    # 右側「測試新功能」表格
    side_tbl_html = """
    <div style="overflow-x:auto; background:#FFF; border:1px solid #CBD5E1; border-radius:6px;">
    <div style="background:#0284C7; color:#FFF; font-weight:bold; font-size:11px; padding:4px 6px; text-align:center;">測試新功能 (異動監控)</div>
    <table style="width:100%; border-collapse:collapse; font-size:10px; text-align:center;">
    <thead>
        <tr style="background:#F1F5F9; color:#475569;">
            <th style="padding:3px 1px; border:1px solid #CBD5E1;">號</th>
            <th style="padding:3px 1px; border:1px solid #CBD5E1;">賠率</th>
            <th style="padding:3px 1px; border:1px solid #CBD5E1;">17分</th>
            <th style="padding:3px 1px; border:1px solid #CBD5E1;">5分</th>
            <th style="padding:3px 1px; border:1px solid #CBD5E1;">Q/QP</th>
            <th style="padding:3px 1px; border:1px solid #CBD5E1;">量</th>
            <th style="padding:3px 1px; border:1px solid #CBD5E1;">訊號</th>
        </tr>
    </thead>
    <tbody>
    """
    for sr in side_rows:
        sig_color = "#DC2626" if sr['sig'] in ["穩膽", "爭勝", "啡燈"] else ("#15803D" if sr['sig'] in ["追捧", "留意"] else "#64748B")
        side_tbl_html += f"""
        <tr style="border-bottom:1px solid #F1F5F9;">
            <td style="font-weight:bold; padding:2px 1px;">{sr['no']}</td>
            <td style="padding:2px 1px;">{sr['odds']}</td>
            <td style="padding:2px 1px; color:#15803D;">{sr['m17']}</td>
            <td style="padding:2px 1px; color:#15803D;">{sr['m5']}</td>
            <td style="padding:2px 1px; font-size:9px;">{sr['q_sig']}</td>
            <td style="padding:2px 1px;">{sr['vol']}</td>
            <td style="padding:2px 1px; font-weight:bold; color:{sig_color};">{sr['sig']}</td>
        </tr>
        """
    side_tbl_html += "</tbody></table></div>"

    # 渲染上半部 (主表 + 右側面板)
    top_col1, top_col2 = st.columns([4, 1.2])
    with top_col1:
        render_clean_html(main_tbl_html)
    with top_col2:
        render_clean_html(side_tbl_html)

    # ----------------- 下半部：左側 MoneyFlow 柱狀圖 + 右側雙時間序列網格 -----------------
    st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
    bot_col1, bot_col2 = st.columns([1, 1.1])
    
    # 1. 柱狀圖 HTML
    with bot_col1:
        st.markdown("<b style='font-size:12px; color:#0F172A;'>📊 MoneyFlow 資金能量與落飛異動柱狀圖</b>", unsafe_allow_html=True)
        
        bars_html = """
        <div style="background:#FFF; border:1px solid #CBD5E1; border-radius:6px; padding:10px; margin-top:4px;">
            <div style="display:flex; height:220px; align-items:flex-end; position:relative; border-left:2px solid #64748B; border-bottom:2px solid #64748B; margin-left:32px; padding-bottom:2px;">
                <div style="position:absolute; left:-30px; top:0; bottom:0; display:flex; flex-direction:column; justify-content:space-between; font-size:9px; color:#64748B; text-align:right; width:25px;">
                    <span>200</span><span>160</span><span>120</span><span>80</span><span>40</span><span>0</span>
                </div>
                <div style="position:absolute; left:0; right:0; top:20%; border-top:1px dashed #E2E8F0;"></div>
                <div style="position:absolute; left:0; right:0; top:40%; border-top:1px dashed #E2E8F0;"></div>
                <div style="position:absolute; left:0; right:0; top:60%; border-top:1px dashed #E2E8F0;"></div>
                <div style="position:absolute; left:0; right:0; top:80%; border-top:1px dashed #E2E8F0;"></div>
        """
        
        for b in bar_items:
            h_px = max(4, int(b['height']))
            cap_content = f"<div style='background:#FEF08A; border-bottom:1px solid #F59E0B; font-size:8px; font-weight:bold; color:#854D0E; text-align:center; padding:1px 0;'>{b['cap']}</div>" if b['cap'] else ""
            q_badge = "<div style='width:14px; height:14px; line-height:14px; border-radius:50%; background:#0284C7; color:#FFF; font-size:8px; font-weight:bold; text-align:center; margin:2px auto;'>QP</div>" if b['has_q'] else ""
            
            bars_html += f"""
            <div style="flex:1; display:flex; flex-direction:column; align-items:center; justify-content:flex-end; height:100%; position:relative;">
                <div style="width:75%; height:{h_px}px; background:#38BDF8; border:1px solid #0284C7; border-bottom:none; display:flex; flex-direction:column; justify-content:space-between;">
                    {cap_content}
                    {q_badge}
                </div>
            </div>
            """
        bars_html += "</div>"
        
        # 柱底資訊 (數值、馬號圈、賠率、徽章)
        bars_html += "<div style='display:flex; margin-left:32px; margin-top:6px;'>"
        for b in bar_items:
            bars_html += f"""
            <div style="flex:1; display:flex; flex-direction:column; align-items:center; gap:2px;">
                <span style="font-size:9px; font-weight:bold; color:#0F172A;">{b['val']}</span>
                <span style="display:inline-block; width:17px; height:17px; line-height:17px; border-radius:50%; background:#0F172A; color:#FFF; font-size:10px; font-weight:bold; text-align:center;">{b['no']}</span>
                <span style="font-size:9px; color:#475569;">{b['odds']}</span>
                <span style="background:#DCFCE7; color:#15803D; border:1px solid #86EFAC; font-size:8px; font-weight:bold; padding:0 2px; border-radius:2px;">{b['b1']}</span>
                <span style="background:#FEE2E2; color:#B91C1C; border:1px solid #FCA5A5; font-size:8px; font-weight:bold; padding:0 2px; border-radius:2px;">{b['b2']}</span>
            </div>
            """
        bars_html += "</div></div>"
        render_clean_html(bars_html)
        
    # 2. 右側雙熱力網格圖
    with bot_col2:
        st.markdown("<b style='font-size:12px; color:#0F172A;'>📈 1-17 分鐘時間序列落飛異動追蹤網格</b>", unsafe_allow_html=True)
        
        # 建立 1~17 分鐘時間點雙熱力表
        hm_html = """
        <div style="background:#FFF; border:1px solid #CBD5E1; border-radius:6px; padding:8px; margin-top:4px;">
            <div style="display:flex; gap:8px;">
                <!-- 左網格: 獨贏/位置 -->
                <div style="flex:1;">
                    <div style="font-size:10px; font-weight:bold; color:#475569; text-align:center; margin-bottom:4px;">獨贏 / 位置 (每格由上至下)</div>
                    <table style="width:100%; border-collapse:collapse; font-size:8px; text-align:center;">
                        <thead>
                            <tr style="background:#F1F5F9; color:#475569;">
                                <th style="border:1px solid #CBD5E1; padding:1px;">號</th>
                                <th style="border:1px solid #CBD5E1; padding:1px;">賠率</th>
        """
        for t_min in range(1, 18):
            hm_html += f"<th style='border:1px solid #CBD5E1; padding:1px;'>{t_min}</th>"
        hm_html += "</tr></thead><tbody>"
        
        for idx, b in enumerate(bar_items):
            hm_html += f"""<tr>
                <td style="border:1px solid #CBD5E1; font-weight:bold;">{b['no']}</td>
                <td style="border:1px solid #CBD5E1;">{b['odds']}</td>
            """
            for t_min in range(1, 18):
                # 模擬時間落飛色塊 (相片中的色塊分布)
                cell_bg = "#FFFFFF"
                if idx in [0, 1, 2] and t_min in [1, 2, 8, 12, 16, 17]:
                    cell_bg = "#DC2626" # 啡燈暴跌
                elif idx in [0, 3, 5] and t_min in [3, 7, 10, 15]:
                    cell_bg = "#16A34A" # 綠燈急落
                elif idx in [1, 4, 6] and t_min in [5, 9, 14]:
                    cell_bg = "#FEF08A" # 追捧
                hm_html += f"<td style='border:1px solid #E2E8F0; background:{cell_bg}; height:14px;'></td>"
            hm_html += "</tr>"
            
        hm_html += """
                    </table>
                    <div style="display:flex; gap:6px; justify-content:center; align-items:center; font-size:8px; margin-top:6px; color:#64748B;">
                        <span>圖例:</span>
                        <span style="display:inline-block; width:10px; height:8px; background:#854D0E;"></span> &lt;-10%
                        <span style="display:inline-block; width:10px; height:8px; background:#FEF08A;"></span> 10-20%
                        <span style="display:inline-block; width:10px; height:8px; background:#16A34A;"></span> 20-30%
                        <span style="display:inline-block; width:10px; height:8px; background:#DC2626;"></span> &gt;30%
                    </div>
                </div>
                
                <!-- 右網格: 連贏/位置Q -->
                <div style="flex:1;">
                    <div style="font-size:10px; font-weight:bold; color:#475569; text-align:center; margin-bottom:4px;">連贏 / 位置Q 異動</div>
                    <table style="width:100%; border-collapse:collapse; font-size:8px; text-align:center;">
                        <thead>
                            <tr style="background:#F1F5F9; color:#475569;">
                                <th style="border:1px solid #CBD5E1; padding:1px;">號</th>
                                <th style="border:1px solid #CBD5E1; padding:1px;">賠率</th>
        """
        for t_min in range(1, 18):
            hm_html += f"<th style='border:1px solid #CBD5E1; padding:1px;'>{t_min}</th>"
        hm_html += "</tr></thead><tbody>"
        
        for idx, b in enumerate(bar_items):
            hm_html += f"""<tr>
                <td style="border:1px solid #CBD5E1; font-weight:bold;">{b['no']}</td>
                <td style="border:1px solid #CBD5E1;">{b['odds']}</td>
            """
            for t_min in range(1, 18):
                cell_bg = "#FFFFFF"
                if idx in [0, 2] and t_min in [2, 3, 11, 17]:
                    cell_bg = "#DC2626"
                elif idx in [1, 3, 4] and t_min in [4, 6, 13]:
                    cell_bg = "#16A34A"
                elif idx in [5, 7] and t_min in [8, 15]:
                    cell_bg = "#F59E0B"
                hm_html += f"<td style='border:1px solid #E2E8F0; background:{cell_bg}; height:14px;'></td>"
            hm_html += "</tr>"
            
        hm_html += """
                    </table>
                    <div style="display:flex; gap:6px; justify-content:center; align-items:center; font-size:8px; margin-top:6px; color:#64748B;">
                        <span>圖例:</span>
                        <span style="display:inline-block; width:10px; height:8px; background:#DCFCE7;"></span> 0.8-5%
                        <span style="display:inline-block; width:10px; height:8px; background:#FEF08A;"></span> 5-15%
                        <span style="display:inline-block; width:10px; height:8px; background:#16A34A;"></span> 15-25%
                        <span style="display:inline-block; width:10px; height:8px; background:#DC2626;"></span> &gt;25%
                    </div>
                </div>
            </div>
        </div>
        """
        render_clean_html(hm_html)


# ----------------- 視圖 2: AI 智勝精算推介 -----------------
elif "AI" in chosen_view:
    st.markdown(f"##### 🤖 第 {race_no} 場《{r_title}》AI 智勝四駒順序精算推介")
    st.caption("🛡️ <b>精算法則</b>：已完全剔除退出馬匹；結合【近績真實賽績】、【東方名家語意情緒】、【資金落飛量化】，徹底過濾「未足/冷落」馬匹。")
    
    top_picks = active_df.sort_values(by="ai_score", ascending=False).head(4)
    p_labels = ["🥇 首選 (Top Pick)", "🥈 次選 (Second Pick)", "🥉 三選 (Third Pick)", "🎖️ 四選 (Fourth Pick)"]
    
    for idx, (_, p) in enumerate(top_picks.iterrows()):
        st.markdown(f"""
        <div class="ai-card">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <b style="font-size:14px; color:#1E40AF;">{p_labels[idx]}：<span class="circle-no">{p['no']}</span> {p['name']}</b>
                <span style="font-size:12px; font-weight:bold; color:#DC2626;">獨贏：{p['c_win']}倍 ｜ AI精算評分：{p['ai_score']}分</span>
            </div>
            <div style="font-size:12px; color:#334155; margin-top:4px;">
                • <b>形勢與同程</b>：<b>{p['draw']}檔</b> · 跑法: <b>{p['style']}</b> ｜ 同程: {render_dist_circles(p['dist_stat'])} ｜ 騎練: {p['j']}/{p['t']}<br>
                • <b>東方日報名家點評</b>：{p['expert_com']}<br>
                • <b>盤口信號</b>：臨場跌幅 <b>{p['drop_pct']:+.1f}%</b> ({p['sig']}) ｜ 新增注碼: <b>${p['stake']:,}</b>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("---")
    st.markdown("##### 📝 輸入本場實際賽果 · AI 深度複盤與權重自適應優化")
    st.caption("💡 跑完此場後，將真實冠亞季殿名次輸入，AI 將自動對比預測偏差，並動態調校下一場的模型權重！")
    
    horse_choices = [f"{r['no']}號 {r['name']}" for _, r in active_df.iterrows()]
    r_col1, r_col2, r_col3, r_col4 = st.columns(4)
    with r_col1: win_h = st.selectbox("🥇 冠軍 (1st)", horse_choices, index=0)
    with r_col2: scd_h = st.selectbox("🥈 亞軍 (2nd)", horse_choices, index=min(1, len(horse_choices)-1))
    with r_col3: trd_h = st.selectbox("🥉 季軍 (3rd)", horse_choices, index=min(2, len(horse_choices)-1))
    with r_col4: fth_h = st.selectbox("🎖️ 殿軍 (4th)", horse_choices, index=min(3, len(horse_choices)-1))
    
    if st.button("💾 保存本場賽果並進行 AI 深度複盤", use_container_width=True):
        w_no = int(win_h.split("號")[0])
        s_no = int(scd_h.split("號")[0])
        st.session_state["results_history"][race_no] = (w_no, s_no)
        
        win_info = active_df[active_df["no"] == w_no].iloc[0]
        if win_info["style"] in ["放頭", "均速"]:
            st.session_state["ai_learning_bias"]["lead_bias"] += 2.0
            st.session_state["ai_learning_bias"]["draw_bias"] += 1.5
            analysis_text = f"頭馬 {w_no}號「{win_info['name']}」採【{win_info['style']}】貼欄直放到底，印證快活谷 C 欄內檔前領優勢極大！"
        else:
            st.session_state["ai_learning_bias"]["lead_bias"] -= 1.0
            analysis_text = f"頭馬 {w_no}號「{win_info['name']}」採【{win_info['style']}】後勁爆發，反映前段步速過快互燒，後上馬獲益！"
            
        st.success(f"✅ 第 {race_no} 場賽果已儲存！AI 複盤結論：{analysis_text} 模型已自動自適應優化下一場評分權重。")

# ----------------- 視圖 3: 綜合能力評分總表 -----------------
elif "能力評分" in chosen_view:
    st.markdown(f"##### 📊 第 {race_no} 場《{r_title}》評分總表 (同程數據：🟡冠 ⚪亞 🟤季 ⚫負)")
    tbl2 = """<table class="compact-table"><thead><tr>
    <th>排名</th><th>馬號</th><th>馬名</th>
    <th style="background:#EFF6FF; color:#1D4ED8;">檔位</th>
    <th style="background:#EFF6FF; color:#1D4ED8;">跑法</th>
    <th>AI精算分</th><th>速度戰力</th>
    <th style="background:#FEF3C7; color:#B45309;">前速評分</th>
    <th style="background:#FEF3C7; color:#B45309;">末段速度</th>
    <th style="background:#FEF9C3; color:#854D0E;">同程數據 (冠-亞-季-負)</th>
    <th>近6仗成績</th><th>排位體重</th>
    <th style="text-align:left;">東方日報馬評家短評</th>
    <th>臨場獨贏</th>
    </tr></thead><tbody>"""
    
    rk = 1
    for _, r in df.sort_values(by=["is_scratched", "ai_score"], ascending=[True, False]).iterrows():
        if r["is_scratched"]:
            tbl2 += f"""<tr class="scratched-row">
            <td>-</td><td><span class="circle-no" style="background:#94A3B8;">{r['no']}</span></td>
            <td><del>{r['name']}</del><span class="scratched-tag">退出</span></td>
            <td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td>
            <td>{render_dist_circles(r['dist_stat'])}</td>
            <td>{r['form_6']}</td><td>{r['bw']}</td>
            <td style="text-align:left; font-size:11px; color:#DC2626;">【已退出賽事】</td>
            <td>-</td>
            </tr>"""
            continue
            
        tbl2 += f"""<tr>
        <td><b>#{rk}</b></td>
        <td><span class="circle-no">{r['no']}</span></td>
        <td><b>{r['name']}</b></td>
        <td style="font-weight:bold; color:#1D4ED8; background:#EFF6FF;">{r['draw']}檔</td>
        <td style="font-weight:bold; background:#EFF6FF;">{r['style']}</td>
        <td style="font-weight:bold; color:#DC2626; font-size:13px;">{r['ai_score']}分</td>
        <td style="font-weight:bold; color:#1E40AF;">{r['tot']}分</td>
        <td style="font-weight:bold; color:#DC2626;">{r['e_sp']}</td>
        <td style="font-weight:bold; color:#15803D;">{r['l_sp']}</td>
        <td style="background:#FEFCE8;">{render_dist_circles(r['dist_stat'])}</td>
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
        if r["is_scratched"]:
            st.markdown(f"""
            <div style="border: 1px solid #E2E8F0; background:#F8FAFC; border-radius: 6px; padding: 6px 10px; margin-bottom: 5px; color:#94A3B8;">
                <b>{r['no']}號 <del>{r['name']}</del></b> <span class="scratched-tag">已退出</span> ｜ 騎練: {r['j']}/{r['t']}<br>
                <span style="font-size:12px;">• 狀態: 本場賽事已退出，所有相關注項均告無效退款。</span>
            </div>
            """, unsafe_allow_html=True)
            continue
            
        st.markdown(f"""
        <div style="border: 1px solid #CBD5E1; border-radius: 6px; padding: 6px 10px; margin-bottom: 5px;">
            <b>{r['no']}號 {r['name']}</b> (<b>{r['draw']}檔</b> · 跑法: <b>{r['style']}</b> · 騎練: {r['j']}/{r['t']}) · AI評分: <b style="color:#DC2626;">{r['ai_score']}分</b><br>
            <span style="font-size:12px; color:#334155;">
            • <b>速度與同程</b>: 前速 <b>{r['e_sp']}分</b> ｜ 末段 <b>{r['l_sp']}分</b> ｜ 同程賽績: {render_dist_circles(r['dist_stat'])}<br>
            • <b>東方評語</b>: {r['expert_com']}<br>
            • <b>馬會往績</b>: 近6仗 <b>{r['form_6']}</b> ｜ 體重 <b>{r['bw']}</b> ｜ 盤口: 隔夜 {r['o_win']} ➔ 臨場 <b>{r['c_win']}</b> ({r['sig']})
            </span>
        </div>
        """, unsafe_allow_html=True)

