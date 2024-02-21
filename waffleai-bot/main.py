import re
import requests
import wikipedia
import telebot
import os
import json
from bs4 import BeautifulSoup

hf_token = ''
telegram_token = ''

def search(topics):
        results = []
        try:
            topic = topics[0]
            try:
                web_search = requests.get("https://noogle-6opb.onrender.com/search", params={"query":topic})
                web_search = web_search.text
            except Exception as e:
                print(f"An error occurred during web search: {e}")
                web_search = ""
            try:
                wiki_text = wikipedia.summary(topic)
            except wikipedia.exceptions.PageError:
                print(f"No Wikipedia page found for: {topic}")
                wiki_text = ""
            except wikipedia.exceptions.DisambiguationError as e:
                print(f"Multiple Wikipedia pages found for: {topic}. Please be more specific. Options include: {e.options}")
                wiki_text = ""
            except Exception as e:
                print(f"An error occurred during Wikipedia summary fetch: {e}")
                wiki_text = ""
            prompt_reformed = f"WEB_RESPONSE: {{search: {web_search}, wiki: {wiki_text}}}"
            results.append(prompt_reformed)
            print(results)
            return "\n".join(results)
        except:
            return "Not found"

API_URL = "https://api-inference.huggingface.co/models/openchat/openchat-3.5-0106"
headers = {"Authorization": f"Bearer {hf_token}"}
def query(payload):
        response = requests.post(API_URL, headers=headers, json=payload)
        return response.json()
    
def replace_assistant(strin):
        e = re.sub(r'<\|system\|>.*<\|assistant\|>', '', strin, flags=re.DOTALL)
        e = re.sub(r'(?<=\?imgae\?)\S+', '', e)
        return e.strip()
    
def search_prompts(user_request):
    prompt = f"""
        <|system|>
        I give you request for an Ai assistant, you think of 1 prompt for internet search (They might be simple and brief.).
        You need to give Google search prompt - it looks like "how to cook waffles" or "how to write telegram bot".
        User gives you question like this - "Hi. Can you help me write a telegram bot in Python?" You need to answer like this - "telegram bot on python"
        You need to print prompt like this:
        "
        <request>
        prompt-goes-here
        </request>
        "
        If no prompts required (user just wants to have a friendly chat, etc.) - Write "" and only this! 
        Always respond in the same language as user used to make his request.

        User request:
        </s>
        <|user|>
        {user_request}
        </s>
        <|assistant|>
        """
    response = query({
        "inputs": prompt,
        "parameters": {"max_new_tokens": 8000, "use_cache": False, "max_time": 120.0},
        "options": {"wait_for_model": True}
    })
    try:
        cleaned_response = replace_assistant(response[0]["generated_text"])
        prompts = re.findall(r'<request>\n\s*(.*?)\n\s*</request>', cleaned_response, re.DOTALL)
        for prompt in prompts:
            print(prompt)
    except:
        prompts = []
    return prompts
    
    
def send(prompt, requested):
        for i in range(0, 10):
            try:
                prompt = f"""
                    <|system|>
                    You are an extremely smart Ai with name WaffleAi (That's ur only name). Give links in the end of prompts. Always finish your answer. Make answers as big as possible. Use markdown.
                    Always resoond in the same language as user used to make his request. WaffleAi is based on OpenChat-3.5 language model. official links for waffleai are (https://waffleai.streamlit.app/ , https://waffleai-stoideas.streamlit.app/ , https://t.me/WaffleAi).
                    </s>
                    <|user|>
                    {prompt}, {requested}
                    </s>
                    <|assistant|>
                    """
                response = query({
                    "inputs": prompt,
                    "parameters": {"max_new_tokens": 9000, "use_cache": False, "max_time": 120.0},
                    "options": {"wait_for_model": True}
                })
                full_response = replace_assistant(response[0]["generated_text"])
                return full_response
                break
            except Exception as e:
                print(response)
                print(e)
                pass
        return "Error"
    
bot = telebot.TeleBot(telegram_token)
    
    
@bot.message_handler(commands=['start'])
def start(message):
        bot.reply_to(message, "Hi! I'm your AI assistant. How can I help you?")
    
@bot.message_handler(func=lambda m: True)
def handle_message(message):
        user_request = message.text
        print(user_request)
        prompts = search_prompts(user_request)
        search_results = search(prompts)
        ai_response = send(user_request, search_results)
        bot.reply_to(message, ai_response,parse_mode="Markdown")
        
    
bot.infinity_polling(skip_pending=True)
