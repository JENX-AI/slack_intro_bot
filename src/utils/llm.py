# -*- coding: utf-8 -*-
import together
from utils.questions import QUESTIONS, answers

MODEL = "togethercomputer/llama-2-13b-chat"
MAX_TOKENS = 400
TEMPERATURE = 0.0
TOP_K = 50
TOP_P = 0.7
REPETITION_PENALTY = 1.1

SYSTEM_PROMPT = f"""
    You need to introduce a user based on their answers to the following questions: {QUESTIONS}
    Start your message with "I'd like to introduce our newest member!" 
"""

def create_prompt(syst_prompt: str, user_answers: str, user: str) -> str:
    return f"<s>[INST] <<SYS>>{syst_prompt}<</SYS>>\\n\\n" \
        f"[INST] Here are {user}'s answers: {user_answers}[/INST]"

def create_output(prompt):
    try:
        output = together.Complete.create(
            prompt,
            model=MODEL, max_tokens=MAX_TOKENS, temperature=TEMPERATURE, 
            top_k=TOP_K, top_p=TOP_P, repetition_penalty=REPETITION_PENALTY,
            stop=["</s>"]
        )
        response = output["output"]["choices"][0]["text"]
    except Exception as e:
        response = f"Error: {e}. \n\nPlease make sure your API key is correct and valid."
    return response

