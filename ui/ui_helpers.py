import streamlit as st
from streamlit.components.v1 import html

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

def right_align_2nd_col():
    st.markdown(
    """
    <style>
        div[data-testid="column"]:nth-of-type(2) p
        {
            font-family: monospace;
            text-align: end;
            position: fixed;
            z-index: 999;
            top: 40px;
            right: 50px;
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
        } 
    </style>
    """,unsafe_allow_html=True)

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

    
def embed_chat_input_handler_js():
    js = """
<script>
console.log("Chat input handler is activating...");

let previousValue = '';

setInterval(() => {
  const originalTextArea = window.parent.document.querySelector('.stChatInputContainer textarea');
  const formInput = window.parent.document.querySelector('div[data-testid="stForm"] input');
  const formButton = window.parent.document.querySelector('div[data-testid="stForm"] button');
  if (originalTextArea && formInput && formButton) {
    if (originalTextArea.value !== previousValue) {
      console.log("Chat input text changed");
      
      const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
      nativeInputValueSetter.call(formInput, originalTextArea.value);
      const event = new Event('input', { bubbles: true });
      formInput.dispatchEvent(event);
      
      previousValue = originalTextArea.value;

      setTimeout(() => {
          formButton.click();
      }, 100);
    }
  } else {
    console.log("Textarea or button not found");
  }
}, 1000);

console.log("Chat input handler is active");
</script>
    """
    html(js, 0, 0, False)
    #st.markdown(js,unsafe_allow_html=True)