import os
from openai import OpenAI, AzureOpenAI
import streamlit as st
from dotenv import load_dotenv
import tiktoken

load_dotenv()

api_key = os.environ.get("OPENAI_API_KEY")
api_type = os.environ.get("API_TYPE")
api_version = os.environ.get("API_VERSION")
api_base = os.environ.get("OPENAI_API_BASE")
model = os.environ.get("MODEL")
temperature = float(os.environ.get("TEMPERATURE"))

encoding = tiktoken.get_encoding("cl100k_base")

def num_tokens_from_messages(messages):
    """Return the number of tokens used by a list of messages."""

    if not messages: return 0

    tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
    tokens_per_name = -1  # if there's a name, the role is omitted

    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens

client = AzureOpenAI(api_key=api_key, 
                     azure_endpoint=api_base, 
                     api_version=api_version,
                     azure_deployment=model) if api_type == "azure" else OpenAI(api_key=api_key)

#### UI starts here

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = model

if "messages" not in st.session_state:
    st.session_state.messages = []

st.markdown(
    """
    <style>
        div[data-testid="column"]:nth-of-type(2)
        {
            text-align: end;
        } 
    </style>
    """,unsafe_allow_html=True
)

col1, col2= st.columns(2)

with col1:
    st.title("Chat")

with col2:
    tokens = num_tokens_from_messages(st.session_state.messages)
    st.write(tokens)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        for response in client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        ):
            if response.choices:
                first_choice = response.choices[0]
                if first_choice.delta and first_choice.delta.content:
                    full_response += first_choice.delta.content
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    st.rerun()