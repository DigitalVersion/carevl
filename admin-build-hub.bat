@echo off
uv run python scripts\build_hub_duckdb.py
if errorlevel 1 (
    echo.
    echo [CareVL Admin] Xay hub DuckDB that bai.
    pause
    exit /b 1
)
echo.
echo [CareVL Admin] Da xay hub DuckDB thanh cong.
pause
