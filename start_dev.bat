@echo off
echo =================================================================
echo                 Starting Genius Dev Environment
echo =================================================================
echo.
echo Launching DevWatch in a new command prompt...
start "Genius DevWatch" cmd /k "python devwatch.py"
echo.
echo Launching Streamlit App...
streamlit run app.py --server.runOnSave true --server.fileWatcherType watchdog
pause
