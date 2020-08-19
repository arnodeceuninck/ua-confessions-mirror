from selenium import webdriver
from config import TOKEN, PAGE_ID
import sys
import facebook
import pickle

url = "https://student-confessions.herokuapp.com/confession/{nr}"

# Load the confession nr
try:
    confession_nr = pickle.load(open("var.pickle", "rb"))
except (OSError, IOError) as e:
    confession_nr = 13821  # The first pending confessions
    pickle.dump(confession_nr, open("var.pickle", "wb"))

# Selenium configuration
opts = webdriver.FirefoxOptions()
opts.headless = True
driver = webdriver.Firefox(options=opts)

# Load the page
rvalue = driver.get(url.format(nr=confession_nr))

if driver.title == "404 Not Found":
    print("[{nr}] Page Not Found".format(nr=confession_nr))
    if confession_nr == 13918:
        confession_nr = 13948 # Een reeks opeenvolgende confessions met een 404 for some reason, sla deze over
    if confession_nr < 14098:
        confession_nr += 1 # There is a gap in the page numbers, so this goes anyway to the next one
    pickle.dump(confession_nr, open("var.pickle", "wb"))
    sys.exit()

# Get the confession from the page
element = driver.find_element_by_tag_name('p')  # The confession is the only paragraph on the page
confession = element.text

# Make a Facebook post
try:
    graph = facebook.GraphAPI(TOKEN)
    graph.put_object(PAGE_ID, "feed", message="#{nr} {text}".format(nr=confession_nr, text=confession))
    confession_nr += 1
    print("Confession {nr} posted successfully".format(nr=confession_nr))

except facebook.GraphAPIError as error:
    against_community = "Your content couldn't be shared, because this link goes against our Community Standards"
    if against_community in error.message:
        # Feauture idea: Censor the part against the community standards and publish anyway
        pass

    # Write away the error
    file_object = open('error.log', 'a+')  # + in case the file doesn't exists
    file_object.write('{error} [{nr}] {text}\n'.format(nr=confession_nr, text=confession, error=error.code))
    file_object.close()

    print('[{nr}] {txt}'.format(nr=confession_nr, txt=error.message))
    confession_nr += 1

# Save the confession number and come back later
pickle.dump(confession_nr, open("var.pickle", "wb"))