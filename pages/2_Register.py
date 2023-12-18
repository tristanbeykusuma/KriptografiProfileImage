import streamlit as st
from deta import Deta
import os
from PIL import Image
import numpy as np
import streamlit_authenticator as stauth
import streamlit_authenticator as stauth
import pandas as pd

project = Deta("c0voubbdad6_eMHjd34iiQDZZciA6U1bjxRzXeetsDQJ")

# Define the drive to store the files.
drive_name = 'Images'
drive = project.Drive(drive_name)

userbase_name = 'User'
userdb = project.Base(userbase_name)

def insert_user(username, name, password):
    """Returns the user on a successful user creation, otherwise raises and error"""
    return userdb.put({"key": username, "name": name, "password": password})

def fetch_all_users():
    """Returns a dict of all users"""
    res = userdb.fetch()
    return res.items


def get_user(username):
    """If not found, the function will return None"""
    return userdb.get(username)


def update_user(username, updates):
    """If the item is updated, returns None. Otherwise, an exception is raised"""
    return userdb.update(updates, username)


def delete_user(username):
    """Always returns None, even if the key does not exist"""
    return userdb.delete(username)

users = fetch_all_users()

usernames = [user["key"] for user in users]
names = [user["name"] for user in users]
hashed_passwords = [user["password"] for user in users]

authenticator = stauth.Authenticate(names, usernames, hashed_passwords,
    "sales_dashboard", "abcdef", cookie_expiry_days=30)

try:
    with st.form("my_form"):
        st.write("Registrasi User")
        # creating input fields
        username=st.text_input('Userame:')
        name=st.text_input('Name:')
        password=st.text_input('Password:')
        # Every form must have a submit button.
        submitted = st.form_submit_button("Submit")
        if submitted:
            hashed_password = stauth.Hasher([password]).generate()
            insert_user(username, name, hashed_password[0])  
            st.success('User registered successfully')
except Exception as e:
    st.error(e)