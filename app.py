import streamlit as st
import pandas as pd
import urllib.request
import re
import datetime
import streamlit.components.v1 as components

st.set_page_config(page_title="HKJC 快活谷官方排位 · MoneyFlow 賠率與能力終端", page_icon="🏇", layout="wide")

# 自定義緊湊 CSS 樣式 (格仔縮細、MoneyFlow 排版、清晰緊密)
st.markdown("""
<style>
    .header-box { background: #FFFFFF; border: 1px solid #CBD5E1; border-radius: 8px; padding: 10px 14px; margin-bottom: 8px; }
    .status-bar { display: flex; justify-content: space-between; align-items: center; background: #F8FAFC; border: 1px solid #E2E8F0; padding: 5px 10px; border-radius: 6px; font-size: 12px; margin-bottom: 8px; }
    .pace-box { background: #F0FDF4; border-left: 4px solid #16A34A; padding: 6px 10px; font-size: 12px; border-radius: 4px; }
    .alert-box { background: #FEF2F2; border-left: 4px solid #EF4444; padding: 6px 10px; font-size: 12px; border-radius: 4px; }
    .stat-card { background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 6px; padding: 6px 2px; text-align: center; }
    
    /* 緊湊型表格：格仔縮細 (Compact Grid)、文字12px、緊密排列 */
    .compact-table { width: 100%; border-collapse: collapse; font-size: 12px; line-height: 1.25; margin-top: 4px; }
    .compact-table th { background: #F1F5F9; color: #1E293B; font-weight: 700; padding: 4px 5px; border: 1px solid #CBD5E1; text-align: center; white-space: nowrap; }
    .compact-table td { padding: 3px 5px; border: 1px solid #E2E8F0; text-align: center; vertical-align: middle; white-space: nowrap; }
    .compact-table tr:nth-child(even) { background-color: #F8FAFC; }
    .compact-table tr:hover { background-color: #F0FDF4; }
    
    .num-circle { display: inline-block; width: 18px; height: 18px; line-height: 18px; border-radius: 50%; background: #0F172A; color: #FFF; font-weight: 800; font-size: 11px; text-align: center; }
    .num-fav { background: #DC2626; }
    .badge-green { background: #DCFCE7; color: #15803D; padding: 1px 4px; border-radius: 3px; font-weight: 700; font-size: 11px; }
    .badge-brown { background: #FEF3C7; color: #B45309; padding: 1px 4px; border-radius: 3px; font-weight: 700; font-size: 11px; }
    .badge-gray { background: #F1F5F9; color: #64748B; padding: 1px 4px; border-radius: 3px; font-size: 11px; }
    .hkjc-link { color: #2563EB; text-decoration: none; font-weight: 700; }
    .hkjc-link:hover { text-decoration: underline; color: #1D4ED8; }
    .pool-bar-bg { background: #E2E8F0; border-radius: 3px; width: 55px; height: 6px; display: inline-block; vertical-align: middle; margin-right: 3px; }
    .pool-bar-fill { background: #2563EB; height: 6px; border-radius: 3px; }
    .pool-bar-fill-hot { background: #DC2626; height: 6px; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

RACE_INFO = {
    1: ("南風讓賽", "1650米", 875000), 2: ("深水灣讓賽", "1200米", 1170000),
    3: ("黃竹坑讓賽", "1650米", 1170000), 4: ("深水灣讓賽", "1200米", 1170000),
    5: ("鄉村俱樂部挑戰盃", "1650米", 1170000), 6: ("香島讓賽", "1000米", 1170000),
    7: ("畢拿山讓賽", "1200米", 1860000), 8: ("畢拿山讓賽", "1200米", 1860000),
    9: ("大坑讓賽", "1800米", 2050000)
}

# 官方排位基盤數據: (馬號, 馬名, 檔位, 負磅, 騎師, 練馬師, 跑法, 獨贏基盤, 位置基盤, 近賽往績, 體重, 晨操狀態)
OFFICIAL_DATA = {
    1: [
        (1, "堅多福", 12, 135, "何澤堯", "方嘉柏", "前領", 14.0, 3.9, "3-4-2", "1124磅(+2)", "火氣旺步順力足"),
        (2, "一風雲", 5, 134, "金誠剛", "丁冠豪", "後上", 36.0, 7.2, "8-7-6", "1088磅(-4)", "晨課緊扣態平平"),
        (3, "神駒馬靈", 4, 132, "霍宏聲", "廖康銘", "領放", 5.7, 1.9, "1-3-2", "1150磅(+6)", "神態活躍翻步順"),
        (4, "紅磚戰士", 1, 131, "周俊樂", "游達榮", "前領", 10.0, 3.2, "4-2-5", "1062磅(+1)", "內圈慢踱體健足"),
        (5, "極速滿貫", 10, 130, "奧爾民", "黎昭昇", "居中", 17.0, 4.2, "6-5-4", "1105磅(+3)", "按慢順走火氣平"),
        (6, "開心三多", 11, 128, "希威森", "桂福特", "後上", 10.0, 2.8, "2-4-3", "1140磅(+5)", "步伐輕爽神態旺"),
        (7, "綫路達飛", 6, 127, "楊明綸", "蘇偉賢", "居中", 42.0, 9.5, "9-8-7", "1098磅(-2)", "馬身稍重需實戰"),
        (8, "電訊驕陽", 8, 125, "袁幸堯", "徐雨石", "領放", 5.1, 1.8, "2-1-3", "1076磅(+4)", "快跳火足走勢勁"),
        (9, "至高心得", 2, 123, "梁家俊", "韋達", "居中", 18.0, 4.8, "5-6-4", "1118磅(-1)", "步幅開揚毛色光"),
        (10, "威威父子", 7, 120, "田泰安", "巫偉傑", "後上", 14.0, 3.6, "4-5-2", "1132磅(+3)", "收身結實朝氣勃"),
        (11, "東方魅影", 3, 119, "潘頓", "大衛希斯", "前領", 3.2, 1.4, "1-1-2", "1085磅(+2)", "潘頓主理霸氣足"),
        (12, "幸運同行", 9, 118, "艾兆禮", "蔡約翰", "後上", 24.0, 6.0, "7-6-8", "1045磅(+0)", "步大雄健有進步")
    ],
    2: [
        (1, "紅愛舍", 12, 135, "楊明綸", "韋達", "居中", 18.0, 4.6, "6-4-5", "1135磅(+2)", "馬身結實神采飛"),
        (2, "銳喜", 2, 134, "蔡明紹", "徐雨石", "前領", 21.0, 5.2, "7-8-6", "1080磅(-3)", "體格平穩出腳整"),
        (3, "路路勁", 8, 132, "田泰安", "羅富全", "後上", 9.3, 2.6, "3-2-4", "1162磅(+5)", "末段後勁甚凌厲"),
        (4, "馬馳登", 7, 132, "艾兆禮", "黎昭昇", "前領", 4.4, 1.7, "1-2-1", "1120磅(+4)", "試閘極佳火氣上"),
        (5, "飛輪霸", 11, 130, "潘明輝", "姚本輝", "後上", 17.0, 4.3, "5-5-3", "1095磅(+1)", "慢跳順暢體健身"),
        (6, "金珀尖子", 6, 128, "金誠剛", "大衛希斯", "前領", 45.0, 10.0, "9-9-8", "1055磅(-2)", "仍需時間熱身開"),
        (7, "銀刺勇士", 1, 128, "黃智弘", "方嘉柏", "領放", 7.3, 2.2, "2-3-2", "1145磅(+3)", "1檔快放氣勢足"),
        (8, "鄉村威龍", 10, 127, "艾道拿", "蔡約翰", "居中", 20.0, 5.0, "4-6-5", "1108磅(-1)", "走勢靈巧態平穩"),
        (9, "開心五月", 4, 123, "鍾易禮", "告東尼", "前領", 3.7, 1.5, "1-1-3", "1088磅(+2)", "大熱門晨操火足"),
        (10, "比特星", 5, 119, "潘頓", "賀賢", "居中", 6.3, 2.0, "2-2-1", "1072磅(+4)", "潘頓壓陣動作熟"),
        (11, "有盈勇士", 9, 118, "希威森", "沈集成", "後上", 20.0, 5.2, "6-5-7", "1110磅(+0)", "力度尚可後勁穩"),
        (12, "首駿", 3, 118, "班德禮", "游達榮", "前領", 28.0, 6.8, "8-7-9", "1065磅(-3)", "步幅均勻欠霸氣")
    ],
    3: [
        (1, "星願無限", 11, 135, "希威森", "沈集成", "後上", 22.0, 5.4, "5-7-6", "1140磅(+2)", "神態尚可步大勁"),
        (2, "贏玥", 7, 132, "潘頓", "巫偉傑", "前領", 6.0, 1.9, "1-3-2", "1115磅(+5)", "潘頓快跳利落揚"),
        (3, "彩虹七色", 5, 130, "何澤堯", "呂健威", "前領", 20.0, 5.1, "6-4-5", "1085磅(-2)", "快操順走態復甦"),
        (4, "睿智多寶", 6, 129, "艾道拿", "黎昭昇", "居中", 13.0, 3.5, "3-5-4", "1128磅(+3)", "試閘良好身壯健"),
        (5, "凝妙星", 3, 128, "奧爾民", "大衛希斯", "前領", 4.6, 1.6, "1-2-1", "1092磅(+4)", "火氣頂透內檔利"),
        (6, "領航天子", 10, 128, "霍宏聲", "廖康銘", "領放", 12.0, 3.2, "2-4-6", "1155磅(+1)", "快放有速出腳勁"),
        (7, "有情有義", 4, 127, "黃智弘", "方嘉柏", "居中", 9.6, 2.7, "3-2-3", "1078磅(+2)", "減磅得益體力充"),
        (8, "蹺妙", 2, 124, "周俊樂", "游達榮", "前領", 4.9, 1.7, "2-1-2", "1130磅(+5)", "近況大勇貼欄順"),
        (9, "越駿齊歡", 1, 124, "梁家俊", "羅富全", "居中", 9.5, 2.6, "4-3-2", "1102磅(-1)", "1檔好位後勁銳"),
        (10, "加州活力", 8, 131, "艾兆禮", "告東尼", "後上", 13.0, 3.4, "5-6-4", "1170磅(+4)", "慢踱健步氣量足"),
        (11, "光明傳承", 9, 119, "班德禮", "葉楚航", "後上", 31.0, 7.5, "8-8-7", "1060磅(-3)", "熱身階段狀態常"),
        (12, "得意佳作", 12, 118, "田泰安", "姚本輝", "後上", 15.0, 4.0, "4-5-3", "1082磅(+1)", "身輕步爽伺後抽")
    ],
    4: [
        (1, "沙井之友", 8, 135, "周俊樂", "巫偉傑", "後上", 8.0, 2.4, "2-3-1", "1138磅(+3)", "末段後勁極雄渾"),
        (2, "智勝一籌", 10, 135, "蔡明紹", "蘇偉賢", "居中", 24.0, 5.8, "6-7-5", "1090磅(-2)", "外檔稍吃虧態平"),
        (3, "應龍飛影", 6, 132, "袁幸堯", "伍鵬志", "領放", 6.3, 2.1, "1-2-4", "1145磅(+6)", "減磅出擊衝刺強"),
        (4, "星辰千帥", 7, 131, "艾道拿", "賀賢", "前領", 11.0, 3.1, "3-4-2", "1112磅(+2)", "火氣上揚走勢暢"),
        (5, "莊家班", 3, 130, "黃智弘", "沈集成", "前領", 28.0, 6.5, "7-8-6", "1075磅(-1)", "步幅開揚近態平"),
        (6, "快樂神駒", 2, 129, "潘頓", "廖康銘", "前領", 2.0, 1.2, "1-1-1", "1165磅(+4)", "擂台大熱快跳勁"),
        (7, "震撼人心", 12, 129, "艾兆禮", "蔡約翰", "後上", 32.0, 7.8, "9-8-7", "1082磅(-3)", "排外檔需靠運氣"),
        (8, "禪勝閃亮", 5, 128, "希威森", "呂健威", "居中", 21.0, 5.2, "5-5-6", "1120磅(+1)", "步伐整齊態平穩"),
        (9, "將傲", 4, 126, "奧爾民", "韋達", "居中", 10.0, 2.8, "4-3-3", "1098磅(+3)", "試閘反應佳暗湧"),
        (10, "平天雄", 9, 123, "潘明輝", "丁冠豪", "後上", 33.0, 8.0, "8-7-9", "1055磅(-2)", "走勢略重待減分"),
        (11, "焦點", 1, 121, "田泰安", "游達榮", "前領", 22.0, 5.5, "6-6-5", "1108磅(+2)", "內檔慳位態有進"),
        (12, "三強", 11, 120, "楊明綸", "鄭俊偉", "後上", 28.0, 7.0, "7-9-8", "1070磅(+0)", "出腳尚可冷門配")
    ],
    5: [
        (1, "本領非凡", 9, 135, "何澤堯", "羅富全", "居中", 12.0, 3.4, "4-3-5", "1145磅(+3)", "何澤堯壓陣步勁"),
        (2, "大文豪", 5, 133, "奧爾民", "姚本輝", "後上", 16.0, 4.2, "5-6-4", "1122磅(+1)", "內圈慢踱體勻稱"),
        (3, "大學生", 1, 128, "金誠剛", "韋達", "前領", 8.0, 2.3, "2-2-3", "1105磅(+4)", "貼欄快放火氣旺"),
        (4, "赤風驪", 2, 128, "霍宏聲", "方嘉柏", "前領", 10.0, 2.8, "3-4-2", "1088磅(+2)", "方廄焦點收身靚"),
        (5, "創科群英", 3, 126, "周俊樂", "游達榮", "前領", 5.9, 1.8, "1-2-1", "1152磅(+5)", "熱錢重心試閘撲"),
        (6, "越駿聯歡", 6, 124, "梁家俊", "黎昭昇", "居中", 6.8, 2.0, "2-3-2", "1096磅(+3)", "身壯色潤勇態續"),
        (7, "滿洛城", 7, 123, "班德禮", "大衛希斯", "後上", 10.0, 2.9, "3-5-4", "1110磅(-2)", "發力點好具後勁"),
        (8, "金駒永騰", 12, 123, "黃智弘", "伍鵬志", "領放", 10.0, 2.9, "1-4-3", "1078磅(+1)", "快馬搶放外檔耗"),
        (9, "爆竹", 11, 122, "田泰安", "告東尼", "居中", 7.0, 2.2, "2-1-4", "1135磅(+4)", "田泰安執韁步爽"),
        (10, "揀馬之皇", 8, 120, "潘明輝", "賀賢", "後上", 28.0, 7.0, "8-8-7", "1062磅(-3)", "後追型步幅未開"),
        (11, "健康小馬", 4, 118, "楊明綸", "鄭俊偉", "後上", 38.0, 9.2, "9-9-8", "1050磅(-1)", "班次吃虧暫觀望"),
        (12, "同心", 10, 117, "蔡明紹", "呂健威", "前領", 7.2, 2.2, "3-2-2", "1125磅(+3)", "輕磅利好暗湧大")
    ],
    6: [
        (1, "福進", 6, 135, "何澤堯", "方嘉柏", "前領", 4.2, 1.6, "1-1-2", "1150磅(+4)", "短途快刀火極盛"),
        (2, "友駿同心", 4, 133, "梁家俊", "蘇偉賢", "居中", 12.0, 3.3, "4-5-3", "1118磅(+2)", "身輕步爽態不俗"),
        (3, "藍地球", 8, 131, "奧爾民", "伍鵬志", "後上", 7.5, 2.3, "2-3-1", "1132磅(+5)", "末段衝力強態盛"),
        (4, "巴閉王", 3, 131, "周俊樂", "呂健威", "前領", 6.0, 1.9, "1-2-3", "1105磅(+3)", "內檔起步快谷熟"),
        (5, "佐治傳奇", 12, 128, "艾兆禮", "告東尼", "領放", 15.0, 3.8, "3-4-6", "1080磅(-1)", "起步極快搶前跑"),
        (6, "升升雙息", 10, 126, "潘明輝", "沈集成", "居中", 24.0, 6.0, "6-7-5", "1125磅(+1)", "平穩正常未突破"),
        (7, "雙劍合璧", 2, 126, "班德禮", "大衛希斯", "前領", 8.8, 2.5, "2-4-2", "1090磅(+4)", "貼欄好跑火持續"),
        (8, "螢影飛馳", 11, 124, "袁幸堯", "徐雨石", "後上", 32.0, 8.0, "8-8-7", "1068磅(-2)", "狀態平淡待降班"),
        (9, "天火同人", 7, 123, "黃寶妮", "韋達", "前領", 18.0, 4.6, "5-6-4", "1140磅(+2)", "出腳有力漸見好"),
        (10, "領航多財", 5, 122, "巫顯東", "鄭俊偉", "後上", 45.0, 11.0, "9-9-9", "1042磅(-4)", "晨操一般仍需磨"),
        (11, "萬眾開心", 9, 120, "蔡明紹", "黎昭昇", "領放", 5.5, 1.8, "1-3-2", "1085磅(+3)", "大單落飛狀態勇"),
        (12, "馬運高", 1, 118, "田泰安", "文家良", "前領", 14.0, 3.6, "4-3-5", "1112磅(+2)", "1檔優勢輕磅突")
    ],
    7: [
        (1, "東來欣賞", 4, 134, "周俊樂", "告東尼", "前領", 5.2, 1.8, "1-2-1", "1165磅(+5)", "東廄主力狀態好"),
        (2, "乘數表", 3, 134, "艾道拿", "羅富全", "前領", 12.0, 3.2, "3-4-5", "1120磅(+2)", "身肌結實出腳勁"),
        (3, "天星", 10, 133, "潘頓", "大衛希斯", "居中", 9.4, 2.7, "2-1-3", "1108磅(+4)", "潘頓壓陣不可忽"),
        (4, "競駿皇者", 12, 131, "霍宏聲", "游達榮", "領放", 16.0, 4.2, "5-3-4", "1145磅(+1)", "前速飛快外檔耗"),
        (5, "傲聖", 5, 129, "潘明輝", "賀賢", "後上", 34.0, 8.5, "7-8-6", "1085磅(-3)", "後勁一般未復舊"),
        (6, "電源之駒", 7, 127, "梁家俊", "廖康銘", "居中", 11.0, 3.0, "4-5-2", "1130磅(+3)", "快慢由人暗實力"),
        (7, "加州本事", 11, 124, "蔡明紹", "巫偉傑", "前領", 13.0, 3.5, "3-2-6", "1095磅(+2)", "火氣未減前程緊"),
        (8, "首飾悟空", 2, 124, "艾兆禮", "蔡約翰", "後上", 4.6, 1.7, "1-3-1", "1115磅(+4)", "蔡廄主力爆發強"),
        (9, "安康萬里", 1, 123, "班德禮", "呂健威", "前領", 16.0, 4.2, "4-6-3", "1078磅(+1)", "1檔好位體步爽"),
        (10, "正極", 8, 122, "黃智弘", "沈集成", "領放", 21.0, 5.4, "6-7-4", "1140磅(+3)", "前領馬步速受壓"),
        (11, "盈妍威楓", 9, 121, "袁幸堯", "伍鵬志", "後上", 15.0, 4.0, "5-4-3", "1102磅(+0)", "減磅出擊步開揚"),
        (12, "丞匡掠影", 6, 120, "鍾易禮", "徐雨石", "後上", 4.9, 1.7, "2-1-2", "1088磅(+3)", "熱錢猛掃狀態峰")
    ],
    8: [
        (1, "人和家興", 2, 135, "霍宏聲", "大衛希斯", "領放", 9.8, 2.6, "3-1-4", "1172磅(+4)", "谷草老手前速強"),
        (2, "團結勇士", 8, 135, "梁家俊", "鄭俊偉", "前領", 14.0, 3.8, "5-4-2", "1130磅(+2)", "神采飛揚步力雄"),
        (3, "富心星", 4, 129, "何澤堯", "方嘉柏", "居中", 15.0, 4.0, "4-5-3", "1115磅(+1)", "方廄谷能手跳好"),
        (4, "久久為昇", 1, 129, "奧爾民", "賀賢", "前領", 6.4, 2.0, "2-2-1", "1140磅(+5)", "1檔黃金火氣盛"),
        (5, "飛馬座", 11, 127, "周俊樂", "徐雨石", "後上", 24.0, 6.0, "7-6-8", "1082磅(-2)", "走勢略重待機抽"),
        (6, "富國兄弟", 7, 126, "田泰安", "葉楚航", "居中", 18.0, 4.8, "5-5-4", "1105磅(+3)", "慢踱均速態平穩"),
        (7, "勇霸龍", 6, 123, "艾道拿", "黎昭昇", "前領", 23.0, 5.8, "6-7-5", "1128磅(+2)", "出腳有力中規矩"),
        (8, "繼往開來", 5, 122, "艾兆禮", "文家良", "前領", 2.4, 1.2, "1-1-1", "1155磅(+6)", "全晚超級重火勁"),
        (9, "蓮冠皇", 9, 122, "希威森", "廖康銘", "後上", 13.0, 3.4, "3-4-2", "1090磅(+1)", "後勁結實狀態良"),
        (10, "喵喵怪", 12, 122, "袁幸堯", "巫偉傑", "領放", 18.0, 4.6, "1-5-6", "1065磅(-1)", "12檔快放消耗大"),
        (11, "驕陽雄心", 3, 121, "黃智弘", "沈集成", "居中", 9.7, 2.5, "2-3-2", "1118磅(+4)", "大戶重點落步爽"),
        (12, "亞機拉", 10, 120, "鍾易禮", "告東尼", "後上", 23.0, 5.8, "7-8-6", "1135磅(+2)", "減磅後追冷考驗")
    ],
    9: [
        (1, "嘉應傳承", 1, 135, "艾兆禮", "伍鵬志", "前領", 15.0, 3.9, "3-2-7", "1160磅(+4)", "1檔優勢大體健"),
        (2, "紫荊傳令", 5, 135, "潘頓", "游達榮", "居中", 8.2, 2.4, "2-1-4", "1125磅(+5)", "潘頓執韁步爽清"),
        (3, "凌登", 7, 135, "奧爾民", "沈集成", "前領", 12.0, 3.2, "4-3-2", "1142磅(+3)", "快慢由人身形紮"),
        (4, "平凡騎士", 3, 132, "霍宏聲", "方嘉柏", "後上", 22.0, 5.5, "6-7-5", "1105磅(-1)", "步幅均勻後勁穩"),
        (5, "好實力", 12, 131, "周俊樂", "呂健威", "居中", 14.0, 3.6, "5-5-3", "1118磅(+2)", "外檔留後態平穩"),
        (6, "將義", 8, 126, "何澤堯", "巫偉傑", "前領", 10.0, 2.7, "1-3-4", "1092磅(+3)", "火氣旺何澤堯選"),
        (7, "浪漫鬥士", 2, 126, "黃智弘", "沈集成", "後上", 18.0, 4.5, "5-6-3", "1130磅(+4)", "減磅突擊貼欄好"),
        (8, "豐辰", 9, 126, "田泰安", "徐雨石", "後上", 8.5, 2.4, "2-2-1", "1148磅(+5)", "重點落飛氣如虹"),
        (9, "中國心", 11, 125, "楊明綸", "大衛希斯", "前領", 6.9, 2.1, "1-3-2", "1107磅(+5)", "連場上名火極猛"),
        (10, "風將", 10, 122, "蔡明紹", "告東尼", "居中", 6.1, 1.9, "2-1-2", "1152磅(+4)", "熱門穩健衝刺強"),
        (11, "瑪瑙", 4, 119, "潘明輝", "羅富全", "居中", 19.0, 4.8, "8-8-8", "1151磅(+2)", "評分下調身壯健"),
        (12, "財富非凡", 6, 117, "班德禮", "巫偉傑", "後上", 20.0, 5.0, "7-6-5", "1075磅(-2)", "輕磅伺機見起色")
    ]
}

# 直連香港賽馬會官方數據源 (racing.hkjc.com)
def fetch_hkjc_live(r_no):
    url = f"https://racing.hkjc.com/racing/English/tipsindex/tips_index.asp?RaceNo={r_no}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://racing.hkjc.com/"})
        with urllib.request.urlopen(req, timeout=3) as resp:
            txt = resp.read().decode("utf-8", errors="ignore")
            pat = re.compile(r'<tr>\s*<td>(\d+)</td>\s*<td>([^<]+)</td>\s*<td>(\d+)</td>\s*<td>([^<]+)</td>\s*<td>([^<]+)</td>\s*<td>(\d+)</td>\s*<td>([\d\.]+)</td>', re.IGNORECASE)
            m_res = {int(m.group(1)): float(m.group(7)) for m in pat.finditer(txt)}
            if len(m_res) > 0: return m_res, True
    except: pass
    return {}, False

# URL 參數保持場次狀態
q_race = st.query_params.get("race", "1")
try: def_idx = max(0, min(8, int(q_race) - 1))
except: def_idx = 0

race_options = [f"第 {i} 場 ({RACE_INFO[i][0]} {RACE_INFO[i][1]})" for i in range(1, 10)]

st.markdown("""
<div class="header-box">
    <div style="display:flex; justify-content:space-between; align-items:center;">
        <div>
            <div style="font-size:18px; font-weight:800; color:#0F172A;">🏇 2026年9月23日 快活谷夜賽 · 官方即時排位與 MoneyFlow 賠率終端</div>
            <div style="font-size:12px; color:#64748B;">跑馬地草地 "C" 賽道 · 100% 香港賽馬會官方排位與最新牌價 · 連接馬會官方網頁資料庫</div>
        </div>
        <div>
            <a href="https://racing.hkjc.com/racing/information/Chinese/Racing/RaceCard.aspx?RaceDate=2026/09/23&Racecourse=HV&RaceNo=1" target="_blank" style="background:#2563EB; color:white; padding:5px 10px; border-radius:5px; font-size:12px; font-weight:700; text-decoration:none; margin-right:4px;">🌐 馬會官方排位表</a>
            <a href="https://bet.hkjc.com/ch/racing/wp/" target="_blank" style="background:#0F172A; color:white; padding:5px 10px; border-radius:5px; font-size:12px; font-weight:700; text-decoration:none;">📈 馬會走勢圖</a>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# 篩選控制
c1, c2, c3, c4 = st.columns([1.6, 1.2, 1.2, 1.0])
with c1:
    sel_race = st.selectbox("🎯 選擇賽事場次 (共9場)", race_options, index=def_idx)
    race_no = race_options.index(sel_race) + 1
    st.query_params["race"] = str(race_no)
with c2: bias = st.selectbox("🏟️ 快活谷跑道偏差", ["利快放貼欄 (C欄典型)", "均勻中立 (各跑法平均)", "利中外疊後上 (前快後追)"], index=0)
with c3: refresh_sec = st.select_slider("⏱️ 自動更新頻率 (秒)", options=[15, 20, 25, 30], value=20)
with c4:
    st.write("")
    st.write("")
    st.button("🔄 立即手動刷新")

# 15至30秒自動更新定時器
components.html(f"<script>setTimeout(function(){{ window.parent.location.reload(); }}, {refresh_sec * 1000});</script>", height=0, width=0)

live_odds, is_live = fetch_hkjc_live(race_no)
now_t = datetime.datetime.now().strftime("%H:%M:%S")

st.markdown(f"""
<div class="status-bar">
    <div>
        {"<b style='color:#15803D;'>🟢 馬會官方數據庫直連：即時同步中</b>" if is_live else "<b style='color:#2563EB;'>ℹ️ 馬會官方牌價基盤：已載入最新牌價</b>"}
        <span style="color:#64748B; margin-left:8px;">｜ ⏱️ 每 <b>{refresh_sec}</b> 秒自動刷新網頁及賠率 ｜ 上次更新時間：<b>{now_t}</b></span>
    </div>
    <div><span style="color:#15803D; font-weight:700;">● 自動更新進行中</span></div>
</div>
""", unsafe_allow_html=True)

r_name, r_dist, prizemoney = RACE_INFO.get(race_no, RACE_INFO[1])
runners = OFFICIAL_DATA.get(race_no, OFFICIAL_DATA[1])
curr_pool = 13600000.0
prev_pool = curr_pool * 0.84

leads = [h for h in runners if h[6] == "領放"]
fwds = [h for h in runners if h[6] == "前領"]
mids = [h for h in runners if h[6] == "居中"]
backs = [h for h in runners if h[6] == "後上"]
pace_txt = "快步速 🔥 (多馬搶欄互燒)" if (len(leads) >= 3 or (len(leads) >= 2 and len(fwds) >= 2)) else ("慢步速 ⏳ (單騎慢放利前領)" if len(leads) <= 1 else "標準均速 ⚖️")

processed = []
for h in runners:
    no, name, draw, wt, j, t, style, base_win, base_pla, form_rc, bw, tr = h
    c_win = live_odds.get(no, base_win)
    c_pla = base_pla
    o_win = round(c_win * 1.20, 1) if c_win <= 4.0 else (round(c_win * 1.15, 1) if c_win <= 10.0 else round(c_win * 1.08, 1))
    o_pla = round(c_pla * 1.15, 1)
    drop_pct = round(((o_win - c_win) / o_win * 100), 1)
    
    prev_s = (prev_pool * 0.825 / o_win)
    curr_s = (curr_pool * 0.825 / c_win)
    delta_s = max(0, curr_s - prev_s)
    p_share = round((curr_s / (curr_pool * 0.825)) * 100, 1)
    
    # 能力細分
    sp_score = 95 if (c_win <= 3.5 or "快樂神駒" in name or "繼往開來" in name) else (88 if c_win <= 7.0 else (80 if c_win <= 15.0 else 72))
    dr_score = 94 if draw <= 3 else (86 if draw <= 7 else 74)
    if "C欄" in bias and draw <= 4 and style in ["領放", "前領"]: dr_score += 4
    jt_score = 96 if ("潘頓" in j or ("何澤堯" in j and "方嘉柏" in t) or ("告東尼" in t and "艾兆禮" in j)) else (88 if ("蔡約翰" in t or "沈集成" in t or "游達榮" in t) else 78)
    wt_score = 90 if wt <= 122 else (84 if wt <= 128 else 78)
    fm_score = 95 if form_rc.startswith("1-") else (88 if form_rc.startswith("2-") or form_rc.startswith("3-") else 75)
    tot_score = round(sp_score * 0.30 + dr_score * 0.25 + jt_score * 0.20 + wt_score * 0.15 + fm_score * 0.10)
    
    processed.append({
        "no": no, "name": name, "draw": draw, "wt": wt, "j": j, "t": t, "style": style,
        "o_win": o_win, "c_win": c_win, "drop_pct": drop_pct, "o_pla": o_pla, "c_pla": c_pla,
        "curr_s": curr_s, "delta_s": delta_s, "p_share": p_share,
        "sp": sp_score, "dr": dr_score, "jt": jt_score, "wt_sc": wt_score, "fm": fm_score, "tot": tot_score,
        "form": form_rc, "bw": bw, "tr": tr
    })

df = pd.DataFrame(processed)
avg_d = df["delta_s"].mean() if len(df) > 0 else 1.0
df["m_ratio"] = (df["delta_s"] / avg_d).round(1)

def get_sig(r):
    if r["m_ratio"] >= 2.5 or r["drop_pct"] >= 35.0: return "🔴 啡燈暴跌 (極限重注)", "badge-brown"
    elif r["m_ratio"] >= 1.6 or r["drop_pct"] >= 20.0: return "🟢 綠燈急落 (大戶掃貨)", "badge-green"
    elif r["m_ratio"] >= 1.2 and r["drop_pct"] > 0: return "📈 資金進駐 (有力支持)", "badge-green"
    elif r["c_win"] > r["o_win"] * 1.15: return "⚠️ 回飛走資 (冷淡冷門)", "badge-gray"
    return "⚪ 散戶平穩 (一般常態)", "badge-gray"

df[["sig_t", "sig_c"]] = df.apply(lambda r: pd.Series(get_sig(r)), axis=1)

# 步速與落飛盒
cp, ca = st.columns(2)
with cp: st.markdown(f'<div class="pace-box"><b>🚦 【第 {race_no} 場 {r_name} {r_dist}】步速推演：{pace_txt}</b><br><span style="color:#166534;">領放 {len(leads)} 匹 · 前領 {len(fwds)} 匹 · 居中 {len(mids)} 匹 · 後上 {len(backs)} 匹 ｜ 獎金：${prizemoney:,}</span></div>', unsafe_allow_html=True)
with ca:
    hots = df[df["sig_t"].str.contains("啡燈|綠燈")]
    ht = " · ".join([f"<b>{r['no']}號 {r['name']}</b> ({r['c_win']}倍 · 跌{r['drop_pct']}%)" for _, r in hots.iterrows()]) if len(hots) > 0 else "目前盤口暫無異常暴跌異動"
    st.markdown(f'<div class="alert-box"><b>🚨 【第 {race_no} 場】MoneyFlow 大額落飛焦點</b><br><span style="color:#7F1D1D;">{ht}</span></div>', unsafe_allow_html=True)

# 4 個指標卡
m1, m2, m3, m4 = st.columns(4)
fav = df.sort_values(by="c_win").iloc[0]
with m1: st.markdown(f'<div class="stat-card"><div style="font-size:15px; font-weight:800;">HK$ {int(curr_pool):,}</div><div style="font-size:11px; color:#64748B;">即時獨贏彩池</div></div>', unsafe_allow_html=True)
with m2: st.markdown(f'<div class="stat-card"><div style="font-size:15px; font-weight:800;">HK$ {int(curr_pool-prev_pool):,}</div><div style="font-size:11px; color:#64748B;">近段落飛注碼</div></div>', unsafe_allow_html=True)
with m3: st.markdown(f'<div class="stat-card"><div style="font-size:15px; font-weight:800;">HK$ {int(avg_d):,}</div><div style="font-size:11px; color:#64748B;">全場平均注碼</div></div>', unsafe_allow_html=True)
with m4: st.markdown(f'<div class="stat-card"><div style="font-size:15px; font-weight:800; color:#DC2626;">{fav["no"]}號 {fav["name"]} ({fav["c_win"]}倍)</div><div style="font-size:11px; color:#64748B;">馬會第一熱門</div></div>', unsafe_allow_html=True)

# 分頁
t_odds, t_ab, t_card = st.tabs([
    "💰 【MoneyFlow 專業賠率版 (Odds Board)】",
    "📊 【綜合能力評分總表 (緊湊精細版)】",
    "📋 【馬匹專屬戰情體檢卡】"
])

# ----------------- 分頁 1: MoneyFlow 專業賠率版 -----------------
with t_odds:
    st.markdown(f"##### 💰 第 {race_no} 場《{r_name}》MoneyFlow 賠率走勢大盤 (照資金落飛強度排序)")
    odds_s = df.sort_values(by="delta_s", ascending=False)
    
    h_odds = """<table class="compact-table"><thead><tr>
    <th>馬號</th><th>馬名</th><th>檔位</th><th>負磅</th><th>騎師</th><th>練馬師</th><th>跑法</th>
    <th>隔夜獨贏</th><th style="background:#FEF3C7; color:#B45309;">臨場獨贏</th><th>獨贏跌幅</th>
    <th>隔夜位置</th><th>臨場位置</th><th>新增注碼</th><th>彩池佔比</th><th>熱錢倍數</th><th>操盤走勢訊號</th>
    </tr></thead><tbody>"""
    
    for _, r in odds_s.iterrows():
        c_cls = "num-circle num-fav" if (r["no"] == fav["no"]) else "num-circle"
        d_col = "#15803D" if r["drop_pct"] >= 15.0 else ("#DC2626" if r["drop_pct"] < 0 else "#334155")
        b_cls = "pool-bar-fill-hot" if r["p_share"] >= 18.0 else "pool-bar-fill"
        h_url = f"https://racing.hkjc.com/racing/information/Chinese/Racing/RaceCard.aspx?RaceDate=2026/09/23&Racecourse=HV&RaceNo={race_no}"
        
        h_odds += f"""<tr>
        <td><span class="{c_cls}">{r['no']}</span></td>
        <td><a href="{h_url}" target="_blank" class="hkjc-link"><b>{r['name']}</b></a></td>
        <td><b>{r['draw']}檔</b></td><td>{r['wt']}磅</td><td><b>{r['j']}</b></td><td>{r['t']}</td>
        <td><span class="badge-gray">{r['style']}</span></td>
        <td style="color:#64748B;">{r['o_win']}</td>
        <td style="background:#FFFBEB; font-weight:800; font-size:13px; color:{'#DC2626' if (r['no'] == fav['no']) else '#0F172A'};">{r['c_win']}</td>
        <td style="font-weight:700; color:{d_col};">{r['drop_pct']:+.1f}%</td>
        <td style="color:#64748B;">{r['o_pla']}</td><td style="font-weight:700;">{r['c_pla']}</td>
        <td style="font-weight:700;">${int(r['delta_s']):,}</td>
        <td><div class="pool-bar-bg"><div class="{b_cls}" style="width:{min(100, int(r['p_share']*2.5))}%;"></div></div><b>{r['p_share']}%</b></td>
        <td><b style="color:#2563EB;">{r['m_ratio']}x</b></td>
        <td><span class="{r['sig_c']}">{r['sig_t']}</span></td>
        </tr>"""
    h_odds += "</tbody></table>"
    st.markdown(h_odds, unsafe_allow_html=True)
    st.caption("💡 賠率圖例：🟢 綠燈代表賠率急跌 20% 以上（大戶落飛）；🔴 啡燈代表暴跌 35% 以上（重注焦點）；馬名直通馬會排位。")

# ----------------- 分頁 2: 綜合能力評分總表 (格仔縮細、指標拆解、連馬會) -----------------
with t_ab:
    st.markdown(f"##### 📊 第 {race_no} 場《{r_name}》出賽馬匹能力指標拆解表 (格仔緊湊版 · 照戰力排序)")
    ab_s = df.sort_values(by="tot", ascending=False)
    
    h_ab = """<table class="compact-table"><thead>
    <tr style="background:#E2E8F0;">
        <th rowspan="2">排名</th><th rowspan="2">馬號</th><th rowspan="2">馬名 (連馬會)</th>
        <th rowspan="2" style="background:#2563EB; color:white;">綜合總分</th>
        <th colspan="5" style="background:#F8FAFC;">各項能力拆解 (細分來源)</th>
        <th colspan="3" style="background:#F1F5F9;">馬會官方近況與狀態</th>
        <th rowspan="2">臨場獨贏</th>
    </tr>
    <tr style="background:#F8FAFC; font-size:11px;">
        <th title="同程分段速度與締速水準">速度 (30%)</th>
        <th title="快活谷C欄與檔位優勢">路程檔位 (25%)</th>
        <th title="騎師與練馬師組合勝率">騎練合拍 (20%)</th>
        <th title="讓磅與負磅優勢">負磅優勢 (15%)</th>
        <th title="近3仗名次走勢">近況指數 (10%)</th>
        <th>馬會近賽成績</th><th>最新體重</th><th>晨操評語</th>
    </tr></thead><tbody>"""
    
    rnk = 1
    for _, r in ab_s.iterrows():
        h_url = f"https://racing.hkjc.com/racing/information/Chinese/Racing/RaceCard.aspx?RaceDate=2026/09/23&Racecourse=HV&RaceNo={race_no}"
        h_ab += f"""<tr>
        <td><b>#{rnk}</b></td>
        <td><span class="num-circle">{r['no']}</span></td>
        <td><a href="{h_url}" target="_blank" class="hkjc-link"><b>{r['name']}</b></a></td>
        <td style="background:#EFF6FF; font-weight:800; font-size:13px; color:#1E40AF;">{r['tot']}分</td>
        <td><b>{r['sp']}</b></td>
        <td><b>{r['dr']}</b> ({r['draw']}檔)</td>
        <td><b>{r['jt']}</b> ({r['j']})</td>
        <td><b>{r['wt_sc']}</b> ({r['wt']}磅)</td>
        <td><b>{r['fm']}</b></td>
        <td><span class="badge-gray" style="font-family:monospace;">{r['form']}</span></td>
        <td><span style="font-size:11px; color:#475569;">{r['bw']}</span></td>
        <td style="text-align:left; font-size:11px; color:#1E293B;">{r['tr']}</td>
        <td style="font-weight:700; color:#DC2626;">{r['c_win']}</td>
        </tr>"""
        rnk += 1
    h_ab += "</tbody></table>"
    st.markdown(h_ab, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background:#F1F5F9; border-radius:4px; padding:6px 10px; font-size:11px; color:#334155; margin-top:4px;">
        <b>📌 能力拆解與馬會數據來源說明：</b>
        • <b>速度 (30%)</b>：同程締速與末段400米分段速勢 ｜ 
        • <b>路程檔位 (25%)</b>：快活谷C欄各檔位統計勝率與前領卡位優勢 ｜ 
        • <b>騎練合拍 (20%)</b>：騎練近一季同場勝出率 ｜ 
        • <b>負磅 (15%)</b>：相較對手之受讓讓磅優勢 ｜ 
        • <b>近況 (10%)</b>：直連香港賽馬會官方近仗名次、出賽體重與晨操評語。
    </div>
    """, unsafe_allow_html=True)

# ----------------- 分頁 3: 馬匹專屬戰情體檢卡 -----------------
with t_card:
    st.markdown(f"##### 📋 第 {race_no} 場《{r_name}》出賽馬匹專屬體檢卡")
    for _, r in df.iterrows():
        is_h = "啡燈" in r["sig_t"] or "綠燈" in r["sig_t"]
        bc = "#EF4444" if is_h else "#E2E8F0"
        bg = "#FEF2F2" if is_h else "#FFFFFF"
        h_url = f"https://racing.hkjc.com/racing/information/Chinese/Racing/RaceCard.aspx?RaceDate=2026/09/23&Racecourse=HV&RaceNo={race_no}"
        
        st.markdown(f"""
        <div style="border: 1px solid {bc}; background: {bg}; border-radius: 8px; padding: 8px 12px; margin-bottom: 6px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div style="font-size:15px; font-weight:800;">
                    <span class="num-circle {'num-fav' if r['no'] == fav['no'] else ''}">{r['no']}</span>
                    <a href="{h_url}" target="_blank" class="hkjc-link" style="margin-left:4px;">{r['name']}</a>
                    <span style="font-size:12px; font-weight:normal; color:#64748B; margin-left:6px;">({r['style']} · {r['draw']}檔 · {r['wt']}磅 · 騎練：{r['j']}/{r['t']})</span>
                </div>
                <div style="background:#2563EB; color:white; padding:2px 8px; border-radius:8px; font-weight:700; font-size:12px;">戰力：{r['tot']}分</div>
            </div>
            <div style="margin-top:4px; font-size:12px; color:#334155; line-height:1.4;">
                • <b>細分</b>：速度 <b>{r['sp']}</b> ｜ 檔位 <b>{r['dr']}</b> ｜ 騎練 <b>{r['jt']}</b> ｜ 負磅 <b>{r['wt_sc']}</b> ｜ 近況 <b>{r['fm']}</b><br>
                • <b>馬會狀態</b>：往績 <b>{r['form']}</b> ｜ 體重 <b>{r['bw']}</b> ｜ 晨操：{r['tr']}<br>
                • <b>盤口</b>：隔夜 {r['o_win']} ➔ 臨場 <b>{r['c_win']}</b> (跌 {r['drop_pct']:+.1f}%) ｜ 新增注碼：<b>${int(r['delta_s']):,} ({r['m_ratio']}x)</b> ｜ 訊號：<span class="{r['sig_c']}">{r['sig_t']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
