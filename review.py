from flask import Flask, url_for, redirect, render_template
import pickle
from main import load_pickle, store_pickle

# A user interface to accept/reject submitted confessions

app = Flask(__name__, template_folder='templates')

accepted_dict = load_pickle("accepted.pickle", dict())
next_review = load_pickle("next_review.pickle", 13821)


def set_status(nr, accepted):
    # Set a given confession number to accepted or rejected
    global next_review

    accepted_dict[nr] = accepted
    store_pickle("accepted.pickle", accepted_dict)

    next_review += 1
    store_pickle("next_review.pickle", next_review)


@app.route('/')
def main():
    global next_review
    return redirect(url_for('confession', id=next_review))


@app.route('/<int:id>')
def confession(id):
    return render_template("confession.html", nr=id)


@app.route('/<int:id>/accept')
def accept(id):
    set_status(id, True)
    return redirect(url_for('main'))


@app.route('/<int:id>/reject')
def reject(id):
    set_status(id, False)
    return redirect(url_for('main'))


if __name__ == '__main__':
    app.debug = True
    app.run(host="0.0.0.0")
