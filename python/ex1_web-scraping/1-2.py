from selenium import webdriver
import pandas as pa
import re
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

#店情報の抽出
def shopext(html_raw,shop_info):
    #店名
    soup = BeautifulSoup(html_raw, 'html.parser')
    shop_name = soup.find(class_='shop-info__name').get_text(strip=True)
    shop_info[shop_name]={}
    #電話
    tell = soup.find(class_='number').get_text(strip=True)
    shop_info[shop_name]["電話番号"] = tell
    #住所
    addr = soup.find(class_='region').get_text(strip=True)
    addr_spr = re.match(r'(.+?(?:都|道|府|県))(.+?(郡|市|区|町|村))(.+)', addr)
    shop_info[shop_name]["都道府県"] = addr_spr.group(1)
    shop_info[shop_name]["市区町村"] = addr_spr.group(2)
    shop_info[shop_name]["番地"] = addr_spr.group(4)
    building = soup.find(class_='locality')
    if building == None:
        shop_info[shop_name]["建物名"] = ""
    else:
        shop_info[shop_name]["建物名"] = building.get('href')
    #店のURL
    raw_url = soup.find(class_='url go-off')
    if raw_url == None:
        shop_info[shop_name]["URL"]=""
        shop_info[shop_name]["SSL"]=""
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
            shop_info[shop_name]["URL"]=""
            shop_info[shop_name]["SSL"]=""
    return shop_info

chop = Options()
chop.add_argument("--headless") 
driver = webdriver.Chrome(options=chop)
driver.get("https://r.gnavi.co.jp/area/jp/rs/?fwp=東京&date=2024101")
url_cls = driver.find_elements(By.CLASS_NAME, "style_title___HrjW")

shopinfo = {}
for url_num in range(len(url_cls)):
    if len(shopinfo) >= 50:
        break
    res =False
    count = 0
    while not res:
        try:
            url_cls2 = driver.find_elements(By.CLASS_NAME, "style_title___HrjW")
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable
                                            ((By.CLASS_NAME, "style_title___HrjW")))
            url_cls2[url_num].click()
            html = driver.page_source.encode('utf-8')
            shopinfo = shopext(html,shopinfo)
            res = True
            time.sleep(3)
            driver.back()
        except Exception as e:
            if count >= 5:
                print(f"{len(shopinfo)}個目のデータ取得に失敗.実行回数:({count})")
                break
            else:
                time.sleep(3)
                count = count + 1

if len(shopinfo) >= 50:
    res = False
else:
    res = True

while res:
    nextpage = driver.find_element(By.CLASS_NAME, "style_nextIcon__M_Me_")
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable
                                    ((By.CLASS_NAME, "style_nextIcon__M_Me_")))
    nextpage.click()
    url_cls = driver.find_elements(By.CLASS_NAME, "style_title___HrjW")
    for url_num in range(len(url_cls)):
        if len(shopinfo) >= 50:
            break
        res =False
        count = 0
        while not res:
            try:
                url_cls2 = driver.find_elements(By.CLASS_NAME, "style_title___HrjW")
                WebDriverWait(driver, 30).until(EC.element_to_be_clickable
                                                ((By.CLASS_NAME, "style_title___HrjW")))
                url_cls2[url_num].click()
                html = driver.page_source.encode('utf-8')
                shopinfo = shopext(html,shopinfo)
                res = True
                time.sleep(3)
                driver.back()
            except Exception as e:
                if count >= 5:
                    print(f"{len(shopinfo)}個目のデータ取得に失敗.実行回数:({count})")
                    break
            else:
                time.sleep(3)
                count = count + 1
        if len(shopinfo) >= 50:
            break
driver.quit()

shopname_list = list(shopinfo.keys())
shop_data =[]
for shop_name in shopname_list:
    tell = shopinfo[shop_name]["電話番号"]
    pref = shopinfo[shop_name]["都道府県"]
    city = shopinfo[shop_name]["市区町村"]
    addr = shopinfo[shop_name]["番地"]
    build = shopinfo[shop_name]["建物名"]
    shopurl = shopinfo[shop_name]["URL"]
    ssl = shopinfo[shop_name]["SSL"]
    shop_data.append([shop_name,tell,"",pref,city,addr,build,shopurl,ssl])
chan = pa.DataFrame(shop_data,columns =["店舗名","電話番号","メールアドレス","都道府県","市区町村","番地名","建物名","URL","SSL"])
chan.to_csv("1-1.csv",index=False)
          
    