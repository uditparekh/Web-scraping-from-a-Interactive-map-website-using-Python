import pathlib
from urllib.error import HTTPError
from datetime import date, timedelta
from collections import deque
from bs4 import BeautifulSoup as soup  # HTML data structure
from urllib.request import urlopen as uReq  # Web client
import requests
import re
import json
import ast
from spinner import Spinner
import pandas as pd

s=Spinner()
s.start()
def get_html_block(id_str):
    headers = {
        'authority': 'ctitowers.com',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'accept': '*/*',
        'origin': 'https://ctitowers.com',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://ctitowers.com/cti-towers-site-locator/',
        'accept-language': 'en-US,en;q=0.9',
    }

    data = {
        'action': 'mmm_async_content_marker',
        'id': id_str
    }

    response = requests.post('https://ctitowers.com/wp-admin/admin-ajax.php', headers=headers, data=data)

    return response.text

page_url = "https://ctitowers.com/cti-towers-site-locator/"
uClient = uReq(page_url)
page_soup = soup(uClient.read(), "html.parser")
uClient.close()

data = page_soup.find_all("script")[-2].string

data = data.split('"markers":')[1].split('}];')[0].strip()
maps_list = ast.literal_eval(data)






def getField(html, field_name):
    # TODO - add some error checking for when not found, etc.
    field = html.split(field_name + ":</b>")[1].split("<")[0].strip()
    #print(field)
    return field

Record = []
for item in maps_list:
    htmltxt = get_html_block(item.get('id'))
    item_soup = soup(htmltxt, 'lxml')
    data = item_soup.find_all("li", class_="adresse")
    data2 = item_soup.find_all("h2")
    ID_Name = data2[0].text
    Address = data[0].text
    Lat_Long = data[1].text
    Tower_Type = getField(htmltxt, "Tower Type")
    STRUCTURE_Height = getField(htmltxt, "Structure Height")
    Ground_Elevation = getField(htmltxt, "Ground Elevation")
    County = getField(htmltxt, "County")
    Account_Manager = getField(htmltxt, "Account Manager")
    Project_Manager = getField(htmltxt, "Project Manager")
    data3 = item_soup.find_all("li", class_="telephone")
    Telephone = data3[0].text
    Record.append(
        (ID_Name, Address, Lat_Long, Tower_Type, STRUCTURE_Height, Ground_Elevation, County, Account_Manager, Project_Manager, Telephone)
    )
df = pd.DataFrame(Record)
df.columns= ['ID_Name', 'Address', 'Lat_Long', 'Tower_Type', 'STRUCTURE_Height', 'Ground_Elevation', 'County', 'Account_Manager', 'Project_Manager', 'Telephone']
df_CTI = df.drop_duplicates(subset=['ID_Name'], keep= 'last')
print(df_CTI)
writer = pd.ExcelWriter('CTI_Tower.xlsx')
df_CTI.to_excel(writer, sheet_name='Sheet1', index=False)
writer.save()
s.stop()



