@echo off
set REPO=https://github.com/rasbot/streamlit_image_annotator
set APP=src/viewer.py

echo Pulling in latest changes from %REPO%...
git pull %REPO%
pause

echo Launching streamlit app...
uv run streamlit run %APP%
pause
