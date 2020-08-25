# Script to work with the confession API
# This sends message to review confessions and posts the next not reviewed confession

import json
import requests
import fbchat
from getpass import getpass


class ApiError(Exception):
    pass


class NoConfessionError(Exception):
    pass


def _url(path):
    return f"http://www.blablabla.com/api/{path}"


class Confession:
    def __init__(self, nr, text, review_status=None, posted=False, *args, **kwargs):
        self.nr = nr
        self.text = text
        self.review_status = review_status  # None if not reviewed, True if accepted, False if rejected
        self.posted = posted  # If true, then it should contain the url of the post

    def __str__(self):
        return f"#{self.nr} {self.text}"


def fetch_confessions_not_reviewed():
    # returns a list of Confessions that aren't reviewed yet
    params = {"review_status": False, "posted": False}
    resp = requests.get(_url("confession"), params=params)
    if resp.status_code != 200:
        raise ApiError()
    confessions = set()
    for confession in resp.json():
        confessions.add(Confession(**confession))
    return confessions

def send_facebook_message(test):
    username = USERNAME
    client = fbchat.Client(username, getpass())
    no_of_friends = int(raw_input("Number of friends: "))
    for i in xrange(no_of_friends):
        name = str(raw_input("Name: "))
        friends = client.getUsers(name)  # return a list of names
        friend = friends[0]
        msg = str(raw_input("Message: "))
        sent = client.send(friend.uid, msg)
        if sent:
            print("Message sent successfully!")


def send_review_message(confession):
    # Send a message with an accept/reject link
    send_facebook_message("Test")
    pass


def send_review_messages():
    # Send a message with a review link for all not reviewed confessions
    not_reviewed = fetch_confessions_not_reviewed()
    for confession in not_reviewed:
        send_review_message(confession)


def get_next_confession():
    # Get the first confession that has been reviewed, but not yet posted
    params = {"review_status": True, "posted": False}
    resp = requests.get(_url("confession"), params=params)
    if resp.status_code != 200:
        raise ApiError()
    if resp.json():
        return Confession(**resp.json())
    else:
        raise NoConfessionError()


def post_to_facebook(text):
    # Posts the given text to the facebook page
    data = {"text": text}
    resp = requests.post(_url("facebook"), data=data)
    if resp.status_code != 201:
        raise ApiError()


def post_next_confession():
    # Post the first confession that has been accepted, but not reviewed yet
    confession = get_next_confession()
    post_to_facebook(str(confession))


def main():
    response = {"nr": 8, "text": "Test", "posted": False, "review_status": False}
    confession = Confession(**response)
    print(f"{confession.nr}")
    return
    send_review_messages()
    post_next_confession()


if __name__ == "__main__":
    main()
