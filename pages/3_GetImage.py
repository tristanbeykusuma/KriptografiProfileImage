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
import base64
import hashlib
import os
import io
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

def fetch_user_images(user):
    """Returns the user on a successful user creation, otherwise raises and error"""
    res = imagekeydb.fetch({"username?contains": user})
    return res.items

def fetch_all_users():
    """Returns a dict of all users"""
    res = userdb.fetch()
    return res.items

def update_user(username, updates):
    """If the item is updated, returns None. Otherwise, an exception is raised"""
    return userdb.update(updates, username)


def delete_user(username):
    """Always returns None, even if the key does not exist"""
    return userdb.delete(username)


def extract_encrypted_data_from_image(encrypted_image):
    # Convert the image to a Numpy array
    encrypted_array = np.array(encrypted_image)

    flat_encrypted_data = encrypted_array.flatten()

    extracted_encrypted_data = bytes(flat_encrypted_data)

    return extracted_encrypted_data

def decrypt_image(encrypted_data, key):
    extracted_iv = encrypted_data[:AES.block_size]
    # Create AES cipher object
    cipher = AES.new(key, AES.MODE_CBC, extracted_iv)

    decrypted_data = cipher.decrypt(encrypted_data[AES.block_size:])

    unpadded_data = unpad(decrypted_data, AES.block_size)

    return unpadded_data

users = fetch_all_users()

placeholder = st.empty()
placeholder.info("username pparker password abc123")

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
    images = fetch_user_images(username)

    imagenames = [image["image"] for image in images]
    imagekeys = [image["imagekey"] for image in images]

    for idx, imagename in enumerate(imagenames):
        embedded_image = Image.open(imagename)
        extracted_data = extract_encrypted_data_from_image(embedded_image)
        with open(imagekeys[idx], 'rb') as key_file:
            key_base64 = key_file.read()
        decrypted_data = decrypt_image(extracted_data, key_base64)
        st.image(decrypted_data)
        # Get the pixel values from the original image
        original_array = np.array(embedded_image)

        # Create a square image (let's assume the size is 32x32)
        square_size = 32
        square_image = Image.new('L', (square_size, square_size), color='white')

        # Calculate the starting index for the original image in the square image
        start_index = (square_size - original_array.shape[1]) // 2

        # Copy pixel values from the original image to every column of the square image
        for i in range(square_size):
            square_image.paste(Image.fromarray(original_array), (i, 0))
        st.image(square_image)

    

