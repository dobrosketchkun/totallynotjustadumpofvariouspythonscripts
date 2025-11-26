@echo off
setlocal enabledelayedexpansion

rem ============================================
rem Resilient video concatenation
rem Handles: different fps, codecs, sample rates, AND missing audio
rem ============================================

rem ============================================
rem CONFIGURATION - Edit only this section
rem ============================================
set TARGET_FPS=30
set TARGET_RES=720x1280
set TARGET_AR=44100
set OUT=combined.mp4

rem List your source videos here (space-separated)
set SOURCE_FILES=1.mp4 2.mp4 3.mp4 4.mp4 5.mp4 6.mp4

rem ============================================
rem Step 1: Normalize all source videos
rem Uses anullsrc to add silent audio if input has none
rem ============================================

echo.
echo Normalizing videos to common format...
echo.

for %%F in (%SOURCE_FILES%) do (
    echo Processing %%F...
    
    rem Check if file has audio stream by counting audio streams
    for /f %%A in ('ffprobe -v error -select_streams a -show_entries stream^=index -of csv^=p^=0 "%%F" 2^>nul ^| find /c /v ""') do set AUDIO_COUNT=%%A
    
    if !AUDIO_COUNT! EQU 0 (
        echo   - No audio detected, adding silent track...
        ffmpeg -y -i "%%F" -f lavfi -i anullsrc=r=!TARGET_AR!:cl=stereo -c:v libx264 -crf 18 -preset fast -r !TARGET_FPS! -s !TARGET_RES! -c:a aac -ar !TARGET_AR! -ac 2 -b:a 192k -map 0:v:0 -map 1:a:0 -shortest "%%~nFa.mp4"
    ) else (
        echo   - Audio detected, normalizing...
        ffmpeg -y -i "%%F" -c:v libx264 -crf 18 -preset fast -r !TARGET_FPS! -s !TARGET_RES! -c:a aac -ar !TARGET_AR! -ac 2 -b:a 192k "%%~nFa.mp4"
    )
)

rem ============================================
rem Step 2: Create concat list from source files
rem ============================================
set LISTFILE=concat_list.txt
if exist %LISTFILE% del %LISTFILE%

for %%F in (%SOURCE_FILES%) do (
    echo file '%%~nFa.mp4'>>%LISTFILE%
)

rem ============================================
rem Step 3: Concatenate (safe to stream-copy now)
rem ============================================
if exist %OUT% del %OUT%

echo.
echo Concatenating normalized videos...
ffmpeg -f concat -safe 0 -i %LISTFILE% -c copy %OUT%

rem ============================================
rem Cleanup temp files
rem ============================================
del %LISTFILE%
for %%F in (%SOURCE_FILES%) do (
    del "%%~nFa.mp4" 2>nul
)

echo.
echo Done. Output: %OUT%
pause
