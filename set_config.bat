@echo off

REM Create config file with default values if it does not exist
set FILE=config.yml

if not exist %FILE% (
    echo Creating %FILE%...
    echo default_directory: >> %FILE%
    echo json_path: >> %FILE%
    echo default_categories: keep, delete, fix, other>> %FILE%
    echo clamp_image: true>> %FILE%
    echo image_height_clamp: 896>> %FILE%
    echo filter_files: png, jpg>> %FILE%
) else (
    echo %FILE% already exists. Skipping creation...
)

set /p default_directory=Please enter a default directory path: 
set /p default_categories=Set default category buttons. See the README for more info. Hit enter to use defaults "keep, delete, fix, other" or provide a comma separated list here: 
set "streamlit_config=%USERPROFILE%\.streamlit\credentials.toml"

REM Add do not track to streamlit credientials file
findstr /c:"[browser]" /c:"gatherUsageStats = false" "%streamlit_config%" >nul

if %errorlevel% equ 0 (
  echo Lines already exist in "%streamlit_config%". Skipping update.
) else (
  echo [browser]>>"%streamlit_config%"
  echo gatherUsageStats = false>>"%streamlit_config%"
  echo Lines added to "%streamlit_config%".
)

REM Replace the directory value and category string in the YAML file
setlocal enableDelayedExpansion
(for /f "tokens=1,* delims=:" %%a in (config.yml) do (
    set "line=%%b"
    if "%%a"=="default_directory" if not "%%b"=="" set "line= %default_directory%"
    if "%%a"=="default_categories" if not "%%b"=="" set "line= %default_categories%"
    echo %%a:!line!
)) > config.tmp
move /y config.tmp config.yml

REM Confirm that the directory was replaced in the file
echo The directory value in config.yml has been updated to "%default_directory%" and the default categories have been set to %categories%
pause