"""Streamlit image viewer with slideshow and shuffle support."""

import os
import random
import time

import streamlit as st
from omegaconf import OmegaConf

from utils import filter_by_keyword, get_filtered_files, load_image


def _get_default_dir() -> str:
    """Read default image directory from config.yml, falling back to cwd."""
    if os.path.isfile("config.yml"):
        conf = OmegaConf.load("config.yml")
        default_dir = str(conf.default_directory) if conf.default_directory else ""
        if default_dir and os.path.isdir(default_dir):
            return default_dir
    return os.getcwd()


DEFAULT_DIR = _get_default_dir()
height_clamp = 785

state = st.session_state
if "img_dir" not in state:
    state.img_dir = DEFAULT_DIR
if "img_file_names" not in state:
    state.img_file_names = []
if "filtered_words" not in state:
    state.filtered_words = []
if "sleep_time" not in state:
    state.sleep_time = 3
if "counter" not in state:
    state.counter = 0
if "files" not in state:
    state.files = []
if "current_file" not in state:
    state.current_file = None
if "show_file_name" not in state:
    state.show_file_name = False
if "is_new_dir" not in state:
    state.is_new_dir = True
if "is_new_keywords" not in state:
    state.is_new_keywords = False
if "height_clamp" not in state:
    state.height_clamp = height_clamp
if "is_clamped" not in state:
    state.is_clamped = False
if "is_shuffled" not in state:
    state.is_shuffled = False
if "is_slideshow" not in state:
    state.is_slideshow = False
if "continuous" not in state:
    state.continuous = False
if "keywords" not in state:
    state.keywords = ""
    state.keyword_filter = ""
    state.sep = " "
    state.split_keywords = []

hide_streamlit_style = """
                <style>
                div[data-testid="stToolbar"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                div[data-testid="stDecoration"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                div[data-testid="stStatusWidget"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                #MainMenu {
                visibility: hidden;
                height: 0%;
                }
                header {
                visibility: hidden;
                height: 0%;
                }
                footer {
                visibility: hidden;
                height: 0%;
                }
                </style>
                """


def get_imgs():
    """Get a sorted list of image paths. Images
    are filtered to png and jpg (specified in config.yml)
    and sorted. If the image directory is not a
    valid directory, return None.

    Returns:
        List[str]: List of sorted image paths.
    """
    if state.is_new_dir:
        state.img_file_names = get_filtered_files(state.img_dir)
        state.is_new_dir = False
        if state.img_file_names:  # and not state.is_shuffled:
            state.img_file_names.sort()
        state.filtered_words = state.img_file_names
    if state.split_keywords and state.is_new_keywords:
        keyword_filtered = []
        for keyword in state.split_keywords:
            _, filtered = filter_by_keyword(
                state.img_file_names, keyword, sep_=state.sep
            )
            keyword_filtered.extend(filtered)
        keyword_filtered = list(set(keyword_filtered))
        state.is_new_keywords = False
        if not state.is_shuffled:
            keyword_filtered.sort()
        state.filtered_words = keyword_filtered

    if not state.split_keywords:
        state.filtered_words = state.img_file_names
    return state.filtered_words


def set_dir():
    """Set the image directory and get image files if any exist.
    Also sets the current file in the state dict."""
    if not os.path.isdir(state.img_dir):
        st.error(f"{state.img_dir} is not a valid directory!")
    else:
        state.files = get_imgs()
    if state.files and state.counter < len(state.files):
        state.current_file = state.files[state.counter]
    else:
        st.write("No image files in folder.")


def show_image():
    """Show image in viewer."""
    file_path = os.path.join(state.img_dir, state.current_file)
    if state.height_clamp > 0:
        state.is_clamped = True
    else:
        state.is_clamped = False
    image = load_image(file_path, state.height_clamp, state.is_clamped)
    img_container.image(image, use_container_width=False)
    if state.show_file_name:
        file_name_placeholder.info(state.current_file)


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
    if (state.counter < 1) or (state.counter >= len(state.files)):
        state.counter = 0
    set_current_file()


def change_dir():
    """Change directory and reset images."""
    if not os.path.isdir(state._img_dir):
        st.error(
            f"{state._img_dir} is not a valid directory...Please enter another one."
        )
    else:
        state.img_dir = state._img_dir
        state.is_new_dir = True


def clear_img():
    """Clear image."""
    state.counter = -1


def shuffle_files():
    """Shuffle file list."""
    random.shuffle(state.files)
    state.counter = 0
    state.is_shuffled = True


def change_height_clamp():
    """Change height clamp value."""
    state.height_clamp = state._height_clamp


def change_keywords():
    """Change keywords if the user provides new keywords."""
    st.write("changing keywords...")
    state.keywords = state._keywords
    if state.keywords:
        state.split_keywords = [opt.strip() for opt in state.keywords.split(",")]
    else:
        state.split_keywords = []
    state.counter = 0
    state.is_new_keywords = True


def get_sep():
    """Get separator if provided by user."""
    state.sep = state._sep


def reset_keywords():
    """Reset split keywords list to an empty list."""
    state.split_keywords = []
    # state.counter = 0


st.set_page_config(layout="wide")
set_dir()
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
img_container = st.empty()
button_col1, button_col2 = st.sidebar.columns(2)
button_col1.button("back", on_click=change_img, args=(-1,))
button_col2.button("next", on_click=change_img, args=(1,))
st.sidebar.markdown("---")
col1, col2 = st.sidebar.columns(2)
col1.button("clear", on_click=clear_img)
col2.button("shuffle", on_click=shuffle_files)
file_name_placeholder = st.sidebar.empty()
scol1, scol2, scol3 = st.sidebar.columns(3)
state.show_file_name = scol1.checkbox("show filename")
state.is_slideshow = scol2.checkbox("slide show", value=False)
if state.is_slideshow:
    state.continuous = scol3.checkbox("continuous", value=False)
    state.sleep_time = st.sidebar.number_input("view time", value=2)
#     shuffle_files()
st.sidebar.markdown("---")
st.sidebar.text_input(
    "full directory path to image files",
    value=DEFAULT_DIR,
    key="_img_dir",
    on_change=change_dir,
)
st.sidebar.info(f"number of images: {len(state.files)}")
state.keyword_filter = st.sidebar.checkbox("Keyword Filter", on_change=reset_keywords)
if state.keyword_filter:
    keycol1, keycol2 = st.sidebar.columns([1, 8])
    keycol1.text_input("sep", key="_sep", on_change=get_sep)
    keycol2.text_input(
        "Keywords (comma separated)",
        key="_keywords",
        on_change=change_keywords,
    )
st.sidebar.number_input(
    "height clamp",
    value=height_clamp,
    key="_height_clamp",
    on_change=change_height_clamp,
)
if state.counter >= 0 and not state.is_slideshow:
    show_image()
# TODO: height clamp if removed should stay that way
# slide show code
if state.is_slideshow and state.counter < len(state.files):
    show_image()
    time.sleep(state.sleep_time)
    if state.counter == len(state.files) - 1 and state.continuous:
        state.counter = 0
    else:
        state.counter += 1
    set_current_file()
    st.rerun()
