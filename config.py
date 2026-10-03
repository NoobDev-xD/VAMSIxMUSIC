import re
from os import getenv

from dotenv import load_dotenv
from pyrogram import filters

load_dotenv()

# Get from my.telegram.org/app
API_ID = int(getenv("API_ID", ""))
API_HASH = getenv("API_HASH", "")

# Get from @BotFather
BOT_TOKEN = getenv("BOT_TOKEN", "")

# Get from MongoDB Atlas
MONGO_DB_URI = getenv("MONGO_DB_URI", "")

DURATION_LIMIT_MIN = int(getenv("DURATION_LIMIT", "60"))

LOGGER_ID = int(getenv("LOGGER_ID", "0"))
OWNER_ID = int(getenv("OWNER_ID", "7574330905"))

# Heroku App Name
HEROKU_APP_NAME = getenv("HEROKU_APP_NAME", "")

# Get from dashboard.heroku.com/account
HEROKU_API_KEY = getenv("HEROKU_API_KEY", "")

UPSTREAM_REPO = getenv(
    "UPSTREAM_REPO",
    "https://github.com/NoobDev-xD/VAMSIxMUSIC",
)

UPSTREAM_BRANCH = getenv("UPSTREAM_BRANCH", "main")

GIT_TOKEN = getenv("GIT_TOKEN")

# Get API Key from @SHRUTIAPIBOT

SUPPORT_CHANNEL = getenv(
    "SUPPORT_CHANNEL",
    "https://t.me/PVUniverse"
)

SUPPORT_CHAT = getenv(
    "SUPPORT_CHAT",
    "https://t.me/+fNTWIJFGzS1lMGE0"
)

AUTO_LEAVING_ASSISTANT = getenv(
    "AUTO_LEAVING_ASSISTANT",
    "False"
).lower() == "true"

# Get from developer.spotify.com/dashboard
SPOTIFY_CLIENT_ID = getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = getenv("SPOTIFY_CLIENT_SECRET")

PLAYLIST_FETCH_LIMIT = int(
    getenv("PLAYLIST_FETCH_LIMIT", "25")
)

TG_AUDIO_FILESIZE_LIMIT = int(
    getenv("TG_AUDIO_FILESIZE_LIMIT", "104857600")
)

TG_VIDEO_FILESIZE_LIMIT = int(
    getenv("TG_VIDEO_FILESIZE_LIMIT", "1073741824")
)

# Get from @Sessionbbbot
STRING1 = getenv("STRING_SESSION")
STRING2 = getenv("STRING_SESSION2")
STRING3 = getenv("STRING_SESSION3")
STRING4 = getenv("STRING_SESSION4")
STRING5 = getenv("STRING_SESSION5")

BANNED_USERS = filters.user()
adminlist = {}
lyrical = {}
votemode = {}
autoclean = []
confirmer = {}

START_IMG_URL = getenv(
    "START_IMG_URL",
    "https://graph.org/file/97d209d2e6b6c8466f656-7623edc528cec4f20f.jpg"
)

PING_IMG_URL = getenv(
    "PING_IMG_URL",
    "https://graph.org/file/e3f44b676bca43a13814b-0952081326229908ba.jpg"
)

PLAYLIST_IMG_URL = "https://graph.org/file/fc0ff3b1e10122cecbb10-4638b9ca1a5b6dba41.jpg"
STATS_IMG_URL = "https://graph.org/file/d7a59b89a4ce36f51b214-e24b2cf72b1c75971f.jpg"
TELEGRAM_AUDIO_URL = "https://graph.org/file/200236eb9153ec8d39abb-a37e1024cf739f2ad7.jpg"
TELEGRAM_VIDEO_URL = "https://graph.org/file/80ddce7b0726dc5ec8e90-2ae43c255f3579a286.jpg"
STREAM_IMG_URL = "https://graph.org/file/95f74f558be6b40210418-4b18f19bccaa5acf70.jpg"
SOUNCLOUD_IMG_URL = "https://graph.org/file/389e88ab6b4f312396f88-0dfeb9d16d46be6e47.jpg"
YOUTUBE_IMG_URL = "https://graph.org/file/15e7170d229260fc6bf3a-bf72e67535bc6daf8d.jpg"
SPOTIFY_ARTIST_IMG_URL = "https://graph.org/file/d7aad09701df67e61093b-6a4900ce5bb819c669.jpg"
SPOTIFY_ALBUM_IMG_URL = "https://graph.org/file/d7aad09701df67e61093b-6a4900ce5bb819c669.jpg"
SPOTIFY_PLAYLIST_IMG_URL = "https://graph.org/file/d7aad09701df67e61093b-6a4900ce5bb819c669.jpg"


def time_to_seconds(time):
    stringt = str(time)
    return sum(
        int(x) * 60 ** i
        for i, x in enumerate(reversed(stringt.split(":")))
    )


DURATION_LIMIT = int(
    time_to_seconds(f"{DURATION_LIMIT_MIN}:00")
)


if SUPPORT_CHANNEL:
    if not re.match("(?:http|https)://", SUPPORT_CHANNEL):
        raise SystemExit(
            "[ERROR] SUPPORT_CHANNEL url must start with https://"
        )

if SUPPORT_CHAT:
    if not re.match("(?:http|https)://", SUPPORT_CHAT):
        raise SystemExit(
            "[ERROR] SUPPORT_CHAT url must start with https://"
        )
