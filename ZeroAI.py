import os
import glob
import re
import requests
import datetime
import time

html_path = "HTML/Stocks/"
Equities_path = os.path.join(html_path, "*美国*.htm*")
Equities_pattern = r'<td\sclass="bold\sleft\snoWrap\selp\splusIconTd">.+?boundblank="">([^><"]+)</a><span.+?data-id="(\d+)"'
dirs = glob.glob( Equities_path )

url = "https://www.investing.com/instruments/HistoricalDataAjax"

headers = {
    'accept': "text/plain, */*; q=0.01",
    'origin': "https://www.investing.com",
    'x-requested-with': "XMLHttpRequest",
    'user-agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36",
    'content-type': "application/x-www-form-urlencoded",
    'cache-control': "no-cache",
    'postman-token': "17db1643-3ef6-fa9e-157b-9d5058f391e4"
    }

st_date_str = (datetime.datetime.utcnow() + datetime.timedelta(days = -200)).strftime("%m-%d-%Y").replace("-","%2F")
end_date_str = (datetime.datetime.utcnow()).strftime("%m-%d-%Y").replace("-","%2F")

for file_path in dirs:
    print( file_path )
    file = open( file_path, "r", encoding="utf-8" )
    file_str = file.read()
    symbol_index = 0
    symbols_match = re.finditer(Equities_pattern,file_str,re.S)
    marketName = os.path.basename(file_path).split('.')[0] 
    list_filename = os.path.join('Output/Stocks/list-' + marketName + '.txt')
    price_filename = os.path.join('Output/Stocks/price-' + marketName + '.csv')
    list_file = open(list_filename, "w", encoding="utf-8")
    price_file = open(price_filename, "w", encoding="utf-8")
    list_file.truncate()
    price_file.truncate()
    price_line = ''
    for symbol_match in symbols_match:
        curr_id_str = symbol_match.group(2)
        if int(curr_id_str) < 1:
           continue
        symbol_str = symbol_match.group(1)
        time.sleep(1)
        payload = "action=historical_data&curr_id="+curr_id_str+"&end_date=" + end_date_str + "&header=null&interval_sec=Daily&smlID=&sort_col=date&sort_ord=DESC&st_date=" + st_date_str
        while True:
            try:
                response = requests.request("POST", url, data=payload, headers=headers, verify=False)
                break
            except:
                print("Retry after 7 seconds……")
                time.sleep(7)
        table_pattern = r'<tr>.+?<td.+?data-real-value="([^><"]+?)".+?</td>' \
            '.+?data-real-value="([^><"]+?)".+?</td>.+?data-real-value="([^><"]+?)".+?</td>'  \
            '.+?data-real-value="([^><"]+?)".+?</td>.+?data-real-value="([^><"]+?)".+?</td>'  \
            '.+?data-real-value="([^><"]+?)".+?</td>'
        row_matchs = re.finditer(table_pattern,response.text,re.S)
        price_list = []
        price_count = 0
        for cell_matchs in row_matchs:
            price_count += 1
            if price_count > 100:
                break
            price = float(str(cell_matchs.group(2)).replace(",",""))
            price_list.append(price)
        if len(price_list) != 100:
            continue
        max_price = max(price_list)
        min_price = min(price_list)
        center_price = (max_price + min_price) / 2
        range_price = max_price - min_price
        if range_price <= 0:
            continue
        symbol_index+=1
        if symbol_index > 1:
            list_file.write("\n")
            price_file.write("\n")
        list_file.write(symbol_str)
        price_line = ""
        print( "%d\t%s\t%s" % (symbol_index, curr_id_str, symbol_str)  )
        for i in range(len(price_list)):
            price_list[i] -= center_price
            price_list[i] /= range_price
            price_list[i] += 0.5
            if price_list[i] > 0.99999:
                price_list[i] = 1.0
            elif price_list[i] < 0.00001:
                price_list[i] = 0.0
            if price_line != "":
                price_line += ","
            price_line += str(price_list[i])
        price_file.write(price_line)
        print(price_line)
    list_file.close()
    price_file.close()
