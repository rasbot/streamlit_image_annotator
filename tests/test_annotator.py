"""Tests for src/annotator.py — Annotator class methods."""

from __future__ import annotations

import sys
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Patch streamlit and utils module-level side-effects before importing
# ---------------------------------------------------------------------------

_mock_st = MagicMock()
_mock_conf = MagicMock()
_mock_conf.filter_files = "png, jpg"

sys.modules.setdefault("streamlit", _mock_st)

# Patch os.path.isfile and OmegaConf.load so utils' module-level config check
# doesn't raise, and streamlit is stubbed when annotator is imported.
with (
    patch("os.path.isfile", return_value=True),
    patch("omegaconf.OmegaConf.load", return_value=_mock_conf),
    patch.dict(sys.modules, {"streamlit": _mock_st}),
):
    import annotator as ann_mod

Annotator = ann_mod.Annotator


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_annotator_with_state(**state_kwargs):
    """Create an Annotator and attach a SimpleNamespace as its state."""
    defaults = dict(
        counter=0,
        hide_state=0,
        categories="keep, delete, fix, other",
        split_categories=["keep", "delete", "fix", "other"],
        keywords="",
        _keywords="",
        split_keywords=[],
        sep=" ",
        files=["a.png", "b.png", "c.png"],
        current_file="a.png",
        annotations={},
        img_dir="/some/dir",
        json_path="/some/dir/annotations.json",
        clamp_state=True,
        is_expanded=False,
        show_meta=False,
        show_prompt=False,
        move=False,
        keyword_and_or=False,
    )
    defaults.update(state_kwargs)
    a = Annotator()
    a.state = SimpleNamespace(**defaults)
    return a


# ---------------------------------------------------------------------------
# __init__
# ---------------------------------------------------------------------------


def test_init_defaults():
    a = Annotator()
    assert a.config_path == "config.yml"
    assert a.image_dir is None
    assert a.json_path is None
    assert a.categories is None
    assert a.img_height_clamp == 0
    assert a.clamp_image is False
    assert a.state is None


# ---------------------------------------------------------------------------
# get_config_data
# ---------------------------------------------------------------------------


def test_get_config_data_bad_extension():
    a = Annotator(config_path="config.json")
    with pytest.raises(ValueError, match="yml or yaml"):
        a.get_config_data()


def test_get_config_data_loads_values(tmp_config):
    """get_config_data should populate image_dir, json_path, categories, etc."""
    a = Annotator(config_path=str(tmp_config))
    # Patch OmegaConf.save so it doesn't write back
    with patch("annotator.OmegaConf.save"):
        a.get_config_data()
    assert a.categories == "keep, delete, fix, other"
    assert a.img_height_clamp == 896
    assert a.clamp_image is True


# ---------------------------------------------------------------------------
# change_img
# ---------------------------------------------------------------------------


def test_change_img_forward():
    a = _make_annotator_with_state(counter=0, files=["a.png", "b.png", "c.png"])
    a.change_img(1)
    assert a.state.counter == 1
    assert a.state.current_file == "b.png"


def test_change_img_lower_bound():
    """Counter should not go below 0."""
    a = _make_annotator_with_state(counter=0, files=["a.png", "b.png"])
    a.change_img(-1)
    assert a.state.counter == 0


# ---------------------------------------------------------------------------
# change_hide_state
# ---------------------------------------------------------------------------


def test_change_hide_state_toggle():
    a = _make_annotator_with_state(hide_state=0)
    a.change_hide_state()
    assert a.state.hide_state == 1
    a.change_hide_state()
    assert a.state.hide_state == 0


# ---------------------------------------------------------------------------
# update_categories
# ---------------------------------------------------------------------------


def test_update_categories():
    a = _make_annotator_with_state(categories="keep, delete")
    a.state._categories = "good, bad, ugly"
    a.update_categories()
    assert a.state.categories == "good, bad, ugly"
    assert a.state.split_categories == ["good", "bad", "ugly"]


# ---------------------------------------------------------------------------
# change_keywords
# ---------------------------------------------------------------------------


def test_change_keywords_non_empty():
    a = _make_annotator_with_state(keywords="")
    a.state._keywords = "cat, dog"
    a.change_keywords()
    assert a.state.split_keywords == ["cat", "dog"]


def test_change_keywords_empty():
    a = _make_annotator_with_state(keywords="cat")
    a.state._keywords = ""
    a.change_keywords()
    assert a.state.split_keywords == []


# ---------------------------------------------------------------------------
# reset_keywords
# ---------------------------------------------------------------------------


def test_reset_keywords():
    a = _make_annotator_with_state(split_keywords=["cat", "dog"])
    a.reset_keywords()
    assert a.state.split_keywords == []


# ---------------------------------------------------------------------------
# set_current_file
# ---------------------------------------------------------------------------


def test_set_current_file_within_bounds():
    """set_current_file should update current_file when counter < len(files)."""
    a = _make_annotator_with_state(counter=1, files=["a.png", "b.png", "c.png"])
    a.set_current_file()
    assert a.state.current_file == "b.png"


def test_set_current_file_at_boundary():
    """set_current_file should not update current_file when counter >= len(files)."""
    a = _make_annotator_with_state(
        counter=3, files=["a.png", "b.png", "c.png"], current_file="a.png"
    )
    a.set_current_file()
    assert a.state.current_file == "a.png"  # unchanged


# ---------------------------------------------------------------------------
# get_keyword_file_dict
# ---------------------------------------------------------------------------


def test_get_keyword_file_dict_builds_mapping(tmp_path):
    """get_keyword_file_dict should map each keyword to matching filenames."""
    for name in ["cat sitting.png", "dog running.png", "cat sleeping.png"]:
        (tmp_path / name).write_text("")
    a = _make_annotator_with_state(
        img_dir=str(tmp_path),
        split_keywords=["cat", "dog"],
        sep=" ",
    )
    a.img_file_names = ["cat sitting.png", "dog running.png", "cat sleeping.png"]
    a.get_keyword_file_dict()
    assert sorted(a.keyword_dict["cat"]) == ["cat sitting.png", "cat sleeping.png"]
    assert a.keyword_dict["dog"] == ["dog running.png"]


# ---------------------------------------------------------------------------
# change_dir
# ---------------------------------------------------------------------------


def test_change_dir_with_valid_dir(tmp_path):
    """change_dir should update img_dir and call reset_imgs for a valid path."""
    a = _make_annotator_with_state(img_dir="/old/dir")
    a.state._img_dir = str(tmp_path)
    a.info_placeholder = MagicMock()
    a.change_dir()
    assert a.state.img_dir == str(tmp_path)


def test_change_dir_guard_missing_key():
    """change_dir should show an error and not update img_dir if _img_dir absent."""
    a = _make_annotator_with_state(img_dir="/old/dir")
    # _img_dir is intentionally NOT set on state
    a.change_dir()
    assert a.state.img_dir == "/old/dir"  # unchanged


# ---------------------------------------------------------------------------
# annotate
# ---------------------------------------------------------------------------


def test_annotate_sets_label_and_advances(tmp_path):
    """annotate should record the label, advance the counter, and write JSON."""
    json_path = str(tmp_path / "annotations.json")
    a = _make_annotator_with_state(
        files=["a.png", "b.png", "c.png"],
        current_file="a.png",
        counter=0,
        annotations={},
    )
    results_d: dict = {"directory": str(tmp_path), "files": {}}
    a.annotate("keep", results_d, json_path)
    assert a.state.annotations["a.png"] == "keep"
    assert a.state.counter == 1
    assert (tmp_path / "annotations.json").exists()


# ---------------------------------------------------------------------------
# get_imgs — keyword filtering
# ---------------------------------------------------------------------------


def test_get_imgs_no_keywords_returns_all(tmp_path):
    """With no keywords, get_imgs returns all image files sorted."""
    (tmp_path / "b.png").write_text("")
    (tmp_path / "a.png").write_text("")
    (tmp_path / "c.txt").write_text("")
    a = _make_annotator_with_state(img_dir=str(tmp_path), split_keywords=[])
    result = a.get_imgs()
    assert result == ["a.png", "b.png"]


def test_get_imgs_or_mode_matches_any_keyword(tmp_path):
    """In OR mode (keyword_and_or=False), a file matching any keyword is included."""
    for name in ["cat sitting.png", "dog running.png", "bird flying.png"]:
        (tmp_path / name).write_text("")
    a = _make_annotator_with_state(
        img_dir=str(tmp_path),
        split_keywords=["cat", "dog"],
        keyword_and_or=False,
        sep=" ",
    )
    result = a.get_imgs()
    assert "cat sitting.png" in result
    assert "dog running.png" in result
    assert "bird flying.png" not in result


def test_get_imgs_and_mode_requires_all_keywords(tmp_path):
    """In AND mode (keyword_and_or=True), a file must match every keyword."""
    for name in ["big cat.png", "small cat.png", "big dog.png"]:
        (tmp_path / name).write_text("")
    a = _make_annotator_with_state(
        img_dir=str(tmp_path),
        split_keywords=["big", "cat"],
        keyword_and_or=True,
        sep=" ",
    )
    result = a.get_imgs()
    assert "big cat.png" in result
    assert "small cat.png" not in result
    assert "big dog.png" not in result
