import streamlit as st
from streamlit_option_menu import option_menu
from logic import *
from ui_helpers import *

client = get_client()

#### UI starts here

# Right align token counter
right_align_2nd_col()
hide_streamlit_menu()

if 'openai_model' not in st.session_state:
    st.session_state['openai_model'] = env_model

if 'messages' not in st.session_state:
    st.session_state.messages = []


with st.sidebar:
    selected = option_menu(None, ['New', 'Some chat 1', 'Some chat 2', 'Settings'], 
        icons=['plus', '','', 'gear'], menu_icon='cast', default_index=1)
    selected

col1, col2= st.columns(2)

if (selected != "New" ):
    with col1:
        st.title('Chat')

    with col2:
        tokens = num_tokens_from_messages(st.session_state.messages)
        st.write(tokens)

for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

temperature = env_temperature if env_temperature else 0.7
system_message = 'You are an AI assistant capable of chained reasoning as humans do'
prompt = ''

#### MODEL SETTINGS
if selected == 'New':
    model_selected = st.selectbox('Model', ('(env): ' + env_model, 'Cust model 2'))
    system_message = st.text_area('System message', system_message)
    temperature= st.slider('Temperature', 0.0, 1.0, temperature, 0.01)
    prompt = st.text_area('Prompt', prompt)
    st.button("Send message", type="primary")
#### CHAT
else:
    if prompt := st.chat_input('What is up?'):
        st.session_state.messages.append({'role': 'user', 'content': prompt})
        with st.chat_message('user'):
            st.markdown(prompt)

        with st.chat_message('assistant'):
            message_placeholder = st.empty()
            full_response = ''
            for response in client.chat.completions.create(
                model=st.session_state['openai_model'],
                messages=[
                    {'role': m['role'], 'content': m['content']}
                    for m in st.session_state.messages
                ],
                stream=True,
            ):
                if response.choices:
                    first_choice = response.choices[0]
                    if first_choice.delta and first_choice.delta.content:
                        full_response += first_choice.delta.content
                message_placeholder.markdown(full_response + '▌')
            message_placeholder.markdown(full_response)
        st.session_state.messages.append({'role': 'assistant', 'content': full_response})
        st.rerun()