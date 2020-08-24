# Opens a selenium browser where you can login to Facebook
# This login session can be used to make the posts

from selenium import webdriver
from cookies import save_cookie

driver = webdriver.Firefox()
driver.get('https://mbasic.facebook.com/login')

foo = input()

save_cookie(driver, 'cookie.pickle')
