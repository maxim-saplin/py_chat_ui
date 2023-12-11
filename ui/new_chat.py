import streamlit as st
from ui.ui_helpers import *

def start_new_chat(model_repository, session_manager, selected_model_name, system_message, prompt, temperature):
    st.title('New Chat')
    model_options = [model.name for model in model_repository.models]
    selected_model_index = model_options.index(selected_model_name) if selected_model_name in model_options else 0
    selected_model_name = st.selectbox('Model', model_options, index=selected_model_index)
    model = model_repository.get_model_by_name(selected_model_name)
    session = None            
    system_message = st.text_area('System message', st.session_state['system_message'])
    temperature = st.slider('Temperature', 0.0, 1.0, temperature, 0.01)
    prompt = st.text_area('Prompt', st.session_state['prompt'])
    if st.button("Send message", type="primary"):
        if prompt:
            session = session_manager.create_session(model, ' '.join(prompt.split()[:5]))
            
            if system_message:
                session.add_message({'role': 'system', 'content': system_message})
            session.add_message({'role': 'user', 'content': prompt})
            
            model.temperature = temperature
            model_repository.update(model)
            model_repository.set_last_used_model(model.name)
    
    # Return the updated state
    state_update = {
        'selected_model_name': model.name,
        'system_message': system_message,
        'temperature': temperature
    }
    if session:
        state_update['selected_menu'] = f'{session.title} ({session.session_id})'
        state_update['chat_session_id'] = session.session_id
        state_update['prompt'] = prompt

    return state_update