import praw

reddit = praw.Reddit()
print(reddit.auth.url(["identity", "edit", "flair", "modconfig", "report", "modlog",
                       "modposts", "modflair", "modcontributors",
                       "modwiki", "mysubreddits", "read", "structuredstyles", "wikiedit",
                       "wikiread", "report", "modmail", "save"],
                      "some state", "permanent"))

code = input("Enter code from redirect: ")
print("refresh_token=", reddit.auth.authorize(code))
print("User authorized:", reddit.user.me())
