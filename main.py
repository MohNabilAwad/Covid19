import requests
import bs4
import json
from ftplib import FTP
import datetime
import time

#https://www.youtube.com/watch?v=e22HHgFqdm0
page = requests.get("https://www.worldometers.info/coronavirus/")
soup=bs4.BeautifulSoup(page.text,'lxml')

table = soup.find('table',id="main_table_countries_today")

headers= [heading.text.replace(",Other","") for heading in table.find_all('th')]
table_rows = [row for row in table.find_all('tr')]

results = [{headers[index]:cell.text for index,cell in enumerate(row.find_all('td'))} for row in table_rows]


now = datetime.datetime.now()

data = {}
data['Info'] = []
data['Info'].append({
    'Last Update': now.strftime("%Y-%m-%d %H:%M:%S")
                    })
data['Covid19'] = []


for i in results:
    if("Country" in i):

        if(i["Country"] != "Total:" and i["#"]!=""):
            data['Covid19'].append({
               'Country': i["Country"].replace("\n",""),
               'ActiveCases': i["ActiveCases"],
                'Population': i["Population"]
                })

with open('data.json', 'w') as outfile:
    json.dump(data, outfile)

FTP.maxline = 163840
ftp = FTP('ftpupload.net')
ftp.login(user="epiz_26155908",passwd="CziCHHeOvM3jNLJ")
ftp.cwd("/mohamad-awad.info/htdocs/")
filename = 'data.json'
ftp.storlines('STOR ' + filename, open(filename, 'rb'))
ftp.quit()

print("Done " + now.strftime("%Y-%m-%d %H:%M:%S"))

time.sleep(10)
