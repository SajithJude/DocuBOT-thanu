import streamlit as st 
import openai
import os
import json
import base64
from typing import List
# import streamlit as st
from pathlib import Path
import json

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

def view_responses(users):
    instructor = [u for u in users if u.username == st.session_state['username']][0]
    students = [u for u in users if u.user_type == "learner" and u.instructor == instructor.username]
    student_usernames = [s.username for s in students]

    selected_student = st.selectbox("Select a student to view their responses", student_usernames)
    selected_student_obj = [s for s in students if s.username == selected_student][0]

    topics = list(set([a["topic"] for a in selected_student_obj.assignments]))
    selected_topic = st.selectbox("Select a topic to view responses", topics)

    if st.button("View Responses"):
        for assignment in selected_student_obj.assignments:
            if assignment["topic"] == selected_topic:
                for i, response in enumerate(assignment["responses"]):
                    st.write(f"Question {i+1}: {response['question']}")
                    st.write(f"Answer: {response['answer']}")
                break



def main():
    
    st.title("Assignment Submission")
    users = load_users()

    # Check if the user is logged in and is an instructor
    if "username" in st.session_state and st.session_state["user_type"] == "instructor":
        view_responses(users)
    else:
        st.warning("Please log in as an instructor to view student responses.")

if __name__ == "__main__":
    
    # users = load_users()
    main()

   