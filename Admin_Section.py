import streamlit as st
import json
from typing import List
from pathlib import Path
from st_pages import Page, show_pages, add_page_title, hide_pages


# Optional -- adds the title and icon to the current page
# add_page_title()

# Specify what pages should be shown in the sidebar, and what their titles and icons
# should be
favicon = "favicon.ac8d93a.69085235180674d80d902fdc4b848d0b (1).png"
st.set_page_config(page_title="DocuBOT", page_icon=favicon)
st.image("Flipick_Logo-1 (1)-fotor-bg-remover-20230419132039.png",width=150)

show_pages(
    [
        Page("Admin_Section.py", "Home", "🏠"),
        Page("pages/DocuBOT.py",  "Chat_with_Books", ":books:"),
        Page("pages/DocuBOT_Quiz_Mode.py",  "Chat_Quiz",":memo:"),
        #Page("pages/sample.py",  "Chat_Quiz",":memo:"),
    ]
)
# hide_pages(["Admin_Controls", "Question_Generation"])

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


def main():
    

    users = load_users()

    container = st.container()

    with container:
        tab1, tab2 = st.tabs(["Login", "Register"])

        with tab1:
            st.subheader("Login")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")

            if st.button("Login"):
                user = [user for user in users if user.username ==
                        username and user.password == password]
                if user:
                    user = user[0]
                    st.session_state['username'] = user.username
                    st.session_state['user_type'] = user.user_type
                    st.success(
                        f"Logged in as {user.username} ({user.user_type}).")
                  
                else:
                    st.write("Invalid username or password.")

        with tab2:
            st.subheader("Register")
            user_type = st.radio("Select user type",
                                 ("student", "instructor"), horizontal=True,)
            if user_type == "instructor":
                username_reg = st.text_input("Username (Instructor)")
                password_reg = st.text_input(
                    "Password (Instructor)", type="password")
                if username_reg and password_reg:
                    new_user = User(username_reg, password_reg, user_type)
                    users.append(new_user)
                    save_users(users)
                    st.success(f"User {username_reg} registered successfully as a {user_type}.")
            else:
                instructors = [user for user in users if user.user_type == "instructor"]
                instructor_usernames = [instructor.username for instructor in instructors]
                selected_instructor = st.selectbox("Assign an Instructor", instructor_usernames)
                username_reg = st.text_input("Username (Learner)")
                password_reg = st.text_input("Password (Learner)", type="password")

                if st.button("Register"):
                    if not username_reg or not password_reg:
                        st.write("Please enter a username and password.")
                    else:
                        new_user = User(username_reg, password_reg, user_type, instructor=selected_instructor)
                        users.append(new_user)
                        save_users(users)
                        st.success(f"User {username_reg} registered successfully as a {user_type}.")

    if st.sidebar.button("Logout"):
        keys_to_remove = list(st.session_state.keys())  # Get a list of all session state keys
        for key in keys_to_remove:
            st.session_state.pop(key, None)  # Remove each key from the session state
        st.write("Logged out successfully.")

if __name__ == "__main__":
    # hide_pages(["Admin_Controls", "Question_Generation"])

    main()
    if "username" in st.session_state:
        users = load_users()
        user = [u for u in users if u.username == st.session_state['username']][0]
        if user.user_type == "instructor":
            show_pages([
            Page("Admin_Section.py", "Home", "🏠"),
            Page("pages/Admin_Controls.py",  "Admin_Controls"),
            Page("pages/Instructor_Quiz_Config.py",  "Question_Generation"),
            Page("pages/instructor_controls.py",  "Instructor controls")
            ])

       
