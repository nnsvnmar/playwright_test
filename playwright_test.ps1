Set-Location "C:\workspace\playwright_test"

& ".\.venv\Scripts\Activate.ps1"

pytest -m "desktop or mobile" -s --browser=chrome --device=none