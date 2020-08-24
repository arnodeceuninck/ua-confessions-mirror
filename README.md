# ua-confessions-mirror
Post automatically confessions on a [Facebook page](https://www.facebook.com/UAntwerpen-Confessions-Mirror-114029007083594), because the admin of [UAntwerpen-Confessions](https://www.facebook.com/UAntwerpenConfessions) seems to be dead. 

## Dependencies
This script is made on an Ubuntu 20.04 environment, so for setup on any other OS, you'll have to find out what works for you. (e.g. notifications will probably only work on Ubuntu)
### Python dependencies
Create a virtual environment and install the python dependencies from the `requirements.txt`.
### Selenium setup
Install the selenium drivers for Firefox. You can find plenty of tutorials online, like [this one](https://tecadmin.net/setup-selenium-with-firefox-on-ubuntu/).

## Getting started
### Review
Once all dependencies are met, you can run the `review.py` file to start accepting/rejecting confessions. This uses a Flask interface on the default port (`localhost:5000`). 
### Login
To post confessions on Facebook, a valid login session is required. You can generate this by running `login.py`, logging in to Facebook, hitting enter in the command line and only when the script is finished closing the browser.
### Add cronjob
With `crontab -e`, you can edit your cronjobs in Ubuntu. Append the lines from `ua-confession-mirror.cron` here to run the script every hour. 

## Posting to Facebook
You can post using Facebook using selenium or using the Facebook Graph API. Using selenium is probably against Facebooks Terms of Services, so it's recommended not to use your main account for this. If you can generate a live token for your Facebook page for the Graph API (on [developers.facebook.com](developers.facebook.com)
), I would recommend to use that, but this is currently impossible for individual users (only for businesses or in a development environment, where you are the only one that can see the posts).

## Warnings
This script will post a Warning on Facebook (after sending notifications to you) when people haven't written any new confessions past weeks or there are new confessions, but you haven't reviewed them for a long time. 

## License
It's The Unlicense, so do whatever you want, but don't come crying if something messed up everything. 

## Still questions?
Don't hesitate to contact me if you've still got any questions/suggestions.
 