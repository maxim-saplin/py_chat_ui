import streamlit as st
import logic.user_state as state
import logic.utility as util
from ui.ui_helpers import (chat_bottom_padding, chat_collapse_markdown_hidden_elements, right_align_2nd_col_tokenizer,
                           show_cancel_generate_button_js, set_chat_input_text,
                           embed_chat_input_js, hide_tokinzer_workaround_form,
                           show_generate_chat_input_js, cancel_generation_button_styles)


def show_chat_session(chat_session: state.ChatSession, model: state.Model):
    if 'generating' not in st.session_state:
        st.session_state['generating'] = False
    if 'token_count' not in st.session_state:
        st.session_state['token_count'] = None
    if 'prompt_for_tokenizer' not in st.session_state:
        st.session_state['prompt_for_tokenizer'] = None
    if 'canceled_prompt' not in st.session_state:
        st.session_state['canceled_prompt'] = None
    if 'get_and_display_ai_reply_BREAK' not in st.session_state:
        st.session_state['get_and_display_ai_reply_BREAK'] = False

    hide_tokinzer_workaround_form()
    chat_bottom_padding()
    chat_collapse_markdown_hidden_elements()
    cancel_generation_button_styles()
    right_align_2nd_col_tokenizer()

    # Hidden elements to trigger server side counting of token in chat input
    with st.form("hidden"):
        txt = st.text_area("tokenizer").strip()
        st.form_submit_button("Submit")
        if txt != st.session_state['prompt_for_tokenizer'] \
                and not (txt == '' and st.session_state['prompt_for_tokenizer'] is None):
            st.session_state['prompt_for_tokenizer'] = None if txt == '' else txt
            st.rerun()

    # Chat header
    col1, col2 = st.columns(2)
    with col1:
        if st.button('Delete Chat'):
            state.session_manager.delete(chat_session.session_id)
            st.session_state['get_and_display_ai_reply_BREAK'] = True
            st.session_state['generating'] = False
            st.rerun()
    with col2:
        if chat_session is not None:
            model_alias = model.alias if model else "No Model"
            if st.session_state['token_count'] is None:
                st.session_state['token_count'] = util.num_tokens_from_messages(chat_session.messages)
            if 'prompt_for_tokenizer' in st.session_state and st.session_state['prompt_for_tokenizer']:
                prompt_tokens = util.num_tokens_from_messages(
                    [{'role': 'User', 'content': st.session_state['prompt_for_tokenizer']}])
            else:
                prompt_tokens = 0
            if prompt_tokens > 0:
                st.write(f"{model_alias} / {st.session_state['token_count'] } +{prompt_tokens}")
            else:
                st.write(f"{model_alias} / {st.session_state['token_count'] }")

    try:
        if chat_session is not None:
            for message in chat_session.messages:
                with st.chat_message(message['role'],
                                     avatar='ui/ai.png' if message['role'] == 'assistant'
                                     else ('ui/user.png' if message['role'] == 'user' else None)):
                    st.markdown(message['content'])

        with st.container():
            if st.button('Cancel generation'):
                st.session_state['generating'] = False
                st.session_state['get_and_display_ai_reply_BREAK'] = True
                try:
                    st.session_state['canceled_prompt'] = chat_session.messages[-1]['content']
                except Exception as e:
                    print(f"Error saving canceled prompt: {e}")
                chat_session.delete_last_user_message()
                st.rerun()

        if not st.session_state['generating']:
            # User prompt came in from New Chat
            if chat_session.messages and chat_session.messages[-1]['role'] == 'user':
                st.session_state['token_count'] = None
                show_cancel_generate_button_js()
                with st.chat_message('assistant', avatar='ui/ai.png'):
                    st.session_state['generating'] = True
                    st.session_state['get_and_display_ai_reply_BREAK'] = False
                    get_and_display_ai_reply(util.create_client(model), model, chat_session)
                    st.session_state['generating'] = False
                    st.rerun()
            else:
                # Tried doing nicely server-sde (setting sttuds to generating after promnpt, show stop button etc.)
                # Yet it srrms the st.chat_input() does way more behind the scenese, when OpenAI ran streaming response
                # thre were some silen failures under the hood of streamlit and not chat generation worked, reliably
                # Deffering to js tricks and toggling control's visibility
                if prompt := st.chat_input('What is up?', disabled=st.session_state['generating']):
                    st.session_state['token_count'] = None
                    st.session_state['prompt_for_tokenizer'] = None
                    st.session_state['generating'] = True
                    chat_session.add_message({'role': 'user', 'content': prompt})
                    show_cancel_generate_button_js()
                    with st.chat_message('assistant', avatar='ui/user.png'):
                        st.markdown(prompt)
                    with st.chat_message('assistant', avatar='ui/ai.png'):
                        st.session_state['get_and_display_ai_reply_BREAK'] = False
                        get_and_display_ai_reply(util.create_client(model), model, chat_session)
                        st.session_state['generating'] = False
                        st.rerun()

            st.session_state['generating'] = False

    except Exception as e:
        st.session_state['generating'] = False
        with st.container():
            st.write('An error occurred while sending Chat API request')
            st.write(e)

    embed_chat_input_js()
    show_generate_chat_input_js()
    # Cancelation happened, fill in chat input with past prompt
    if st.session_state['canceled_prompt'] not in (None, ''):
        set_chat_input_text(st.session_state['canceled_prompt'])
        st.session_state['canceled_prompt'] = None


def get_and_display_ai_reply(client, model: state.Model,
                             chat_session: state.ChatSession) -> None:
    if st.session_state['get_and_display_ai_reply_BREAK']:
        return
    print('get_and_display_ai_reply')
    try:
        message_placeholder = st.empty()
        full_response = ''

        for response in client.chat.completions.create(
                    model=model.model_or_deployment_name,
                    temperature=model.temperature,
                    messages=[
                        {'role': m['role'], 'content': m['content']}
                        for m in chat_session.messages
                    ],
                    stream=True,
                ):
            if response.choices:
                if st.session_state['get_and_display_ai_reply_BREAK']:
                    print('get_and_display_ai_reply - breaking')
                    break
                first_choice = response.choices[0]
                if hasattr(first_choice, 'delta') and first_choice.delta and first_choice.delta.content:
                    full_response += first_choice.delta.content
                elif hasattr(first_choice, 'content') and first_choice.content:
                    full_response = first_choice.content
            message_placeholder.markdown(full_response + '▌')
        message_placeholder.markdown(full_response)
        if not st.session_state['get_and_display_ai_reply_BREAK']:
            chat_session.add_message({'role': 'assistant', 'content': full_response})
        print('get_and_display_ai_reply - completing')
        return full_response
    finally:
        st.session_state['get_and_display_ai_reply_BREAK'] = False
