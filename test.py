from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
from hashlib import sha256
import hashlib
import os
from PIL import Image
import numpy as np

def encrypt_image(input_path, key, seed=None):
    with open(input_path, 'rb') as image_file:
        image_data = image_file.read()

    seed_bytes = seed.encode() if seed else b''

    if(len(seed_bytes)>=AES.block_size):
      seed_bytes = b''

    additional_random_bytes = get_random_bytes(AES.block_size - len(seed_bytes))

    iv = seed_bytes + additional_random_bytes

    cipher = AES.new(key, AES.MODE_CBC, iv)

    padded_data = pad(image_data, AES.block_size)

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

user_provided_seed = input("Enter a seed (or leave blank for random): ")
key = get_random_bytes(32)
input_image_path = 'download.jpg'
base_name = os.path.splitext(os.path.basename(input_image_path))[0]
width, height = 640, 480

encrypted_data = encrypt_image(input_image_path, key, user_provided_seed)

with open(f"{base_name}_key.bin", 'wb') as key_file:
        key_file.write(key)

embedded_image = embed_encrypted_data_into_image(encrypted_data, width, height)
embedded_image.save('embedded_image.png')