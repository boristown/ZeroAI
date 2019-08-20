import os
import glob
import re
import requests
import datetime
import time

mode=6

markets = {
    1: "Stocks",
    2: "Crypto",
    3: "Currencies",
    4: "Stocks2",
    5: "指数",
    6: "Indices"
    }
startdays = {
    1: 180,
    2: 120,
    3: 365,
    4: 180,
    5: 180,
    6: 180,
    }
paths = {
    1: "Stocks/",
    2: "Crypto/",
    3: "Currencies/",
    4: "Stocks/2/",
    5: "指数",
    6: "Indices",
    }
MaxRows = {
    1: 10000,
    2: 200,
    3: 1000,
    4: 10000,
    5: 200,
    6: 200,
    }
patterns = {
    1: r'<td\sclass="bold\sleft\snoWrap\selp\splusIconTd">.+?boundblank="">([^><"]+)</a><span.+?data-id="(\d+)"',
    2: r'<tr.+?rank\sicon">\d+<.+?title="(.+?)".+?title=".+?".+?pid-(\d+)-last.+?</tr>',
    3: r'class="bold\sleft\snoWrap\selp\splusIconTd".+?boundblank="">([^><"]+)</a>.+?\sdata-id="(\d+)"',
    4: r'<td\sclass="bold\sleft\snoWrap\selp\splusIconTd">.+?boundblank="">([^><"]+)</a><span.+?data-id="(\d+)"',
    #<span data-name="上证指数" data-id="40820" data-volume="35,105,617,183" class="alertBellGrayPlus js-plus-icon genToolTip oneliner" data-tooltip="创建提醒"></span>
    5: r'<td\sclass="flag".+?title="([^><"]+)".+?<span\sdata-name="([^><"]+)"\sdata-id="(\d+)"',
    6: r'<td\sclass="flag".+?title="([^><"]+)".+?<span\sdata-name="([^><"]+)"\sdata-id="(\d+)"',
    }

html_path = "HTML/" + paths[mode]
#html_path = "HTML/Crypto/"
Equities_path = os.path.join(html_path, "*.htm*")
Equities_pattern = patterns[mode]
#Equities_pattern = r'<tr.+?rank\sicon">\d+<.+?title="(.+?)".+?title=".+?".+?pid-(\d+)-last.+?</tr>'
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

st_date_str = (datetime.datetime.utcnow() + datetime.timedelta(days = -startdays[mode])).strftime("%m-%d-%Y").replace("-","%2F")
end_date_str = (datetime.datetime.utcnow()).strftime("%m-%d-%Y").replace("-","%2F")

symbol_index = 0
list_filename = os.path.join('Output/' + markets[mode] +'/list-' + markets[mode] + '.txt')
price_filename = os.path.join('Output/' + markets[mode] +'/price-' + markets[mode] + '_' + datetime.datetime.utcnow().strftime("%Y%m%d") + '.csv')
reversed_filename = os.path.join('Output/' + markets[mode] +'/reversed-' + markets[mode] + '_' + datetime.datetime.utcnow().strftime("%Y%m%d") + '.csv')
list_file = open(list_filename, "w", encoding="utf-8")
price_file = open(price_filename, "w", encoding="utf-8")
reversed_file = open(reversed_filename, "w", encoding="utf-8")
list_file.truncate()
price_file.truncate()
reversed_file.truncate()
for file_path in dirs:
    print( file_path )
    file = open( file_path, "r", encoding="utf-8" )
    file_str = file.read()
    symbols_match = re.finditer(Equities_pattern,file_str,re.S)
    marketName = os.path.basename(file_path).split('.')[0] 
    price_line = ''
    reversed_line = ''
    for symbol_match in symbols_match:
        if len(symbol_match.groups()) == 3:
            marketName = symbol_match.group(1)
            symbol_str = symbol_match.group(2)
            curr_id_str = symbol_match.group(3)
        else:
            symbol_str = symbol_match.group(1)
            curr_id_str = symbol_match.group(2)
        symbol_str=symbol_str.replace("amp;", "")
        if int(curr_id_str) < 1:
           continue
        time.sleep(0.5)
        payload = "action=historical_data&curr_id="+curr_id_str+"&end_date=" + end_date_str + "&header=null&interval_sec=Daily&smlID=&sort_col=date&sort_ord=DESC&st_date=" + st_date_str
        while True:
            try:
                response = requests.request("POST", url, data=payload, headers=headers, verify=False)
                break
            except:
                print("Retry after 7 seconds……")
                time.sleep(3)
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
            if price_count == 1 or price != price_list[price_count-2]:
                price_list.append(price)
            else:
                price_count -= 1
        if len(price_list) != 100:
            print(len(price_list))
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
            reversed_file.write("\n")
        list_file.write(marketName + "\t" + symbol_str)
        price_line = ""
        reversed_line = ""
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
                reversed_line = "," + reversed_line
            price_line += str(price_list[i])
            reversed_line = str(price_list[i]) + reversed_line
        price_file.write(price_line)
        reversed_file.write(reversed_line)
        if symbol_index>=MaxRows[mode]:
            break
        #print(price_line)
list_file.close()
price_file.close()
reversed_file.close()