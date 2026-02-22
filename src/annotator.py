"""Main script to run annotator logic."""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Any

import streamlit as st
from omegaconf import OmegaConf

__all__ = ["Annotator"]

from utils import (
    filter_by_keyword,
    get_filtered_files,
    get_metadata_str,
    load_image,
    load_json,
    save_json,
    update_json,
)


class Annotator:
    """Orchestrates the Streamlit image annotation UI.

    Loads configuration from a YAML file, manages Streamlit session state,
    renders sidebar and main-area widgets, handles user interactions
    (annotation, directory changes, keyword filtering, file moves), and
    coordinates annotation persistence to JSON.
    """

    def __init__(self, config_path: str = "config.yml"):
        """Initialize the Annotator class.

        Args:
            config_path (str, optional): Path to config file. Defaults to "config.yml".
        """
        self.config_path = config_path
        self.image_dir: str | None = None
        self.json_path: str | None = None
        self.categories: str | None = None
        self.img_height_clamp: int = 0
        self.clamp_image: bool = False
        self.state: Any = None
        self.back_placeholder: Any = None
        self.info_placeholder: Any = None
        self.options_buttons_placeholder: Any = None
        self.move_clear_buttons_placeholder: Any = None
        self.checkbox_placeholder: Any = None
        self.move_placeholder: Any = None
        self.prompt_info: Any = None
        self.meta_info: Any = None
        self.expander_placeholder: Any = None
        self.keyword_dict: dict[str, list[str]] | None = None
        self.img_file_names: list[str] | None = None
        self.remaining: int | None = None
        self.n_annotated: int | None = None
        self.move_col: Any = None
        self.clear_col: Any = None
        self.reset_col: Any = None
        self.clamp_col: Any = None
        self.prompt_col: Any = None
        self.meta_col: Any = None
        self.clear_annotations: bool | None = None
        self.button_cols: list[Any] | None = None
        self.keyword_filter: bool | None = None
        self.add_hide_button: bool | None = None
        self.key1: Any = None
        self.key2: Any = None
        self.keyword_move: bool | None = None
        self.file_path: str | None = None

    def get_config_data(self) -> None:
        """Load config data from the yml file. This will save the config file
        with defaults based on the working directory if they are blank.
        These are where `update_config` is set to true.
        """
        update_config = False
        if Path(self.config_path).suffix not in (".yml", ".yaml"):
            raise ValueError("Config file must be a yml or yaml file.")
        conf = OmegaConf.load(self.config_path)
        if not conf.default_directory or not os.path.isdir(conf.default_directory):
            update_config = True
            conf.default_directory = os.getcwd()
        if not conf.json_path:
            update_config = True
            conf.json_path = os.path.join(os.getcwd(), "annotations.json")
        if not conf.default_categories:
            update_config = True
            conf.default_categories = "keep, delete, fix, other"
        if update_config:
            OmegaConf.save(conf, self.config_path)
        self.image_dir = conf.default_directory
        self.json_path = conf.json_path
        self.categories = conf.default_categories
        self.img_height_clamp = int(conf.image_height_clamp)
        self.clamp_image = conf.clamp_image

    def set_state_dict(self) -> None:
        """Set the state dictionary by adding key
        value pairs that will be used in the app.
        Some default to config variables, others default to empty
        strings or 0.
        """
        self.state = st.session_state

        if "img_dir" not in self.state:
            self.state.img_dir = self.image_dir
        if "json_path" not in self.state:
            self.state.json_path = self.json_path
        if "categories" not in self.state:
            self.state.categories = self.categories
            self.state.split_categories = [
                opt.strip() for opt in self.categories.split(",")
            ]
        if "clamp_state" not in self.state:
            self.state.clamp_state = self.clamp_image
        if "counter" not in self.state:
            self.state.counter = 0
        if "hide_state" not in self.state:
            self.state.hide_state = 0
        if "annotations" not in self.state:
            self.state.annotations = {}
        if "files" not in self.state:
            self.state.files = []
        if "is_expanded" not in self.state:
            self.state.is_expanded = False
        if "show_meta" not in self.state:
            self.state.show_meta = False
        if "show_prompt" not in self.state:
            self.state.show_prompt = False
        if "keywords" not in self.state:
            self.state.keywords = ""
            self.state.sep = " "
            self.state.split_keywords = []
        if "keyword_and_or" not in self.state:
            self.state.keyword_and_or = False
        if "move" not in self.state:
            self.state.move = False

    def set_ui(self) -> None:
        """Set the order of the UI elements for the sidebar."""
        st.set_page_config(layout="wide")
        st.sidebar.title("Image Annotator")
        # set up order of sidebar UI elements
        self.back_placeholder = st.sidebar.empty()
        self.info_placeholder = st.sidebar.empty()
        self.options_buttons_placeholder = st.sidebar.empty()
        st.sidebar.markdown("---")
        self.move_clear_buttons_placeholder = st.sidebar.empty()
        self.checkbox_placeholder = st.sidebar.empty()
        st.sidebar.markdown("---")
        self.move_placeholder = st.sidebar.empty()
        self.prompt_info = st.sidebar.empty()
        self.meta_info = st.sidebar.empty()
        self.expander_placeholder = st.sidebar.empty()

    def set_dir(self) -> None:
        """Set the image directory and get image files if any exist.
        Also sets the current file in the state dict."""
        if not os.path.isdir(self.state.img_dir):
            st.error(f"{self.state.img_dir} is not a valid directory!")
        else:
            self.state.files = self.get_imgs()
        if self.state.files and self.state.counter < len(self.state.files):
            self.state.current_file = self.state.files[self.state.counter]
        else:
            st.write("No image files in folder. Nothing to annotate.")

    def set_current_file(self) -> None:
        """Set the current file to the index of the
        state.counter.
        """
        if self.state.counter < len(self.state.files):
            self.state.current_file = self.state.files[self.state.counter]

    def change_img(self, val: int) -> None:
        """Increase/decrease state.counter and sets
        the current file, displaying a different image.

        Args:
            val (int): Value to change counter (1/-1)
        """
        self.state.counter += val
        if self.state.counter < 1:
            self.state.counter = 0
        self.set_current_file()

    def change_hide_state(self) -> None:
        """Flips the state of state.hide_state. If 0 -> 1,
        if 1 -> 0.
        """
        self.state.hide_state = 1 - self.state.hide_state

    def annotate(
        self, label: str, results_d: dict[str, dict[str, str]], json_path: str
    ) -> None:
        """Set annotation for the current file, change the image, and update the
        json file.

        results_d will have a 'directory' key with a value containing the directory
        path of the image folder, and a 'files' key with file_name/annotation pairs.

        Args:
            label (str): Annotation label to assign to img file.
            results_d (dict[str, dict[str, str]]): Dictionary of annotations.
            json_path (str): Path to json file.
        """
        self.state.annotations[self.state.current_file] = label
        self.change_img(1)
        update_json(results_d, json_path)

    def get_keyword_file_dict(self) -> None:
        """Create a dictionary with key = keyword, val = list of filtered file names
        that contain the keyword.

        Note: Filtering is performed on image filenames only, not prompt content.
        """
        file_list_ = self.img_file_names.copy()
        self.keyword_dict = {}
        for keyword in self.state.split_keywords:
            if not self.state.sep:
                self.state.sep = " "
            file_list_, filtered_files = filter_by_keyword(
                file_list_, keyword, self.state.sep
            )
            self.keyword_dict[keyword] = filtered_files

    def make_folders_move_files(self, use_keywords: bool = False) -> None:
        """Make folders for each unique annotation. Filter state dict
        and move annotated files to their respective folders.
        Remove files from json and delete the json file if it is empty.

        Args:
            use_keywords (bool, optional): If True, use keyword dict instead
                of json dict to move files.
        """
        self.img_file_names = get_filtered_files(self.state.img_dir)
        if use_keywords:
            self.get_keyword_file_dict()
            folder_names = {key for key, val in self.keyword_dict.items() if val}
        else:
            if os.path.exists(self.state.json_path):
                json_d = load_json(self.state.json_path)
            else:
                return
            folder_names = set(json_d["files"].values())
        for folder_name in folder_names:
            n_files = 0
            remove_files = []
            os.makedirs(os.path.join(self.state.img_dir, folder_name), exist_ok=True)
            if use_keywords:
                filtered_files = self.keyword_dict[folder_name]
            else:
                filtered_files = [
                    file
                    for (file, label) in json_d["files"].items()
                    if folder_name == label
                ]
            for file in filtered_files:
                if file in self.img_file_names:
                    n_files += 1
                    remove_files.append(file)
                    img_file_path = os.path.join(self.state.img_dir, file)
                    file_dest = os.path.join(self.state.img_dir, folder_name, file)
                    shutil.move(img_file_path, file_dest)
            st.info(f"moving {n_files} images to {folder_name}...")
            for file in remove_files:
                if not use_keywords:
                    self.state.annotations.pop(file, None)
                    json_d["files"].pop(file, None)
        if not use_keywords:
            if len(json_d["files"]) > 0:
                save_json(json_d, self.state.json_path)
            else:
                os.remove(self.state.json_path)
            self.state.counter = 0

    def get_imgs(self) -> list[str]:
        """Get a sorted list of image paths. Images
        are filtered to png and jpg (specified in config.yml)
        and sorted. If the image directory is not a
        valid directory, return an empty list.

        Returns:
            list[str]: List of sorted image paths.
        """
        img_file_names = get_filtered_files(self.state.img_dir)
        if img_file_names:
            img_file_names.sort()
        if self.state.split_keywords:
            keyword_filtered = []
            for keyword in self.state.split_keywords:
                if self.state.keyword_and_or:
                    if not keyword_filtered:
                        filter_files = img_file_names
                    else:
                        filter_files = keyword_filtered
                    _, filtered = filter_by_keyword(
                        filter_files, keyword, sep_=self.state.sep
                    )
                    keyword_filtered = filtered
                else:
                    _, filtered = filter_by_keyword(
                        img_file_names, keyword, sep_=self.state.sep
                    )
                    keyword_filtered.extend(filtered)
            keyword_filtered = list(set(keyword_filtered))
            keyword_filtered.sort()
            return keyword_filtered
        return img_file_names

    def reset_imgs(self) -> None:
        """Reset variables when a directory is changed."""
        img_file_names = self.get_imgs()
        self.state.counter = 0
        self.state.annotations = {}
        self.state.files = img_file_names
        if self.state.files:
            self.state.current_file = self.state.files[self.state.counter]
        self.remaining = len(self.state.files)
        self.n_annotated = 0
        self.info_placeholder.info(
            f"Annotated: {self.n_annotated}, Remaining: {self.remaining}"
        )

    def change_dir(self) -> None:
        """Change directory and reset images."""
        new_dir = getattr(self.state, "_img_dir", None)
        if not new_dir or not os.path.isdir(new_dir):
            st.error(f"{new_dir!r} is not a valid directory. Please enter another one.")
        else:
            self.state.img_dir = new_dir
            self.reset_imgs()

    def update_categories(self) -> None:
        """Update the categories variable."""
        new_categories = getattr(self.state, "_categories", None)
        if not new_categories:
            return
        self.state.categories = new_categories
        self.state.split_categories = [opt.strip() for opt in new_categories.split(",")]

    def reset_keywords(self) -> None:
        """Reset split keywords list to an empty list."""
        self.state.split_keywords = []

    def change_keywords(self) -> None:
        """Change keywords if the user provides new keywords."""
        new_keywords = getattr(self.state, "_keywords", None)
        self.state.keywords = new_keywords or ""
        if new_keywords:
            self.state.split_keywords = [opt.strip() for opt in new_keywords.split(",")]
        else:
            self.state.split_keywords = []

    def keyword_move_files(self) -> None:
        """Move files based on keywords."""
        self.state._keywords = ""
        if self.state.split_keywords:
            self.make_folders_move_files(use_keywords=True)
            self.state.split_keywords = []
            self.reset_imgs()

    def get_sep(self) -> None:
        """Get separator if provided by user."""
        self.state.sep = getattr(self.state, "_sep", self.state.sep)

    def set_ui_values(self) -> None:
        """Set the UI element values and change any display values needed."""
        self.n_annotated = len(self.state.annotations)
        self.remaining = len(self.state.files) - self.state.counter
        self.back_placeholder.button("BACK", on_click=self.change_img, args=(-1,))
        self.info_placeholder.info(
            f"Annotated: {self.n_annotated}, Remaining: {self.remaining}"
        )
        (
            self.move_col,
            self.clear_col,
            self.reset_col,
        ) = self.move_clear_buttons_placeholder.columns([2, 3, 2])
        (
            self.clamp_col,
            self.prompt_col,
            self.meta_col,
        ) = self.checkbox_placeholder.columns(3)
        self.move_col.button("Move Files", on_click=self.make_folders_move_files)
        self.clear_annotations = self.clear_col.button("Reset Annotations?")
        self.state.clamp_state = self.clamp_col.checkbox("Clamp Height", value=True)
        self.state.show_prompt = self.prompt_col.checkbox("Show Prompt", value=False)
        self.state.show_meta = self.meta_col.checkbox("Metadata", value=False)
        container = self.expander_placeholder.expander(
            "Expand for more options", expanded=self.state.is_expanded
        )
        with container:
            self.state.is_expanded = True
            st.text_input(
                "full directory path to image files",
                value=self.image_dir,
                key="_img_dir",
                on_change=self.change_dir,
            )
            show_categories = self.state.categories
            if isinstance(show_categories, list):
                show_categories = ", ".join(show_categories)
            st.text_input(
                "annotation button names (comma separated)",
                value=self.categories,
                key="_categories",
                on_change=self.update_categories,
            )
            self.button_cols = self.options_buttons_placeholder.columns(
                len(self.state.split_categories)
            )
            subcol1, subcol2, subcol3 = st.columns(3)
            self.keyword_filter = subcol1.checkbox(
                "Keyword Filter",
                on_change=self.reset_keywords,
                help="If checked, results will be filtered \
                        to only ones that contain keywords provided.",
            )
            self.state.keyword_and_or = subcol2.checkbox(
                "AND",
                help="If checked, results must have \
                        ALL comma separated phrases. If unchecked, \
                        results can have ANY comma separated phrase.",
            )
            self.add_hide_button = subcol3.checkbox(
                "Hide Image Button",
                help="If checked, a button called 'CLEAR' will be added \
                    next to the 'Reset Annotations?' button. When pressed, \
                    images will not be displayed.",
            )
            if self.keyword_filter:
                keycol1, keycol2 = st.columns([1, 8])
                keycol1.text_input("sep", key="_sep", on_change=self.get_sep)
                keycol2.text_input(
                    "Keywords (comma separated)",
                    key="_keywords",
                    on_change=self.change_keywords,
                )
                self.key1, self.key2 = st.columns(2)
                self.keyword_move = self.key1.checkbox("Keyword Move Button")
                if self.keyword_move:
                    st.warning(
                        "Clicking this will move any files with matching keywords \
                        to folders in order of keyword!"
                    )
                    self.key2.button("Keyword MOVE", on_click=self.keyword_move_files)
        if self.clear_annotations:
            if self.state.files and self.state.json_path:
                save_json({}, self.state.json_path)
            self.reset_imgs()
        if self.add_hide_button:
            self.reset_col.button("CLEAR", on_click=self.change_hide_state)
        if self.state.counter < len(self.state.files):
            if self.state.hide_state == 0:
                self.file_path = os.path.join(
                    self.state.img_dir, self.state.current_file
                )
                prompts, meta_data = get_metadata_str(self.file_path)
                if self.state.show_prompt:
                    self.prompt_info.markdown(prompts, unsafe_allow_html=True)
                if self.state.show_meta:
                    self.meta_info.markdown(meta_data, unsafe_allow_html=True)
                image = load_image(
                    self.file_path, self.img_height_clamp, self.state.clamp_state
                )
                st.image(image, use_container_width=False)
                st.write(self.state.current_file)
                json_dict = {
                    "directory": self.state.img_dir,
                    "files": self.state.annotations,
                }
                for idx, option in enumerate(self.state.split_categories):
                    self.button_cols[idx].button(
                        f"{option}",
                        on_click=self.annotate,
                        args=(option, json_dict, self.state.json_path),
                    )
            else:
                for idx, option in enumerate(self.state.split_categories):
                    self.button_cols[idx].button(f"{option}")

        else:
            self.options_buttons_placeholder.info("Everything is annotated.")

    def run(self) -> None:
        """Method that keeps track of the order of methods called."""
        self.get_config_data()
        self.set_state_dict()
        self.set_ui()
        self.set_dir()
        self.set_ui_values()


if __name__ == "__main__":
    annotator = Annotator("config.yml")
    annotator.run()
