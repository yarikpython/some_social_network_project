from ssn import app
import secrets
import os
from PIL import Image


def save_profile_image(form_profile_img_data):
    hashed_filename_img = secrets.token_hex(8)
    _, ext = os.path.splitext(form_profile_img_data.filename)
    new_profile_img_filename = hashed_filename_img + ext
    path_new_img = os.path.join(app.root_path, 'static/profile_pics', new_profile_img_filename)
    output_size = (250, 250)
    img = Image.open(form_profile_img_data)
    img.resize(output_size)
    img.save(path_new_img)
    return new_profile_img_filename


def save_post_image(form_post_image_data):
    hashed_post_image_data_filename = secrets.token_hex(8)
    _, ext = os.path.splitext(form_post_image_data.filename)
    new_post_image_file_name = hashed_post_image_data_filename + ext
    path = os.path.join(app.root_path, 'static/post_pics', new_post_image_file_name)
    output_size = (600, 600)
    img = Image.open(form_post_image_data)
    img.thumbnail(output_size)
    img.save(path)
    return new_post_image_file_name
