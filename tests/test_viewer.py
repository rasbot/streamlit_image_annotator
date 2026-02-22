"""Tests for src/viewer.py — _get_default_dir and show_image."""

from __future__ import annotations

import os
import sys
from unittest.mock import MagicMock, patch

# ---------------------------------------------------------------------------
# Import viewer functions by patching away Streamlit and module-level side
# effects so the top-level script code does not execute during import.
# ---------------------------------------------------------------------------


def _make_columns(n):
    """Return n MagicMock objects so tuple unpacking works."""
    size = n if isinstance(n, int) else len(n)
    return [MagicMock() for _ in range(size)]


def _import_viewer():
    """Import the viewer module without executing Streamlit top-level code."""
    mock_st = MagicMock()
    mock_st.session_state = MagicMock()
    # Make columns() return the correct number of values for tuple unpacking
    mock_st.sidebar.columns.side_effect = _make_columns
    mock_st.columns.side_effect = _make_columns

    # Patch streamlit in sys.modules so 'import streamlit' in viewer returns mock
    with patch.dict(sys.modules, {"streamlit": mock_st}):
        # Also stub utils' module-level config read
        mock_conf = MagicMock()
        mock_conf.filter_files = "png, jpg"
        with (
            patch("os.path.isfile", return_value=True),
            patch("omegaconf.OmegaConf.load", return_value=mock_conf),
        ):
            # Remove cached module if already imported
            sys.modules.pop("viewer", None)
            import viewer

            return viewer


_viewer = _import_viewer()
_get_default_dir = _viewer._get_default_dir


# ---------------------------------------------------------------------------
# _get_default_dir
# ---------------------------------------------------------------------------


def test_get_default_dir_valid_config(tmp_path):
    """Should return the directory from config when it exists."""
    mock_conf = MagicMock()
    mock_conf.default_directory = str(tmp_path)

    with (
        patch("os.path.isfile", return_value=True),
        patch("omegaconf.OmegaConf.load", return_value=mock_conf),
    ):
        result = _get_default_dir()

    assert result == str(tmp_path)


def test_get_default_dir_no_config():
    """When config.yml does not exist, should fall back to cwd."""
    with patch("os.path.isfile", return_value=False):
        result = _get_default_dir()

    assert result == os.getcwd()


def test_get_default_dir_invalid_path_in_config():
    """When config has a path that is not a real directory, fall back to cwd."""
    mock_conf = MagicMock()
    mock_conf.default_directory = "/nonexistent/path/xyz123"

    with (
        patch("os.path.isfile", return_value=True),
        patch("omegaconf.OmegaConf.load", return_value=mock_conf),
    ):
        result = _get_default_dir()

    assert result == os.getcwd()


# ---------------------------------------------------------------------------
# show_image
# ---------------------------------------------------------------------------


def test_show_image_does_nothing_when_current_file_is_none():
    """show_image should return early without rendering if current_file is None."""
    _viewer.state.current_file = None
    mock_container = MagicMock()
    mock_placeholder = MagicMock()

    _viewer.show_image(mock_container, mock_placeholder)

    mock_container.image.assert_not_called()


def test_show_image_renders_image(tmp_image):
    """show_image should call img_container.image when current_file is set."""
    _viewer.state.current_file = tmp_image.name
    _viewer.state.img_dir = str(tmp_image.parent)
    _viewer.state.height_clamp = 100
    _viewer.state.show_file_name = False

    mock_container = MagicMock()
    mock_placeholder = MagicMock()

    _viewer.show_image(mock_container, mock_placeholder)

    mock_container.image.assert_called_once()


def test_show_image_shows_filename_when_enabled(tmp_image):
    """show_image should call file_name_placeholder.info when show_file_name is True."""
    _viewer.state.current_file = tmp_image.name
    _viewer.state.img_dir = str(tmp_image.parent)
    _viewer.state.height_clamp = 100
    _viewer.state.show_file_name = True

    mock_container = MagicMock()
    mock_placeholder = MagicMock()

    _viewer.show_image(mock_container, mock_placeholder)

    mock_placeholder.info.assert_called_once_with(tmp_image.name)
