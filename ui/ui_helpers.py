import streamlit as st
from streamlit.components.v1 import html


def global_ui_tweaks():
    st.markdown("""
    <style>
        header[data-testid="stHeader"] {
            visibility: hidden;
        }
    </style>
    """, unsafe_allow_html=True)


def register_button_as_link():
    st.markdown("""
    <style>
        div.row-widget button[kind="secondary"] {
            text-decoration: underline;
            cursor: pointer;
            border: none;
            background-color: transparent;
        }
    </style>
    """, unsafe_allow_html=True)


def sidebar_about_link():
    st.markdown("""
    <style>
        div[data-testid="stSidebarUserContent"] div.element-container:last-child  {
            position: fixed;
            top: 13px;
            opacity: 0.5;
            backdrop-filter: blur(15px);
            -webkit-backdrop-filter: blur(15px);
        }
    </style>
    """, unsafe_allow_html=True)


def login_background():
    st.markdown("""
    <style>
        div.stApp {
            background: repeating-linear-gradient(
                45deg,
                rgba(128, 128, 128, 0.15),
                rgba(128, 128, 128, 0.15) 80px,
                transparent 80px,
                transparent 160px
            );
        }

        div.stApp div[data-testid="stForm"]{
            background-color: #232323;
            box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
        }
    </style>
    """, unsafe_allow_html=True)


def right_align_2nd_col_tokenizer():
    st.markdown("""
    <style>
        div[data-testid="column"]:nth-of-type(2) p {
            font-family: monospace;
            text-align: end;
            position: fixed;
            z-index: 999;
            top: 20px;
            right: 40px;
            color: yellow;
            text-shadow: 1.5px 1px 0px black;
            font-weight: 900;
            backdrop-filter: blur(15px);
            -webkit-backdrop-filter: blur(15px);
            padding-left: 20px;
            padding-right: 15px;
            padding-top: 5px;
            padding-bottom: 5px;
            mask-image: radial-gradient(circle, rgba(0,0,0,1) 85%, transparent 100%);
            transition: opacity 100ms ease-in;
            opacity: 0;
            animation: fadeIn 100ms ease-in forwards;
        }

        @keyframes fadeIn {
            to {
                opacity: 1;
            }
        }
    </style>
    """, unsafe_allow_html=True)


def hide_streamlit_toolbar():
    """
    Running man at the top right corner when a request is executed
    """
    st.markdown("""
    <style>
        div[data-testid="stToolbar"] {
            display: none;
        }
    </style>
    """, unsafe_allow_html=True)


def add_theme_customizations():
    """
    Adjusting those styles that were not possible to be changed in config.toml
    """
    st.markdown("""

    <style>
        div.stChatMessage p{
            font-family: sans-serif;
        }
    </style>
    """, unsafe_allow_html=True)


def hide_streamlit_menu():
    """
    Deply, Three Dots button, as well as Made with Streamlit at the bottom
    """
    st.markdown("""
    <style>
        .reportview-container {
            margin-top: -2em;
        }
        #MainMenu {visibility: hidden;}
        .stDeployButton {display:none;}
        footer {visibility: hidden;}
        #stDecoration {display:none;}
    </style>
""", unsafe_allow_html=True)


def hide_tokinzer_workaround_form():
    st.markdown("""
    <style>
        div[data-testid="stForm"] {
            height: 0px;
            overflow: hidden;
            margin: 0;
            padding: 0;
            border: 0;
            opacity: 0;
        }
        section.main div[data-testid="stVerticalBlock"]:last-of-type,
        section.main div[data-testid="stVerticalBlock"]:nth-last-of-type(2) {
            height: 0;
        }
    </style>
""", unsafe_allow_html=True)


def chat_bottom_padding():
    st.markdown("""
        <style>
            div.stChatFloatingInputContainer {
                padding-bottom: 30px;
            }
        </style>
    """, unsafe_allow_html=True)


def stop_generation_button_styles():
    """
    And hide generation button
    """
    st.markdown("""
        <style>
            div[data-testid="stVerticalBlock"]>div[data-testid="stVerticalBlockBorderWrapper"] div.row-widget.stButton {
                text-align: center;
                position: fixed;
                bottom: 31px;
                visibility: hidden;
                z-index: 999;
            }
        </style>
    """, unsafe_allow_html=True)


def show_generate_button_js():
    """
    And hide chat input
    """

    js = """
<script>
console.log("show_generate_button_js");
const stopButton = window.parent.document.querySelector(
    'div[data-testid="stVerticalBlock"]>div[data-testid="stVerticalBlockBorderWrapper"] div.row-widget.stButton');
stopButton.style.visibility = 'visible';
const chatInputContainer = window.parent.document.querySelector('div.stChatInputContainer');
chatInputContainer.style.visibility = 'hidden';
</script>
    """
    html(js, 0, 0, False)


def show_generate_chat_input_js():
    js = """
<script>
console.log("show_generate_chat_input_js");
const stopButton = window.parent.document.querySelector(
    'div[data-testid="stVerticalBlock"]>div[data-testid="stVerticalBlockBorderWrapper"] div.row-widget.stButton');
stopButton.style.visibility = 'hidden';
const chatInputContainer = window.parent.document.querySelector('div.stChatInputContainer');
chatInputContainer.style.visibility = 'visible';
</script>
    """
    html(js, 0, 0, False)


def embed_chat_input_js():
    js = """
<script>
//console.log("Chat input handler is activating...");

let previousValue = '';
const originalTextArea = window.parent.document.querySelector('.stChatInputContainer textarea');
const originalButton = window.parent.document.querySelector('.stChatInputContainer button');
const formInput = window.parent.document.querySelector('div[data-testid="stForm"] input');
const formButton = window.parent.document.querySelector('div[data-testid="stForm"] button');

originalButton.addEventListener('click', () => {
  console.log('Button clicked with text:');
});

originalTextArea.addEventListener('keyup', () => {
    clearTimeout(window.debounceTimeout);
    window.debounceTimeout = setTimeout(() => {
        if (originalTextArea.value !== previousValue) {
            console.log("Chat input text changed");

            const nativeInputValueSetter =
                Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
            nativeInputValueSetter.call(formInput, originalTextArea.value);
            const event = new Event('input', { bubbles: true });
            formInput.dispatchEvent(event);

            previousValue = originalTextArea.value;

            setTimeout(() => {
                formButton.click();
            }, 100);
        }
    }, 300);
});

console.log("Chat input handler is active");
</script>
    """
    html(js, 0, 0, False)
