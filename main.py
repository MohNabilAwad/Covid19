import requests
import bs4
import json
from ftplib import FTP
import datetime
import csv
import requests
import base64

# https://www.youtube.com/watch?v=e22HHgFqdm0
page = requests.get("https://www.worldometers.info/coronavirus/")
soup = bs4.BeautifulSoup(page.text, 'lxml')

table = soup.find('table', id="main_table_countries_today")

headers = [heading.text.replace(",Other","") for heading in table.find_all('th')]
table_rows = [row for row in table.find_all('tr')]

results = [{headers[index]:cell.text for index,cell in enumerate(row.find_all('td'))} for row in table_rows]
now = datetime.datetime.now()

csv_file = open('ICU Beds.csv', encoding="utf8")
reader = csv.reader(csv_file, delimiter=',')
ICUBEDS = list(reader)
ICUBEDS[0][0] = ICUBEDS[0][0].replace("\ufeff","")

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
            if (str(i["Country"]) == "Brunei "):
                CountryCode = "BRN"
                i["Country"] = "Brunei"
            for j in range(0,220):
                if (str(i["Country"]) == str(ICUBEDS[j][0])):
                    icuBeds=ICUBEDS[j][1]
                    CountryDE=ICUBEDS[j][3]
                    CountryFR=ICUBEDS[j][4]
                    CountryES=ICUBEDS[j][5]
            for j in range(0,220):
                if (str(i["Country"]) == str(ICUBEDS[j][0])):
                    CountryCode=ICUBEDS[j][2]
                ActCases100 = int(str(str(i["ActiveCases"]).replace(",","")).replace(" ",""))/(int(str(i["Population"]).replace(",",""))/100000)
                if(ActCases100!=0):
                    Rate= float(icuBeds)/ActCases100
                else:
                    Rate=0
            data['Covid19'].append({
                'Country': i["Country"].replace("\n","") ,
                'CountryDE': CountryDE,
                'CountryES': CountryFR,
                'CountryFR': CountryES,
                'CountryCode': CountryCode,
                'ActiveCases': i["ActiveCases"],
                'Population/100k': int(str(str(i["Population"]).replace(" ","")).replace(",","")),
                'ActiveCasesPer100k': ActCases100,
                'ICU Beds per 100k before Rate':icuBeds,
                'ICUBedsPer100k': round(float(Rate),2),
                'CountryCategory': RateCategory(float(Rate))
                })


with open('data.json', 'w') as outfile:
    json.dump(data, outfile)

with open('data.json', 'r') as f:
    json_data = json.load(f)
    data_list = json_data['Covid19']

    json_data['Covid19'] = sorted(data_list, key=lambda k:k ['ICUBedsPer100k'],reverse=True)

with open('data.json', 'w') as f:
    json.dump(json_data, f)


#upload data to guthub
token = "02bf29c25181460ec263b9"+"fcde985fecb5cc264f"
repo = 'MohNabilAwad/Covid19'
path = 'data.json'
data = open("data.json", "r").read()

# to get the key for github
response = requests.get('https://api.github.com/repos/MohNabilAwad/Covid19/contents/data.json')
GitHubText = json.loads(response.text)
r = requests.put(
    f'https://api.github.com/repos/{repo}/contents/{path}',
    headers = {
        'Authorization': f'Token {token}'
    },
    json = {
        "message": "add new file",
        "content": base64.b64encode(data.encode()).decode(),
        "branch": "master",
        "sha":GitHubText["sha"]
    }
)
print(r.status_code)
print(r.json())
print(r)





# upload data to my host
FTP.maxline = 163840
ftp = FTP('ftpupload.net')
ftp.login(user="epiz_26155908",passwd="CziCHHeOvM3jNLJ")
ftp.cwd("/mohamad-awad.info/htdocs/")
filename = 'data.json'
ftp.storlines('STOR ' + filename, open(filename, 'rb'))
ftp.quit()

print("Done " + now.strftime("%Y-%m-%d %H:%M:%S"))
print("New Version V.2")
