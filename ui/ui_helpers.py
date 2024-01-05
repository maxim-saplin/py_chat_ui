import streamlit as st
from streamlit.components.v1 import html


def global_ui_tweaks():
    st.write("""
    <style>
        header[data-testid="stHeader"] {
            visibility: hidden;
        }
    </style>
    """, unsafe_allow_html=True)


def register_button_as_link():
    st.write("""
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
    st.write("""
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
    st.write("""
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
    st.write("""
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
    st.write("""
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
    st.write("""

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
    st.write("""
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


def hide_tokenzer_workaround_form():
    st.write("""
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


def new_chat_collapse_markdown_hidden_elements():
    st.write("""
        <style>
            section[tabindex="0"]>div>div>div>div[data-testid="stVerticalBlock"] {
                margin-top: -150px;
                margin-bottom: -80px;
            }
        </style>
    """, unsafe_allow_html=True)


def new_chat_calculate_tokens():
    embed_chat_tokenizer_js('section[tabindex="0"] textarea[aria-label="Prompt"]',
                            'section[tabindex="0"] textarea[aria-label="tokenizer"]',
                            300)


def settings_collapse_markdown_hidden_elements():
    st.write("""
        <style>
            section[tabindex="0"]>div>div>div>div[data-testid="stVerticalBlock"] {
                margin-top: -80px;
                margin-bottom: -100px;
            }
        </style>
    """, unsafe_allow_html=True)


def chat_collapse_markdown_hidden_elements():
    st.write("""
        <style>
            section[tabindex="0"]>div>div>div>div[data-testid="stVerticalBlock"] {
                margin-top: -100px;
                margin-bottom: -80px;
            }
        </style>
    """, unsafe_allow_html=True)


def chat_bottom_padding():
    st.write("""
        <style>
            div.stChatFloatingInputContainer {
                padding-bottom: 30px;
            }
            section[tabindex="0"] > div > div > div > div[data-testid="stVerticalBlock"] > div[data-testid="element-container"] {
                height: 0;
                # display: none;
                # border: none;
                # padding: none;
            }
        </style>
    """, unsafe_allow_html=True)


def cancel_generation_button_styles():
    """
    And hide generation button
    """
    st.write("""
        <style>
            div[data-testid="stVerticalBlock"]>div[data-testid="stVerticalBlockBorderWrapper"] div.row-widget.stButton {
                text-align: center;
                position: fixed;
                bottom: 31px;
                visibility: hidden;
                z-index: 999;
                background-color: transparent;
            }
        </style>
    """, unsafe_allow_html=True)


stop_button_selector =\
    'div[data-testid="stVerticalBlock"]>div[data-testid="stVerticalBlockBorderWrapper"] div.row-widget.stButton'


def show_cancel_generate_button_js():
    """
    And hide chat input
    """
    js = f"""
<script>
console.log("show_generate_button_js");
const stopButton = window.parent.document.querySelector('{stop_button_selector}');
stopButton.style.visibility = 'visible';
const chatInputContainer = window.parent.document.querySelector('div.stChatInputContainer');
chatInputContainer.style.visibility = 'hidden';
</script>
    """
    html(js, 0, 0, False)


def show_stop_generate_chat_input_js():
    js = f"""
<script>
console.log("show_generate_chat_input_js");
const stopButton = window.parent.document.querySelector('{stop_button_selector}');
if (stopButton) stopButton.style.visibility = 'hidden';
const chatInputContainer = window.parent.document.querySelector('div.stChatInputContainer');
if (chatInputContainer) chatInputContainer.style.visibility = 'visible';
</script>
    """
    html(js, 0, 0, False)


def set_chat_input_text(promptText: str):
    escaped_prompt_text = promptText.replace('`', '\\`').replace('\n', '\\n')
# !!! Since react controls state, simle DOM values setting won't work, goind the hard way of simulating user interaction
    js = f"""
<script>
const chatInput = window.parent.document.querySelector('.stChatInputContainer textarea');
const nativeTextAreaValueSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, "value").set;
nativeTextAreaValueSetter.call(chatInput, `{escaped_prompt_text}`);
const event = new Event('input', {{ bubbles: true }});
chatInput.dispatchEvent(event);
</script>
    """
    html(js, 0, 0, False)


def embed_chat_input_tokenizer():
    embed_chat_tokenizer_js('.stChatInputContainer textarea',
                            'section[tabindex="0"] textarea[aria-label="tokenizer2"]', 300, stop_button_selector)


def embed_chat_tokenizer_js(srcSelector: str, dstSelector: str, debounceTimeout: int = 800, cancelSelector: str = ""):
    """
    cancelSelector - if present in DOM, no action will take place
    """
    js = """
<script>
setTimeout(() => {
    let previousValue = '';
    const originalTextArea = window.parent.document.querySelector('""" + srcSelector + """');
    const formTextArea = window.parent.document.querySelector('""" + dstSelector + """');

    if (originalTextArea && formTextArea) {
        originalTextArea.addEventListener('input', (event) => {
            clearTimeout(window.debounceTimeout);
            window.debounceTimeout = setTimeout(() => {
                if (originalTextArea.value !== previousValue) {
                    console.log("Prompt input text changed");

                    const nativeInputValueSetter =
                        Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, "value").set;
                    nativeInputValueSetter.call(formTextArea, originalTextArea.value);
                    const event = new Event('input', { bubbles: true });
                    formTextArea.dispatchEvent(event);

                    previousValue = formTextArea.value;

                    setTimeout(() => {
                        selector = '""" + cancelSelector + """';
                        const cancelElement = selector ? window.parent.document.querySelector(selector) : null;
                        let computedStyle = null;
                        if (cancelElement) {
                            computedStyle = window.parent.window.getComputedStyle(cancelElement);
                        }
                        if (!computedStyle || computedStyle.display === 'none' || computedStyle.visibility === 'hidden') {
                            let event = new KeyboardEvent('keydown', {
                                key: 'Enter',
                                keyCode: 13, // Enter key's keyCode is 13
                                metaKey: true, // metaKey is true if Cmd is pressed (on Mac)
                                ctrlKey: false, // Use true if you want to simulate Ctrl+Enter on non-Mac systems
                                altKey: false,
                                shiftKey: false,
                                bubbles: true
                            });

                            formTextArea.dispatchEvent(event);
                        }

                    }, 100);
                }
            },""" + str(debounceTimeout) + """);
        });
        console.log("Prompt input handler is active");
    }
    else {
        console.log("Prompt input not active, chat input not found");
    }
}, 150);
</script>
"""
    html(js, 0, 0, False)
