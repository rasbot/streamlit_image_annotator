@echo off
set /p default_directory=Please enter a default directory path: 
set /p options=Set default options buttons. See the README for more info. Hit enter to use defaults "keep, delete, fix, other" or provide a comma separated list here: 
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

REM Replace the directory value in the YAML file
setlocal enableDelayedExpansion
(for /f "tokens=1,* delims=:" %%a in (config.yml) do (
    set "line=%%b"
    if "%%a"=="default_directory" if not "%%b"=="" set "line= %default_directory%"
    if "%%a"=="json_path" set "line= %default_directory%\annotations.json"
    if "%%a"=="options" set "line= %options%"
    echo %%a:!line!
)) > config.tmp
move /y config.tmp config.yml

REM Confirm that the directory was replaced in the file
echo The directory value in config.yml has been updated to "%default_directory%" and the default options have been set to %options%
pause