"""Tests for src/viewer.py — _get_default_dir function."""

from __future__ import annotations

import os
import sys
from unittest.mock import MagicMock, patch

# ---------------------------------------------------------------------------
# We only test _get_default_dir, which is a pure helper.
# Import it by patching away streamlit and the module-level session-state
# code so we avoid running all the top-level Streamlit calls.
# ---------------------------------------------------------------------------


def _make_columns(n):
    """Return n MagicMock objects so tuple unpacking works."""
    size = n if isinstance(n, int) else len(n)
    return [MagicMock() for _ in range(size)]


def _import_get_default_dir():
    """Import _get_default_dir without executing Streamlit top-level code."""
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

            return viewer._get_default_dir


_get_default_dir = _import_get_default_dir()


# ---------------------------------------------------------------------------
# Tests
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
