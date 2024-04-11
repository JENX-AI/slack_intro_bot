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

# ====================================
# Slack event listeners
# ====================================

@app.event(("member_joined_channel"))
def handle_member_joined_channel(event: dict, say: slack_bolt.Say, logger: logging.Logger) -> None:
    channel_id = event['channel']
    user_id = event['user']
    bot_id = "U06RWGEU2LX"
    say(f"Welcome <@{user_id}> to the <#{channel_id}> channel! Please mention me by typing <@{bot_id}> and fill out the subsequent form!")

@app.event(("app_mention"))
def handle_app_mention_event(body: dict, say: slack_bolt.Say, logger: logging.Logger) -> None:
    ...