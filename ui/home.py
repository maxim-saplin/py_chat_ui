import streamlit as st
from streamlit_option_menu import option_menu
from enum import Enum
import logic.user_state as state
import logic.utility as util
from ui.chat_session import show_chat
from ui.ui_helpers import *

def show_home(show_logout: callable) -> None:
    # Right align token counter
    right_align_2nd_col()
    hide_streamlit_menu()

    class NavMenuOptions(Enum):
        NEW = 'New'
        SETTINGS = 'Settings'

    # Initialize session state variables
    session_state_defaults = {
        'system_message': 'You are an AI assistant capable of chained reasoning as humans do',
        'prompt': '',
        'chat_session_id': None,
        'selected_model_name': None,
        'selected_menu': None,
    }
    for key, default_value in session_state_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

    # Get Model
    if st.session_state['selected_model_name'] is None:
        model = state.model_repository.get_last_used_model()
        if model is not None:
            st.session_state['selected_model_name'] = model.name
        else:
            st.session_state['selected_model_name'] = None

    # Get Chat session
    if st.session_state['chat_session_id'] is not None:
        session = state.session_manager.get_session_by_id(st.session_state['chat_session_id'])    
    else: session = None

    # Set current view
    if 'selected_menu' not in st.session_state:
        if st.session_state['chat_session_id'] is not None and session is not None:
            st.session_state['selected_menu'] = f'{session.title} ({session.session_id})'
        else:
            st.session_state['selected_menu'] = NavMenuOptions.NEW.value if state.model_repository.models else NavMenuOptions.SETTINGS.value

    # Helpers to get model and OpenAI client
    def get_model() -> state.Model | None:
        if st.session_state['selected_model_name']:
            return state.model_repository.get_model_by_name(st.session_state['selected_model_name'])
        return None

    # App Navigation
    with st.sidebar:
        if show_logout:
            show_logout()
        sessions = state.session_manager.list_sessions()
        session_names = [f'{session.title} ({session.session_id})' for session in sessions]
        menu_options =  session_names + [NavMenuOptions.SETTINGS.value] + [NavMenuOptions.NEW.value] if get_model() else session_names + [NavMenuOptions.SETTINGS.value]
        #previous_menu = st.session_state['selected_menu']
        st.session_state['selected_menu'] = option_menu(None, menu_options, 
            icons=[''] * len(session_names) + ['gear'] + ['plus'], menu_icon='cast', default_index= 0 if session_names else 1)
        if st.session_state['selected_menu'] in [NavMenuOptions.NEW.value, NavMenuOptions.SETTINGS.value]:
            st.session_state['chat_session_id'] = None
            session = None
        else:
            _, session_id_str = st.session_state['selected_menu'].rsplit(' (', 1)
            session_id = int(session_id_str.rstrip(')'))
            st.session_state['chat_session_id'] = session_id
            session = state.session_manager.get_session_by_id(st.session_state['chat_session_id'])

    #### Settings
    if st.session_state['selected_menu'] == NavMenuOptions.SETTINGS.value:
        st.title('Manage Models')
        model_options = ['Add New Model'] + [model.name for model in state.model_repository.models]
        model_selected_index = model_options.index(st.session_state['selected_model_name']) if 'selected_model_name' in st.session_state and st.session_state['selected_model_name'] in model_options else 0
        model_selected_name = st.selectbox('Select Model', model_options, index=model_selected_index)
        selected_model = next((model for model in state.model_repository.models if model.name == model_selected_name), None)
        is_env_model = selected_model.is_env if selected_model else False
        
        is_new_model = model_selected_name == 'Add New Model'
        st.subheader('Add New Model' if is_new_model else 'Environment Model Parameters' if is_env_model else 'Custom Model Settings')

        api_type_options = [option.value for option in state.ApiTypeOptions]
        api_type_index = api_type_options.index(selected_model.api_type) if selected_model else 0
        api_type = st.selectbox('API Type', api_type_options, index=api_type_index, disabled=is_env_model, on_change=lambda: st.rerun())
        is_openai_type = api_type == state.ApiTypeOptions.OPENAI.value

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
                model = state.Model(name, api_key, api_type, api_version, api_base, temperature)
                state.model_repository.add(model)
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
                    state.model_repository.update(selected_model)
                    st.session_state['selected_model_name'] = selected_model.name 
                    st.success('Model updated successfully!')
                    st.rerun()
                if st.button('Delete Model'):
                    state.delete(selected_model.name)
                    st.success('Model deleted successfully!')
                    last_model = state.model_repository.get_last_used_model()
                    st.session_state['selected_model_name'] = last_model.name if last_model else None
                    st.rerun()
                
    #### Starting a chat
    elif st.session_state['selected_menu'] == NavMenuOptions.NEW.value:
        st.title('New Chat')
        model_options = [model.name for model in state.model_repository.models]
        selected_model_index = model_options.index(st.session_state['selected_model_name']) if st.session_state['selected_model_name'] in model_options else 0
        st.session_state['selected_model_name'] = st.selectbox('Model', model_options, index=selected_model_index)
        st.session_state['system_message'] = st.text_area('System message', st.session_state['system_message'])
        temperature = st.slider('Temperature', 0.0, 1.0, get_model().temperature, 0.01)
        prompt = st.text_area('Prompt', st.session_state['prompt'])
        st.button("Send message", type="primary")
        if prompt:
            title = prompt.split()[:5]
            model = get_model()
            session = state.session_manager.create_session(model, ' '.join(title))
            if st.session_state['system_message']:
                session.add_message({'role': 'system', 'content': st.session_state['system_message']})
            session.add_message({'role': 'user', 'content': prompt}) 
            st.session_state['selected_menu'] = f'{session.title} ({session.session_id})'
            st.session_state['chat_session_id'] = session.session_id
            model.temperature = temperature
            state.model_repository.update(model)
            state.model_repository.set_last_used_model(model.name)
            st.rerun()

        # def start_new_chat(model_name, system_message, prompt, temperature):
        #     st.title('New Chat')
        #     model_options = [model.name for model in state.model_repository.models]
        #     selected_model_index = model_options.index(model_name) if model_name in model_options else 0
        #     model_name = st.selectbox('Model', model_options, index=selected_model_index)
        #     system_message = st.text_area('System message', system_message)
        #     temperature = st.slider('Temperature', 0.0, 1.0, get_model().temperature, 0.01)
        #     prompt = st.text_area('Prompt', prompt)
        #     st.button("Send message", type="primary")
        #     if prompt:
        #         title = prompt.split()[:5]
        #         model = get_model()
        #         session = state.session_manager.create_session(model, ' '.join(title))
        #         if system_message:
        #             session.add_message({'role': 'system', 'content': system_message})
        #         session.add_message({'role': 'user', 'content': prompt}) 
        #         st.session_state['selected_menu'] = f'{session.title} ({session.session_id})'
        #         st.session_state['chat_session_id'] = session.session_id
        #         model.temperature = temperature
        #         state.model_repository.update(model)
        #         state.model_repository.set_last_used_model(model.name)
        #         st.rerun()

        # # Call the function with current state values
        # start_new_chat(
        #     st.session_state['selected_model_name'],
        #     st.session_state['system_message'],
        #     st.session_state['prompt'],
        #     get_model().temperature
        # )
            
            
    #### Chat
    else:
        show_chat(session, get_model())
