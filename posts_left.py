
import pickle
accepted_dict = pickle.load(open("accepted.pickle", "rb"))
last_posted = pickle.load(open("var.pickle", "rb"))
posts_left = 0
for key, value in accepted_dict.items():
  if value and key > last_posted:
      posts_left += 1
print("{} posts left, aka +-{} days".format(posts_left, posts_left/12))
