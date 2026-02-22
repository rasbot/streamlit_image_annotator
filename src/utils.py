"""Helper functions for main scripts"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from omegaconf import OmegaConf
from PIL import Image

__all__ = [
    "FILTER_EXT_LIST",
    "filter_by_keyword",
    "get_filtered_files",
    "get_metadata_str",
    "load_image",
    "load_json",
    "save_json",
    "update_json",
]

# C-1: Resolve relative to this file so the check is independent of the
# process working directory.
_CONFIG_PATH = Path(__file__).parent.parent / "config.yml"
if not os.path.isfile(_CONFIG_PATH):
    raise FileNotFoundError(
        f"config.yml not found at {_CONFIG_PATH}. "
        "Please run `set_config.bat` to create it."
    )
conf = OmegaConf.load(_CONFIG_PATH)
FILTER_EXT_LIST = ["." + filt.strip() for filt in conf.filter_files.split(",")]


def concat_arr(arr: list[str]) -> list[str]:
    """Concat elements in a list. For an element with
    a colon, concat all elements after that do not have a
    colon. This is used for getting the meta_dict.

    Args:
        arr (list[str]): List of strings for metadata.

    Returns:
        list[str]: Concatenated list of strings for metadata.
    """
    result = []
    current_string = ""
    for row in arr:
        if ":" in row:
            if current_string:
                result[-1] += current_string
                current_string = ""
            result.append(row)
        else:
            current_string += row
    if current_string and result:
        result[-1] += current_string

    return result


def get_metadata_dict(image_path: str) -> dict[str, Any]:
    """Get a dictionary of metadata from an image.
    This will only apply to images generated with Stable
    Diffusion using Automatic1111's webui repo.

    Args:
        image_path (str): Path to image file.

    Returns:
        dict[str, Any]: Dict with metadata info. Values may be ``str``,
            ``bytes``, ``int``, or other PIL info types when the image has
            no Stable Diffusion parameters.
    """
    with Image.open(image_path) as img_file:
        metadata = img_file.info
    if "parameters" not in metadata:
        return metadata
    metadata_str = "Prompt: " + metadata["parameters"]
    split_meta = metadata_str.split("\n")
    if len(split_meta) > 2:
        # list length should be = 2 so concat all elements before the last one
        split_meta = ["".join(split_meta[:-1]), split_meta[-1]]
    sub_split = split_meta[-1].split(", ")
    split_meta = split_meta[:-1]
    split_meta.extend(sub_split)
    split_meta = concat_arr(split_meta)
    meta_d = {}
    for row in split_meta:
        parts = row.rsplit(": ", 1)
        if len(parts) == 2:
            meta_d[parts[0]] = parts[1]
    return meta_d


def get_metadata_str(image_path: str) -> tuple[str, str]:
    """Get a metadata dict from an image path and
    create a string with markdown code to display in the
    main app.

    Args:
        image_path (str): Path to image file.

    Returns:
        tuple[str, str]: String of prompt data and string
            of metadata.
    """
    if Path(image_path).suffix.lower() != ".png":
        return "", ""
    meta_dict = get_metadata_dict(image_path)
    prompts = ""
    meta_data = ""
    for meta_key, meta_val in meta_dict.items():
        if meta_key in ("Prompt", "Negative prompt"):
            prompts += (
                f"{meta_key} : <span style='color:darkorange'>{meta_val}</span>\n"
            )
        else:
            meta_data += (
                f"{meta_key} : <span style='color:darkorange'>{meta_val}</span>\n"
            )
    return prompts, meta_data


def filter_by_keyword(
    str_list: list[str], keyword: str, sep_: str = " "
) -> tuple[list[str], list[str]]:
    """Filter a list of strings to ones that contain a keyword phrase.
    This can be multiple words.

    Args:
        str_list (list[str]): List of strings to filter.
        keyword (str): Keyword(s) to filter file names to.
        sep_ (str, optional): Separator that will be used to split
            the file names. Defaults to " ".

    Returns:
        tuple[list[str], list[str]]: List of filtered file names not
            containing the keyword(s) and a list of file names that do
            contain the keyword(s).
    """
    if not sep_:
        sep_ = " "
    str_list_ = str_list.copy()
    filtered = []
    for file in str_list:
        no_ext = file.rsplit(".", 1)[0]
        char_filter = "-_',()!?:"
        char_filter = char_filter.replace(sep_, "")
        for char in char_filter:
            no_ext = no_ext.replace(char, "")
        split_file = no_ext.split(sep_)
        split_keyword = keyword.split(sep_) if sep_ in keyword else [keyword]
        n_key = len(split_keyword)
        first_idxs = [
            idx for idx, val in enumerate(split_file) if val == split_keyword[0]
        ]
        if first_idxs:
            for idx in first_idxs:
                if (
                    split_file[idx : idx + n_key] == split_keyword
                    and file not in filtered
                ):
                    filtered.append(file)
                    str_list_.remove(file)
    return str_list_, filtered


def save_json(json_dict: dict[str, Any], json_path: str | Path) -> None:
    """Save a dictionary to a json file.

    Args:
        json_dict (dict[str, Any]): Dictionary to serialise.
        json_path (str | Path): File path for json file.
    """
    json_object = json.dumps(json_dict, indent=4)
    with open(json_path, "w", encoding="utf-8") as outfile:
        outfile.write(json_object)


def load_json(json_path: str | Path) -> dict[str, Any]:
    """Load a json file and return a dictionary.

    Args:
        json_path (str | Path): Full path to the json file.

    Returns:
        dict[str, Any]: Dictionary of json data.

    Raises:
        FileNotFoundError: If the file does not exist at ``json_path``.
    """
    if not Path(json_path).exists():
        raise FileNotFoundError(f"JSON file not found: {json_path}")
    with open(json_path, encoding="utf-8") as infile:
        json_dict = json.load(infile)
    return json_dict


def update_json(json_dict: dict[str, Any], json_path: str | Path) -> None:
    """Update a json file by loading it into a dict, updating
    the dict, and saving the dict as a json file.

    Args:
        json_dict (dict[str, Any]): Dictionary to merge in.
        json_path (str | Path): Path of the json file.
    """
    if Path(json_path).exists():
        with open(json_path, encoding="utf-8") as infile:
            data = json.load(infile)
    else:
        data = {}
    data.update(json_dict)
    save_json(data, json_path)


def get_filtered_files(file_dir: str, ext_list: list[str] | None = None) -> list[str]:
    """Get files in directory and return a list of files that
    have file extensions provided in ``ext_list``.

    Args:
        file_dir (str): File directory with files to filter.
        ext_list (list[str] | None): List of valid file extensions.
            Defaults to ``FILTER_EXT_LIST`` from config when ``None``.

    Returns:
        list[str]: Filtered list of files with valid extensions.
    """
    if ext_list is None:
        ext_list = FILTER_EXT_LIST
    try:
        files = os.listdir(file_dir)
        return [file for file in files if Path(file).suffix in ext_list]
    except OSError:
        return []


def load_image(
    image_path: str, height: int = 896, is_clamped: bool = True
) -> Image.Image:
    """Load an image. If `is_clamped` is True, clamp the image height.
    This makes it so larger images can be shown in the browser.
    The `height` parameter will be used to clamp the height of the
    image and the width will change proportionally.

    Args:
        image_path (str): Path to the image to load.
        height (int, optional): Height of the image if clamped.
            Defaults to 896.
        is_clamped (bool, optional): True if the image will be clamped,
            False will return the full image size. Defaults to True.

    Returns:
        Image: PIL Image that is either full resolution or clamped.
    """
    with Image.open(image_path) as img:
        if not is_clamped:
            return img.copy()
        aspect_ratio = img.width / img.height
        if img.height > height:
            width = int(height * aspect_ratio)
        else:
            height = img.height
            width = img.width
        return img.resize((width, height))
