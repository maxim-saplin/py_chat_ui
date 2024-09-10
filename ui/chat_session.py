import time
import streamlit as st
import logic.user_state as state
import logic.utility as util
from logic.utility import get_tokenizer
from logic import env_vars
from ui.ui_helpers import (
    chat_collapse_markdown_hidden_elements,
    right_align_2nd_col_tokenizer,
    show_cancel_generate_button_js,
    set_chat_input_text,
    embed_chat_input_tokenizer,
    hide_tokenzer_workaround_form,
    show_stop_generate_chat_input_js,
    cancel_generation_button_styles,
    right_align_message_delete_button,
)


@st.dialog("Confirm deletion")
def confirm_delete(message_index):
    st.write(
        "Are you sure you want to delete this message and all subsequent messages?"
    )
    col1, col2, _ = st.columns([1, 1, 3])
    with col1:
        if st.button("Yes"):
            st.session_state["delete_confirmed"] = message_index
            st.rerun()
    with col2:
        if st.button("No"):
            st.session_state["delete_confirmed"] = None
            st.rerun()


def show_chat_session(chat_session: state.ChatSession):
    init_session_state(chat_session)

    hide_tokenzer_workaround_form()
    chat_collapse_markdown_hidden_elements()
    cancel_generation_button_styles()
    right_align_2nd_col_tokenizer()
    right_align_message_delete_button()

    # Chat header
    col1, col2 = st.columns(2)

    try:
        if chat_session is not None:
            for i, message in enumerate(chat_session.messages):
                with st.chat_message(
                    message["role"],
                    avatar=(
                        "ui/ai.png"
                        if message["role"] == "assistant"
                        else ("ui/user.png" if message["role"] == "user" else None)
                    ),
                ):
                    st.markdown(message["content"])
                    if message["role"] == "user":
                        if st.button("␡", key=f"delete_{i}"):
                            confirm_delete(i)

        # Handle deletion if confirmed
        if st.session_state["delete_confirmed"]:
            index_to_delete = st.session_state.delete_confirmed
            deleted_message = chat_session.messages[index_to_delete]["content"]
            while len(chat_session.messages) > index_to_delete:
                chat_session.delete_last_message()
            if deleted_message:
                st.session_state["canceled_prompt"] = deleted_message
            st.session_state["delete_confirmed"] = None
            st.rerun()

        with st.container():
            if st.button("Cancel generation"):
                st.session_state["generating"] = False
                st.session_state["get_and_display_ai_reply_BREAK"] = True
                try:
                    st.session_state["canceled_prompt"] = chat_session.messages[-1][
                        "content"
                    ]
                except Exception as e:
                    print(f"Error saving canceled prompt: {e}")
                chat_session.delete_last_user_message()
                st.rerun()

        # Recovery from inconsistent state
        if (
            st.session_state["generating"]
            and chat_session.messages
            and chat_session.messages[-1]["role"] == "user"
        ):
            st.session_state["generating"] = False
        #     st.session_state['get_and_display_ai_reply_BREAK'] = True

        if not st.session_state["generating"]:
            # Tried doing nicely server-sde (setting sttuds to generating after promnpt, show stop button etc.)
            # Yet it seems the st.chat_input() does way more behind the scenese, when OpenAI ran streaming response
            # thre were some silen failures under the hood of streamlit and not chat generation worked, reliably
            # Deffering to js tricks and toggling control's visibility

            prompt = None
            user_message_last = False
            # User prompt came in from New Chat
            if chat_session.messages and chat_session.messages[-1]["role"] == "user":
                prompt = chat_session.messages[-1]["content"]
                user_message_last = True
            else:
                prompt = st.chat_input(
                    "What is up?", disabled=st.session_state["generating"]
                )

            if prompt is not None:
                st.session_state["token_count"] = None
                st.session_state["prompt_for_tokenizer"] = None
                st.session_state["generating"] = True
                if not user_message_last:
                    chat_session.add_message({"role": "user", "content": prompt})
                    with st.chat_message("assistant", avatar="ui/user.png"):
                        st.markdown(prompt)
                show_cancel_generate_button_js()
                with st.chat_message("assistant", avatar="ui/ai.png"):
                    message_placeholder = st.empty()
                    st.session_state["get_and_display_ai_reply_BREAK"] = False
                    get_and_display_ai_reply(
                        util.create_client(chat_session.model),
                        chat_session.model,
                        chat_session,
                        message_placeholder,
                    )
                    st.session_state["generating"] = False
                    st.rerun()

            st.session_state["generating"] = False

    except Exception as e:
        st.session_state["generating"] = False
        st.session_state["get_and_display_ai_reply_BREAK"] = False
        with st.container():
            st.write("An error occurred while sending Chat API request")
            st.write(e)

    if not st.session_state["generating"]:
        with col2:
            with st.form("hidden"):
                txt = st.text_area("tokenizer2").strip()
                st.form_submit_button("Submit")
                if txt != st.session_state["prompt_for_tokenizer"] and not (
                    txt == "" and st.session_state["prompt_for_tokenizer"] is None
                ):
                    st.session_state["prompt_for_tokenizer"] = (
                        None if txt == "" else txt
                    )
                    # st.rerun()
            embed_chat_input_tokenizer()

    show_stop_generate_chat_input_js()
    # Cancelation happened, fill in chat input with past prompt
    if st.session_state["canceled_prompt"] not in (None, ""):
        set_chat_input_text(st.session_state["canceled_prompt"])
        st.session_state["canceled_prompt"] = None
    elif st.session_state["prompt_for_tokenizer"]:
        set_chat_input_text(st.session_state["prompt_for_tokenizer"])
        st.session_state["prompt_for_tokenizer"] = None

    with col1:
        if st.button("Delete Chat"):
            state.session_manager.delete(chat_session.session_id)
            st.session_state["get_and_display_ai_reply_BREAK"] = True
            st.session_state["generating"] = False
            st.rerun()

    # Stats, top right corners
    with col2:
        display_stats(chat_session)


def display_stats(chat_session):
    if chat_session is not None:
        model_alias = chat_session.model.alias if chat_session.model else "No Model"
        tokenizer = get_tokenizer(
            env_vars.TokenizerKind(chat_session.model.tokenizer_kind)
        )
        stats = ""
        if st.session_state["token_count"] is None:
            st.session_state["token_count"] = util.num_tokens_from_messages(
                chat_session.messages, tokenizer
            )
        if (
            "prompt_for_tokenizer" in st.session_state
            and st.session_state["prompt_for_tokenizer"]
        ):
            prompt_tokens = util.num_tokens_from_messages(
                [
                    {
                        "role": "User",
                        "content": st.session_state["prompt_for_tokenizer"],
                    }
                ],
                tokenizer,
            )
        else:
            prompt_tokens = 0
        if prompt_tokens > 0:
            stats += f"{model_alias} / {st.session_state['token_count']} tokens +{prompt_tokens}"
        else:
            stats += f"{model_alias} / {st.session_state['token_count']} tokens"

            # Performance metrics
        if st.session_state["time_to_first_chunk"] and st.session_state["total_time"]:
            # Network time is included, first chunk tokens generation time is also included
            time_to_first_chunk = st.session_state["time_to_first_chunk"]
            total_time = st.session_state["total_time"]
            tokens_last_message = util.num_tokens_from_messages(
                [st.session_state.get("last_message")], tokenizer
            )
            # First chunk is not a full message
            tokens_first_chunk = (
                util.num_tokens_from_messages(
                    [st.session_state.get("first_chunk")], tokenizer
                )
                - 4
            )
            token_count = tokens_last_message - tokens_first_chunk
            tokens_per_second = (
                (token_count / total_time if total_time > 0 else float("inf"))
                if token_count is not None
                else None
            )

            stats += (
                f"  \nTTF Chunk: {time_to_first_chunk:.2f}s / "
                if time_to_first_chunk
                else "TTF Chunk: N/A /"
            )
            stats += f"TPS: {tokens_per_second:.2f}" if total_time else "TPS: N/A"

        st.write(stats)


def init_session_state(chat_session):
    session_state_defaults = {
        "generating": False,
        "token_count": None,
        "prompt_for_tokenizer": None,
        "canceled_prompt": None,
        "get_and_display_ai_reply_BREAK": False,
        "prev_chat_session": None,
        "time_to_first_chunk": None,
        "last_message": None,
        "first_chunk": None,
        "total_time": None,
        "delete_confirmed": None,
    }

    for key, default_value in session_state_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

    # if a new chat session is open - reset state
    if (
        not st.session_state["prev_chat_session"]
        or chat_session.file_path != st.session_state["prev_chat_session"].file_path
    ):
        st.session_state["token_count"] = None
        st.session_state["time_to_first_chunk"] = None
        st.session_state["last_message"] = None
        st.session_state["first_chunk"] = None
        st.session_state["total_time"] = None
        st.session_state["prev_chat_session"] = chat_session


def get_and_display_ai_reply(
    client, model: state.Model, chat_session: state.ChatSession, message_placeholder
) -> None:
    if st.session_state["get_and_display_ai_reply_BREAK"]:
        return
    print("get_and_display_ai_reply")
    try:
        full_response = ""
        message_placeholder.markdown("...")

        start_time = time.time()
        first_chunk_time = None
        first_chunk = None

        for response in client.chat.completions.create(
            model=model.model_or_deployment_name,
            temperature=model.temperature,
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in chat_session.messages
            ],
            stream=True,
            # stream_options={"include_usage": True},
            # Doesn't work for Azure https://github.com/Azure/azure-sdk-for-net/issues/44237
        ):
            if response.choices:
                if st.session_state["get_and_display_ai_reply_BREAK"]:
                    print("get_and_display_ai_reply - breaking")
                    break
                first_choice = response.choices[0]
                if (
                    hasattr(first_choice, "delta")
                    and first_choice.delta
                    and first_choice.delta.content
                ):
                    if first_chunk_time is None:
                        first_chunk_time = time.time()
                        first_chunk = first_choice.delta.content
                    full_response += first_choice.delta.content
                elif hasattr(first_choice, "content") and first_choice.content:
                    full_response = first_choice.content
            # if response.usage:
            #     token_count = response.usage.completion_tokens
            message_placeholder.markdown(full_response + "▌")
        end_time = time.time()

        message_placeholder.markdown(full_response)
        message = {"role": "assistant", "content": full_response}
        if not st.session_state["get_and_display_ai_reply_BREAK"]:
            chat_session.add_message(message)
        print("get_and_display_ai_reply - completing")

        time_to_first_chunk = (
            first_chunk_time - start_time if first_chunk_time else None
        )
        total_time = end_time - first_chunk_time if first_chunk_time else None

        st.session_state["time_to_first_chunk"] = time_to_first_chunk
        st.session_state["last_message"] = message
        st.session_state["first_chunk"] = {"role": "assistant", "content": first_chunk}
        st.session_state["total_time"] = total_time

    finally:
        st.session_state["get_and_display_ai_reply_BREAK"] = False
