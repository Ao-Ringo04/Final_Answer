from selenium import webdriver
import pandas
import re
import time
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()
driver.get("https://r.gnavi.co.jp/area/jp/rs/?fwp=東京&date=2024101")
url_cls = driver.find_elements(By.CLASS_NAME, "style_titleLink__oiHVJ")
あいうえお


