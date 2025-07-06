pyinstaller --noconfirm --onefile --windowed otoczkaWypukla-v4.py
move /Y dist\otoczkaWypukla-v4.exe .
rd /S /Q dist
rd /S /Q build
del otoczkaWypukla-v4.spec