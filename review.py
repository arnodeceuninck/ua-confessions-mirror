from flask import Flask, url_for, redirect, render_template
import pickle

app = Flask(__name__, template_folder='templates')

try:
    accepted_dict = pickle.load(open("accepted.pickle", "rb"))
    next_review = pickle.load(open("next_review.pickle", "rb"))
except (OSError, IOError) as e:
    accepted_dict = dict()  # num:true if accepted
    next_review = 13821 # one before the first unaccepted

def set_status(nr, accepted):
    global next_review
    accepted_dict[nr] = accepted
    pickle.dump(accepted_dict, open("accepted.pickle", "wb"))
    next_review += 1
    pickle.dump(accepted, open("next_review.pickle", "wb"))


@app.route('/')
def main():
    global next_review
    return render_template("confession.html", nr=next_review)


@app.route('/<int:id>/accept')
def accept(id):
    set_status(id, True)
    return redirect(url_for('main'))


@app.route('/<int:id>/reject')
def reject(id):
    set_status(id, False)
    return redirect(url_for('main'))
