'''
作者 : wade chen
測試日期 : 2019/2/28
'''

import requests
import os
import re
import time
import datetime
import pymysql

# 使用chrome瀏覽器資訊
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36',
}

# 創建網路連接
s = requests.Session()
# 先訪問網頁取得後續網頁內容認證項目,連接網址為威力彩路徑 ; 大樂透查詢路徑為 http://www.taiwanlottery.com.tw/Lotto/Lotto649/history.aspx ; 大福彩查詢路徑為 http://www.taiwanlottery.com.tw/Lotto/Lotto740/history.aspx
url = 'http://www.taiwanlottery.com.tw/Lotto/Lotto740/history.aspx'

# 需先獲取網頁查詢資訊"認證"及可查詢最大年份 ;
r = s.get(url=url, headers=headers)
__VIEWSTATEGENERATORpat = re.compile('<input.*?id="__VIEWSTATEGENERATOR" value="(.*?)" />')
__VIEWSTATEGENERATOR = __VIEWSTATEGENERATORpat.findall(r.text)[0]
__VIEWSTATEpat = re.compile('<input.*?id="__VIEWSTATE" value="(.*?)" />')
__VIEWSTATE = __VIEWSTATEpat.findall(r.text)[0]
__EVENTVALIDATIONpat = re.compile('<input.*?id="__EVENTVALIDATION" value="(.*?)" />')
__EVENTVALIDATION = __EVENTVALIDATIONpat.findall(r.text)[0]

# 從此年開始抓取各年份完整紀錄,官網最早只能選從103年開始
# 大福彩最早可查詢日期為104年4月
start_year = 104
# 查詢結束年份,預設將官網所設定的最新年份定為可查詢最大年份設定
last_yearpat = re.compile('<option selected="selected" value="\d\d\d">(.*?)</option>')
last_year = last_yearpat.findall(r.text)[0]

# 資料儲存成檔案設定,預設儲存在 D 磁碟跟目錄下存成 SuperLotto638_日期.txt 文件
# 儲存路徑
filepath = 'd:\\'
# 儲存檔案名稱
today = str(datetime.date.today()).replace('-', '')
filename = 'SuperLotto638' + '_' + today + '.txt'
# 將路徑和檔案名稱結合成完整路徑
savepath = os.path.join(filepath, filename)

# mysql連接資料
host = '資料庫位置'
port = 3306
user = '使用者名稱'
password = '密碼'
database = '連接資料庫名稱'
charset = 'utf8'


# 如要將查詢資訊寫入資料庫需自行新增mysql資料庫並建立 Lotto740的資料表,

# 大福彩,大福彩開獎日期從105年8月24日(第102000068期)開始才有第8位特別號
def Lotto740(savedata, updatedb):
    url = 'http://www.taiwanlottery.com.tw/Lotto/Lotto740/history.aspx'
    # 查詢y年m月的開獎號碼
    for y in range(start_year, int(last_year) + 1):
        if y < 104:
            print('大福彩可查詢年份從104年開始')
            continue
        elif y == 104:
            month = range(4, 13)
        else:
            month = range(1, 13)
        for m in month:
            # 先將無資料旗標設定為假
            nodata_flog = False
            # 如果無資料旗標沒有變為True則進入資料查詢
            if not nodata_flog:
                # 查詢表單提交格式
                post_data = {
                    '__EVENTTARGET': '',
                    '__EVENTARGUMENT': '',
                    '__LASTFOCUS': '',
                    '__VIEWSTATE': __VIEWSTATE,
                    '__VIEWSTATEGENERATOR': __VIEWSTATEGENERATOR,
                    '__EVENTVALIDATION': __EVENTVALIDATION,
                    'Lotto740Control_history$DropDownList1': '11',
                    'Lotto740Control_history$chk': 'radYM',
                    'Lotto740Control_history$dropYear': y,
                    'Lotto740Control_history$dropMonth': m,
                    'Lotto740Control_history$btnSubmit': '查詢'
                }

                # 建立請求對象
                request = s.get(url=url, headers=headers)
                # 發送資料請求
                lottodata = s.post(url=url, headers=headers, data=post_data)

                # 確認是否有資料
                nodatapat = re.compile('<span id="Lotto740Control_history_Label1".*?>(.*?)</span>')
                nodata = nodatapat.findall(lottodata.text)[0]
                if nodata == "查無資料":
                    # 如果沒有資料則將無資料旗標改為True,並跳出循環
                    nodata_flog = True
                    print('%s年%s月份已經查無資料' % (y, m))
                    break

                # 期別
                DrawTermpat = re.compile(
                    r'<span id="Lotto740Control_history_dlQuery_L740_DrawTerm_\d{1,2}">(.*?)</span>')
                DrawTerm = DrawTermpat.findall(lottodata.text)
                # 開獎日
                DDatepat = re.compile(r'<span id="Lotto740Control_history_dlQuery_L740_DDate_\d{1,2}">(.*?)</span>')
                DDate = DDatepat.findall(lottodata.text)
                # 兌獎截止日
                EDatepat = re.compile(r'<span id="Lotto740Control_history_dlQuery_L740_EDate_\d{1,2}">(.*?)</span>')
                EDate = EDatepat.findall(lottodata.text)
                # 開獎大小順序 前6個號碼為第一區數字 第7個號碼為第二區數字
                No1pat = re.compile(r'<span id="Lotto740Control_history_dlQuery_No1_\d{1,2}">(.*?)</span>')
                No1 = No1pat.findall(lottodata.text)
                No2pat = re.compile(r'<span id="Lotto740Control_history_dlQuery_No2_\d{1,2}">(.*?)</span>')
                No2 = No2pat.findall(lottodata.text)
                No3pat = re.compile(r'<span id="Lotto740Control_history_dlQuery_No3_\d{1,2}">(.*?)</span>')
                No3 = No3pat.findall(lottodata.text)
                No4pat = re.compile(r'<span id="Lotto740Control_history_dlQuery_No4_\d{1,2}">(.*?)</span>')
                No4 = No4pat.findall(lottodata.text)
                No5pat = re.compile(r'<span id="Lotto740Control_history_dlQuery_No5_\d{1,2}">(.*?)</span>')
                No5 = No5pat.findall(lottodata.text)
                No6pat = re.compile(r'<span id="Lotto740Control_history_dlQuery_No6_\d{1,2}">(.*?)</span>')
                No6 = No6pat.findall(lottodata.text)
                No7pat = re.compile(r'<span id="Lotto740Control_history_dlQuery_No7_\d{1,2}">(.*?)</span>')
                No7 = No7pat.findall(lottodata.text)
                No8pat = re.compile(r'<span id="Lotto740Control_history_dlQuery_SNo8_\d{1,2}">(.*?)</span>')
                No8 = No8pat.findall(lottodata.text)

                # 連結mysql資料庫
                if updatedb:
                    conn = pymysql.connect(host=host, port=port, user=user, password=password, db=database,
                                           charset=charset)
                    cursor = conn.cursor()

                # 數據處理
                # 官網會先提供由大到小的期數,改為由小到大的期數順序
                for i in range(len(DrawTerm) - 1, -1, -1):
                    # 寫入資料庫,需先確認表格名稱及各欄位名稱對應狀況
                    if updatedb:
                        try:
                            sql = "insert into lotto_lotto740(drawterm,no1,no2,no3,no4,no5,no6,no7,no8,ddate,edate) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                            ret = cursor.execute(sql,
                                                 [DrawTerm[i], No1[i], No2[i], No3[i], No4[i], No5[i], No6[i], No7[i],
                                                  No8[i], DDate[i], EDate[i]])
                            conn.commit()
                        except Exception as err:
                            print('寫入資料庫出現錯誤 : %s' % err)

                    # 螢幕顯示處理數據
                    print('開始查詢%s年%s月份資訊 :' % (y, m))
                    print("第%s期大福彩, 開獎日期:%s,兌獎截止日期:%s" % (DrawTerm[i], DDate[i], EDate[i]))
                    print("號碼大小順序為 :%s,%s,%s,%s,%s,%s,%s,特別號號碼為:%s" % (
                        No1[i], No2[i], No3[i], No4[i], No5[i], No6[i], No7[i], No8[i]))
                    print('=' * 100)

                    # 將數據寫入文件
                    if savedata:
                        filedata = DrawTerm[i] + ';' + No1[i] + ';' + No2[i] + ';' + No3[i] + ';' + No4[i] + ';' + No5[
                            i] + ';' + \
                                   No6[i] + ';' + No7[i] + ';' + No8[i] + ';' + DDate[i] + ';' + EDate[i] + '\r\n'
                        with open(savepath, "a+", encoding="utf8") as f:
                            f.write(filedata)

                # 關閉資料庫連接
                if updatedb:
                    cursor.close()
                    conn.close()

                # 避免伺服器查詢負載過大,切換月份時延遲3秒再進行下一次查詢
                time.sleep(3)


def main():
    # 想在電腦儲存檔案請將參數改為 savedata=True , 想將資料寫入數據庫請將updatedb = False改為updatedb = True
    # 抓取大福彩資料
    Lotto740(savedata=False, updatedb=False)

if __name__ == '__main__':
    main()
