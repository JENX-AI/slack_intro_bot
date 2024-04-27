import os, logging
import slack_bolt
import together
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk import WebClient
from dotenv import load_dotenv

# Utilities
from utils.llm import SYSTEM_PROMPT, create_prompt, create_output
from utils.logger import get_logger
from utils.questions import QUESTIONS, answers, existing_users

# Credentials
load_dotenv()
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_APP_TOKEN = os.environ["SLACK_APP_TOKEN"]
together.api_key = os.environ["TOGETHER_API_KEY"]

app = App(token=SLACK_BOT_TOKEN)
client = WebClient(SLACK_BOT_TOKEN)
logger = get_logger(__name__)

# ====================================
# Slack event listeners
# ====================================

@app.event(("member_joined_channel"))
def handle_member_joined_channel(event: dict, say: slack_bolt.Say, logger: logging.Logger) -> None:
    """
    Handles response to a new member joining a channel
    
    Parameters
    ----------
    event : dict
        event received from Slack user in Channels
    
    say : slack_bolt.Say
        sends message to Slack
    
    logger : logging.Logger
        logging object
    """
    try:
        user_id = event['user']
        bot_id = app.client.auth_test()['user_id']
        channel_id = event['channel']
    
        if user_id not in existing_users and user_id != bot_id:
            say(f"Welcome <@{user_id}> to the <#{channel_id}> channel! Please mention me by typing <@{bot_id}> and answer the subsequent questions!")
    
    except Exception as e:
        logger.error(f"Error: {e}")


@app.event(("app_mention"))
def handle_app_mention_event(body: dict, say: slack_bolt.Say, logger: logging.Logger) -> None:
    """
    Handles direct (@) messages to chatbot within Channels
    
    Parameters
    ----------
    body : dict
        message received from Slack user in Channels
    
    say : slack_bolt.Say
        sends message to Slack
    
    logger : logging.Logger
        logging object
    """
    try:
        user_id = body['event']['user']
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
                # remove the bot's slack ID from the answer
                user_answer = body['event']['text'].split('>')[1].strip()    
                answers[user_id][QUESTIONS[counter]] = user_answer
                # intended key error here on counter 5 + 1 (QUESTIONS[6] doesn't exist)
                say(QUESTIONS[counter + 1], thread_ts = thread_timestamp)    
                answers[user_id][QUESTIONS[counter + 1]] = ''
            print(answers)
        
        except KeyError:    # intended key error fires here to finish off the task  
            if user_id not in existing_users: 
                # Send acknowledgement in same thread
                say("Thank you for answering my questions. You may close this thread", thread_ts = thread_timestamp)
                
                # Generate prompt based on user's output
                created_prompt = create_prompt(SYSTEM_PROMPT, answers, user_id)
                # Use prompt to generate introduction
                complete_output = create_output(created_prompt)
                say(complete_output)
                # BELOW LINE IS FOR REPEATED USER INTROS
                answers.pop(user_id)
                
            else:
                say("Hi again, I've introduced you already :)", thread_ts = thread_timestamp)
    
    except Exception as e:
        logger.error(f"Error: {e}")

       
# ====================================
# Initialisation
# ====================================

if __name__ == "__main__":
    # Create an app-level token with connections:write scope
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()
