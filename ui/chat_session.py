import streamlit as st
import logic.user_state as state
import logic.utility as util
from logic.utility import get_tokenizer
from ui.ui_helpers import (chat_bottom_padding, chat_collapse_markdown_hidden_elements, right_align_2nd_col_tokenizer,
                           show_cancel_generate_button_js, set_chat_input_text,
                           embed_chat_input_tokenizer, hide_tokenzer_workaround_form,
                           show_stop_generate_chat_input_js, cancel_generation_button_styles)


def show_chat_session(chat_session: state.ChatSession):
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
    if 'prev_chat_session' not in st.session_state:
        st.session_state['prev_chat_session'] = None

    if chat_session != st.session_state['prev_chat_session']:
        st.session_state['token_count'] = None  # if a new chat session is open - recalculate messages size
        st.session_state['prev_chat_session'] = chat_session

    hide_tokenzer_workaround_form()
    chat_bottom_padding()
    chat_collapse_markdown_hidden_elements()
    cancel_generation_button_styles()
    right_align_2nd_col_tokenizer()

    # Chat header
    col1, col2 = st.columns(2)

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
                st.session_state['generating'] = False
                try:
                    st.session_state['canceled_prompt'] = chat_session.messages[-1]['content']
                except Exception as e:
                    print(f"Error saving canceled prompt: {e}")
                chat_session.delete_last_user_message()
                st.rerun()

        # Recovery from inconsistent state
        if st.session_state['generating'] and chat_session.messages and chat_session.messages[-1]['role'] == 'user':
            st.session_state['generating'] = False
        #     st.session_state['get_and_display_ai_reply_BREAK'] = True

        if not st.session_state['generating']:
            # Tried doing nicely server-sde (setting sttuds to generating after promnpt, show stop button etc.)
            # Yet it srrms the st.chat_input() does way more behind the scenese, when OpenAI ran streaming response
            # thre were some silen failures under the hood of streamlit and not chat generation worked, reliably
            # Deffering to js tricks and toggling control's visibility

            prompt = None
            user_message_last = False
            # User prompt came in from New Chat
            if chat_session.messages and chat_session.messages[-1]['role'] == 'user':
                prompt = chat_session.messages[-1]['content']
                user_message_last = True
            else:
                prompt = st.chat_input('What is up?', disabled=st.session_state['generating'])

            if prompt is not None:
                st.session_state['token_count'] = None
                st.session_state['prompt_for_tokenizer'] = None
                st.session_state['generating'] = True
                if not user_message_last:
                    chat_session.add_message({'role': 'user', 'content': prompt})
                    with st.chat_message('assistant', avatar='ui/user.png'):
                        st.markdown(prompt)
                show_cancel_generate_button_js()
                with st.chat_message('assistant', avatar='ui/ai.png'):
                    message_placeholder = st.empty()
                    st.session_state['get_and_display_ai_reply_BREAK'] = False
                    get_and_display_ai_reply(util.create_client(chat_session.model), chat_session.model, chat_session, message_placeholder)
                    st.session_state['generating'] = False
                    st.rerun()

            st.session_state['generating'] = False

    except Exception as e:
        st.session_state['generating'] = False
        st.session_state['get_and_display_ai_reply_BREAK'] = False
        with st.container():
            st.write('An error occurred while sending Chat API request')
            st.write(e)

    if not st.session_state['generating']:
        model = model_repository.get_last_used_model()
        with col2:
            with st.form("hidden"):
                txt = st.text_area("tokenizer2").strip()
                st.form_submit_button("Submit")
                if txt != st.session_state['prompt_for_tokenizer'] \
                        and not (txt == '' and st.session_state['prompt_for_tokenizer'] is None):
                    st.session_state['prompt_for_tokenizer'] = None if txt == '' else txt
                    # st.rerun()
            embed_chat_input_tokenizer()

    show_stop_generate_chat_input_js()
    # Cancelation happened, fill in chat input with past prompt
    if st.session_state['canceled_prompt'] not in (None, ''):
        set_chat_input_text(st.session_state['canceled_prompt'])
        st.session_state['canceled_prompt'] = None

    with col1:
        if st.button('Delete Chat'):
            state.session_manager.delete(chat_session.session_id)
            st.session_state['get_and_display_ai_reply_BREAK'] = True
            st.session_state['generating'] = False
            st.rerun()
    with col2:
        if chat_session is not None:
            model_alias = chat_session.model.alias if chat_session.model else "No Model"
            if st.session_state['token_count'] is None:
                tokenizer = get_tokenizer(chat_session.model.tokenizer_kind)
                st.session_state['token_count'] = util.num_tokens_from_messages(chat_session.messages, tokenizer)
            if 'prompt_for_tokenizer' in st.session_state and st.session_state['prompt_for_tokenizer']:
                prompt_tokens = util.num_tokens_from_messages(
                    [{'role': 'User', 'content': st.session_state['prompt_for_tokenizer']}], tokenizer)
            else:
                prompt_tokens = 0
            if prompt_tokens > 0:
                st.write(f"{model_alias} / {st.session_state['token_count'] } +{prompt_tokens}")
            else:
                st.write(f"{model_alias} / {st.session_state['token_count'] }")


def get_and_display_ai_reply(client, model: state.Model,
                             chat_session: state.ChatSession,
                             message_placeholder) -> None:
    if st.session_state['get_and_display_ai_reply_BREAK']:
        return
    print('get_and_display_ai_reply')
    try:
        full_response = ''
        message_placeholder.markdown('...')

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
