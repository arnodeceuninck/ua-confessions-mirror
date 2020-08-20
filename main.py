from selenium import webdriver
from config import TOKEN, PAGE_ID
import sys
import facebook
import pickle
from datetime import datetime
import time
from cookies import load_cookie


class NotFoundError(Exception):
    def __str__(self):
        return "Page not found"


def set_confession_nr(nr):
    pickle.dump(nr, open("var.pickle", "wb"))


def get_confession_nr():
    # Load the confession nr
    try:
        confession_nr = pickle.load(open("var.pickle", "rb"))
    except (OSError, IOError) as e:
        confession_nr = 13821  # The first pending confessions

    try:
        accepted_dict = pickle.load(open("accepted.pickle", "rb"))
    except (OSError, IOError):
        raise Exception("Please run the review unit first")

    try:
        while not accepted_dict[confession_nr]:
            confession_nr += 1  # Get the first accepted
    except:
        raise Exception(
            "Already went through all reviewed items")  # todo: check if exception exists, if so send a notification

    set_confession_nr(confession_nr)
    return confession_nr


def get_confession(confession_nr):
    url = "https://student-confessions.herokuapp.com/confession/{nr}"

    # Selenium configuration
    opts = webdriver.FirefoxOptions()
    opts.headless = True
    driver = webdriver.Firefox(options=opts)

    # Load the page
    rvalue = driver.get(url.format(nr=confession_nr))

    if driver.title == "404 Not Found":
        raise NotFoundError()

    # Get the confession from the page
    element = driver.find_element_by_tag_name('p')  # The confession is the only paragraph on the page
    confession = element.text
    return confession


def post_to_facebook(confession, confession_nr):
    # Make a Facebook post
    text = "#{nr} {text}".format(nr=confession_nr, text=confession)
    facebook_post_selenium(text)
    # facebook_post_graph_api(text)


def facebook_post_selenium(message):
    from selenium import webdriver
    from selenium.webdriver.common.keys import Keys
    from time import sleep
    from selenium.common.exceptions import TimeoutException
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support.ui import Select
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions
    from selenium.common.exceptions import NoSuchElementException

    opts = webdriver.FirefoxOptions()
    opts.headless = True
    driver = webdriver.Firefox(options=opts)
    driver.get('https://mbasic.facebook.com/')
    load_cookie(driver, 'cookie.pickle')
    driver.get('https://mbasic.facebook.com/UAntwerpen-Confessions-Mirror-114029007083594/')
    print("Page loaded...")
    post_box = driver.find_element_by_id("u_0_0")
    # post_box = driver.find_element_by_xpath('//textarea[@placeholder="What\'s on your mind?"')
    post_box.click()
    print("Clicked on post textbox...")
    time.sleep(3)
    post_box.send_keys(message)
    sleep(2)
    post_it = driver.find_element_by_name("view_post")
    # post_it = driver.find_element_by_xpath("//input[@value=\"Post\"")
    post_it.click()
    print("Posted...")


def facebook_post_graph_api(message):
    try:
        graph = facebook.GraphAPI(TOKEN)
        graph.put_object(PAGE_ID, "feed", message=message)
        print("{time} Confession {nr} posted successfully".format(nr=confession_nr, time=str(datetime.now())))

    except facebook.GraphAPIError as error:
        against_community = "Your content couldn't be shared, because this link goes against our Community Standards"
        if against_community in error.message:
            # Feauture idea: Censor the part against the community standards and publish anyway
            # confession = censor(confession, error.message)
            # post_to_facebook(confession, confession_nr)
            pass

        # Write away the error
        file_object = open('error.log', 'a+')  # + in case the file doesn't exists
        file_object.write('{error} [{nr}] {text}\n'.format(nr=confession_nr, text=confession, error=error.code))
        file_object.close()

        print('{time} [{nr}] {txt}'.format(nr=confession_nr, txt=error.message, time=str(datetime.now())))


def incr_confession_nr():
    confession_nr = get_confession_nr()
    # Save the confession number and come back later
    confession_nr += 1
    pickle.dump(confession_nr, open("var.pickle", "wb"))


def main():
    # facebook_post_selenium("Facebook doet weer moeilijk met hun GraphAPI #weodend")
    # return
    try:
        confession_nr = get_confession_nr()
        confession = get_confession(confession_nr)
        print(confession)
        post_to_facebook(confession, confession_nr)
        incr_confession_nr()
    except NotFoundError:
        print("{time} [{nr}] Page Not Found".format(nr=confession_nr, time=str(datetime.now())))
        main()  # All accepted confessions should exist
        return
        last_known_confession = 14098
        if confession_nr < last_known_confession:
            # There are still confessions, try to find the next one
            incr_confession_nr()
            main()
        # If there is still a not found beyond the last_known_confession, it must be the end of the confessions,
        #  so try again later if there are any new confessions
    except Exception as e:
        print("{time} [{nr}] An error occured".format(nr=confession_nr, time=str(datetime.now())))
        raise e

if __name__ == "__main__":
    main()
