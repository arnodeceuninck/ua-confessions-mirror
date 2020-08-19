from selenium import webdriver
from config import TOKEN, PAGE_ID
import sys
import facebook
import pickle
from datetime import datetime

class NotFoundError(Exception):
    super.__init__()

def set_confession_nr(nr):
    pickle.dump(nr, open("var.pickle", "wb"))


def get_confession_nr():
    # Load the confession nr
    try:
        confession_nr = pickle.load(open("var.pickle", "rb"))
    except (OSError, IOError) as e:
        confession_nr = 13821  # The first pending confessions
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
    try:
        graph = facebook.GraphAPI(TOKEN)
        graph.put_object(PAGE_ID, "feed", message="#{nr} {text}".format(nr=confession_nr, text=confession))
        print("{time} Confession {nr} posted successfully".format(nr=confession_nr, time=str(datetime.now())))

    except facebook.GraphAPIError as error:
        against_community = "Your content couldn't be shared, because this link goes against our Community Standards"
        if against_community in error.message:
            # Feauture idea: Censor the part against the community standards and publish anyway
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
    try:
        confession_nr = get_confession_nr()
        confession = get_confession(confession_nr)
        post_to_facebook(confession, confession_nr)
        incr_confession_nr()
    except NotFoundError:
        print("{time} [{nr}] Page Not Found".format(nr=confession_nr, time=str(datetime.now())))
        last_known_confession = 14098
        if confession_nr < last_known_confession:
            # There are still confessions, try to find the next one
            incr_confession_nr()
            main()


if __name__ == "__main__":
    main()
