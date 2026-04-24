@echo off
uv run python scripts\check_runtime_branches.py
if errorlevel 1 (
    echo.
    echo [CareVL Admin] Kiem tra branch runtime DB that bai.
    pause
    exit /b 1
)
echo.
echo [CareVL Admin] Da kiem tra branch runtime DB xong.
pause
