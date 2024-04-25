import os, logging
import slack_bolt
import together
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk import WebClient
from dotenv import load_dotenv

# Utilities
from utils.user_bank import existing_users
from utils.questions import QUESTIONS, answers
from utils.llm import SYSTEM_PROMPT, MODEL, MAX_TOKENS, TEMPERATURE, TOP_K, TOP_P, REPETITION_PENALTY, create_prompt, create_output

# Credentials
load_dotenv()
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
    bot_id = "U06U9E0BGVC"
    channel_id = event['channel']

    if user_id not in existing_users and user_id != bot_id:
        say(f"Welcome <@{user_id}> to the <#{channel_id}> channel! Please mention me by typing <@{bot_id}> and answer the subsequent questions!")

@app.event(("app_mention"))
def handle_app_mention_event(body: dict, say: slack_bolt.Say, logger: logging.Logger) -> None:
    user_id = body['event']['user']
    bot_id = "U06U9E0BGVC"
    output_channel = body['event']['channel']
    try:
        channel_id = body["event"]["thread_ts"]
    except KeyError:
        channel_id = body["event"]["ts"]
    thread_timestamp = body["event"]["ts"]

    try:
        # If it is user's first mention, ask question 1, and create placeholder answer
        counter = 1 if user_id not in answers.keys() else (len(answers[user_id]))
        if user_id not in answers.keys():
            say(QUESTIONS[1], thread_ts = thread_timestamp)
            answers[user_id] = {}
            answers[user_id][QUESTIONS[1]] = ''
    
        # If it isn't the user's first mention, check the length of the user's answers
        # Add the answer to the previous answer's empty placeholder, ask and append the next question
        else:
            user_answer = body['event']['text'].split('>')[1].strip()    # remove the bot's slack ID from the answer
            answers[user_id][QUESTIONS[counter]] = user_answer
            say(QUESTIONS[counter + 1], thread_ts = thread_timestamp)    # intended key error here on counter 5 + 1 (QUESTIONS[6] doesn't exist)
            answers[user_id][QUESTIONS[counter + 1]] = ''
        print(answers)
    except KeyError:    # intended key error fires here to finish off the task  
        if user_id not in existing_users: 
            print(answers)
            print('here we go')
            say("Thank you for answering my questions. You may close this thread", thread_ts = thread_timestamp)
            created_prompt = create_prompt(SYSTEM_PROMPT, answers, user_id)
            complete_output = create_output(created_prompt)
            say(complete_output)
            # existing_users.append(user_id)
            # BELOW LINE IS FOR REPEATED USER INTROS
            answers.pop(user_id)
            
        else:
            say("Hi again, I've introduced you already :)", thread_ts = thread_timestamp)
            
# ====================================
# Initialisation
# ====================================

if __name__ == "__main__":
    # Create an app-level token with connections:write scope
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()