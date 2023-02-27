import os
import shutil
from typing import Dict, List

import streamlit as st
from omegaconf import OmegaConf

from utils import (get_filtered_files, load_image, load_json, save_json,
                   update_json)

class Annotator:
    def __init__(self, config_path: str="config.yml"):
        self.config_path = config_path

    def get_config_data(self):
        update_config = False
        assert self.config_path.rsplit(".", 1)[-1] in ("yml", "yaml"), "Config file must be a yml or yaml file."
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
        self.IMAGE_DIR = conf.default_directory
        self.JSON_PATH = conf.json_path
        self.CATEGORIES = conf.default_categories
        self.IMG_HEIGHT_CLAMP = int(conf.image_height_clamp)
        self.CLAMP_IMAGE = conf.clamp_image

    def set_state_dict(self):

        self.state = st.session_state

        if "img_dir" not in self.state:
            self.state.img_dir = self.IMAGE_DIR
        if "update_dir" not in self.state:
            self.state.update_dir = ""
        if "json_path" not in self.state:
            self.state.json_path = self.JSON_PATH
        if "categories" not in self.state:
            self.state.categories = self.CATEGORIES
        if "update_categories" not in self.state:
            self.state.update_categories = ""
        if "clamp_state" not in self.state:
            self.state.clamp_state = self.CLAMP_IMAGE
        if "counter" not in self.state:
            self.state.counter = 0
        if "hide_state" not in self.state:
            self.state.hide_state = 0
        if "annotations" not in self.state:
            self.state.annotations = {}
        if "files" not in self.state:
            self.state.files = []

    def set_ui(self):
        st.sidebar.title("Image Annotator")
        # set up order of sidebar UI elements
        self.back_placeholder = st.sidebar.empty()
        self.info_placeholder = st.sidebar.empty()
        self.options_buttons_placeholder = st.sidebar.empty()
        st.sidebar.markdown("---")
        self.move_clear_buttons_placeholder = st.sidebar.empty()
        st.sidebar.markdown("---")
        self.move_placeholder = st.sidebar.empty()
        self.expander_placeholder = st.sidebar.empty()

    def set_dir(self):
        if not os.path.isdir(self.state.img_dir):
            st.error(f"{self.state.img_dir} is not a valid directory!")
        else:
            self.state.files = self.get_imgs()
        if self.state.files and self.state.counter < len(self.state.files):
            self.state.current_file = self.state.files[self.state.counter]
        else:
            st.write("No image files in folder. Nothing to annotate.")

    def set_current_file(self):
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

    def change_hide_state(self):
        """Flips the state of state.hide_state. If 0 -> 1,
        if 1 -> 0.
        """
        self.state.hide_state = 1 - self.state.hide_state

    def annotate(self, label: str, results_d: Dict[str, Dict[str, str]], json_path: str) -> None:
        """Set annotation for the current file, change the image, and update the
        json file.

        results_d will have a 'directory' key with a value containing the directory path
        of the image folder, and a 'files' key with a dictionary of file_name/annotation pairs.

        Args:
            label (str): Annotation label to assign to img file.
            results_d (Dict[str, Dict[str, str]): Dictionary of annotations.
            json_path (str): Path to json file.
        """
        self.state.annotations[self.state.current_file] = label
        self.change_img(1)
        update_json(results_d, json_path)


    def make_folders_move_files(self) -> None:
        """Make folders for each unique annotation. Filter state dict
        and move annotated files to their respective folders.
        Remove files from json and delete the json file if it is empty.
        """
        if os.path.exists(self.state.json_path):
            json_d = load_json(self.state.json_path)
        else:
            return
        annotation_set = set(json_d["files"].values())
        img_file_names = get_filtered_files(self.state.img_dir)
        for annotation in annotation_set:
            n_files = 0
            remove_files = []
            os.makedirs(os.path.join(self.state.img_dir, annotation), exist_ok=True)
            filtered_files = [
                file for (file, label) in json_d["files"].items() if annotation == label
            ]
            for file in filtered_files:
                if file in img_file_names:
                    n_files += 1
                    remove_files.append(file)
                    img_file_path = os.path.join(self.state.img_dir, file)
                    file_dest = os.path.join(self.state.img_dir, annotation, file)
                    shutil.move(img_file_path, file_dest)
            self.move_placeholder.write(f"moving {n_files} to {annotation}...")
            for file in remove_files:
                self.state.annotations.pop(file, None)
                json_d["files"].pop(file, None)
        if len(json_d["files"]) > 0:
            save_json(json_d, self.state.json_path)
        else:
            os.remove(self.state.json_path)
        self.state.counter = 0

    def get_imgs(self) -> List[str]:
        """Get a sorted list of image paths. Images
        are filtered to png and jpg (specified in config.yml)
        and sorted. If the image directory is not a
        valid directory, return None.

        Args:
            image_dir (str): Directory with images to annotate.

        Returns:
            List[str]: List of sorted image paths.
        """
        img_file_names = get_filtered_files(self.state.img_dir)
        if img_file_names:
            img_file_names.sort()
        return img_file_names


    def reset_imgs(self) -> None:
        """Reset variables when a directory is changed.
        """
        img_file_names = self.get_imgs()
        if img_file_names is None:
            return
        self.state.counter = 0
        self.state.annotations = {}
        self.state.files = img_file_names
        if self.state.files:
            self.state.current_file = self.state.files[self.state.counter]
        else:
            st.write("No image files in folder. Nothing to annotate.")
        self.remaining = len(self.state.files)
        self.n_annotated = 0
        self.info_placeholder.info(f"Annotated: {self.n_annotated}, Remaining: {self.remaining}")

    def change_dir(self):
        if not os.path.isdir(self.state.update_dir):
            st.error("Not a valid directory...Please enter another one.")
        else:
            self.state.img_dir = self.state.update_dir
            self.reset_imgs()

    def update_categories(self):
        self.state.categories = self.state.update_categories

    def set_ui_values(self):
        self.n_annotated = len(self.state.annotations)
        self.remaining = len(self.state.files) - self.state.counter
        self.back_placeholder.button("BACK", on_click=self.change_img, args=(-1,))
        self.info_placeholder.info(f"Annotated: {self.n_annotated}, Remaining: {self.remaining}")
        self.move_col, self.clamp_col, self.reset_col = self.move_clear_buttons_placeholder.columns(3)
        self.move_col.button("Move Files", on_click=self.make_folders_move_files)
        self.state.clamp_state = self.clamp_col.checkbox("Clamp Height", value=True)
        with self.expander_placeholder.expander("Expand for more options"):
            st.text_input(
                "full directory path to image files", key="update_dir", placeholder=self.state.img_dir, on_change=self.change_dir
            )
            show_categories = self.state.categories
            if type(show_categories) == list:
                show_categories = ", ".join(show_categories)
            st.text_input(
                "annotation button names (comma separated)", key="update_categories", placeholder=show_categories, on_change=self.update_categories
            )
            if type(self.state.categories) == str:
                self.state.categories = [opt.strip() for opt in self.state.categories.split(",")]
            self.button_cols = self.options_buttons_placeholder.columns(len(self.state.categories))
            self.c1, self.c2 = st.columns(2)
            self.clear_annotations = self.c1.button("Reset Annotations?")
            self.add_hide_button = self.c2.checkbox("Hide Image Button")
        if self.clear_annotations:
            if self.state.files:
                save_json({}, self.state.json_path)
                self.remaining = len(self.state.files)
            else:
                self.remaining = 0
            self.state.annotations = {}
            self.n_annotated = 0
            self.state.counter = 0
            self.info_placeholder.info(f"Annotated: {self.n_annotated}, Remaining: {self.remaining}")

        if self.add_hide_button:
            self.reset_col.button("CLEAR", on_click=self.change_hide_state)
        if self.state.counter < len(self.state.files):
            if self.state.hide_state == 0:
                selected_file = self.state.current_file
                file_path = os.path.join(self.state.img_dir, selected_file)
                image = load_image(file_path, self.IMG_HEIGHT_CLAMP, self.state.clamp_state)
                st.image(image, use_column_width="never")
                st.write(selected_file)
                json_dict = {"directory": self.state.img_dir, "files": self.state.annotations}
                for idx, option in enumerate(self.state.categories):
                    self.button_cols[idx].button(
                        f"{option}", on_click=self.annotate, args=(option, json_dict, self.state.json_path)
                    )
            else:
                for idx, option in enumerate(self.state.categories):
                    self.button_cols[idx].button(f"{option}")

        else:
            self.options_buttons_placeholder.info("Everything is annotated.")


    def run(self):
        self.get_config_data()
        self.set_state_dict()
        self.set_ui()
        self.set_dir()
        self.set_ui_values()

if __name__ == '__main__':
    annotator = Annotator("config.yml")
    annotator.run()
