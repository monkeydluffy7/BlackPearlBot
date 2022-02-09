from os import environ


BOT_CMD = "/fetch"
START_CMD = "/start"
HELP_CMD = "/help"
CHAT_ID = str(environ["CHAT_ID"])
TG_BOT_TOKEN = str(environ["BOT_TOKEN"])
APP_ID = int(environ["API_ID"])
API_HASH = str(environ["API_HASH"])
TIMEOUT = int(environ["TIME_OUT"])
OMDB_API = str(environ["OMDB_KEY"])
TMDB_API = str(environ["TMDB_KEY"])
DRIVE_ID = str(environ["FOLDER_ID"])
INDEX_URL = str(environ["INDEX_URL"])
IS_TD = True
