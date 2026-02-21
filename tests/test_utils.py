"""Tests for src/utils.py"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from PIL import Image

# ---------------------------------------------------------------------------
# Patch out the module-level config.yml check before importing utils
# ---------------------------------------------------------------------------
_mock_conf = MagicMock()
_mock_conf.filter_files = "png, jpg"

with (
    patch("os.path.isfile", return_value=True),
    patch("omegaconf.OmegaConf.load", return_value=_mock_conf),
):
    import utils  # noqa: E402  (src/ is on sys.path via pyproject.toml pythonpath)


# ---------------------------------------------------------------------------
# concat_arr
# ---------------------------------------------------------------------------


def test_concat_arr_basic():
    arr = ["Prompt: a dog", " running fast", "Steps: 20"]
    result = utils.concat_arr(arr)
    assert result == ["Prompt: a dog running fast", "Steps: 20"]


def test_concat_arr_empty():
    assert utils.concat_arr([]) == []


def test_concat_arr_no_colons():
    arr = ["hello", "world"]
    # No element has a colon, so result stays empty (nothing to anchor to)
    result = utils.concat_arr(arr)
    assert result == []


# ---------------------------------------------------------------------------
# filter_by_keyword
# ---------------------------------------------------------------------------


def test_filter_by_keyword_single_match():
    files = ["cat sitting.png", "dog running.png", "cat sleeping.png"]
    remaining, matched = utils.filter_by_keyword(files, "cat")
    assert matched == ["cat sitting.png", "cat sleeping.png"]
    assert "dog running.png" in remaining
    assert "cat sitting.png" not in remaining


def test_filter_by_keyword_no_match():
    files = ["dog running.png", "bird flying.png"]
    remaining, matched = utils.filter_by_keyword(files, "cat")
    assert matched == []
    assert remaining == files


def test_filter_by_keyword_multi_word():
    files = ["a big cat.png", "small cat.png", "a big dog.png"]
    remaining, matched = utils.filter_by_keyword(files, "big cat")
    assert "a big cat.png" in matched
    assert "small cat.png" not in matched
    assert "a big dog.png" not in matched


def test_filter_by_keyword_empty_list():
    remaining, matched = utils.filter_by_keyword([], "cat")
    assert remaining == []
    assert matched == []


def test_filter_by_keyword_special_chars():
    # When sep is '-', hyphens split words and other special chars are stripped.
    # With default sep=' ', hyphens are removed entirely (no split), so
    # "cat-sitting" -> "catsitting" which does NOT match "sitting".
    # With sep='-', "cat-sitting" -> ["cat", "sitting"] which DOES match.
    files = ["cat-sitting.png", "dog-running.png"]
    remaining, matched = utils.filter_by_keyword(files, "sitting", sep_="-")
    assert "cat-sitting.png" in matched
    assert "dog-running.png" not in matched


# ---------------------------------------------------------------------------
# get_filtered_files
# ---------------------------------------------------------------------------


def test_get_filtered_files_valid_dir(tmp_path):
    (tmp_path / "a.png").write_text("")
    (tmp_path / "b.jpg").write_text("")
    (tmp_path / "c.txt").write_text("")
    result = utils.get_filtered_files(str(tmp_path), [".png", ".jpg"])
    assert sorted(result) == ["a.png", "b.jpg"]


def test_get_filtered_files_invalid_dir():
    result = utils.get_filtered_files("/nonexistent/path/xyz", [".png"])
    assert result == []


def test_get_filtered_files_no_match(tmp_path):
    (tmp_path / "readme.txt").write_text("")
    result = utils.get_filtered_files(str(tmp_path), [".png", ".jpg"])
    assert result == []


# ---------------------------------------------------------------------------
# save_json / load_json roundtrip
# ---------------------------------------------------------------------------


def test_save_and_load_json_roundtrip(tmp_path):
    data = {"key": "value", "number": 42}
    json_path = str(tmp_path / "data.json")
    utils.save_json(data, json_path)
    loaded = utils.load_json(json_path)
    assert loaded == data


def test_load_json_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        utils.load_json(str(tmp_path / "missing.json"))


# ---------------------------------------------------------------------------
# update_json
# ---------------------------------------------------------------------------


def test_update_json_creates_new(tmp_path):
    json_path = str(tmp_path / "new.json")
    utils.update_json({"a": 1}, json_path)
    loaded = utils.load_json(json_path)
    assert loaded == {"a": 1}


def test_update_json_merges_existing(tmp_path):
    json_path = str(tmp_path / "existing.json")
    utils.save_json({"a": 1, "b": 2}, json_path)
    utils.update_json({"b": 99, "c": 3}, json_path)
    loaded = utils.load_json(json_path)
    assert loaded == {"a": 1, "b": 99, "c": 3}


# ---------------------------------------------------------------------------
# load_image
# ---------------------------------------------------------------------------


def test_load_image_clamped(tmp_image):
    """Image taller than clamp height should be resized."""
    img = utils.load_image(str(tmp_image), height=50, is_clamped=True)
    assert img.height == 50


def test_load_image_unclamped(tmp_image):
    """Unclamped load should return original dimensions (100x200)."""
    img = utils.load_image(str(tmp_image), is_clamped=False)
    assert img.size == (100, 200)


def test_load_image_no_clamp_needed(tmp_path):
    """When image height <= clamp height, dimensions are unchanged."""
    img_path = tmp_path / "small.png"
    Image.new("RGB", (50, 30)).save(str(img_path))
    img = utils.load_image(str(img_path), height=896, is_clamped=True)
    assert img.size == (50, 30)


# ---------------------------------------------------------------------------
# get_metadata_str
# ---------------------------------------------------------------------------


def test_get_metadata_str_non_png(tmp_path):
    """Non-PNG files should return empty strings without error."""
    jpg_path = tmp_path / "photo.jpg"
    jpg_path.write_bytes(b"")
    prompts, meta = utils.get_metadata_str(str(jpg_path))
    assert prompts == ""
    assert meta == ""
