import streamlit as st
from streamlit.components.v1 import html

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
            color: red;
            text-shadow: 1px 1px 0px green;
            font-weight: 900;
        } 
    </style>
    """,unsafe_allow_html=True)


def hide_streamlit_menu():
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
    
def hide_form():
    st.markdown("""
    <style>
        div[data-testid="stForm"] {
            opacity: 0;
            position: absolute;
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
    if (originalTextArea.value !== '' && originalTextArea.value !== previousValue) {
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
    html(js)
    #st.markdown(js,unsafe_allow_html=True)