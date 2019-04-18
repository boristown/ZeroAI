import os
import glob
import re

html_path = "HTML/Stocks/"
Equities_path = os.path.join(html_path, "*.htm*")
Equities_pattern = r'<td\sclass="bold\sleft\snoWrap\selp\splusIconTd">.+?boundblank="">([^><"]+)</a><span.+?data-id="(\d+)"'
dirs = glob.glob( Equities_path )

url = "https://www.investing.com/instruments/HistoricalDataAjax"

for file_path in dirs:
    print( file_path )
    file = open( file_path, "r", encoding="utf-8" )
    file_str = file.read()
    symbol_index = 0
    symbols_match = re.finditer(Equities_pattern,file_str,re.S)
    #end_date_str = (datetime.datetime.utcnow() + datetime.timedelta(days = -1)).strftime("%m-%d-%Y").replace("-","%2F")
    for symbol_match in symbols_match:
        symbol_index+=1
        curr_id_str = symbol_match.group(2)
        if int(curr_id_str) < 1:
           continue
        symbol_str = symbol_match.group(1)
        print( "%d\t%s\t%s" % (symbol_index, curr_id_str, symbol_str)  )