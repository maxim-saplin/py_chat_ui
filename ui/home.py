import streamlit as st
from streamlit_option_menu import option_menu
from enum import Enum
import logic.user_state as state
from ui.chat_session import show_chat_session
from ui.new_chat import start_new_chat
from ui.settings import manage_models
from ui.ui_helpers import sidebar_about_link


def show_home(show_logout: callable) -> None:

    class NavMenuOptions(Enum):
        NEW = "New"
        SETTINGS = "Settings"

    # Initialize session state variables
    session_state_defaults = {
        "system_message": "You are an AI assistant capable of chained reasoning as humans do",
        "prompt": "",
        "chat_session_id": None,
        "selected_menu": None,
    }
    for key, default_value in session_state_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

    # Set current view
    if "selected_menu" not in st.session_state:
        st.session_state["selected_menu"] = NavMenuOptions.NEW.value
    elif st.session_state["selected_menu"] is None:
        st.session_state["selected_menu"] = NavMenuOptions.NEW.value

    def get_model() -> state.Model | None:
        return state.model_repository.get_last_used_model()

    # App Navigation
    with st.sidebar:
        if show_logout:
            show_logout()
        sessions = state.session_manager.list_sessions()
        session_names = [
            f"{session.title} ({session.session_id})" for session in sessions
        ]
        model_available = True if get_model() else False
        menu_options = (
            [NavMenuOptions.NEW.value, NavMenuOptions.SETTINGS.value] + session_names
            if model_available
            else [NavMenuOptions.SETTINGS.value] + session_names
        )

        if st.session_state["selected_menu"] not in menu_options:
            st.session_state["selected_menu"] = NavMenuOptions.NEW.value

        def update_selected_menu(selected_menu):
            st.session_state["selected_menu"] = st.session_state["sidebar_option_menu"]

        option_menu(
            None,
            menu_options,
            styles={
                "nav": {"font-family": "monospace;"},
            },
            icons=["plus", "gear"] + [""] * len(session_names),
            menu_icon="cast",
            key="sidebar_option_menu",
            on_change=update_selected_menu,
            manual_select=(menu_options.index(st.session_state["selected_menu"])),
        )
        # st.session_state["selected_menu"] = selected_menu
        if st.session_state["selected_menu"] in [
            NavMenuOptions.NEW.value,
            NavMenuOptions.SETTINGS.value,
        ]:
            st.session_state["chat_session_id"] = None
        else:
            _, session_id_str = st.session_state["selected_menu"].rsplit(" (", 1)
            session_id = int(session_id_str.rstrip(")"))
            st.session_state["chat_session_id"] = session_id

        sidebar_about_link()
        st.markdown(
            "[[?]](https://github.com/maxim-saplin/py_chat_ui/tree/main) · "
            + st.session_state["version"]
            + " · ツ"
        )

    # Settings
    if st.session_state["selected_menu"] == NavMenuOptions.SETTINGS.value:
        state_updates = manage_models(state.model_repository)

        apply_to_st_session(state_updates)
        if st.session_state["models_changed"]:
            st.rerun()

    # New Chat
    elif st.session_state["selected_menu"] == NavMenuOptions.NEW.value:
        st.session_state["prompt"] = None

        state_updates = start_new_chat(
            state.model_repository,
            state.session_manager,
            st.session_state["system_message"],
            get_model().temperature,
        )

        apply_to_st_session(state_updates)
        if st.session_state["chat_session_id"]:
            st.rerun()

    # Chat session/Dialog
    else:
        if st.session_state["selected_menu"] not in [
            NavMenuOptions.NEW.value,
            NavMenuOptions.SETTINGS.value,
        ]:
            session = state.session_manager.get_session_by_id(
                st.session_state["chat_session_id"]
            )
            show_chat_session(session)
        else:
            st.session_state["selected_menu"] = NavMenuOptions.NEW.value


def apply_to_st_session(state_updates):
    for key, value in state_updates.items():
        st.session_state[key] = value
