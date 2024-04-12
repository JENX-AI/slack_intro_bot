import os, logging
import slack_bolt
import together
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack import WebClient
from dotenv import load_dotenv

# Utilities
from utils.user_bank import existing_users
from utils.questions import QUESTIONS, answers
from utils.llm import SYSTEM_PROMPT, MODEL, MAX_TOKENS, TEMPERATURE, TOP_K, TOP_P, REPETITION_PENALTY, create_prompt, create_output

# Credentials
load_dotenv("../.env")
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_APP_TOKEN = os.environ["SLACK_APP_TOKEN"]
together.api_key = os.environ["TOGETHER_API_KEY"]

app = App(token=SLACK_BOT_TOKEN)
client = WebClient(SLACK_BOT_TOKEN)
logger = logging.getLogger(__name__)

# ====================================
# Slack event listeners
# ====================================

@app.event(("member_joined_channel"))
def handle_member_joined_channel(event: dict, say: slack_bolt.Say, logger: logging.Logger) -> None:
    user_id = event['user']
    bot_id = "U06RWGEU2LX"
    channel_id = event['channel']

    if user_id not in existing_users:
        say(f"Welcome <@{user_id}> to the <#{channel_id}> channel! Please mention me by typing <@{bot_id}> and answer the subsequent questions!")


@app.event(("app_mention"))
def handle_app_mention_event(body: dict, say: slack_bolt.Say, logger: logging.Logger) -> None:
    user_id = body['event']['user']
    bot_id = "U06RWGEU2LX"
    output_channel = body['event']['channel']
    try:
        channel_id = body["event"]["thread_ts"]
    except KeyError:
        channel_id = body["event"]["ts"]
    thread_timestamp = body["event"]["ts"]
    
    try:
        counter = 1 if user_id not in answers.keys() else (len(answers[user_id]) + 1)
        say(QUESTIONS[counter], thread_ts = thread_timestamp)
        if user_id not in answers.keys():
            answers[user_id] = [QUESTIONS[counter]]
        else: 
            answers[user_id].append(body['event']['text'] + " | " + QUESTIONS[counter])
        print(answers)
    except KeyError:
        if user_id not in existing_users:
            answers[user_id].append(body['event']['text'])
            print(answers)
            say("Thank you for answering my questions. You may close this thread", thread_ts = thread_timestamp)
            created_prompt = create_prompt(SYSTEM_PROMPT, answers, user_id)
            complete_output = create_output(created_prompt)
            # say(complete_output, thread_ts = thread_timestamp)
            say(complete_output)
            existing_users.append(user_id)
        else:
            say("User has already been introduced", thread_ts = thread_timestamp)
        
    # if user_id not in existing_users:
    #     say(QUESTIONS, thread_ts = thread_timestamp)
    #     existing_users.append(user_id)
    # else:
    #     say("You are not a new user.", thread_ts = thread_timestamp)





# ====================================
# Initialisation
# ====================================

if __name__ == "__main__":
    # Create an app-level token with connections:write scope
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()