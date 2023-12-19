"""Upload image file from disk to deta using streamlit.

References:

  streamlit:
    https://docs.streamlit.io/library/api-reference/widgets/st.file_uploader

  deta:
    https://docs.deta.sh/docs/drive/sdk#put
"""

import streamlit as st
from deta import Deta
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import base64
import os
import io
import time
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

imagekeybase_name = 'ImageKey'
imagekeydb = project.Base(imagekeybase_name)

def insert_image(imagename, imagekey, user):
    """Returns the user on a successful user creation, otherwise raises and error"""
    return imagekeydb.put({"image": imagename, "imagekey": imagekey, "username": user})

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


def encrypt_image(bytes_data, key, seed=None):

    seed_bytes = seed.encode() if seed else b''

    if(len(seed_bytes)>=AES.block_size):
      seed_bytes = b''

    additional_random_bytes = get_random_bytes(AES.block_size - len(seed_bytes))

    iv = seed_bytes + additional_random_bytes

    cipher = AES.new(key, AES.MODE_CBC, iv)

    padded_data = pad(bytes_data, AES.block_size)

    encrypted_data = cipher.encrypt(padded_data)

    return iv + encrypted_data

def embed_encrypted_data_into_image(encrypted_data, width, height):
    # Convert the encrypted data to a NumPy array
    encrypted_array = np.frombuffer(encrypted_data, dtype=np.uint8)
    # Reshape the array into a 2D array
    encrypted_array = encrypted_array[:width * height]
    # Create a new image from the array
    encrypted_image = Image.fromarray(encrypted_array, mode='L')

    return encrypted_image

users = fetch_all_users()

usernames = [user["key"] for user in users]
names = [user["name"] for user in users]
hashed_passwords = [user["password"] for user in users]

authenticator = stauth.Authenticate(names, usernames, hashed_passwords,
    "sales_dashboard", "abcdef", cookie_expiry_days=30)

name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status == False:
    st.error("Username/password is incorrect")

if authentication_status == None:
    st.warning("Please enter your username and password")

if authentication_status:
    authenticator.logout('Logout', 'main')
    # Initialize a streamlit file uploader widget.
    uploaded_file = st.file_uploader("Choose a file")

    # If user attempts to upload a file.
    if uploaded_file is not None:
        start_time = time.time()
        user_provided_seed='test'
        bytes_data = uploaded_file.getvalue()
        with open(uploaded_file.name, mode='wb') as w:
            w.write(bytes_data)
        with open(uploaded_file.name, 'rb') as image_file:
            bytes_data = image_file.read()
        key = get_random_bytes(32)
        width, height = 640, 480

        encrypted_data = encrypt_image(bytes_data, key, user_provided_seed)

        with open(f"{uploaded_file.name}_key.bin", 'wb') as key_file:
            key_file.write(key)

        embedded_image = embed_encrypted_data_into_image(encrypted_data, width, height)
        saved_image_name='embedded_image_'+uploaded_file.name+'.png'
        embedded_image.save(saved_image_name)
        finish_time = time.time()
        time_difference = finish_time - start_time
        insert_image(saved_image_name,f"{uploaded_file.name}_key.bin", username)
        st.write(f'filename: {uploaded_file.name}')
        st.image(bytes_data)
        st.write(embedded_image.size)
        st.write(time_difference)