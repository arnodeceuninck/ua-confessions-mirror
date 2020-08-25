# Script to work with the confession API
# This sends message to review confessions and posts the next not reviewed confession

import json
import requests
# import fbchat
from config import USERNAME, PASSWORD, BEARER_TOKEN
# from fbchat.models import Message, ThreadType
import time
from main import notify

headers = {"Authorization": f"Bearer {BEARER_TOKEN}"}


class ApiError(Exception):
    pass


class NoConfessionError(Exception):
    pass


def accept_url(nr, accepted):
    # Url to respond whether a confession has been accepted/rejected
    return f"http://192.168.1.22/api/{nr}/{'accept' if accepted else 'reject'}"


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
    resp = requests.get(_url("confession"), params=params, headers=headers)
    if resp.status_code != 200:
        raise ApiError()
    confessions = set()
    for confession in resp.json():
        confessions.add(Confession(**confession))
    return confessions


def get_message_receiver(client, name):
    friends = client.searchForUsers(name, limit=1)  # return a list of names
    return friends[0]


def send_facebook_message(msg, client):
    notify("You've got a new message", msg)
    pass
    # Not recommended to do this, Facebook disabled my account, it's a better idea to work with sessions
    # receiver = get_message_receiver(client, "Arno Deceuninck")
    # client.send(Message(text=msg), thread_id=receiver.uid, thread_type=ThreadType.USER)
    # time.sleep(1)  # Prevent being kicked from Facebook because of sending to fast


def send_review_message(confession, client):
    # Send a message with an accept/reject link
    message = f"{str(confession)}\n" \
              f"Accept: {accept_url(confession.nr, True)}\n" \
              f"Reject: {accept_url(confession.nr, False)}"
    send_facebook_message(message, client)
    pass


def handle_response(nr, accepted):
    # Handle the response when clicked on the accept/reject links in messenger
    params = {"review_status": accepted}
    resp = requests.put(_url(f"{nr}"), params=params, headers=headers)
    if not resp.status_code == 200:
        raise ApiError()


def send_review_messages():
    # Send a message with a review link for all not reviewed confessions
    # not_reviewed = fetch_confessions_not_reviewed()
    not_reviewed = [Confession(nr=69, text="Never gonna give you up"),
                    Confession(nr=420, text="Never gonna let you down")]
    # client = fbchat.Client(USERNAME, PASSWORD)
    client = None  # Facebook disabled my account after using fbchat, it would probably work better when using sessions
    if not_reviewed:
        send_facebook_message("There are confessions that aren't reviewed yet:", client)
    for confession in not_reviewed:
        send_review_message(confession, client)
    # client.logout()


def get_next_confession():
    # Get the first confession that has been reviewed, but not yet posted
    params = {"review_status": True, "posted": False}
    resp = requests.get(_url("confession"), params=params, headers=headers)
    if resp.status_code != 200:
        raise ApiError()
    if resp.json():
        return Confession(**resp.json())
    else:
        raise NoConfessionError()


def post_to_facebook(text):
    # Posts the given text to the facebook page
    data = {"text": text}
    resp = requests.post(_url("facebook"), data=data, headers=headers)
    if resp.status_code != 201:
        raise ApiError()


def post_next_confession():
    # Post the first confession that has been accepted, but not reviewed yet
    confession = get_next_confession()
    post_to_facebook(str(confession))


def main():
    send_review_messages()
    # post_next_confession()


if __name__ == "__main__":
    main()
