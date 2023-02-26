import os
import shutil
from typing import Dict, List

import streamlit as st
from omegaconf import OmegaConf

from utils import (get_filtered_files, load_image, load_json, save_json,
                   update_json)

# TODO: Add toggle for full resolution
# TODO: Maybe add height clamp option

def set_current_file():
    """Set the current file to the index of the
    state.counter.
    """
    if state.counter < len(state.files):
        state.current_file = state.files[state.counter]


def change_img(val: int) -> None:
    """Increase/decrease state.counter and sets
    the current file, displaying a different image.

    Args:
        val (int): Value to change counter (1/-1)
    """
    state.counter += val
    if state.counter < 1:
        state.counter = 0
    set_current_file()


def change_hide_state():
    """Flips the state of state.hide_state. If 0 -> 1,
    if 1 -> 0.
    """
    state.hide_state = 1 - state.hide_state


def annotate(label: str, results_d: Dict[str, Dict[str, str]], json_path: str) -> None:
    """Set annotation for the current file, change the image, and update the
    json file.

    results_d will have a 'directory' key with a value containing the directory path
    of the image folder, and a 'files' key with a dictionary of file_name/annotation pairs.

    Args:
        label (str): Annotation label to assign to img file.
        results_d (Dict[str, Dict[str, str]): Dictionary of annotations.
        json_path (str): Path to json file.
    """
    state.annotations[state.current_file] = label
    change_img(1)
    # if USE_JSON:
    update_json(results_d, json_path)


def filter_json():
    """Filter a json file by removing keys.
    """
    # filter and remove keys from json file
    json_d = load_json(state.json_path)
    remove_keys = state.annotations.keys()
    filtered_d = {
        file: annotation
        for (file, annotation) in json_d["files"].items()
        if file not in remove_keys
    }
    if len(filtered_d) == 0:
        json_d = {}
    else:
        json_d["files"] = filtered_d
    save_json(json_d, state.json_path)


def make_folders_move_files() -> None:
    """Make folders for each unique annotation. Filter state dict
    and move annotated files to their respective folders.
    Remove files from json and delete the json file if it is empty.
    """
    json_d = load_json(state.json_path)
    annotation_set = set(json_d["files"].values())
    img_file_names = get_filtered_files(state.img_dir)
    for annotation in annotation_set:
        n_files = 0
        remove_files = []
        os.makedirs(os.path.join(state.img_dir, annotation), exist_ok=True)
        filtered_files = [
            file for (file, label) in json_d["files"].items() if annotation == label
        ]
        for file in filtered_files:
            if file in img_file_names:
                n_files += 1
                remove_files.append(file)
                img_file_path = os.path.join(state.img_dir, file)
                file_dest = os.path.join(state.img_dir, annotation, file)
                shutil.move(img_file_path, file_dest)
        st.sidebar.write(f"moving {n_files} to {annotation}...")
        for file in remove_files:
            state.annotations.pop(file, None)
            json_d["files"].pop(file, None)
    if len(json_d["files"]) > 0:
        st.write("non zero json")
        save_json(json_d, state.json_path)
    else:
        st.write("delete that guy")
        os.remove(state.json_path)


def get_imgs(image_dir: str) -> List[str]:
    """Get a sorted list of image paths. Images
    are filtered to png and jpg (specified in config.yml)
    and sorted. If the image directory is not a
    valid directory, return None.

    Args:
        image_dir (str): Directory with images to annotate.

    Returns:
        List[str]: List of sorted image paths.
    """
    img_file_names = get_filtered_files(image_dir)
    if img_file_names is None:
        st.write(
            "Folder path does not seem to point to a valid directory. \
                 Try another one please."
        )
        return None
    img_file_names.sort()
    return img_file_names


def reset_imgs(image_dir: str) -> None:
    """Reset variables when a directory is changed

    Args:
        image_dir (str): New directory of images.
    """
    img_file_names = get_imgs(image_dir)
    if img_file_names is None:
        return
    state.counter = 0
    state.annotations = {}
    state.files = img_file_names
    if state.files:
        state.current_file = state.files[0]
    else:
        st.write("No image files in folder. Nothing to annotate.")
    remaining_imgs = len(state.files)
    n_annotated_imgs = 0
    info_placeholder.info(f"Annotated: {n_annotated_imgs}, Remaining: {remaining_imgs}")


conf = OmegaConf.load("config.yml")
IMAGE_DIR = conf.default_directory
if not IMAGE_DIR or not os.path.exists(IMAGE_DIR):
    IMAGE_DIR = os.getcwd()
JSON_PATH = os.path.join(IMAGE_DIR, "annotations.json")
CATEGORIES = conf.default_categories
if not CATEGORIES:
    CATEGORIES = "keep, delete, fix, other"
is_image_clamp = conf.clamp_image
IMG_HEIGHT_CLAMP = int(conf.image_height_clamp)

state = st.session_state
img_names = get_imgs(IMAGE_DIR)
st.sidebar.title("Image Annotator")

if "img_dir" not in state:
    state.img_dir = IMAGE_DIR
if "json_path" not in state:
    state.json_path = JSON_PATH
if "categories" not in state:
    state.categories = CATEGORIES
if "counter" not in state:
    state.counter = 0
if "hide_state" not in state:
    state.hide_state = 0
if "annotations" not in state and not img_names is None:
    state.annotations = {}
    state.files = img_names
    if state.files:
        state.current_file = state.files[0]
    else:
        st.write("No image files in folder. Nothing to annotate.")

# only create a empty json file if the directory has images
if not os.path.exists(JSON_PATH) and state.files:
    st.write("SAVE EMPTY JSON")
    save_json({}, JSON_PATH)
# set order of UI elements
n_annotated = len(state.annotations)
remaining = len(state.files) - state.counter
st.sidebar.button("BACK", on_click=change_img, args=(-1,))
info_placeholder = st.sidebar.empty()
info_placeholder.info(f"Annotated: {n_annotated}, Remaining: {remaining}")
cols_placeholder = st.sidebar.empty()
st.sidebar.markdown("---")
move_col, reset_col = st.sidebar.columns(2)
move_col.button("Move Files", on_click=make_folders_move_files)
st.sidebar.markdown("---")
with st.sidebar.expander("Expand for more options"):
    new_img_dir = st.text_input(
        "full directory path to image files", value=state.img_dir
    )
    if new_img_dir != state.img_dir:
        state.img_dir = new_img_dir
        state.json_path = os.path.join(new_img_dir, "annotations.json")
        reset_imgs(state.img_dir)
        if not os.path.exists(state.json_path) and state.files:
            save_json({}, state.json_path)
    state.categories = st.text_input(
        "annotation button names (comma separated)", value=CATEGORIES
    )
    state.categories = [opt.strip() for opt in state.categories.split(",")]
    side_cols = cols_placeholder.columns(len(state.categories))
    c1, c2 = st.columns(2)
    clear_annotations = c1.button("Reset Annotations?")
    add_hide_button = c2.checkbox("Hide Image Button")

if clear_annotations:
    st.write("CLEAR")
    save_json({}, state.json_path)
    state.annotations = {}
    n_annotated = 0
    remaining = len(state.files)
    state.counter = 0
    info_placeholder.info(f"Annotated: {n_annotated}, Remaining: {remaining}")
if state.counter < len(state.files):
    if state.hide_state == 0:
        selected_file = state.current_file
        file_path = os.path.join(state.img_dir, selected_file)
        image = load_image(file_path, IMG_HEIGHT_CLAMP)
        st.image(image, use_column_width="never")
        st.write(selected_file)
        json_dict = {"directory": state.img_dir, "files": state.annotations}
        for idx, option in enumerate(state.categories):
            side_cols[idx].button(
                f"{option}", on_click=annotate, args=(option, json_dict, state.json_path)
            )
    else:
        for idx, option in enumerate(state.categories):
            side_cols[idx].button(f"{option}")

    if add_hide_button:
        reset_col.button("CLEAR", on_click=change_hide_state)

else:
    cols_placeholder.info("Everything is annotated.")
