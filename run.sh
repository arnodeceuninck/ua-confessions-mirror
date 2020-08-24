# A script to run using a cronjob
# Set the right working environment
cd /home/arno/Documents/ua-confessions-mirror
PATH=$PATH:/usr/local/bin:/usr/local/bin/geckodriver:/usr/bin/notify-send

# Make notifications possible
eval "export $(pgrep -u $LOGNAME gnome-session | head -n 1 | xargs -I{} cat /proc/{}/environ | egrep -z DBUS_SESSION_BUS_ADDRESS)";

# Run the python code
python3 main.py  >>ua-confession-mirror-info.log 2>>ua-confession-mirror-error.log