from selenium import webdriver
from cookies import save_cookie

driver = webdriver.Firefox()
driver.get('https://mbasic.facebook.com/login')

foo = input()

save_cookie(driver, 'cookie.pickle')