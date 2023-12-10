import streamlit as st
import logic.user_state as state
import logic.utility as util
from ui.ui_helpers import *

def get_ai_reply(client: util.OpenAI, model: state.Model, session: state.ChatSession, prompt: str | None) -> str:
    message_placeholder = st.empty()
    full_response = ''

    if prompt != None:
        session.add_message({'role': 'user', 'content': prompt})
    for response in client.chat.completions.create(
                model=model.name,
                temperature=model.temperature,
                messages=[
                    {'role': m['role'], 'content': m['content']}
                    for m in session.messages
                ],
                stream=True,
            ):
        if response.choices:
            first_choice = response.choices[0]
            if first_choice.delta and first_choice.delta.content:
                full_response += first_choice.delta.content
        message_placeholder.markdown(full_response + '▌')
    message_placeholder.markdown(full_response)
    session.add_message({'role': 'assistant', 'content': full_response})
    return full_response

def show_chat(session: state.ChatSession, model: state.Model):
    if 'prompt_for_tokenizer' not in st.session_state:
        st.session_state['prompt_for_tokenizer'] = None

    hide_tokinzer_workaround_form()
    with st.form("hidden"):
        txt = st.text_input("hidden prompt for tokenizer")
        submitted = st.form_submit_button("Submit")
        if submitted and txt:
            st.session_state['prompt_for_tokenizer'] = txt
            st.rerun()

    # Chat header
    col1, col2 = st.columns(2)
    with col1:
        if st.button('Delete Chat'):
            state.session_manager.delete(session.session_id)
            st.success('Chat deleted successfully!')
            st.rerun()
    with col2:
        if session is not None:
            model_name = model.name if model else "No Model"
            tokens = util.num_tokens_from_messages(session.messages)
            if 'prompt_for_tokenizer' in st.session_state and st.session_state['prompt_for_tokenizer']:
                prompt_tokens = util.num_tokens_from_messages([{'role':'User','content': st.session_state['prompt_for_tokenizer']}])
            else:
                prompt_tokens = 0
            if prompt_tokens > 0:
                st.write(f"{model_name} / {tokens} +{prompt_tokens}")
            else:
                st.write(f"{model_name} / {tokens}")

    if session != None:
        for message in session.messages:
            with st.chat_message(message['role']):
                st.markdown(message['content'])

    if session.messages and session.messages[-1]['role'] == 'user':
        with st.chat_message('assistant'):
            get_ai_reply(util.create_client(model) , model, session, None)
        st.rerun()
    if prompt := st.chat_input('What is up?'):
        st.session_state['prompt_for_tokenizer'] = None
        with st.chat_message('user'):
            st.markdown(prompt)

        with st.chat_message('assistant'):
            get_ai_reply(util.create_client(model) , model, session, prompt)
        st.rerun()
    else:
        st.session_state['prompt_for_tokenizer'] = None 

    embed_chat_input_handler_js()