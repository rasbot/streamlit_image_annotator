@echo off
set REPO=https://github.com/rasbot/streamlit_image_annotator
set APP=viewer.py

echo Pulling in latest changes from %REPO%...
git pull %REPO%
pause

echo Launching streamlit app...
streamlit run %APP%
pause