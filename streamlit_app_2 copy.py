import openai
import streamlit as st
import streamlit_chat

openai.api_key = st.secrets["OPENAI_API_KEY"]

def move_focus():
    # inspect the HTML to determine which control to specify to receive focus (e.g. text or textarea).
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

def userid_change():
    st.session_state.userid = st.session_state.userid_input

def complete_messages():
    response_content = "basic response"
    return response_content

def main():
    # set model as session state
    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-3.5-turbo"

    # create message variable as session state
    if "messages" not in st.session_state:
        st.session_state.messages = []

    with st.container():
        st.title("Streamlit ChatGPT Bot")
        stick_it_good()

    # create sidebar for intro text and the option to clear chat history
    st.sidebar.write('Some sort of text')
    if st.sidebar.button("Clear Conversation", key='clear_chat_button'):
        # Move "The first prompt" to the top of the chat messages
        st.session_state.messages.insert(0, {"role": "assistant", "content": "The first prompt", "key": 'intro_message_1'})
        move_focus()

    # Loop through the existing messages to display them
    for i, message in enumerate(st.session_state.messages):
        nkey = int(i / 2)
        if message["role"] == "user":
            streamlit_chat.message(message["content"], is_user=True, key=f'chat_messages_user_{nkey}')
        else:
            streamlit_chat.message(message["content"], is_user=False, key=f'chat_messages_assistant_{nkey}')

    if user_content := st.chat_input("Type your question here."):  # using streamlit's st.chat_input because it stays put at the bottom, chat.openai.com style.
        nkey = int(len(st.session_state.messages) / 2)
        streamlit_chat.message(user_content, is_user=True, key=f'chat_messages_user_{nkey}')
        st.session_state.messages.append({"role": "user", "content": user_content})
        assistant_content = complete_messages()
        streamlit_chat.message(assistant_content, key=f'chat_messages_assistant_{nkey}')
        st.session_state.messages.append({"role": "assistant", "content": assistant_content})
        # len(st.session_state.messages)

if __name__ == '__main__':
    main()
