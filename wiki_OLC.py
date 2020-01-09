import urllib.request
from lxml import etree
from datetime import datetime, date, timedelta
import csv
from pathlib import Path


monthDict = {"January" : 1, "February" : 2, "March" : 3, "April" : 4, "May" : 5, "June" : 6, "July" : 7, "August" : 8, "September" : 9, "October" : 10, "November" : 11, "December" : 12}

def getHTML(url):
    headers=("User-Agent","Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0")
    opener = urllib.request.build_opener()
    opener.addheaders = [headers]
    urllib.request.install_opener(opener)
    page=urllib.request.urlopen(url,timeout=10).read()
    return page

def toISO8601Date(dateStr):
    date = dateStr.split(" ")
    day = int(date[0])
    month = monthDict[date[1]]
    return datetime.strptime("2019-" + str(month) + "-" + str(day), "%Y-%m-%d").strftime("%G-%m-%dT00:00:00+00:00")

def countSuccessLaunch(rows):
    launchDayDict = {}
    curDay = ""
    successLaunch = False
    for row in rows:
        date = row.xpath('td[1][@rowspan]/span/text()[1]')
        if date != []:
            if successLaunch :
                launchDayDict[curDay] = launchDayDict.setdefault(curDay, 0) + 1
            curDay = toISO8601Date(date[0])
            successLaunch = False
        elif not successLaunch:
            state = row.xpath('td[6]/text()[1]')
            if state != []:
                state[0] = state[0].rstrip()
                if state[0] == "Successful" or state[0] == "Operational" or state[0] == "En route":
                     successLaunch = True
    if successLaunch :
        launchDayDict[curDay] = launchDayDict.setdefault(curDay, 0) + 1
    return launchDayDict

def creatAllYearList(launchDayDict):
    yearCountList = []
    sdate = date(2019, 1, 1)   # start date
    edate = date(2019, 12, 31)   # end date
    delta = edate - sdate
    for i in range(delta.days + 1):
        day = sdate + timedelta(days=i)
        day = day.strftime("%G-%m-%dT00:00:00+00:00")
        if day in launchDayDict:
            yearCountList.append([day, launchDayDict[day]])
        else:
            yearCountList.append([day, 0])
    return yearCountList

def exportToCVS(yearCountList):
    with open("wiki_OLC_output.csv", 'w', newline='', encoding='utf-8') as f:
        f_csv=csv.writer(f)
        headers = ["date", "value"]
        f_csv.writerow(headers)
        for dailyData in yearCountList:
            f_csv.writerow(dailyData)

url="https://en.wikipedia.org/wiki/2019_in_spaceflight#Orbital_launches"
wikiPage = getHTML(url)
source = etree.HTML(wikiPage)
rows = source.xpath('//h2[span[contains(text(),"Orbital launches")]]/following-sibling::table[2]/tbody/tr')
launchDayDict = countSuccessLaunch(rows)
yearCountList = creatAllYearList(launchDayDict)
exportToCVS(yearCountList)

