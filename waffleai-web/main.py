import streamlit as st
import requests
import time
import re
import wikipedia

hf_token = ""

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

def send(prompt, requested):
    print(requested)
    for i in range(0, 10):
        try:
            prompt = f"""
                <|system|>
                You are an extremely smart Ai with name WaffleAi (That's ur only name). Give links in the end of prompts. Always finish your answer and use markdown. 
                Always resoond in the same language as user used to make his request. WaffleAi is based on OpenChat-3.5 language model. official links for waffleai are (https://waffleai.streamlit.app/ - official link, https://waffleai-stoideas.streamlit.app/ - second official link, https://t.me/WaffleAi - official telegram channel, https://t.me/waffleai_bot). You were created by Wafflelover404 (tg: @Wafflelover404) and csoftware (tg: @halflifelover)  
                </s>
                <|user|>
                {prompt}, {requested}
                </s>
                <|assistant|>
                """
            response = query({
                "inputs": prompt,
                "parameters": {"max_new_tokens": 8000, "use_cache": False, "max_time": 120.0},
                "options": {"wait_for_model": True}
            })
            print(response)
            full_response = replace_assistant(response[0]["generated_text"])
            return full_response
            break
        except Exception as e:
            print(e)
            pass
    return "Error"

# Streamlit code starts here
st.set_page_config(
        page_title="WaffleAI",
        page_icon=":waffle:"
)
st.markdown("""
    <style>
        footer {visibility: hidden;}
        .reportview-container {
            margin-top: -3em;

        }
        #MainMenu {visibility: hidden;}
        .stDeployButton {display:none;}

        #stDecoration {display:none;}
        [data-testid="baseButton-header"] {visibility: hidden;}
        img{max-width: 30%;max-height: 40%;}
        img[alt="Running..."]{visibility: hidden};
    </style>
</div>
""", unsafe_allow_html=True)
st.title("WaffleAI reimaginated")

message_list = []
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
if prompt := st.chat_input("Enter your prompt"):
    st.markdown("""
    <style>
        div[data-baseweb="base-input"] {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    prompts = search_prompts(prompt)
    search_results = search(prompts)
    ai_response = send(prompt, search_results)
    message_placeholder = st.chat_message("assistant").empty()
    full_response = ""
    for message in ai_response:
        full_response += message
        if full_response == "":
            full_response = "Nothing is generated"
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    st.markdown("""
    <style>
        div[data-baseweb="base-input"] {visibility: visible;}
    </style>
    """, unsafe_allow_html=True)
