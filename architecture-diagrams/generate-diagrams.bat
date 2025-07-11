@echo off
echo Installing dependencies...
pip install -r requirements.txt

echo Generating current architecture diagram...
python current-architecture.py

echo Generating future architecture diagram...
python future-architecture.py

echo.
echo ✅ Architecture diagrams generated successfully!
echo Files created:
echo - pupper-current-architecture.png
echo - pupper-future-architecture.png
echo.
pause