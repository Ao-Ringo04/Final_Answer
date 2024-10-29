import requests
import pandas as pa
import re
from bs4 import BeautifulSoup
import time
import json
#HTMLの取得
def gethtml(url):
    option ={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36" }
    res = False
    count = 0
    while not res:
        try:
            html_raw = requests.get(url,headers=option)
            html_raw.encoding = 'utf-8'
            html_raw = html_raw.text
            res = True
        except Exception as e:
            if count >= 5:
                print("サーバーからのデータ取得に失敗")
                break
            else:
                time.sleep(3)
                count = count + 1
    return html_raw
#店情報の抽出
def shopext(html_raw,shop_info):
    #店名
    soup = BeautifulSoup(html_raw, 'html.parser')
    shop_name = soup.find(class_='shop-info__name').get_text(strip=True)
    shop_info[shop_name]={}
    #電話
    tell = soup.find(class_='number').get_text(strip=True)
    shop_info[shop_name]["電話番号"] = tell
    #メールアドレス
    raw_mail = soup.find('a', href=re.compile(r'^mailto:'))
    if raw_mail == None:
        shop_info[shop_name]["メールアドレス"] = ""
    else:
        mail = raw_mail['href'].replace('mailto:',"")
        shop_info[shop_name]["メールアドレス"] = mail
    #住所
    addr = soup.find(class_='region').get_text(strip=True)
    addr_spr = re.match(r'(.+?(?:都|道|府|県))(.+?(郡|市|区|町|村))(.+)', addr)
    shop_info[shop_name]["都道府県"] = addr_spr.group(1)
    shop_info[shop_name]["市区町村"] = addr_spr.group(2)
    shop_info[shop_name]["番地"] = addr_spr.group(4)
    #建物
    building = soup.find(class_='locality')
    if building == None:
        shop_info[shop_name]["建物名"] = ""
    else:
        shop_info[shop_name]["建物名"] = building.get_text(strip=True)
    #店のURL
    raw_url = soup.find(class_='url go-off')
    if raw_url == None:
        raw_url = soup.find('a', class_='sv-of double')
        if raw_url == None:
            shop_info[shop_name]["URL"]=""
            shop_info[shop_name]["SSL"]=""
        else:
            shop_url = raw_url['href']
            shop_info[shop_name]["URL"]=shop_url
            if "https" in shop_url:
                shop_info[shop_name]["SSL"]= True
            elif "http"in shop_url:
                shop_info[shop_name]["SSL"]= False
    else:
        raw_url = raw_url.get('data-o')
        jsondata = json.loads(raw_url)
        if jsondata is not None:
            a_url = jsondata["a"]
            b_url = jsondata["b"]
            shop_url = b_url +"://"+ a_url
            shop_info[shop_name]["URL"]=shop_url
            if "https" in shop_url:
                shop_info[shop_name]["SSL"]= True
            elif "http"in shop_url:
                shop_info[shop_name]["SSL"]= False
        else:
            raw_url = soup.find('a', class_='sv-of double')
            if raw_url == None:
                shop_info[shop_name]["URL"]=""
                shop_info[shop_name]["SSL"]=""
            else:
                shop_url = raw_url['href']
                shop_info[shop_name]["URL"]=shop_url
                if "https" in shop_url:
                    shop_info[shop_name]["SSL"]= True
                elif "http"in shop_url:
                    shop_info[shop_name]["SSL"]= False

    return shop_info
#urlからの情報取得
url = "https://r.gnavi.co.jp/area/jp/rs/?fwp=東京&date=20241014"
html_data = gethtml(url)
soup = BeautifulSoup(html_data, 'html.parser')
links = soup.find_all("a", class_="style_titleLink__oiHVJ")
urls = [url.get("href") for url in links if url.get("href") and 'https://r.gnavi' in url.get("href")]
urls = list(set(urls))
shop_info = {}
for url in urls:
    html_data = gethtml(url)
    shop_extr = shopext(html_data,shop_info)
    time.sleep(3)
if len(shop_extr) < 50:
    res = True
    page_num = 2 #webページの指定
else:
    res = False
while res:
    url = f"https://r.gnavi.co.jp/area/jp/rs/?fwp=%E6%9D%B1%E4%BA%AC&date=20241014&p={page_num}"
    page_num = page_num + 1
    html_data = gethtml(url)
    soup = BeautifulSoup(html_data, 'html.parser')
    links = soup.find_all("a", class_="style_titleLink__oiHVJ")
    urls = [url.get("href") for url in links if url.get("href") and 'https://r.gnavi' in url.get("href")]
    urls = list(set(urls))
    for url in urls:
        if len(shop_extr) ==50:
            res = False
            break
        html_data = gethtml(url)
        shop_extr = shopext(html_data,shop_extr)
        time.sleep(3)
#CSVの作成
shopname_list = list(shop_extr.keys())
shop_data =[]
for shop_name in shopname_list:
    tell = shop_extr[shop_name]["電話番号"]
    mailadd= shop_extr[shop_name]["メールアドレス"]
    pref = shop_extr[shop_name]["都道府県"]
    city = shop_extr[shop_name]["市区町村"]
    addr = shop_extr[shop_name]["番地"]
    build = shop_extr[shop_name]["建物名"]
    shopurl = shop_extr[shop_name]["URL"]
    ssl = shop_extr[shop_name]["SSL"]
    shop_data.append([shop_name,tell,mailadd,pref,city,addr,build,shopurl,ssl])
chan = pa.DataFrame(shop_data,columns =["店舗名","電話番号","メールアドレス","都道府県","市区町村","番地名","建物名","URL","SSL"])
chan.to_csv("1-1.csv",index=False,encoding='utf-8-sig')
