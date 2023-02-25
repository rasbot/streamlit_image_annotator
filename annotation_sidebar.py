import os
import random
import shutil
from typing import Dict
from omegaconf import OmegaConf
from PIL import Image
import streamlit as st
import config as cf
from utils import get_filtered_files, update_json, load_json, save_json


def clamp_image_size(image_path: str, height: int) -> Image:

    img = Image.open(image_path)
    aspect_ratio = img.width / img.height
    if img.height > height:
        width = int(height * aspect_ratio)
    else:
        height = img.height
        width = img.width
    resized_image = img.resize((width, height))
    return resized_image


def go_back():
    state.counter -= 1
    set_current_file()


def go_forward():
    state.counter += 1
    set_current_file()


def set_current_file():
    if state.counter < len(state.files):
        state.current_file = state.files[state.counter]


def change_hide_state():
    state.hide_state = 1 - state.hide_state


def annotate(label: str, results_d: Dict[str, str], json_path: str):
    state.annotations[state.current_file] = label
    go_forward()
    # if args.json:
    update_json(results_d, json_path)

def make_folders_move_files(image_dir: str):
    # filter and remove keys from json file
    json_d = load_json(JSON_PATH)
    remove_keys = state.annotations.keys()
    filtered_d = {file:annotation for (file, annotation) in json_d["files"].items() if file not in remove_keys}
    if len(filtered_d) == 0:
        json_d = {}
    else:
        json_d["files"] = filtered_d
    save_json(json_d, JSON_PATH)

    annotation_set = set(state.annotations.values())
    img_names = get_filtered_files(image_dir, ["png", "jpg"])
    for annotation in annotation_set:
        n_files = 0
        remove_files = []
        os.makedirs(os.path.join(image_dir, annotation), exist_ok=True)
        filtered_files = [
            file for (file, label) in state.annotations.items() if annotation == label
        ]
        for file in filtered_files:
            if file in img_names:
                n_files += 1
                remove_files.append(file)
                file_path = os.path.join(image_dir, file)
                file_dest = os.path.join(image_dir, annotation, file)
                shutil.move(file_path, file_dest)
        st.sidebar.write(f"moving {n_files} to {annotation}...")
        for file in remove_files:
            state.annotations.pop(file, None)

def get_imgs(image_dir: str) -> list:
    img_names = get_filtered_files(image_dir, ["png", "jpg"])
    img_names.sort()
    return img_names

def reset_imgs(image_dir: str):
    img_names = get_imgs(image_dir)
    state.counter = 0
    state.annotations = {}
    state.files = img_names
    if state.files:
        state.current_file = state.files[0]
    else:
        st.write("No image files in folder. Nothing to annotate.")
    remaining = len(state.files)
    n_annotated = 0
    info_placeholder.info(f"Annotated: {n_annotated}, Remaining: {remaining}")


conf = OmegaConf.load('config.yml')
JSON_PATH = conf.json_path
IMG_HEIGHT_CLAMP = int(conf.image_height_clamp)

# st.set_page_config(layout="wide")
state = st.session_state
img_names = get_imgs(cf.IMAGE_DIR)
st.sidebar.title("Image Labeler")

if "clear_json" not in state:
    state.clear_json = 0
if "img_dir" not in state:
    state.img_dir = cf.IMAGE_DIR
if "options" not in state:
    state.options = cf.OPTIONS
if "counter" not in state:
    state.counter = 0
if "hide_state" not in state:
    state.hide_state = 0
if "annotations" not in state:
    state.annotations = {}
    state.files = img_names
    if state.files:
        state.current_file = state.files[0]
    else:
        st.write("No image files in folder. Nothing to annotate.")

# set order of UI elements
n_annotated = len(state.annotations)
remaining = len(state.files) - state.counter
st.sidebar.button("BACK", on_click=go_back)
info_placeholder = st.sidebar.empty()
info_placeholder.info(f"Annotated: {n_annotated}, Remaining: {remaining}")
cols_placeholder = st.sidebar.empty()
st.sidebar.markdown("---")
move_col, reset_col = st.sidebar.columns(2)
move_col.button("Move Files", on_click=make_folders_move_files, args=(state.img_dir,))
st.sidebar.markdown("---")
with st.sidebar.expander("Expand for more options"):
    new_img_dir = st.text_input("full directory path to image files", value=state.img_dir)
    if new_img_dir != state.img_dir:
        state.img_dir = new_img_dir
        reset_imgs(state.img_dir)
    state.options = st.text_input("annotation button names (comma separated)", value=cf.OPTIONS)
    state.options = [opt.strip() for opt in state.options.split(",")]
    side_cols = cols_placeholder.columns(len(state.options))
    c1, c2 = st.columns(2)
    clear_annotations = c1.button("Reset Annotations?")
    add_hide_button = c2.checkbox("Hide Image Button")

if clear_annotations:
    st.write("CLEAR")
    save_json({}, JSON_PATH)
    state.annotations = {}
    n_annotated = 0
    remaining = len(state.files)
    state.counter = 0
    info_placeholder.info(f"Annotated: {n_annotated}, Remaining: {remaining}")
if state.counter < len(state.files):
    if state.hide_state == 0:
        selected_file = state.current_file
        file_path = os.path.join(state.img_dir, selected_file)
        image = clamp_image_size(file_path, IMG_HEIGHT_CLAMP)
        st.image(image, use_column_width="never")
        st.write(selected_file)
        json_dict = {"directory": state.img_dir, "files": state.annotations}
        for idx, option in enumerate(state.options):
            side_cols[idx].button(
                f"{option}", on_click=annotate, args=(option, json_dict, JSON_PATH)
            )
    else:
        for idx, option in enumerate(state.options):
            side_cols[idx].button(f"{option}")

    if add_hide_button:
        reset_col.button("RESET", on_click=change_hide_state)

else:
    cols_placeholder.info("Everything is annotated.")
