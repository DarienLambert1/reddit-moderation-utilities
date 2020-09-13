# Reddit Moderation Utilities by u/DarienLambert
This is just a collection of miscellaneous scripts to make Reddit moderation easier.

* `get_auth.py`: Gets a `refresh_token` for use in other scripts.
* `copy_sub.py`: Copies a sub (settings, wikis, etc) to another sub. Useful when configuring similar subs or families of subs.

# Requirements
* Python 3.7
* [PRAW](https://praw.readthedocs.io/en/latest/) (the steps below will install it in a virtualenv)

# Installation
```
mkdir -p ~/apps && cd ~/apps
git clone https://github.com/DarienLambert1/reddit-moderation-utilities
cd reddit-moderation-utilities
mkdir -p ~/.virtualenvs
python3 -m venv ~/.virtualenvs/reddit-moderation-utilities
source ~/.virtualenvs/reddit-moderation-utilities/bin/activate
pip3 install -r requirements.txt
```

# First-Time Setup
## Create an app
Go to Reddit's [app creation page](https://ssl.reddit.com/prefs/apps/). Select "script" for the type and give it a name. Put `http://localhost:8080` for the redirect URI. Click "Create App".

Copy the Client ID which appears just below the title and "personal use script" on the app you created. It is not labeled Client ID but it's alpha-numeric and can contain dashes.

Copy the secret which appears just below the Client ID. This only appears once so make sure to copy it.

## Get a refresh token
1. Copy `praw.ini.dist` to `praw.ini`
```
cp praw.ini.dist praw.ini
```

2. Edit `praw.ini` in your text editor of choice, such as `nano praw.ini`.

3. Add the values for client_id and client_secret you copied above.

5. Change the `bot_name` and `bot_author` to values matching your information.

6. Authenticate to Reddit by running the following script:

```
~/.virtualenvs/reddit-moderation-utilities/bin/python3 ~/apps/reddit-moderation-utilities/get_auth.py
```

7. Go to the URL it prints. Allow Reddit access to the app you created. It will redirect you to an invalid URI, but an authentication `code` is in the URI.

8. Copy this `code` and paste it into the script that is still running and press enter.

9. The script will print a `refresh_token` value that you must copy to the `praw.ini` setting.

10. You are now ready to run moderation scripts below. These steps only need to be performed once.

## Run Moderation Scripts
### Copy Sub to Another Sub

1. Execute the script
```
~/.virtualenvs/reddit-moderation-utilities/bin/python3 ~/apps/reddit-moderation-utilities/copy_sub.py
```
2. Input the source sub and target sub (without `r/`).
3. Follow the menu choices.

# License
See `LICENSE.md`