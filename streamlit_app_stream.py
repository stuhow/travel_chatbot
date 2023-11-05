import openai
import streamlit as st
import streamlit_chat
import time

from travel_chatbot.stream_agents import run_francis, bq_run_francis, bq_stream_francis
from travel_chatbot.tools import get_tools
from travel_chatbot.basemodels import TravelDetails
from travel_chatbot.utils import conversation_history
from langchain.callbacks import StreamlitCallbackHandler
import streamlit as st



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
        # nkey = int(len(st.session_state.messages)/2)
        # opening_content = "Hello, this is Francis your personal travel chat bot. How can i help you today?"
        # streamlit_chat.message(opening_content,key='chat_messages_user_'+str(nkey))
        # st.session_state.messages.append({"role": "assistant", "content": opening_content})
        st.session_state.messages.append({"role": "assistant", "content": "Hello, this is Francis your personal travel chat bot. How can i help you today?"})

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


    # ongoing conversation
    if user_content := st.chat_input("Type your question here."): # using streamlit's st.chat_input because it stays put at bottom, chat.openai.com style.
            nkey = int(len(st.session_state.messages)/2) + 1
            # streamlit_chat.message(user_content, is_user=True, key='chat_messages_user_'+str(nkey))
            # st.session_state.messages.append({"role": "user", "content": user_content})
            # st.session_state.messages.append({"role": "assistant", "content": user_content})
            st.session_state.messages.append({"role": "user", "content": user_content})
            with st.chat_message("user"):
                st.markdown(user_content)
            # assistant_content = complete_messages(0,1)
            conversation = conversation_history(st.session_state.messages)
            # with st.spinner(f"Thinking... (If I'm thinking for a while it's usually because I'm about to present you with itinerary options)"):
            agent, user_details = bq_stream_francis(user_content,
                                                    conversation,
                                                    st.session_state["user_travel_details"],
                                                    st.session_state.list_of_interests,
                                                    st.session_state.interest_asked,
                                                    st.session_state["tools"],
                                                    st.session_state.asked_for,
                                                    st.session_state.solution_presented)

            st_callback = StreamlitCallbackHandler(st.container())
            #     assistant_content = agent.run(user_content, callbacks=[st_callback]) #

            # # print(user_details)
            st.session_state["user_travel_details"] = user_details

            # streamlit_chat.message(assistant_content, key='chat_messages_assistant_'+str(nkey))
            # st.session_state.messages.append({"role": "assistant", "content": assistant_content})
            # st.session_state.messages.append({"role": "assistant", "content": assistant_content})

            with st.chat_message("assistant"):
                st_callback = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
                message_placeholder = st.empty()
                full_response = ""
                for response in agent.run(user_content, callbacks=[st_callback]):
                    full_response += response # .choices[0].delta.get("content", "")
                    message_placeholder.markdown(full_response + "▌")
                    message_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})

                # st_callback = StreamlitCallbackHandler(st.container()) # streamlit container for output
                # answer = agent.run(user_content, callbacks=[st_callback])
                # st.session_state.messages.append({"role": "assistant", "content": answer})
                # st.markdown(answer)


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
