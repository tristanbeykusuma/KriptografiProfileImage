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
from hashlib import sha256
import hashlib
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
