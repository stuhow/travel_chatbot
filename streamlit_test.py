import openai
import streamlit as st
from travel_chatbot.tools import get_tools
from travel_chatbot.basemodels import TravelDetails
from travel_chatbot.stream_agents import bq_stream_francis
from travel_chatbot.utils import conversation_history

st.title("ChatGPT-like clone")

openai.api_key = st.secrets["OPENAI_API_KEY"]

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if "messages" not in st.session_state:
    st.session_state.messages = []

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


st.session_state.messages.append({"role": "assistant", "content": "Hello, this is Francis your personal travel chat bot. How can i help you today?"})

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    conversation = conversation_history(st.session_state.messages)

    with st.chat_message("assistant"):

        agent, user_details = bq_stream_francis(prompt,
                                                        conversation,
                                                        st.session_state["user_travel_details"],
                                                        st.session_state.list_of_interests,
                                                        st.session_state.interest_asked,
                                                        st.session_state["tools"],
                                                        st.session_state.asked_for,
                                                        st.session_state.solution_presented)


        message_placeholder = st.empty()
        full_response = ""
        for response in agent.run(prompt):
            full_response += response.choices[0].delta.get("content", "")
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})
