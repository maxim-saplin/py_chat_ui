import streamlit as st

def right_align_2nd_col():
    st.markdown(
    """
    <style>
        div[data-testid="column"]:nth-of-type(2)
        {
            text-align: end;
            position: fixed;
            z-index: 999;
            top: 40px;
            right: 50px;
            background: linear-gradient(to right, rgba(255, 255, 255, 0) 0%, rgba(255, 255, 255, 0.8) 100%);
        } 
    </style>
    """,unsafe_allow_html=True
)

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

