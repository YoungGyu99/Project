from selenium import webdriver
import time
driver = webdriver.Chrome('chromedriver.exe')
driver.implicitly_wait(3)
url = 'http://www.naver.com'
driver.get(url)
time.sleep(1)
print('a')