from sqlalchemy import table
import streamlit as st
from streamlit_chat import message
import json
from typing import List
from pathlib import Path

DB_FILE = "db.json"


class User:
    def __init__(self, username, password, user_type, instructor=None, assignments=None):
        self.username = username
        self.password = password
        self.user_type = user_type
        self.instructor = instructor
        self.assignments = assignments if assignments else []

    def to_dict(self):
        return {
            "username": self.username,
            "password": self.password,
            "user_type": self.user_type,
            "instructor": self.instructor,
            "assignments": self.assignments,
        }


def load_users() -> List[User]:
    if Path(DB_FILE).is_file():
        with open(DB_FILE, "r") as f:
            users_data = json.load(f)
        return [User(**user_data) for user_data in users_data]
    else:
        return []


def save_users(users: List[User]):
    users_data = [user.to_dict() for user in users]
    with open(DB_FILE, "w") as f:
        json.dump(users_data, f)




# Define a function to create tabs
def create_tabs(count):
    # Define the tabs as dictionary keys
    tabs = {}
    for i in range (count):
        tabs['Tab '+str(i)] = i

    # Define the tab labels as a list
    tab_labels = list(tabs.keys())

    # Use the `session_state` to store the current tab index
    if 'tab_index' not in st.session_state:
        st.session_state.tab_index = 0

    # Create a selectbox to switch between tabs
    st.sidebar.write('Switch Tab:')
    selected_tab = st.sidebar.selectbox('', tab_labels, index=st.session_state.tab_index)

    # Get the index of the selected tab
    st.session_state.tab_index = tabs[selected_tab]

    # Return the selected tab index
    return st.session_state.tab_index


st.set_page_config(
    page_title="DocuBOT QuizMode",
    page_icon=":robot:"
)

st.header("DocuBOT QuizMode")

users = load_users()
if 'generated' not in st.session_state:
            st.session_state['generated'] = []

if 'past' not in st.session_state:
    st.session_state['past'] = []

if 'current_question' not in st.session_state:
    st.session_state['current_question'] = 0



if "tab_index" not in st.session_state:  
    st.session_state['tab_index'] = 0
if "username" in st.session_state:
    user = [u for u in users if u.username == st.session_state['username']][0]
    if user.user_type == "learner":
        questions = user.assignments
        
        if st.session_state['tab_index'] < len(questions):
            st.write(questions[st.session_state['tab_index']]['question'])
        

            with st.form(key="input_form"):
                user_input = ""
                user_input = st.text_input("You: ", value=user_input, key="input")
                submit_button = st.form_submit_button(label="Submit")
            if  submit_button and user_input:
                st.session_state['past'].append(user_input)
                st.session_state['current_question'] += 1
                st.session_state['tab_index'] += 1
                st.experimental_rerun()

            st.sidebar.header("Quiz History")
            for i, question in enumerate(questions):
                if i < st.session_state['current_question']:
                    st.sidebar.write("Bot: "+question['question'])
                    st.sidebar.write("You: " + st.session_state['past'][i])


        else:
            responses = []
            for i, question in enumerate(questions):
                response = {
                    "question": question['question'],
                    "response": st.session_state['past'][i]
                }
                responses.append(response)

            user.assignments = responses
            save_users(users)

            message("Thank you for answering all the questions. Your responses have been saved.", is_user=False)
            st.sidebar.write("Thank you for answering all the questions. Your responses have been saved.")

            st.sidebar.download_button(
                label="Download Responses",
                data=json.dumps(responses),
                file_name="responses.json",
                mime="application/json"
            )

    if st.session_state['generated']:
        for i in range(len(st.session_state['generated'])+1, 1, 1):
            message(st.session_state["generated"][i], key=str(i))
            message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
            st.sidebar.write("Bot: ", st.session_state["generated"][i])
else:
    st.info("Please Login or Register")