@echo off
echo Setting up Python virtual environment and installing dependencies...

REM Set up virtual environment
python -m venv venv

REM Activate virtual environment
call venv\Scripts\activate

REM Upgrade pip
pip install --upgrade pip

REM Install required packages
pip install -r requirements.txt

REM Download Chromium for Windows
echo Downloading Chromium for Windows...
curl -o chrome-win.zip https://www.googleapis.com/download/storage/v1/b/chromium-browser-snapshots/o/Win%2F901912%2Fchrome-win.zip?alt=media

REM Extract Chromium
echo Extracting Chromium...
tar -xf chrome-win.zip

REM Set CHROME_PATH environment variable
set CHROME_PATH=%cd%\chrome-win\chrome.exe

echo Setup completed successfully.
