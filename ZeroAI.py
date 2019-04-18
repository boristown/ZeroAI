import os
import glob
import re

html_path = "HTML/"
Equities_path = os.path.join(html_path, "*股市*.htm*")
Equities_pattern = r'<td\sclass="bold\sleft\snoWrap\selp\splusIconTd">.+?boundblank="">([^><"]+)</a><span.+?data-id="(\d+)"'
dirs = glob.glob( Equities_path )

url = "https://www.investing.com/instruments/HistoricalDataAjax"

for file_path in dirs:
    print( file_path )