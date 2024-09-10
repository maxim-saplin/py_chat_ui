import streamlit as st
from streamlit.components.v1 import html


def global_ui_tweaks():
    st.write(
        """
    <style>
        header[data-testid="stHeader"] {
            visibility: hidden;
        }
    </style>
    """,
        unsafe_allow_html=True,
    )


def register_button_as_link():
    st.write(
        """
    <style>
        div.row-widget button[kind="secondary"] {
            text-decoration: underline;
            cursor: pointer;
            border: none;
            background-color: transparent;
        }
    </style>
    """,
        unsafe_allow_html=True,
    )


def sidebar_about_link():
    st.write(
        """
    <style>
        div[data-testid="stSidebarUserContent"] div.element-container:last-child  {
            position: fixed;
            top: 13px;
            opacity: 0.5;
            backdrop-filter: blur(15px);
            -webkit-backdrop-filter: blur(15px);
            width: 200px !important;
        }
    </style>
    """,
        unsafe_allow_html=True,
    )


def login_background():
    st.write(
        """
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
    """,
        unsafe_allow_html=True,
    )


def right_align_message_delete_button():
    st.write(
        """
    <style>
        div[data-testid="stChatMessageContent"] div:has(> .stButton) {
            position: absolute;
            left: -100px;
            top: -15px;
            width: 0px !important;
        }
        div[data-testid="stChatMessageContent"] div.stButton button {
            border: none;
            opacity: 0.2;
            background: rgba(127, 127, 127, 0.0);
            padding: 0;
            border: 0;
        }
        div[data-testid="stChatMessageContent"] div.stButton button:hover {
            opacity: 1.0;
            background: rgba(127, 127, 127, 0.03);
        }
        div[data-testid="stChatMessageContent"] div.stButton button p {
            font-size: 36px;
        }

    </style>
    """,
        unsafe_allow_html=True,
    )


# flake8: noqa: e501
def right_align_2nd_col_tokenizer():
    st.write(
        """
    <style>
        div[data-testid="column"]:nth-of-type(2)>div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stMarkdown"]>div[data-testid="stMarkdownContainer"]>p {
            font-family: monospace;
            font-size: 13px;
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
    """,
        unsafe_allow_html=True,
    )


def hide_streamlit_toolbar():
    """
    Running man at the top right corner when a request is executed
    """
    st.write(
        """
    <style>
        div[data-testid="stToolbar"] {
            display: none;
        }
    </style>
    """,
        unsafe_allow_html=True,
    )


def add_theme_customizations():
    """
    Adjusting those styles that were not possible to be changed in config.toml
    """
    st.write(
        """

    <style>
        div.stChatMessage p{
            font-family: sans-serif;
        }
    </style>
    """,
        unsafe_allow_html=True,
    )


def hide_streamlit_menu():
    """
    Deply, Three Dots button, as well as Made with Streamlit at the bottom
    """
    st.write(
        """
    <style>
        .reportview-container {
            margin-top: -2em;
        }
        #MainMenu {visibility: hidden;}
        .stDeployButton {display:none;}
        footer {visibility: hidden;}
        #stDecoration {display:none;}
    </style>
""",
        unsafe_allow_html=True,
    )


def hide_tokenzer_workaround_form():
    st.write(
        """
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
""",
        unsafe_allow_html=True,
    )


def new_chat_collapse_markdown_hidden_elements():
    st.write(
        """
        <style>
            section[tabindex="0"]>div>div>div>div[data-testid="stVerticalBlock"] {
                margin-top: -150px;
                margin-bottom: -80px;
            }
        </style>
    """,
        unsafe_allow_html=True,
    )


def new_chat_calculate_tokens():
    embed_chat_tokenizer_js(
        'section[tabindex="0"] textarea[aria-label="Prompt"]',
        'section[tabindex="0"] textarea[aria-label="tokenizer"]',
        1500,
    )


def settings_collapse_markdown_hidden_elements():
    st.write(
        """
        <style>
            section[tabindex="0"]>div>div>div>div[data-testid="stVerticalBlock"] {
                margin-top: -80px;
                margin-bottom: -100px;
            }
        </style>
    """,
        unsafe_allow_html=True,
    )


def chat_collapse_markdown_hidden_elements():
    st.write(
        """
        <style>
            section[tabindex="0"]>div>div>div>div[data-testid="stVerticalBlock"] {
                margin-top: -100px;
                margin-bottom: -80px;
            }
        </style>
    """,
        unsafe_allow_html=True,
    )


def chat_bottom_padding():
    st.write(
        """
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
    """,
        unsafe_allow_html=True,
    )


def cancel_generation_button_styles():
    """
    And hide generation button
    """
    st.write(
        """
        <style>
            div[data-testid="stVerticalBlock"]>div[data-testid="stVerticalBlockBorderWrapper"]>div>div>div>div.row-widget.stButton {
                text-align: center;
                position: fixed;
                bottom: 31px;
                visibility: hidden;
                z-index: 999;
                background-color: transparent;
            }
        </style>
    """,
        unsafe_allow_html=True,
    )


stop_button_selector = 'div[data-testid="stVerticalBlock"]>div[data-testid="stVerticalBlockBorderWrapper"] div.row-widget.stButton'


def show_cancel_generate_button_js():
    """
    And hide chat input
    """
    js = f"""
<script>
console.log("show_generate_button_js");
const stopButton = window.parent.document.querySelector('{stop_button_selector}');
stopButton.style.visibility = 'visible';
const chatInputContainer = window.parent.document.querySelector('div.stChatInput');
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
const chatInputContainer = window.parent.document.querySelector('div.stChatInput');
if (chatInputContainer) chatInputContainer.style.visibility = 'visible';
</script>
    """
    html(js, 0, 0, False)


def set_chat_input_text(promptText: str):
    escaped_prompt_text = promptText.replace("`", "\\`").replace("\n", "\\n")
    # !!! Since react controls state, simle DOM values setting won't work, goind the hard way of simulating user interaction
    js = f"""
<script>
const chatInput = window.parent.document.querySelector('.stChatInput textarea');
const nativeTextAreaValueSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, "value").set;
nativeTextAreaValueSetter.call(chatInput, `{escaped_prompt_text}`);
const event = new Event('input', {{ bubbles: true }});
chatInput.dispatchEvent(event);
</script>
    """
    html(js, 0, 0, False)


def embed_chat_input_tokenizer():
    embed_chat_tokenizer_js(
        'textarea[placeholder="What is up?"]',
        'section[tabindex="0"] textarea[aria-label="tokenizer2"]',
        1500,
        stop_button_selector,
        ".stChatInput button",
    )


def embed_chat_tokenizer_js(
    srcSelector: str,
    dstSelector: str,
    debounceTimeout: int = 800,
    cancelSelector: str = "",
    submitButtonSelector: str = "",
):
    """
    cancelSelector - if present in DOM, no action will take place
    submitButtonSelector - when pressed, no action will take place after (if timer hits)
    """
    js = (
        """
<script>
setTimeout(() => {
    let previousValue = '';
    const originalTextArea = window.parent.document.querySelector('"""
        + srcSelector
        + """');
    const formTextArea = window.parent.document.querySelector('"""
        + dstSelector
        + """');
    buttonSelector = '"""
        + submitButtonSelector
        + """';
    const button = buttonSelector ? window.parent.document.querySelector(buttonSelector) : null;

    if (button) {
        button.addEventListener('click', () => {
            console.log('CLEAR')
            clearTimeout(window.debounceTimeout);
        });
    }

    if (originalTextArea && formTextArea) {
        originalTextArea.addEventListener('keydown', (event) => {
            clearTimeout(window.debounceTimeout);
            if (event.keyCode == 13) return;
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
                        selector = '"""
        + cancelSelector
        + """';
                        const cancelElement = selector ? window.parent.document.querySelector(selector) : null;
                        let computedStyle = null;
                        if (cancelElement) {
                            computedStyle = window.parent.window.getComputedStyle(cancelElement);
                        }
                        if (!computedStyle || computedStyle.display === 'none' || computedStyle.visibility === 'hidden') {
                            const newEvent = new KeyboardEvent('keydown', {
                                key: 'Enter',
                                keyCode: 13, // Enter key's keyCode is 13
                                metaKey: true, // metaKey is true if Cmd is pressed (on Mac)
                                ctrlKey: true, // Use true if you want to simulate Ctrl+Enter on non-Mac systems
                                altKey: false,
                                shiftKey: false,
                                bubbles: true
                            });

                            formTextArea.dispatchEvent(newEvent);
                        }

                    }, 100);
                }
            },"""
        + str(debounceTimeout)
        + """);
        });
        console.log("Prompt input handler is active");
    }
    else {
        console.log("Prompt input not active, chat input not found");
    }
}, 150);
</script>
"""
    )
    html(js, 0, 0, False)


def new_chat_add_command_enter_handler():
    js = """
<script>
document.addEventListener('DOMContentLoaded', () => {
    const promptTextArea = window.parent.document.querySelector('textarea[aria-label="Prompt"]');


    if (promptTextArea) {
        promptTextArea.addEventListener('keydown', (event) => {
            if ((event.metaKey || event.ctrlKey) && event.key === 'Enter') {
                setTimeout(() => {
                    const primaryButton = window.parent.document.querySelector
                        ('button[kind="primary"][data-testid="baseButton-primary"]');
                    primaryButton.dispatchEvent(new MouseEvent('click', { bubbles: true }));
                    console.log(primaryButton)
                    console.log("Cmd/Ctrl + Enter pressed, button clicked");
                }, 500); // Adjust the timeout as necessary
            }
        });
    } else {
        console.log("Textarea or button not found");
    }
});
</script>
"""
    html(js, 0, 0, False)
