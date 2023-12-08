import streamlit as st
from streamlit_option_menu import option_menu
from enum import Enum
from logic import *
from ui_helpers import *

# Right align token counter
right_align_2nd_col()
hide_streamlit_menu()

class MenuOptions(Enum):
    NEW = 'New'
    SETTINGS = 'Settings'

if 'system_message' not in st.session_state:
    st.session_state['system_message'] = 'You are an AI assistant capable of chained reasoning as humans do'
if 'prompt' not in st.session_state:
    st.session_state['prompt'] = ''
if 'chat_session_id' not in st.session_state:
    st.session_state['chat_session_id'] = None
if 'selected_model_name' not in st.session_state:
    model = model_repository.get_last_used_model()
    st.session_state['selected_model_name'] = model.name if model else None

def getModel() -> Model | None:
    if st.session_state['selected_model_name']:
        return model_repository.get_model_by_name(st.session_state['selected_model_name'])
    return None

def get_client() -> OpenAI | AzureOpenAI:
    return create_client(getModel())

session = None
if st.session_state['chat_session_id'] is not None:
    session = session_manager.get_session_by_id(st.session_state['chat_session_id'])    

if 'selected_menu' not in st.session_state:
    if st.session_state['chat_session_id'] is not None:
        st.session_state['selected_menu'] = f'{session.title} ({session.session_id})'
    else:
        st.session_state['selected_menu'] = MenuOptions.NEW.value if model_repository.models else MenuOptions.SETTINGS.value

with st.sidebar:
    sessions = session_manager.list_sessions()
    session_names = [f'{session.title} ({session.session_id})' for session in sessions]
    menu_options = [MenuOptions.NEW.value] + session_names + [MenuOptions.SETTINGS.value] if getModel() else session_names + [MenuOptions.SETTINGS.value]
    selected_index = menu_options.index(st.session_state['selected_menu'])
    previous_menu = st.session_state['selected_menu']
    st.session_state['selected_menu'] = option_menu(None, menu_options, 
        icons=['plus'] + [''] * len(session_names) + ['gear'], menu_icon='cast', default_index=0)#manual_select=selected_index)
    if st.session_state['selected_menu'] in [MenuOptions.NEW.value, MenuOptions.SETTINGS.value]:
        st.session_state['chat_session_id'] = None
        session = None
    else:
        session_title, session_id_str = st.session_state['selected_menu'].rsplit(' (', 1)
        session_id = int(session_id_str.rstrip(')'))
        st.session_state['chat_session_id'] = session_id
        session = session_manager.get_session_by_id(st.session_state['chat_session_id'])
    # if previous_menu != st.session_state['selected_menu']:
    #     st.rerun()

col1, col2= st.columns(2)

if st.session_state['selected_menu'] not in [MenuOptions.NEW.value, MenuOptions.SETTINGS.value]:
    with col1:
        st.title('Chat')

    with col2:
        if session is not None:
            tokens = num_tokens_from_messages(session.messages)
            st.write(tokens)

if session != None:
    for message in session.messages:
        with st.chat_message(message['role']):
            st.markdown(message['content'])

def get_ai_reply(client: OpenAI | AzureOpenAI, model: Model, session: ChatSession, prompt: str | None) -> str:
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

#### Settings
if st.session_state['selected_menu'] == MenuOptions.SETTINGS.value:
    st.title('Manage Models')
    model_options = ['Add New Model'] + [model.name for model in model_repository.models]
    model_selected_index = model_options.index(st.session_state['selected_model_name']) if 'selected_model_name' in st.session_state and st.session_state['selected_model_name'] in model_options else 0
    model_selected_name = st.selectbox('Select Model', model_options, index=model_selected_index)
    selected_model = next((model for model in model_repository.models if model.name == model_selected_name), None)
    is_env_model = selected_model.is_env if selected_model else False
    
    is_new_model = model_selected_name == 'Add New Model'
    st.subheader('Add New Model' if is_new_model else 'Environment Model Settings' if is_env_model else 'Custom Model Settings')

    api_type_options = [option.value for option in ApiTypeOptions]
    api_type_index = api_type_options.index(selected_model.api_type) if selected_model else 0
    api_type = st.selectbox('API Type', api_type_options, index=api_type_index, disabled=is_env_model, on_change=lambda: st.rerun())
    is_openai_type = api_type == ApiTypeOptions.OPENAI.value

    name = st.text_input('Model Name', value=model_selected_name if not is_new_model else '', disabled=is_env_model)
    api_key = st.text_input('API Key', selected_model.api_key if selected_model else '', disabled=is_env_model)
    api_version = st.text_input('API Version', selected_model.api_version if selected_model else '', disabled=is_env_model or is_openai_type)
    api_base = st.text_input('API Base', selected_model.api_base if selected_model else '', disabled=is_env_model or is_openai_type)
    temperature = st.slider('Temperature', 0.0, 1.0, selected_model.temperature if selected_model else 0.7, 0.01, disabled=is_env_model)

    # Validation summary
    errors = []
    if not name and not is_env_model and is_new_model:
        errors.append('Model Name is required.')
    if not api_key and not is_env_model:
        errors.append('API Key is required.')
    if not api_version and not is_env_model and not is_openai_type:
        errors.append('API Version is required.')
    if not api_base and not is_env_model and not is_openai_type:
        errors.append('API Base is required.')
    if temperature is None and not is_env_model:
        errors.append('Temperature is required.')

    if errors:
        for error in errors:
            st.error(error)
    
    if is_new_model:
        if st.button('Add Model') and not errors:
            model = Model(name, api_key, api_type, api_version, api_base, temperature)
            model_repository.add(model)
            st.success('Model added successfully!')
            st.session_state['selected_model_name'] = model.name 
            st.rerun()
    else:
        if not is_env_model:
            if st.button('Update Model') and not errors:
                selected_model.name = name
                selected_model.api_key = api_key
                selected_model.api_type = api_type
                selected_model.api_version = api_version
                selected_model.api_base = api_base
                selected_model.temperature = temperature
                model_repository.update(selected_model)
                st.session_state['selected_model_name'] = selected_model.name 
                st.success('Model updated successfully!')
                st.rerun()
            if st.button('Delete Model'):
                model_repository.delete(selected_model.name)
                st.success('Model deleted successfully!')
                last_model = model_repository.get_last_used_model()
                st.session_state['selected_model_name'] = last_model.name if last_model else None
                st.rerun()
            
#### Starting a chat
elif st.session_state['selected_menu'] == MenuOptions.NEW.value:
    st.title('New Chat')
    model_options = [model.name for model in model_repository.models]
    selected_model_index = model_options.index(st.session_state['selected_model_name']) if st.session_state['selected_model_name'] in model_options else 0
    st.session_state['selected_model_name'] = st.selectbox('Model', model_options, index=selected_model_index)
    st.session_state['system_message'] = st.text_area('System message', st.session_state['system_message'])
    temperature = st.slider('Temperature', 0.0, 1.0, getModel().temperature, 0.01)
    prompt = st.text_area('Prompt', st.session_state['prompt'])
    st.button("Send message", type="primary")
    if prompt:
        title = prompt.split()[:5]
        model = getModel()
        session = session_manager.create_session(model, ' '.join(title))
        if st.session_state['system_message']:
            session.add_message({'role': 'system', 'content': st.session_state['system_message']})
        session.add_message({'role': 'user', 'content': prompt}) 
        st.session_state['selected_menu'] = f'{session.title} ({session.session_id})'
        st.session_state['chat_session_id'] = session.session_id
        model.temperature = temperature
        model_repository.update(model)
        st.rerun()
#### Chat
else:
    if session.messages and session.messages[-1]['role'] == 'user':
        with st.chat_message('assistant'):
            full_response = get_ai_reply(get_client() , getModel(), session, None)
        #session.add_message({'role': 'assistant', 'content': full_response})
        st.rerun()
    if prompt := st.chat_input('What is up?'):
        session.add_message({'role': 'user', 'content': prompt})
        with st.chat_message('user'):
            st.markdown(prompt)

        with st.chat_message('assistant'):
            full_response = get_ai_reply(get_client() , getModel(), session, prompt)
        #session.add_message({'role': 'assistant', 'content': full_response})
        st.rerun()
