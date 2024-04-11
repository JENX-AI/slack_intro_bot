import os, logging
import slack_bolt
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack import WebClient
from dotenv import load_dotenv

# Credentials
load_dotenv("../.env")
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_APP_TOKEN = os.environ["SLACK_APP_TOKEN"]

app = App(token=SLACK_BOT_TOKEN)
client = WebClient(SLACK_BOT_TOKEN)
logger = logging.getLogger(__name__)