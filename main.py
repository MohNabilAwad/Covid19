import requests
import bs4
import json
from ftplib import FTP
import datetime
import csv

# https://www.youtube.com/watch?v=e22HHgFqdm0
page = requests.get("https://www.worldometers.info/coronavirus/")
soup = bs4.BeautifulSoup(page.text,'lxml')

table = soup.find('table',id="main_table_countries_today")

headers = [heading.text.replace(",Other","") for heading in table.find_all('th')]
table_rows = [row for row in table.find_all('tr')]

results = [{headers[index]:cell.text for index,cell in enumerate(row.find_all('td'))} for row in table_rows]
now = datetime.datetime.now()

csv_file = open('ICU Beds.csv')
reader = csv.reader(csv_file, delimiter=',')
ICUBEDS = list(reader)

one = 'Lc05' # smaller than 0.05
two = 'Mc05' # bigger than 0.05
three = 'Mc10' # bigger than 0.1
four = 'Mc50' # bigger than 0.5
five = 'M1' # bigger than 1
six = 'M2' # bigger than 2
seven = 'M10' # bigger than 10
eight = 'M50' # bigger than 50

def RateCategory(Rate):
    if(0.0000001 < Rate < 0.05):
        return one
    if (0.05 < Rate < 0.1):
        return two
    if(0.1 < Rate < 0.5):
        return three
    if(0.5<Rate<1):
        return four
    if(1<Rate<2):
        return five
    if(2<Rate<10):
        return six
    if(10<Rate<50):
        return seven
    if(Rate>50):
        return eight
    if(Rate == 0 ):
        return "def"

data = {}
data['Info'] = []
data['Info'].append({
    'LastUpdate': now.strftime("%Y-%m-%d %H:%M:%S")
                    })
data['Covid19'] = []
#print(results)
for i in results:

    if("Country" in i):
        #print(ICUBEDS[j][0])
        if(i["Country"] != "Total:" and i["#"]!=""):
            if(i["ActiveCases"]=='N/A'):
                i["ActiveCases"]= "0"
            if(i["Population"]==' '):
                i["Population"]= "1"
            for j in range(0,220):
                if (str(i["Country"]) == str(ICUBEDS[j][0])):
                    icuBeds=ICUBEDS[j][1]
            for j in range(0,220):
                if (str(i["Country"]) == str(ICUBEDS[j][0])):
                    CountryCode=ICUBEDS[j][2]
                    break
                if (str(i["Country"]) == "Brunei "):
                    CountryCode = "BRN"
            data['Covid19'].append({
                'Country': i["Country"].replace("\n","") ,
                'CountryCode': CountryCode,
                'ActiveCases': i["ActiveCases"],
                'Population': str(i["Population"]).replace(" ",""),
                'ActiveCasesPer100k': round(int(str(str(i["ActiveCases"]).replace(",","")).replace(" ",""))/(int(str(i["Population"]).replace(",",""))/100000),2),
                'ICUBedsPer100k': round(float(icuBeds),2),
                'CountryCategory': RateCategory(round(float(icuBeds),2))
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
print("New Version V.2")

