import openai
import streamlit as st
import streamlit_chat
import time

from travel_chatbot.agents import run_francis, bq_run_francis
from travel_chatbot.tools import get_tools
from travel_chatbot.basemodels import TravelDetails
from travel_chatbot.utils import conversation_history

openai.api_key = st.secrets["OPENAI_API_KEY"]

def move_focus():
    # inspect the html to determine which control to specify to receive focus (e.g. text or textarea).
    st.components.v1.html(
        f"""
            <script>
                var textarea = window.parent.document.querySelectorAll("textarea[type=textarea]");
                for (var i = 0; i < textarea.length; ++i) {{
                    textarea[i].focus();
                }}
            </script>
        """,
    )


def stick_it_good():

    # make header sticky.
    st.markdown(
        """
            <div class='fixed-header'/>
            <style>
                div[data-testid="stVerticalBlock"] div:has(div.fixed-header) {
                    position: sticky;
                    top: 2.875rem;
                    background-color: white;
                    z-index: 999;
                }
                .fixed-header {
                    border-bottom: 1px solid black;
                }
            </style>
        """,
        unsafe_allow_html=True
    )


def main():
    # set model as session state
    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-3.5-turbo"

    # set tools as session state - work to be done
    if "tools" not in st.session_state:
        st.session_state["tools"] = get_tools()

    # user_travel_details as session state
    if "user_travel_details" not in st.session_state:
        st.session_state["user_travel_details"] = TravelDetails(introduction=False,
                                                                    qualification="",
                                                                    country="",
                                                                    departing_after=None,
                                                                    departing_before=None,
                                                                    max_budget=None,
                                                                    max_duration=None,
                                                                    min_duration=None,
                                                                    )

    # list_of_interests as session state
    if "list_of_interests" not in st.session_state:
        st.session_state.list_of_interests = []

    # interest_asked as session state
    if "interest_asked" not in st.session_state:
        st.session_state.interest_asked = []

    # solution_presented as session state
    if "solution_presented" not in st.session_state:
        st.session_state.solution_presented = []

    # asked_for as session state
    if "asked_for" not in st.session_state:
        st.session_state.asked_for = []

    # create message variable a session state
    if "messages" not in st.session_state:
        st.session_state.messages = []

    with st.container():
        st.title("Francis: The Travel Agent Bot")
        stick_it_good()


    # first message from francis to iniciate conversation
    if len(st.session_state.messages) == 0:
        st.session_state.messages.append({"role": "assistant", "content": "Hello, this is Francis your personal travel chat bot. How can i help you today?"})

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # ongoing conversation
    if user_content := st.chat_input("Type your question here."): # using streamlit's st.chat_input because it stays put at bottom, chat.openai.com style.
            st.session_state.messages.append({"role": "user", "content": user_content})
            with st.chat_message("user"):
                st.markdown(user_content)

        # Generate a new response if last message is not from assistant
    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                conversation = conversation_history(st.session_state.messages)
                assistant_content, user_details = bq_run_francis(user_content,
                                        conversation,
                                        st.session_state["user_travel_details"],
                                        st.session_state.list_of_interests,
                                        st.session_state.interest_asked,
                                        st.session_state["tools"],
                                        st.session_state.asked_for,
                                        st.session_state.solution_presented)
                st.write(assistant_content)
        message = {"role": "assistant", "content": assistant_content}
        st.session_state.messages.append(message)
        st.session_state["user_travel_details"] = user_details

    # create sidebar for intro text and the open to clear chat history
    st.sidebar.write("Welcome to Francis, your personal travel chat bot.")
    st.sidebar.write("Francis is here to have a conversation with you, understanding your basic travel needs such as your destination and budget. Additionally, he'll inquire about your interests to provide you with tailored group tour recommendations.")
    st.sidebar.write("If you have any issues or want to start again you can clear the conversation with the button below.")

    if st.sidebar.button("Clear Conversation", key='clear_chat_button'):
        st.session_state.messages = []
        st.session_state["user_travel_details"] = TravelDetails(introduction=False,
                                                                    qualification="",
                                                                    country="",
                                                                    departing_after=None,
                                                                    departing_before=None,
                                                                    max_budget=None,
                                                                    max_duration=None,
                                                                    min_duration=None,
                                                                    )
        st.session_state.list_of_interests = []
        st.session_state.interest_asked = []
        st.session_state.asked_for = []
        move_focus()

    st.sidebar.write(st.session_state["user_travel_details"].dict())
    st.sidebar.write(st.session_state.list_of_interests)
    st.sidebar.write(st.session_state.interest_asked)
    st.sidebar.write(st.session_state.asked_for)
    st.sidebar.write(st.session_state.solution_presented)

if __name__ == '__main__':
    main()
