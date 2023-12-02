import streamlit as st
from logic import *
from ui_helpers import *

client = get_client()

#### UI starts here

# Right align token counter
right_align_2nd_col()
hide_streamlit_menu()

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = model

if "messages" not in st.session_state:
    st.session_state.messages = []


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