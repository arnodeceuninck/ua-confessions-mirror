from selenium import webdriver

import os
import facebook
import pickle
from datetime import datetime, date, time
import time
from cookies import load_cookie

import subprocess

GRAPH_API = False  # Set to True if using graph api

if GRAPH_API:
    from config import TOKEN, PAGE_ID  # Only relevant if using GraphAPI

MAX_ATTEMPTS = 10


def timestr():
    # Timestring to use in log
    return str(datetime.now())


def load_pickle(name, default):
    try:
        var = pickle.load(open(name, "rb"))
    except (OSError, IOError):
        var = default
    return var


def store_pickle(name, var):
    pickle.dump(var, open(name, "wb"))


def notify(title, message):
    # Send a notification in ubuntu
    # Using the python notify2 module would be better, but dbus gives a problem
    subprocess.Popen(['notify-send', title, message])
    return


class NotFoundError(Exception):
    # Error you get when you load the page for a confession and get a not found back
    def __str__(self):
        return "Page not found"


class NoConfessionError(Exception):
    # Error when there were no confessions found to post
    def __str__(self):
        return "No more accepted confessions, check your notifications to know whether there are still confessions to be reviewed"


class ConfessionNotReviewedError(Exception):
    # Error when there are still confessions that have to be reviewed
    def __str__(self):
        return "There are still confessions you should review!"


class MaxAttemptsReached(Exception):
    # Error when the max nr of attempts has been reached
    def __str__(self):
        return "The maximum number of attempts for getting the confession has been reached"


def set_confession_nr(nr):
    # Update the last posted confession number
    pickle.dump(nr, open("var.pickle", "wb"))


def get_page_driver(confession_nr):
    # Get the selenium page driver for the given confession number
    url = "https://student-confessions.herokuapp.com/confession/{nr}"

    # Selenium configuration
    opts = webdriver.FirefoxOptions()
    opts.headless = True
    driver = webdriver.Firefox(options=opts)

    # Load the page
    driver.get(url.format(nr=confession_nr))

    if driver.title == "404 Not Found":
        raise NotFoundError()

    return driver


def get_confession(confession_nr):
    # Given a confession number, get the text of the confession from the website
    driver = get_page_driver(confession_nr)  # Get the page
    element = driver.find_element_by_tag_name('p')  # The confession is the only paragraph on the page
    confession = element.text
    return confession


def check_confessions_after(nr, range=51, jump_size=1):
    # Check whether there are still confessions from (and after) a given number
    # It test a few pages (inside the range) whether they all give a 404 (and thus there are no confessions)
    # Required because you've got sometimes random 404 between confessions
    try:
        get_page_driver(nr)
    except NotFoundError:
        pass
    else:
        # We found a confession
        return True

    # Make bigger jumps to prevent testing each page in the range (but still prioritize the first ones more)
    jump_size *= 2
    if range > jump_size:
        range = range - jump_size
        nr = nr + jump_size
        return check_confessions_after(nr, range, jump_size)
    pass


def get_confession_nr():
    # Get the number of the next confession to post

    # Load the number
    confession_nr = load_pickle("var.pickle", default=13821)  # The first confession as default

    # Load the dict containing which confessions are accepted/rejected
    accepted_dict = load_pickle("accepted.pickle", default=None)
    if accepted_dict is None:
        raise Exception("Please run the review unit first")

    # Find the first confession that has been accepted
    try:
        while not accepted_dict[confession_nr]:
            confession_nr += 1  # Get the first accepted
    except KeyError:
        # No more accepted confessions found, check whether there are no confessions anymore
        #  (because there can still be confessions that aren't reviewed yet)
        if check_confessions_after(confession_nr):
            raise ConfessionNotReviewedError()
        else:
            raise NoConfessionError()

    # Remember the new number
    set_confession_nr(confession_nr)
    return confession_nr


def post_to_facebook(text):
    # Post text to facebook
    if GRAPH_API:
        facebook_post_graph_api(text)
    else:
        facebook_post_selenium(text)


def post_confession(confession, confession_nr):
    # Make a Facebook post
    text = f"#{confession_nr} {confession}"
    post_to_facebook(text)


def facebook_post_selenium(message):
    # Post a message on Facebook using selenium
    # Warning: This requires your login to be completed
    opts = webdriver.FirefoxOptions()
    opts.headless = True
    driver = webdriver.Firefox(options=opts)

    # Login
    driver.get('https://mbasic.facebook.com/')  # You can only set cookies at the page you're at, so go to facebook
    load_cookie(driver, 'cookie.pickle')  # Set the session cookies

    driver.get('https://mbasic.facebook.com/UAntwerpen-Confessions-Mirror-114029007083594/')

    # Click on the post box, to enter text
    post_box = driver.find_element_by_id("u_0_0")
    post_box.click()
    time.sleep(3)

    # Type the message
    post_box.send_keys(message)
    time.sleep(2)

    # Post it
    post_it = driver.find_element_by_name("view_post")
    post_it.click()


# Posting to facebook using selenium, since the GraphAPI is currently only available for business users
def facebook_post_graph_api(message):
    # Post a message on Facebook using the Graph API
    # Warning: This requires you to enter your page id and token in config.py
    # Your token should be in live (if you want post to show up live) with permission to write text to the page
    # This is currently only available for business users (don't know why, Facebook just being weird)

    try:
        # Post it
        graph = facebook.GraphAPI(TOKEN)
        graph.put_object(PAGE_ID, "feed", message=message)
    except facebook.GraphAPIError as error:
        # An error happened while posting

        # Guidlines violation error
        against_community = "Your content couldn't be shared, because this link goes against our Community Standards"
        if against_community in error.message:
            # Feauture idea: Censor the part against the community standards and publish anyway
            # confession = censor(confession, error.message)
            # post_confession(confession, confession_nr)
            pass

        # Write away the error
        file_object = open('error.log', 'a+')  # + in case the file doesn't exists
        file_object.write(f'{datetime.now()} Error {error.code}: {error.message} ({message})\n')
        file_object.close()

        notify("Error", "An error has occured when posting using GraphAPI, please check the log")


def incr_confession_nr():
    # Increase and save the confession number to start from next time
    confession_nr = get_confession_nr()
    confession_nr += 1
    pickle.dump(confession_nr, open("var.pickle", "wb"))


def add_days_passed(pickle_name):
    days_without = load_pickle(pickle_name, set())
    days_without_len = len(days_without)  # used for jump

    today = date.today()
    days_without.add(today)

    days_passed = len(days_without)
    # prevent doing something every time this script is ran on a given day
    jump = days_without_len != days_passed  # True if this addition made the number of days change

    store_pickle(pickle_name, days_without)

    return days_passed, jump


def is_time_between(begin_time, end_time, check_time=None):
    # If check time is not given, default to current UTC time
    check_time = check_time or datetime.utcnow().time()
    if begin_time < end_time:
        return begin_time <= check_time <= end_time
    else:  # crosses midnight
        return check_time >= begin_time or check_time <= end_time


def peak_hour():
    return is_time_between(time(16, 30), time(21, 30))


def done_today():
    store_pickle("last_day.pickle", date.today())


def already_done_today():
    today = date.today()
    last_day = load_pickle("last_day.pickle", None)
    return today == last_day


def main():
    found_confession = True  # Will be set to False if there aren't any new confessions
    reviewed = True  # Will be set to False if there are confessions still waiting to be reviewed

    confession_nr = 0  # in case of crash during get_confession_nr()

    try:
        # Get the confession and post it to Facebook
        confession_nr = get_confession_nr()  # Also checks new confessions to be reviewed, do this every time
        # Post a confession only once a day:
        if already_done_today() or not peak_hour():
            return
        confession = get_confession(confession_nr)
        post_confession(confession, confession_nr)
        incr_confession_nr()
        done_today()
        notify("Posted confession", confession)
        print(f"{timestr()} Confession {confession_nr} posted successfully")

    except NotFoundError:
        # The confession was accepted, so it must exist, but was not found, so try again
        print(f"{timestr()} [{confession_nr}] Page Not Found")
        global MAX_ATTEMPTS
        if MAX_ATTEMPTS:
            MAX_ATTEMPTS -= 1
            main()  # All accepted confessions should exist
        else:
            notify("Max attempts reached", f"Max attempts reached for confession #{confession_nr}")
            raise MaxAttemptsReached()

    except NoConfessionError:
        print("{time} No confessions to post".format(time=str(datetime.now())))

        # If 2 weeks no new confessions post a reminder on Facebook
        found_confession = False  # Don't reset the day counter

        days, jump = add_days_passed("days_without.pickle")

        if days == 3 and jump:
            post = "Er waren geen nieuwe confessions afgelopen twee dagen. \n" \
                   "Iedereen heeft wel confessions die hij/zij kwijt wil. " \
                   "Geef ze door via https://www.facebook.com/UAntwerpenConfessions/app/208195102528120. " \
                   "The truth will set you free.\n" \
                   "Als je denkt dat dit een error is, laat het dan zeker weten."
            facebook_post_selenium(post)
            notify("No confessions", "Posted a reminder that there were no confessions")
        elif days == 2 and jump:
            notify("No confessions", "Morgen post ik een reminder")

        if days % 14 == 0 and jump:
            post = "Er waren geen nieuwe confessions afgelopen twee weken. \n" \
                   "Iedereen heeft wel confessions die hij/zij kwijt wil. " \
                   "Geef ze door via https://www.facebook.com/UAntwerpenConfessions/app/208195102528120. " \
                   "The truth will set you free.\n" \
                   "Als je denkt dat dit een error is, laat het dan zeker weten."
            facebook_post_selenium(post)
            notify("No confessions", "Posted a reminder that there were no confessions")

        elif days % 7 == 0 and jump:
            notify("No confessions", "Already went 7 days without confessions")

    except ConfessionNotReviewedError:
        reviewed = False  # Don't reset day counter

        # Let now there are still questions to be reviewed
        notify(f'New post after #{confession_nr}',
               'We found a post that hasn\'t been reviewed yet, please do so ASAP.')

        print(f"{timestr()} Warning: found new post waiting to be reviewed, "
              f"you should've received a notification about this")

        days, jump = add_days_passed("days_without_review.pickle")

        if days == 7 and jump:
            post = "Er zijn ondertussen wel nog confessions ingediend, " \
                   "maar de admin heeft deze niet meer gecontroleerd. " \
                   "Indien je dit leest, kan je best even horen bij hem of alles nog oke is."
            facebook_post_selenium(post)
            notify("No confessions reviewed", "Bro, are you alive? There are still confessions waiting to be reviewed")

        elif days == 4 and jump:
            notify("Review confessions (or I'll post a warning)", "There are still confessions waiting to be reviewed!")

    except Exception as e:
        message = "{time} [{nr}] An error occured".format(nr=confession_nr, time=str(datetime.now()))
        print(message)
        notify("Confession error", message)
        raise e

    # Stop the streaks without if necessarily
    if found_confession and os.path.exists("days_without.pickle"):
        os.remove("days_without.pickle")
    if reviewed and os.path.exists("days_without_review.pickle"):
        os.remove("days_without_review.pickle")


if __name__ == "__main__":
    main()
