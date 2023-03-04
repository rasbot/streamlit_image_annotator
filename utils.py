import json
import os
from typing import List, Dict, Tuple

from omegaconf import OmegaConf
from PIL import Image

conf = OmegaConf.load("config.yml")
FILTER_EXT_LIST = [filt.strip() for filt in conf.filter_files.split(",")]


def concat_arr(arr: List[str]) -> List[str]:
    """Concat elements in a list. For an element with
    a colon, concat all elements after that do not have a
    colon. This is used for getting the meta_dict.

    Args:
        arr (List[str]): List of strings for metadata.

    Returns:
        List[str]: Concatenated list of strings for metadata.
    """
    result = []
    current_string = ''
    for i, s in enumerate(arr):
        if ':' in s:
            if current_string:
                result[-1] += current_string
                current_string = ''
            result.append(s)
        else:
            current_string += s
    if current_string:
        result[-1] += current_string

    return result


def get_metadata_dict(image_path: str) -> Dict[str, str]:
    """Get a dictionary of metadata from an image.
    This will only apply to images generated with Stable
    Diffusion using Automatic1111's webui repo.

    Args:
        image_path (str): Path to image file.

    Returns:
        Dict[str, str]: Dict with metadata info.
    """
    with Image.open(image_path) as img_file:
        metadata = img_file.info
    metadata_str = 'Prompt: ' + metadata["parameters"]
    split_meta = metadata_str.split("\n")
    sub_split = split_meta[-1].split(", ")
    split_meta = split_meta[:-1]
    split_meta.extend(sub_split)
    split_meta = concat_arr(split_meta)
    meta_d = {}
    for row in split_meta:
        key, val = row.rsplit(": ", 1)
        meta_d[key] = val
    return meta_d


def get_metadata_str(image_path: str) -> Tuple[str, str]:
    """Get a metadata dict from an image path and
    create a string with markdown code to display in the
    main app.

    Args:
        image_path (str): Path to image file.

    Returns:
        Tuple[str, str]: String of prompt data and string
            of metadata.
    """
    meta_dict = get_metadata_dict(image_path)
    prompts = ""
    meta_data = ""
    for k,v in meta_dict.items():
        if k in ("Prompt", "Negative prompt"):
            prompts += f"{k} : <span style='color:darkorange'>{v}</span>\n"
        else:
            meta_data += f"{k} : <span style='color:darkorange'>{v}</span>\n"
    return prompts, meta_data


def save_json(json_dict: dict, json_path: str) -> None:
    """Save a dictionary to a json file.

    Args:
        json_dict (dict): Dictionary.
        json_path (str): File path for json file.
    """
    json_object = json.dumps(json_dict, indent=4)
    with open(json_path, "w") as outfile:
        outfile.write(json_object)


def load_json(json_path: str) -> dict:
    """Load a json file and return a dictionary.

    Args:
        json_path (str): Full path to the json file.

    Returns:
        dict: Dictionary of json data.
    """
    assert os.path.exists(json_path), "Json path invalid, file not found!"
    with open(json_path, "r") as infile:
        json_dict = json.load(infile)
    return json_dict


def update_json(json_dict: dict, json_path: str) -> None:
    """Update a json file by loading it into a dict, updating
    the dict, and saving the dict as a json file.

    Args:
        json_dict (dict): Dictionary to update.
        json_path (str): Path of the json file.
    """
    if os.path.exists(json_path):
        with open(json_path, "r") as infile:
            data = json.load(infile)
    else:
        data = {}
    data.update(json_dict)
    save_json(data, json_path)


def get_filtered_files(
    file_dir: str, ext_list: List[str] = FILTER_EXT_LIST
) -> List[str]:
    """Get files in directory and return a list of files that
    have file extensions provided in `ext_list`.

    Args:
        file_dir (str): File directory with files to filter.
        ext_list (List[str], optional): List of valid file extensions.

    Returns:
        List[str]: Filtered list of files with valid extensions.
    """
    try:
        files = os.listdir(file_dir)
        return [file for file in files if file.rsplit(".", 1)[-1] in ext_list]
    except:
        return None


def load_image(image_path: str, height: int = 896, is_clamped: bool = True) -> Image:
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
    img = Image.open(image_path)
    if not is_clamped:
        return img
    aspect_ratio = img.width / img.height
    if img.height > height:
        width = int(height * aspect_ratio)
    else:
        height = img.height
        width = img.width
    resized_image = img.resize((width, height))
    return resized_image
