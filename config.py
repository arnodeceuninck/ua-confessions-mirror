# An explanation on how to get your page token can be found here:
# https://www.pythoncircle.com/post/666/automating-facebook-page-posts-using-python-script/
# Note: under permissions, you have to add "pages_manage_posts" and generate a new token with this
# Be sure to generate a Page acces token, and not a user access token
# Trigger the live switch if you want your post to be seen by everyone (and not only by yourself)
TOKEN = "INSERT_HERE_YOUR_FACEBOOK_PAGE_TOKEN"
# Page ID can be found at the bottom of the about section of your page
PAGE_ID = "INSERT_HERE_YOUR_PAGE_ID"

# For sending messenger messages, you have to provide your username and password
# Note: It's not recommended to use your main account for this
# Sending messages too often, might get you banned from facebook
USERNAME = "INSERT_HERE_YOUR_FACEBOOK_USERNAME"
PASSWORD = "INSERT_HERE_YOUR_FACEBOOK_PASSWORD"

# For accessing the confessions API
BEARER_TOKEN = "INSERT_HERE_YOUR_BEARER_YWT_TOKEN"
