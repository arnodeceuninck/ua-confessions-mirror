from selenium import webdriver
from token import TOKEN
import time
import facebook

confession_nr = 13821  # The first pending confessions
url = "https://student-confessions.herokuapp.com/confession/{nr}"

# Selenium configuration
opts = webdriver.FirefoxOptions()
opts.headless = False
driver = webdriver.Firefox(options=opts)

# Load the page
driver.get(url.format(nr=confession_nr))

# Get the confession from the page
element = driver.find_element_by_tag_name('p')  # The confession is the only paragraph on the page
confession = element.text
print("Found confession {nr}: {text}".format(nr=confession_nr, text=confession))

# Make a Facebook post
graph = facebook.GraphAPI(TOKEN)
facebook_page_id = "67509909999999"
graph.put_object(facebook_page_id, "feed", message='test message')