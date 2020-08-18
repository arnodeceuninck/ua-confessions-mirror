from selenium import webdriver
import time

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

# Generate a token by creating an app on https://developers.facebook.com/apps/
