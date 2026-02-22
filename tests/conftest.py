"""Shared pytest fixtures."""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from PIL import Image


@pytest.fixture()
def tmp_config(tmp_path):
    """Write a minimal config.yml to a temp directory and return its path."""
    config_content = """\
default_directory: ""
json_path: ""
default_categories: "keep, delete, fix, other"
filter_files: "png, jpg"
image_height_clamp: 896
clamp_image: true
"""
    config_path = tmp_path / "config.yml"
    config_path.write_text(config_content)
    return config_path


@pytest.fixture()
def tmp_image(tmp_path):
    """Create a small valid PNG image and return its path."""
    img_path = tmp_path / "test_image.png"
    img = Image.new("RGB", (100, 200), color=(128, 64, 32))
    img.save(str(img_path))
    return img_path


@pytest.fixture()
def mock_state():
    """A SimpleNamespace that stands in for st.session_state."""
    return SimpleNamespace(
        counter=0,
        hide_state=0,
        categories="keep, delete, fix, other",
        split_categories=["keep", "delete", "fix", "other"],
        keywords="",
        split_keywords=[],
        sep=" ",
        files=[],
        annotations={},
        img_dir="",
        json_path="",
        clamp_state=True,
        is_expanded=False,
        show_meta=False,
        show_prompt=False,
        move=False,
        keyword_and_or=False,
    )
