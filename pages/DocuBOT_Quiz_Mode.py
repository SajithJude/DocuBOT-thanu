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

if "username" in st.session_state:
    user = [u for u in users if u.username == st.session_state['username']][0]
    if user.user_type == "learner":
        assignments = user.assignments
        topics = [topic["topic"] for topic in assignments]
        topics.insert(0,"")
        #if "selected_topic" not in st.session_state:
        selected_topic = st.selectbox('Select a topic:', topics)
        st.session_state["selected_topic"] = selected_topic
            #st.experimental_rerun()
        for x in assignments:
            st.write(st.session_state["selected_topic"])
            if st.session_state["selected_topic"] == x['topic']:
                if 'pos' not in st.session_state or st.session_state['pos'] is None:
                    st.session_state['pos'] = assignments.index(x)
                questions = x['responses']
                if st.session_state['current_question'] < len(questions):
                    current_question = questions[st.session_state['current_question']]
                    message(current_question['question'], is_user=False, key=str(st.session_state['current_question']))

                    with st.form(key="input_form"):
                        user_input = st.text_input("You: ", "", key="input")
                        submit_button = st.form_submit_button(label="Submit")
                    
                    if  submit_button and user_input:
                        st.session_state['past'].append(user_input)
                        st.session_state['current_question'] += 1
                        st.experimental_rerun()
                    
                    st.sidebar.header("Conversation History")
                    for i, question in enumerate(questions):
                        if i < st.session_state['current_question']:
                            st.sidebar.write("Bot: "+question['question'])
                            st.sidebar.write("You: " + st.session_state['past'][i])

            
                else:
                    responses = []
                    for i, question in enumerate(questions):
                        response = {
                            "question": question['question'],
                            "answer": st.session_state['past'][i]
                        }
                        responses.append(response)

                    user.assignments[st.session_state['pos']] = {"topic": st.session_state['selected_topic'], "responses":responses}
                    save_users(users)

                    message("Thank you for answering all the questions. Your responses have been saved.", is_user=False, key=str(st.session_state['selected_topic']))
                    st.sidebar.write("Thank you for answering all the questions. Your responses have been saved.")
                    st.session_state['current_question'] = 0
                    st.session_state['selected_topic'] = ""
                    st.session_state['pos'] = None
                    st.session_state['past'] = []
                    st.session_state['generated'] = []
                   
                    #st.stop()
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