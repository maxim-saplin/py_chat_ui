import streamlit as st
from streamlit_option_menu import option_menu
from enum import Enum
import logic as lg
import time
from ui_helpers import *

def show_chat(show_logout: callable) -> None:
    # Right align token counter
    right_align_2nd_col()
    hide_streamlit_menu()

    class MenuOptions(Enum):
        NEW = 'New'
        SETTINGS = 'Settings'

    # Initialize session state variables
    session_state_defaults = {
        'system_message': 'You are an AI assistant capable of chained reasoning as humans do',
        'prompt': '',
        'chat_session_id': None,
        'selected_model_name': None,
        'selected_menu': None,
        'prompt_for_tokenizer': None
    }
    for key, default_value in session_state_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

    # Get Model
    if st.session_state['selected_model_name'] is None:
        model = lg.model_repository.get_last_used_model()
        if model is not None:
            st.session_state['selected_model_name'] = model.name
        else:
            st.session_state['selected_model_name'] = None

    # Get Chat session
    if st.session_state['chat_session_id'] is not None:
        session = lg.session_manager.get_session_by_id(st.session_state['chat_session_id'])    
    else: session = None

    # Set current view
    if 'selected_menu' not in st.session_state:
        if st.session_state['chat_session_id'] is not None and session is not None:
            st.session_state['selected_menu'] = f'{session.title} ({session.session_id})'
        else:
            st.session_state['selected_menu'] = MenuOptions.NEW.value if lg.model_repository.models else MenuOptions.SETTINGS.value

    # Helpers to get model and OpenAI client
    def getModel() -> lg.Model | None:
        if st.session_state['selected_model_name']:
            return lg.model_repository.get_model_by_name(st.session_state['selected_model_name'])
        return None

    def get_client() -> lg.OpenAI | lg.AzureOpenAI:
        return lg.create_client(getModel())

    # App Navigation
    with st.sidebar:
        if show_logout:
            show_logout()
        sessions = lg.session_manager.list_sessions()
        session_names = [f'{session.title} ({session.session_id})' for session in sessions]
        menu_options =  session_names + [MenuOptions.SETTINGS.value] + [MenuOptions.NEW.value] if getModel() else session_names + [MenuOptions.SETTINGS.value]
        #previous_menu = st.session_state['selected_menu']
        st.session_state['selected_menu'] = option_menu(None, menu_options, 
            icons=[''] * len(session_names) + ['gear'] + ['plus'], menu_icon='cast', default_index= 0 if session_names else 1)
        if st.session_state['selected_menu'] in [MenuOptions.NEW.value, MenuOptions.SETTINGS.value]:
            st.session_state['chat_session_id'] = None
            session = None
        else:
            _, session_id_str = st.session_state['selected_menu'].rsplit(' (', 1)
            session_id = int(session_id_str.rstrip(')'))
            st.session_state['chat_session_id'] = session_id
            session = lg.session_manager.get_session_by_id(st.session_state['chat_session_id'])


    def get_ai_reply(client: lg.OpenAI | lg.AzureOpenAI, model: lg.Model, session: lg.ChatSession, prompt: str | None) -> str:
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
        model_options = ['Add New Model'] + [model.name for model in lg.model_repository.models]
        model_selected_index = model_options.index(st.session_state['selected_model_name']) if 'selected_model_name' in st.session_state and st.session_state['selected_model_name'] in model_options else 0
        model_selected_name = st.selectbox('Select Model', model_options, index=model_selected_index)
        selected_model = next((model for model in lg.model_repository.models if model.name == model_selected_name), None)
        is_env_model = selected_model.is_env if selected_model else False
        
        is_new_model = model_selected_name == 'Add New Model'
        st.subheader('Add New Model' if is_new_model else 'Environment Model Parameters' if is_env_model else 'Custom Model Settings')

        api_type_options = [option.value for option in lg.ApiTypeOptions]
        api_type_index = api_type_options.index(selected_model.api_type) if selected_model else 0
        api_type = st.selectbox('API Type', api_type_options, index=api_type_index, disabled=is_env_model, on_change=lambda: st.rerun())
        is_openai_type = api_type == lg.ApiTypeOptions.OPENAI.value

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
                model = lg.Model(name, api_key, api_type, api_version, api_base, temperature)
                lg.model_repository.add(model)
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
                    lg.model_repository.update(selected_model)
                    st.session_state['selected_model_name'] = selected_model.name 
                    st.success('Model updated successfully!')
                    st.rerun()
                if st.button('Delete Model'):
                    lg.delete(selected_model.name)
                    st.success('Model deleted successfully!')
                    last_model = lg.model_repository.get_last_used_model()
                    st.session_state['selected_model_name'] = last_model.name if last_model else None
                    st.rerun()
                
    #### Starting a chat
    elif st.session_state['selected_menu'] == MenuOptions.NEW.value:
        st.title('New Chat')
        model_options = [model.name for model in lg.model_repository.models]
        selected_model_index = model_options.index(st.session_state['selected_model_name']) if st.session_state['selected_model_name'] in model_options else 0
        st.session_state['selected_model_name'] = st.selectbox('Model', model_options, index=selected_model_index)
        st.session_state['system_message'] = st.text_area('System message', st.session_state['system_message'])
        temperature = st.slider('Temperature', 0.0, 1.0, getModel().temperature, 0.01)
        prompt = st.text_area('Prompt', st.session_state['prompt'])
        st.button("Send message", type="primary")
        if prompt:
            title = prompt.split()[:5]
            model = getModel()
            session = lg.session_manager.create_session(model, ' '.join(title))
            if st.session_state['system_message']:
                session.add_message({'role': 'system', 'content': st.session_state['system_message']})
            session.add_message({'role': 'user', 'content': prompt}) 
            st.session_state['selected_menu'] = f'{session.title} ({session.session_id})'
            st.session_state['chat_session_id'] = session.session_id
            model.temperature = temperature
            lg.model_repository.update(model)
            lg.model_repository.set_last_used_model(model.name)
            st.rerun()
            
    #### Chat
    else:
        hide_tokinzer_workaround_form()
        with st.form("hidden"):
            txt = st.text_input("hidden prompt for tokenizer")
            submitted = st.form_submit_button("Submit")
            if submitted and txt:
                st.session_state['prompt_for_tokenizer'] = txt
                st.rerun()

        # Chat header
        if st.session_state['selected_menu'] not in [MenuOptions.NEW.value, MenuOptions.SETTINGS.value]:
            col1, col2 = st.columns(2)
            with col1:
                if st.button('Delete Chat'):
                    lg.session_manager.delete(session.session_id)
                    st.success('Chat deleted successfully!')
                    st.session_state['selected_menu'] = MenuOptions.NEW.value
                    st.session_state['chat_session_id'] = None
                    st.rerun()
            with col2:
                if session is not None:
                    model_name = getModel().name if getModel() else "No Model"
                    tokens = lg.num_tokens_from_messages(session.messages)
                    if 'prompt_for_tokenizer' in st.session_state and st.session_state['prompt_for_tokenizer']:
                        prompt_tokens = lg.num_tokens_from_messages([{'role':'User','content': st.session_state['prompt_for_tokenizer']}])
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
                get_ai_reply(get_client() , getModel(), session, None)
            st.rerun()
        if prompt := st.chat_input('What is up?'):
            st.session_state['prompt_for_tokenizer'] = None
            with st.chat_message('user'):
                st.markdown(prompt)

            with st.chat_message('assistant'):
                get_ai_reply(get_client() , getModel(), session, prompt)
            st.rerun()
        else:
           st.session_state['prompt_for_tokenizer'] = None 

        embed_chat_input_handler_js()
