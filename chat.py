import os
from openai import OpenAI, AzureOpenAI
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get("OPENAI_API_KEY")
api_type = os.environ.get("API_TYPE")
api_version = os.environ.get("API_VERSION")
api_base = os.environ.get("OPENAI_API_BASE")
model = os.environ.get("MODEL")
temperature = float(os.environ.get("TEMPERATURE"))

st.title("Chat")

client = AzureOpenAI(api_key=api_key, 
                     azure_endpoint=api_base, 
                     api_version=api_version,
                     azure_deployment=model) if api_type == "azure" else OpenAI(api_key=api_key)

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = model

if "messages" not in st.session_state:
    st.session_state.messages = []

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